"""Scoring: hidden tests, project gate, and best-effort keyword checks.

The keyword checks are explicitly *not* a substitute for reading the answer.
Every result carries score_source="auto_keyword" and needs_human_review=true.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------- process helper
def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, check=False)
    else:
        proc.kill()


def _decode(raw: bytes) -> str:
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", "replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", "replace")


def run_capture(cmd: list[str], cwd: Path, timeout: int, env: dict[str, str]) -> tuple[int, str, bool]:
    """Run a local command, kill the whole tree on timeout, merge stdout+stderr."""
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    timed_out = False
    try:
        raw, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_tree(proc)
        try:
            raw, _ = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            raw = b""
    return proc.returncode, _decode(raw), timed_out


# ---------------------------------------------------------------- scoring config
def load_scoring(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.get("tasks")
    if not isinstance(tasks, dict):
        raise ValueError(f"{path}: missing 'tasks' object")
    for name, cfg in tasks.items():
        if "gate_cmd" not in cfg:
            raise ValueError(f"{path}: tasks.{name}.gate_cmd is required")
        # Hidden tests are optional (LMA tasks are gated by the project gate only).
        if cfg.get("hidden_src") and "hidden_cmd" not in cfg:
            raise ValueError(f"{path}: tasks.{name}.hidden_cmd is required when hidden_src is set")
    return data


def to_wsl_path(path: Path | str) -> str:
    text = os.path.abspath(str(path))
    drive, rest = os.path.splitdrive(text)
    if drive:
        return "/mnt/" + drive[0].lower() + rest.replace("\\", "/")
    return text.replace("\\", "/")


def _quote_single(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def command_context(run_dir: Path, python_cmd: str) -> dict[str, str]:
    wsl_dir = to_wsl_path(run_dir)
    return {
        "dir": str(run_dir),
        "wsl_dir": wsl_dir,
        "wsl_dir_q": _quote_single(wsl_dir),
        "python": python_cmd,
        "shim": str(Path(__file__).resolve().parent / "shim"),
    }


def render_cmd(template: list[str] | str, ctx: dict[str, str]) -> list[str]:
    parts = [template] if isinstance(template, str) else template
    return [str(part).format(**ctx) for part in parts]


# ---------------------------------------------------------------- parsers
def parse_unittest(text: str) -> tuple[int | None, int | None]:
    """Return (passed, total) from `python -m unittest -v` output."""
    match = re.search(r"^Ran (\d+) tests? in ", text, re.M)
    if not match:
        return None, None
    total = int(match.group(1))
    failures = re.search(r"failures=(\d+)", text)
    errors = re.search(r"errors=(\d+)", text)
    failed = int(failures.group(1)) if failures else 0
    errored = int(errors.group(1)) if errors else 0
    return max(total - failed - errored, 0), total


def parse_cargo(text: str) -> tuple[int | None, int | None]:
    """Sum every `test result: ...` line (a run may compile several test targets)."""
    passed = failed = 0
    seen = False
    for match in re.finditer(r"test result: \w+\. (\d+) passed; (\d+) failed;", text):
        seen = True
        passed += int(match.group(1))
        failed += int(match.group(2))
    if not seen:
        return None, None
    return passed, passed + failed


def parse_counts(parser: str, text: str) -> tuple[int | None, int | None]:
    if parser == "cargo":
        return parse_cargo(text)
    return parse_unittest(text)


# ---------------------------------------------------------------- hidden test / gate
def run_gate(cfg: dict[str, Any], run_dir: Path, timeout: int, env: dict[str, str],
             python_cmd: str) -> dict[str, Any]:
    ctx = command_context(run_dir, python_cmd)
    cmd = render_cmd(cfg["gate_cmd"], ctx)
    rc, output, timed_out = run_capture(cmd, run_dir, timeout, env)
    lines = [line for line in output.splitlines() if line.strip()]
    tail = "\n".join(lines[-5:])[-800:]
    passed = (rc == 0) and not timed_out
    marker = cfg.get("gate_ok")
    if passed and marker and marker not in output:
        passed = False
    return {
        "passed": passed,
        "exit_code": rc,
        "timed_out": timed_out,
        "tail": tail,
    }


def run_hidden(cfg: dict[str, Any], hidden_src: Path, run_dir: Path, timeout: int,
               env: dict[str, str], python_cmd: str) -> dict[str, Any]:
    dest = run_dir / cfg["hidden_dest"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup = dest.read_bytes() if dest.exists() else None
    try:
        shutil.copyfile(hidden_src, dest)
        ctx = command_context(run_dir, python_cmd)
        ctx["hidden_dest"] = cfg["hidden_dest"]
        cmd = render_cmd(cfg["hidden_cmd"], ctx)
        rc, output, timed_out = run_capture(cmd, run_dir, timeout, env)
    finally:
        if backup is not None:
            dest.write_bytes(backup)
        else:
            try:
                dest.unlink()
            except OSError:
                pass
    parser = cfg.get("parser", "unittest")
    passed, total = parse_counts(parser, output)
    return {
        "pass": passed if passed is not None else 0,
        "total": total,
        "ok": bool(total) and passed == total,
        "exit_code": rc,
        "timed_out": timed_out,
        "parser": parser,
        "tail": "\n".join([line for line in output.splitlines() if line.strip()][-8:])[-1200:],
    }


# ---------------------------------------------------------------- keyword checks
_CODE_SPECS: dict[str, dict[str, Any]] = {
    "kod1": {
        "bugs": {
            "median": [r"n\s*//\s*2\s*-\s*1", r"IndexError"],
            "binary_search": [r"lo\s*<=\s*hi", r"<=\s*hi", r"while\s+lo\s*<="],
            "chunk": [r"range\(\s*0", r"range\s*\(\s*0"],
            "merge_config": [r"mutable", r"default", r"override", r"paylaş"],
            "last_n": [r"n\s*==\s*0", r"n\s*=\s*0", r"-\s*0", r"boş", r"empty"],
        },
        "traps": ["is_leap", "apply_discount"],
        "optional": [],
    },
    "kod2": {
        "bugs": {
            "LRUCache": [r"move_to_end"],
            "increment": [r"lock", r"kilit", r"with\s+self"],
            "page": [r"-\s*1|\-\s*1", r"zero-based|0-based", r"offset"],
            "mean_of_positive": [r"list\(", r"generator", r"tüket", r"count"],
            "is_expired": [r"timezone", r"aware", r"utc"],
        },
        "traps": ["merge_intervals", "retry", "utc_now"],
        "optional": {"round_half_even_cents": [r"Decimal", r"float"]},
    },
}

_FACT_KEYS = {
    "belge1": {"3", "6", "8", "11"},
    "belge2": {"5", "6", "8", "11", "12"},
}
_WRONG_WORDS = re.compile(r"yanlış|hatalı|wrong|incorrect|değil|false", re.I)


def _window(text: str, needle: str, radius: int = 450) -> str:
    pos = text.lower().find(needle.lower())
    if pos < 0:
        return ""
    return text[max(0, pos - radius):pos + radius]


def _code_review_score(task: str, answer: str) -> dict[str, Any]:
    spec = _CODE_SPECS[task]
    checks: dict[str, bool] = {}
    details: dict[str, str] = {}
    for name, hints in spec["bugs"].items():
        window = _window(answer, name)
        hit = bool(window) and any(re.search(hint, window, re.I) for hint in hints)
        checks[name] = hit
        details[name] = "bug described" if hit else ("missing" if not window else "mentioned without fix")

    for name in spec["traps"]:
        window = _window(answer, name)
        if not window:
            checks[name] = False
            details[name] = "missing"
            continue
        flagged = re.search(r"\bBUG\b|hatalı|broken", window, re.I) is not None
        checks[name] = not flagged
        details[name] = "flagged as BUG (false positive)" if flagged else "correctly OK"

    optional_hits = {}
    for name, hints in (spec.get("optional") or {}).items():
        window = _window(answer, name)
        optional_hits[name] = bool(window) and any(re.search(hint, window, re.I) for hint in hints)

    required = [key for key in checks if key not in (spec.get("optional") or {})]
    score = sum(bool(checks[key]) for key in required) / len(required) if required else 0.0
    return {
        "score": round(score, 4),
        "checks": checks,
        "optional_checks": optional_hits,
        "details": details,
    }


def _fact_score(task: str, answer: str) -> dict[str, Any]:
    expected = _FACT_KEYS[task]
    predicted: set[str] = set()
    for line in answer.splitlines():
        if not _WRONG_WORDS.search(line):
            continue
        for match in re.finditer(r"(?<!\d)(\d{1,2})(?!\d)", line):
            number = str(int(match.group(1)))
            if 1 <= int(number) <= 12:
                predicted.add(number)
        for match in re.finditer(r"\bY\s*-?\s*(\d{1,2})\b", line, re.I):
            predicted.add(str(int(match.group(1))))
    hits = expected & predicted
    false_pos = predicted - expected
    raw = (len(hits) - 0.5 * len(false_pos)) / len(expected)
    return {
        "score": round(max(0.0, min(1.0, raw)), 4),
        "expected": sorted(expected, key=int),
        "predicted": sorted(predicted, key=lambda value: int(value)),
        "hits": sorted(hits, key=int),
        "false_positives": sorted(false_pos, key=lambda value: int(value)),
        "note": "Line-based number extraction; verify by hand.",
    }


def _ghost_score(answer: str) -> dict[str, Any]:
    low = answer.lower()
    correct_claim = re.search(
        r"(kod|fonksiyon).{0,80}(doğru|hatasız)|hata\s+yok|hatalı\s+değil|"
        r"no\s+bug|is\s+correct|works?\s+correctly|doğru\s+çalış", low, re.S) is not None
    merge_window = _window(answer, "merge_intervals")
    merge_explains = bool(merge_window) and (
        "<=" in merge_window or "dokunan" in merge_window.lower() or "touching" in merge_window.lower())
    leap_window = _window(answer, "is_leap")
    leap_explains = bool(leap_window) and "400" in leap_window and "2000" in leap_window
    bad_fix = False
    if "def merge_intervals" in low and "start <=" not in low:
        bad_fix = True
    if "def is_leap" in low and "% 400" not in low:
        bad_fix = True
    checks = {
        "says_code_is_correct": correct_claim,
        "explains_touching_intervals": merge_explains,
        "explains_400_rule": leap_explains,
        "no_bogus_rewrite": not bad_fix,
    }
    return {
        "score": round(sum(checks.values()) / len(checks), 4),
        "checks": checks,
        "note": "Two wrong-complaint prompts were concatenated into one run.",
    }


# ---------------------------------------------------------------- number answers (zor)
# Expected answers are copied verbatim from _kit/zor-test.py; the prompts ask for
# one number, so the *last* number in the answer is the model's final answer.
EXPECTED_NUMBERS = {"zor1": "460", "zor2": "1695", "zor3": "5019"}
_NUMBER = re.compile(r"(?<![\d.])(-?\d[\d,_]*)(?![\d])")


def number_score(task: str, answer: str) -> dict[str, Any]:
    expected = EXPECTED_NUMBERS[task]
    found = None
    for match in _NUMBER.finditer(answer):
        found = match.group(1).replace(",", "").replace("_", "")
    exact = found == expected
    return {
        "score": 1.0 if exact else 0.0,
        "expected": expected,
        "found": found,
        "auto_exact": exact,
        "note": "Compares the last number in the answer with the expected value.",
    }


def keyword_score(task: str, answer: str) -> dict[str, Any]:
    """Best-effort automatic scoring; always flagged for human review."""
    if task in EXPECTED_NUMBERS:
        detail = number_score(task, answer)
    elif task in ("kod1", "kod2"):
        detail = _code_review_score(task, answer)
    elif task in ("belge1", "belge2"):
        detail = _fact_score(task, answer)
    elif task == "ghost":
        detail = _ghost_score(answer)
    else:
        detail = {"score": 0.0, "note": "no keyword rule"}
    detail.update({
        "score_source": "auto_keyword",
        "needs_human_review": True,
        "answer_chars": len(answer),
    })
    return detail
