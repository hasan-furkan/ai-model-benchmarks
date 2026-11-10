"""Parse OpenCode `--format json` event streams and recover usage.

The stream observed on this machine contains both snake_case and kebab-case
mirrors of the same event (for example `step_start` and `step-start` with the
same `part.id`), and older harnesses redirected stderr into the same file, so
every event is de-duplicated before it is counted.  Ignoring this doubles the
cost and token totals.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------- reading
def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or (b"\x00" in raw[:400]):
        text = raw.decode("utf-16", "replace")
    else:
        text = raw.decode("utf-8-sig", "replace")
    events: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def part_of(event: dict[str, Any]) -> dict[str, Any]:
    part = event.get("part")
    return part if isinstance(part, dict) else {}


def kind_of(event: dict[str, Any]) -> str:
    value = event.get("type")
    if isinstance(value, str) and value:
        return value
    value = part_of(event).get("type")
    return value if isinstance(value, str) else ""


def dedupe_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop mirrored duplicates while keeping first-seen order."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for event in events:
        part = part_of(event)
        pid = part.get("id") or event.get("id")
        if pid:
            key = f"{kind_of(event)}|{pid}|{event.get('timestamp')}"
        else:
            blob = json.dumps(event, sort_keys=True, ensure_ascii=False, default=str)
            key = "raw|" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(event)
    return out


# ---------------------------------------------------------------- session id / directory
def extract_session_id(events: list[dict[str, Any]]) -> str | None:
    for event in events:
        for key in ("sessionID", "sessionId"):
            value = event.get(key)
            if isinstance(value, str) and value:
                return value
        value = event.get("session")
        if isinstance(value, dict):
            for key in ("id", "sessionID", "sessionId"):
                if isinstance(value.get(key), str):
                    return value[key]
        value = part_of(event).get("sessionID")
        if isinstance(value, str) and value:
            return value
    return None


def event_session_dirs(events: list[dict[str, Any]]) -> list[str]:
    """Directories the stream itself names (cwd/directory/workdir only)."""
    found: list[str] = []
    for event in events:
        containers = [event]
        for key in ("session", "info", "project"):
            if isinstance(event.get(key), dict):
                containers.append(event[key])
        for container in containers:
            for key in ("cwd", "directory", "workdir"):
                value = container.get(key)
                if isinstance(value, str) and value and value not in found:
                    found.append(value)
    return found


# ---------------------------------------------------------------- usage / steps
def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _message_key(event: dict[str, Any]) -> str:
    part = part_of(event)
    return str(part.get("messageID") or event.get("messageID") or part.get("id") or "")


def parse_step_usage(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Sum step-finish usage and count steps.

    Returns zeros when the stream has no finish event; callers decide whether
    to fall back to the session database.
    """
    starts: list[str] = []
    finishes: list[str] = []
    input_tokens = output_tokens = reasoning_tokens = 0
    cache_read = cache_write = 0
    cost = 0.0
    finish_count = 0

    for event in events:
        kind = kind_of(event)
        part = part_of(event)
        if kind in ("step_start", "step-start") or part.get("type") == "step-start":
            starts.append(_message_key(event))
        elif kind in ("step_finish", "step-finish") or part.get("type") == "step-finish":
            finishes.append(_message_key(event))
            finish_count += 1
            tokens = part.get("tokens")
            if not isinstance(tokens, dict):
                tokens = event.get("tokens") if isinstance(event.get("tokens"), dict) else {}
            cache = tokens.get("cache") if isinstance(tokens.get("cache"), dict) else {}
            input_tokens += _as_int(tokens.get("input"))
            output_tokens += _as_int(tokens.get("output"))
            reasoning_tokens += _as_int(tokens.get("reasoning"))
            cache_read += _as_int(cache.get("read"))
            cache_write += _as_int(cache.get("write"))
            cost += float(part.get("cost") or event.get("cost") or 0.0)

    started = {key for key in starts if key}
    finished = {key for key in finishes if key}
    missing_final = bool(started - finished) if started else finish_count == 0
    total = input_tokens + cache_read + cache_write + output_tokens + reasoning_tokens

    return {
        "steps": len([key for key in starts if key]) if starts else finish_count,
        "step_finish_events": finish_count,
        "input_tokens": input_tokens,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total,
        "cost_usd": round(cost, 10),
        "missing_final_step_usage": missing_final,
    }


