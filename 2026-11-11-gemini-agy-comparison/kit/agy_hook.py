"""PreToolUse isolation hook for the Antigravity (AGY) arms.

AGY runs the command in `<run_dir>/.agents/hooks.json` through `cmd /c` with
cwd = `<run_dir>/.agents` (the folder containing hooks.json).  It receives the
hook payload as JSON on stdin (camelCase keys, including
`toolCall: {name, args}`, `cwd`, `workspacePaths`) and must print exactly one
JSON object on stdout:

    {"decision": "allow"}
    {"decision": "deny", "reason": "..."}

Invocation (written by bench_config.write_agy_hooks):

    py -3 -I <abs path to agy_hook.py> <mode> <abs run_dir>

`mode` is `agent` (deny browser/web/url/search tools, paths that resolve
outside run_dir -- Windows, UNC, WSL/Unix, `..`, `~`, `%VAR%` -- and the WSL
bridge, environment-variable and folder-lookup escapes; allow the rest) or `notool` (deny every tool).  Every decision
is appended as one JSON line to `<run_dir>/.agents/hook-log.jsonl`.

Fail closed: a malformed payload, an unknown mode, a missing tool name or an
unreadable run directory all produce a deny.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MODES = ("agent", "notool")

# Tool names matching this are denied in agent mode.
DENY_NAME = re.compile(r"browser_|web|url|search", re.I)

# Absolute Windows paths inside free text or a parameter value.
WIN_ABS = re.compile(r"(?<![\w])([A-Za-z]:[\\/][^\s\"'<>|;]*)")
UNC_ABS = re.compile(r"(\\\\[^\s\"'<>|;]+)")
# `..\` / `../` used as a path component.
TRAVERSAL = re.compile(r"(?:^|[\s\"'=:;])\.\.[\\/]")
TOKEN_SPLIT = re.compile(r"[\s\"'=:;]+")
# A bare `..` argument (`cd ..`, `Set-Location ..`); `0..10` and `a..b` are not matched.
BARE_DOTDOT = re.compile(r"(?:^|[\s\"'=;(,])\.\.(?=$|[\s\"';),|])")
# `~` as the home directory (`cd ~`, `~/x`, `~\x`).
TILDE = re.compile(r"(?:^|[\s\"'=;(,])~(?=$|[\/\s\"';),])")
# Unix absolute paths into a Linux (WSL) filesystem.
UNIX_ABS = re.compile(
    r"(?:^|[\s\"'=;(,])(/(?:home|mnt|root|etc|usr|tmp|var|opt|proc|dev|srv|run|boot|sys|snap|lib|lib64|bin|sbin|media)(?=$|[/\s\"';),|])[^\s\"'<>|;]*)")
# Commands and APIs that reach outside the run folder without a literal path:
# the WSL bridge and Linux shells, and .NET/PowerShell folder lookups.
ESCAPE_CMD = re.compile(
    r"(?:^|[\s\"'=;(&|,])(wsl|wsl\.exe|bash\.exe|wslpath)(?=$|[\s\"';)&|,])"
    r"|GetFolderPath|GetTempPath|GetEnvironmentVariable|\$PSHOME|\$HOME\b|\$PROFILE\b|\$env:|\$\{env:",
    re.I)
# `%NAME%` (cmd) environment references; expanded and checked like a literal path.
CMD_ENV = re.compile(r"%([A-Za-z_][A-Za-z0-9_()]*)%")


# ---------------------------------------------------------------- paths
def _norm(path: str) -> str | None:
    try:
        return os.path.normcase(os.path.realpath(str(path)))
    except (OSError, ValueError):
        return None


def _inside(path: str, run_root: str) -> bool:
    """True when path (already or about to be resolved) stays inside run_root."""
    resolved = _norm(path)
    if resolved is None:
        return False
    return resolved == run_root or resolved.startswith(run_root + os.sep)


def _iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def outside_paths(args, run_root: str) -> list[str]:
    """Absolute paths in tool args that resolve outside run_root."""
    findings: list[str] = []
    for raw in _iter_strings(args):
        escape = ESCAPE_CMD.search(raw)
        if escape:
            findings.append(escape.group(0).strip(" \"';=(&|,"))
        for match in UNIX_ABS.findall(raw):
            findings.append(match)
        if TILDE.search(raw):
            findings.append("~ (home directory)")
        if BARE_DOTDOT.search(raw) and not _inside(os.path.join(run_root, ".."), run_root):
            findings.append(".. (parent directory)")
        text = CMD_ENV.sub(lambda m: os.environ.get(m.group(1), m.group(0)), raw)
        for pattern in (WIN_ABS, UNC_ABS):
            for match in pattern.findall(text):
                if match and not _inside(match, run_root):
                    findings.append(match)
        if TRAVERSAL.search(text):
            for token in TOKEN_SPLIT.split(text):
                if ".." not in token:
                    continue
                if not _inside(os.path.join(run_root, token), run_root):
                    findings.append(token)
        if len(findings) >= 20:
            return findings
    return findings


# ---------------------------------------------------------------- logging
def log_decision(run_dir: Path | None, record: dict) -> None:
    if run_dir is None:
        return
    try:
        path = Path(run_dir) / ".agents" / "hook-log.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except OSError:
        # A log failure must never change the decision.
        pass


# ---------------------------------------------------------------- decision
def decide(mode: str, run_dir: Path, payload: dict, tool: str) -> tuple[bool, str]:
    if mode == "notool":
        return False, f"no-tool task: every tool is denied ({tool})"
    if DENY_NAME.search(tool):
        return False, f"tool {tool} is not allowed: browser, web, url and search tools are disabled"
    run_root = _norm(str(run_dir))
    if not run_root:
        return False, "run directory cannot be resolved"
    call = payload.get("toolCall")
    args = call.get("args") if isinstance(call, dict) else None
    findings = outside_paths(args if args is not None else {}, run_root)
    if findings:
        return False, "path outside the run folder: " + ", ".join(findings[:3])
    return True, "allowed"


def _preview(payload: dict | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    call = payload.get("toolCall")
    if not isinstance(call, dict) or "args" not in call:
        return None
    try:
        text = json.dumps(call.get("args"), ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "<unserialisable>"
    return text[:1000]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    mode = args[0] if args else ""
    run_dir: Path | None = None
    if len(args) > 1:
        try:
            run_dir = Path(args[1])
        except (OSError, ValueError):
            run_dir = None

    decision = "deny"
    reason = "fail closed"
    tool: str | None = None
    payload = None

    try:
        # Read bytes: the payload is UTF-8 regardless of the console code page.
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        payload = json.loads(raw)
    except (ValueError, OSError) as error:
        payload = None
        reason = f"malformed hook payload: {error}"
    else:
        if not isinstance(payload, dict):
            payload = None
            reason = "malformed hook payload: not a JSON object"

    if payload is not None:
        call = payload.get("toolCall")
        if isinstance(call, dict):
            name = call.get("name")
            if isinstance(name, str) and name:
                tool = name
        if mode not in MODES:
            reason = f"unknown hook mode: {mode!r}"
        elif run_dir is None:
            reason = "run directory argument missing"
        elif tool is None:
            reason = "malformed hook payload: tool name missing"
        else:
            allowed, reason = decide(mode, run_dir, payload, tool)
            decision = "allow" if allowed else "deny"

    log_decision(run_dir, {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "mode": mode,
        "tool": tool,
        "decision": decision,
        "reason": reason,
        "args_preview": _preview(payload),
    })

    output: dict[str, str] = {"decision": decision}
    if decision != "allow":
        output["reason"] = reason
    data = (json.dumps(output, ensure_ascii=False) + "\n").encode("utf-8")
    try:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    except (AttributeError, OSError):
        sys.stdout.write(data.decode("utf-8"))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