def parse_tool_calls(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalise tool calls from both event dialects."""
    calls: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event in events:
        kind = kind_of(event)
        part = part_of(event)
        name = tool_input = None
        call_id = None
        if kind == "tool_use" and part.get("type") == "tool":
            name = part.get("tool")
            state = part.get("state") if isinstance(part.get("state"), dict) else {}
            tool_input = state.get("input")
            call_id = part.get("id") or part.get("partID")
        elif kind == "tool_call":
            name = event.get("tool") or part.get("tool")
            tool_input = event.get("input") if "input" in event else part.get("input")
            call_id = event.get("callId") or event.get("id") or part.get("id")
        if not isinstance(name, str) or not name:
            continue
        if call_id and str(call_id) in seen:
            continue
        if call_id:
            seen.add(str(call_id))
        calls.append({
            "tool": name,
            "input": tool_input if isinstance(tool_input, (dict, list, str)) else {},
        })
    return calls


def parse_errors(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Collect explicit error events only; stderr is recorded separately."""
    errors: list[dict[str, str]] = []
    for event in events:
        kind = kind_of(event)
        part = part_of(event)
        if kind != "error" and part.get("type") != "error":
            # Some versions signal failure through a status phase.
            if not (kind == "status" and str(event.get("phase", "")).lower() in ("error", "failed")):
                continue
        message = _error_message(event)
        errors.append({"type": kind or "error", "message": message[:300]})
    return errors


def _error_message(event: dict[str, Any]) -> str:
    candidates: list[Any] = []
    part = part_of(event)
    for container in (event, part):
        candidates.append(container.get("message"))
        error = container.get("error")
        if isinstance(error, str):
            candidates.append(error)
        elif isinstance(error, dict):
            candidates.append(error.get("message"))
            data = error.get("data")
            if isinstance(data, dict):
                candidates.append(data.get("message"))
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return json.dumps(event, ensure_ascii=False, default=str)


def answer_text(events: list[dict[str, Any]]) -> str:
    """All assistant text parts, in order, joined by blank lines."""
    chunks: list[str] = []
    for event in events:
        kind = kind_of(event)
        part = part_of(event)
        if kind == "text" or part.get("type") == "text":
            text = part.get("text") if isinstance(part.get("text"), str) else event.get("text")
            if isinstance(text, str) and text:
                chunks.append(text)
    return "\n\n".join(chunks)


def final_message_text(events: list[dict[str, Any]]) -> str:
    """Text of the last assistant message only.

    Last-line contract rules (ENDPOINT:, ROOT CAUSE:, RESULT:, ASSUMPTIONS:) are
    checked here, so earlier narration in the transcript cannot satisfy them.
    """
    order: list[str] = []
    texts: dict[str, list[str]] = {}
    for index, event in enumerate(events):
        kind = kind_of(event)
        part = part_of(event)
        if kind != "text" and part.get("type") != "text":
            continue
        text = part.get("text") if isinstance(part.get("text"), str) else event.get("text")
        if not isinstance(text, str) or not text:
            continue
        key = str(part.get("messageID") or event.get("messageID") or f"#{index}")
        if key not in texts:
            texts[key] = []
            order.append(key)
        texts[key].append(text)
    if not order:
        return ""
    return "\n\n".join(texts[order[-1]])


# ---------------------------------------------------------------- session database fallback
def _env_dir(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None


DB_CANDIDATES = [
    Path.home() / ".local" / "share" / "opencode" / "opencode.db",
    *[base / "opencode" / "opencode.db" for base in
      (_env_dir("LOCALAPPDATA"), _env_dir("APPDATA")) if base is not None],
    Path.home() / ".opencode" / "opencode.db",
]
DB_TABLES = ("session_v2", "session")


def find_session_db() -> Path | None:
    for path in DB_CANDIDATES:
        try:
            if path.is_file():
                return path
        except OSError:
            continue
    return None


def read_session_row(session_id: str | None, db_path: Path | None = None) -> dict[str, Any] | None:
    """Return {column: value} for the session, or None.  Never raises."""
    if not session_id:
        return None
    path = db_path or find_session_db()
    if not path:
        return None
    try:
        conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True, timeout=3)
    except sqlite3.Error:
        return None
    try:
        conn.row_factory = sqlite3.Row
        for table in DB_TABLES:
            try:
                row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (session_id,)).fetchone()
            except sqlite3.Error:
                continue
            if row is not None:
                result = {key: row[key] for key in row.keys()}
                # Some OpenCode versions keep the working directory only in the
                # project table that the session points at.
                project_id = result.get("project_id") or result.get("projectID")
                if project_id and not any(key in result for key in DIRECTORY_COLUMNS):
                    try:
                        prow = conn.execute("SELECT * FROM project WHERE id = ?",
                                            (project_id,)).fetchone()
                    except sqlite3.Error:
                        prow = None
                    if prow is not None:
                        for key in ("worktree", "directory", "path"):
                            if key in prow.keys() and prow[key] and key not in result:
                                result[key] = prow[key]
                return result
    finally:
        conn.close()
    return None


DIRECTORY_COLUMNS = ("directory", "worktree", "cwd", "dir", "path")


def row_directory(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    for key in DIRECTORY_COLUMNS:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def row_usage(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """Map a session row onto the token/cost field names used in runs.jsonl."""
    if not row:
        return None
    keys = set(row)
    if not ({"tokens_input", "tokens_output"} & keys):
        return None

    def pick(*names: str) -> int | None:
        for name in names:
            if name in keys and row[name] is not None:
                return _as_int(row[name])
        return None

    input_tokens = pick("tokens_input")
    output_tokens = pick("tokens_output")
    reasoning = pick("tokens_reasoning") or 0
    cache_read = pick("tokens_cache_read") or 0
    cache_write = pick("tokens_cache_write") or 0
    total = sum(value or 0 for value in (input_tokens, output_tokens, reasoning, cache_read, cache_write))
    cost = row.get("cost") if "cost" in keys else None
    return {
        "input_tokens": input_tokens,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning,
        "total_tokens": total,
        "cost_usd": float(cost) if isinstance(cost, (int, float)) else None,
    }


# ---------------------------------------------------------------- outside-folder detection
_WIN_ABS = re.compile(r"(?<![\w])([A-Za-z]:[\\/][^\s\"'<>|]*)")
_UNC_ABS = re.compile(r"(\\\\[^\s\"'<>|]+)")
_POSIX_ABS = re.compile(r"(?<![\w])/(?:mnt/[a-z]|home|tmp|usr|etc|opt|root|var|bin|sbin|lib|proc|sys)(?:/[^\s\"'<>|]*)?")
_HOME_ABS = re.compile(r"(?<![\w])(~[\\/][^\s\"'<>|]*)")
_TRAVERSAL = re.compile(r"(?:^|[\s\"'=:])\.\.[\\/]")


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def windows_view(path: str) -> str:
    """Map WSL/git-bash paths onto a Windows path so they can be compared."""
    match = re.match(r"^/mnt/([A-Za-z])/(.*)$", path)
    if match:
        return f"{match.group(1).upper()}:\\" + match.group(2).replace("/", "\\")
    match = re.match(r"^/([A-Za-z])/(.*)$", path)
    if match:
        return f"{match.group(1).upper()}:\\" + match.group(2).replace("/", "\\")
    return path


def _inside(path: str, run_dir: Path) -> bool:
    try:
        resolved = Path(windows_view(path))
    except (OSError, ValueError):
        return False
    try:
        resolved.resolve().relative_to(run_dir.resolve())
        return True
    except (OSError, ValueError, RuntimeError):
        return False


def find_outside_access(calls: list[dict[str, Any]], run_dir: Path) -> list[dict[str, str]]:
    """Every absolute path mentioned by a tool that resolves outside run_dir.

    Relative paths are assumed to resolve inside the run folder (the process
    cwd), which is what OpenCode does for tools.  The check is deliberately
    conservative: a path that cannot be resolved counts as outside.
    """
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for call in calls:
        tool = call["tool"]
        for text in _iter_strings(call.get("input")):
            if _TRAVERSAL.search(text):
                key = (tool, "..")
                if key not in seen:
                    seen.add(key)
                    findings.append({"tool": tool, "path": "../ (relative traversal)"})
            for pattern in (_WIN_ABS, _UNC_ABS, _POSIX_ABS, _HOME_ABS):
                for match in pattern.findall(text):
                    path = match
                    if not path or path in (".", ".."):
                        continue
                    if _inside(path, run_dir):
                        continue
                    key = (tool, path)
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append({"tool": tool, "path": path[:500]})
                    if len(findings) >= 100:
                        return findings
    return findings
