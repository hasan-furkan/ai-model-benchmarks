"""Model-comparison harness: 4 OpenCode arms x 9 tasks x 3 reps.

This file only *runs* models when invoked without --dry-run.  While writing and
reviewing the harness, use --dry-run: it validates every input and prints the
exact command forms without starting OpenCode.

Isolation contract
------------------
* Every run lives in %TEMP%\\mb-2026-11-09\\<run_id>, outside _benchmark.
* cwd and PWD both point at that folder (OpenCode reads the project from PWD).
* opencode.json permits edits/bash only for agent tasks; no-tool runs deny all.
* The harness records any tool call that names an absolute path outside the
  run folder as `outside_access`.
* The session directory is read back from the event stream and, when needed,
  from OpenCode's own session database; a mismatch/unknown marks the run invalid.

Usage
-----
    python kit/run_bench.py --dry-run
    python kit/run_bench.py --pilot
    python kit/run_bench.py --arms luna,deepseek --tasks stok,kod1 --reps 1
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bench_config as cfg
import cli_constraints
import events as evmod
import score as scoring


# ---------------------------------------------------------------- CLI
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--arms", default=",".join(cfg.ARMS),
                        help="comma-separated arms (default: all four)")
    parser.add_argument("--tasks", default=None,
                        help="task names or groups: all, agent, py, rs, cli, lma, notool, zor, ...")
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=None,
                        help="seconds per model run (default: 900, agent-lma 1800)")
    parser.add_argument("--score-timeout", type=int, default=None,
                        help="seconds for the gate / hidden test (default: 900, agent-lma 1800)")
    parser.add_argument("--pilot", action="store_true",
                        help="one rep, tasks stok and kod1, all selected arms")
    parser.add_argument("--seed", type=int, default=20261109)
    parser.add_argument("--runs-file", default=str(cfg.RESULTS / "runs.jsonl"))
    parser.add_argument("--scoring-config", default=str(cfg.KIT / "scoring.json"))
    parser.add_argument("--opencode-bin", default="opencode")
    parser.add_argument("--dry-run", action="store_true",
                        help="validate inputs and print the plan; never starts OpenCode")
    parser.add_argument("--force", action="store_true", help="re-run completed run_ids")
    parser.add_argument("--no-session-check", action="store_true",
                        help="do not invalidate runs whose session directory cannot be verified")
    return parser.parse_args(argv)


# ---------------------------------------------------------------- OpenCode resolution
def parse_cmd_shim(path: Path) -> list[str] | None:
    """Turn an npm .cmd shim into [node, script] so prompts never pass through cmd.exe.

    cmd.exe quoting is unsafe for prompts that contain quotes, ampersands or
    newlines, and OpenCode prompts do contain all three.
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None
    parent = path.parent
    node = parent / "node.exe"
    if not node.is_file():
        found = shutil.which("node")
        node = Path(found) if found else None

    candidates: list[Path] = []
    for match in re.finditer(r'"([^"\r\n]+)"', text):
        raw = match.group(1)
        if "node_modules" not in raw and "opencode" not in raw.lower():
            continue
        cleaned = (raw.replace("%~dp0\\", "").replace("%~dp0", "")
                   .replace("%dp0%\\", "").replace("%dp0%", ""))
        if "%" in cleaned:
            continue
        candidate = Path(cleaned.lstrip("\\/"))
        if not candidate.is_absolute():
            candidate = parent / candidate
        if candidate.is_file():
            candidates.append(candidate)

    # npm shims often point at an extensionless node script
    # (node_modules/opencode-ai/bin/opencode), so accept those too.
    scripts = [c for c in candidates if c.suffix.lower() in ("", ".js", ".mjs", ".cjs")]
    if node and scripts:
        return [str(node), str(scripts[-1])]
    return None


def resolve_opencode(bin_name: str) -> list[str] | None:
    if os.name != "nt":
        found = shutil.which(bin_name)
        return [found or bin_name]
    found = shutil.which(bin_name)
    if not found:
        for suffix in (".exe", ".cmd", ".bat", ".ps1"):
            found = shutil.which(bin_name + suffix)
            if found:
                break
    if not found:
        return None
    low = found.lower()
    if low.endswith(".exe"):
        return [found]
    if low.endswith((".cmd", ".bat")):
        parsed = parse_cmd_shim(Path(found))
        return parsed or ["cmd", "/c", found]
    if low.endswith(".ps1"):
        return ["powershell", "-NoProfile", "-File", found]
    return [found]


# ---------------------------------------------------------------- command / env
def build_command(base: list[str], arm: str, run_id: str, mode: str, prompt: str) -> list[str]:
    # Exactly the contracted form; run_id is carried by the session events and
    # the artifact folder, so no extra CLI flags are added.
    cmd = base + [
        "run", "--standalone", "--auto", "--format", "json",
        "-m", cfg.ARMS[arm]["model"],
    ]
    if mode == "agent":
        cmd += ["--file", "TASK.md", cfg.AGENT_INSTRUCTION]
    else:
        cmd.append(prompt)
    return cmd


def build_env(run_dir: Path, rust: bool = False) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items()
           if not re.match(r"(CLAUDE|ANTHROPIC|DEEPSEEK_WORKER)", key, re.I)}
    for key in ("PWD", "OLDPWD", "INIT_CWD"):
        env.pop(key, None)
    env["PWD"] = str(run_dir)
    env["OPENCODE_DISABLE_CLAUDE_CODE"] = "1"
    if rust:
        # cargo/clippy/fmt/audit/deny must reach WSL; only Rust groups get the shim
        # so a stray cargo.cmd never shadows a real tool for the Python tasks.
        env["PATH"] = str(cfg.SHIM) + os.pathsep + env.get("PATH", "")
    return env


def norm_path(value: str) -> str:
    return os.path.normcase(os.path.abspath(evmod.windows_view(value)))


def verify_session_dir(unique: list[dict[str, Any]], run_dir: Path,
                       row: dict[str, Any] | None) -> dict[str, Any]:
    found = list(evmod.event_session_dirs(unique))
    db_dir = evmod.row_directory(row)
    if db_dir:
        found.append(db_dir)
    source = []
    if evmod.event_session_dirs(unique):
        source.append("events")
    if db_dir:
        source.append("session_db")
    if not found:
        return {"verified": None, "source": [], "expected": str(run_dir), "found": []}
    expected = norm_path(str(run_dir))
    verified = any(norm_path(value) == expected for value in found)
    return {
        "verified": verified,
        "source": source,
        "expected": str(run_dir),
        "found": found[:5],
    }


# ---------------------------------------------------------------- small file helpers
def read_text_retry(path: Path, attempts: int = 6) -> str:
    for attempt in range(attempts):
        try:
            raw = path.read_bytes()
            if raw:
                if raw.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in raw[:400]:
                    return raw.decode("utf-16", "replace")
                return raw.decode("utf-8-sig", "replace")
        except OSError:
            pass
        time.sleep(0.25 * (attempt + 1))
    return ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- runner
class Runner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.arms = [a.strip() for a in args.arms.split(",") if a.strip()]
        if not self.arms:
            raise SystemExit("no arms selected")
        unknown = [a for a in self.arms if a not in cfg.ARMS]
        if unknown:
            raise SystemExit(f"unknown arm(s): {', '.join(unknown)}")
        self.tasks = cfg.PILOT_TASKS if args.pilot else cfg.resolve_tasks(args.tasks)
        self.reps = 1 if args.pilot else args.reps
        self.scoring = scoring.load_scoring(Path(args.scoring_config))
        self.python_cmd = self.scoring.get("python_cmd", "py -3")
        self.runs_file = Path(args.runs_file)
        self.baseline_hash = cfg.inputs_hash()
        self.stop = threading.Event()
        self.write_lock = threading.Lock()
        self.log_lock = threading.Lock()
        self.log_path = cfg.RESULTS / "run_log.txt"
        self.base_cmd = resolve_opencode(args.opencode_bin)
        self.completed = self._load_completed()
        self.runs_handle = None
        # LMA runs (Rust workspace + npm gate) are capped at 2 at a time.
        self.lma_sem = threading.Semaphore(cfg.LMA_MAX_PARALLEL)

    # -- per-group limits
    def timeout_for(self, group: str) -> int:
        if self.args.timeout is not None:
            return self.args.timeout
        return cfg.GROUP_TIMEOUTS.get(group, cfg.DEFAULT_TIMEOUT)

    def score_timeout_for(self, group: str) -> int:
        if self.args.score_timeout is not None:
            return self.args.score_timeout
        return cfg.GROUP_SCORE_TIMEOUTS.get(group, cfg.DEFAULT_SCORE_TIMEOUT)

    # -- logging
    def log(self, message: str) -> None:
        line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {message}"
        with self.log_lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()

    # -- plan
    def build_items(self) -> list[dict[str, Any]]:
        items = []
        for rep in range(1, self.reps + 1):
            for arm in self.arms:
                for task in self.tasks:
                    items.append({
                        "run_id": f"{task}-{arm}-r{rep}",
                        "task": task,
                        "group": cfg.group_of(task),
                        "arm": arm,
                        "rep": rep,
                    })
        random.Random(self.args.seed).shuffle(items)
        for index, item in enumerate(items):
            item["order_index"] = index
        return items

    def _load_completed(self) -> set[str]:
        done: set[str] = set()
        try:
            with open(self.runs_file, encoding="utf-8") as handle:
                for line in handle:
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(row, dict) and row.get("run_id"):
                        done.add(row["run_id"])
        except OSError:
            pass
        return done

    # -- validation shared by dry-run and real run
    def validate(self) -> list[str]:
        problems: list[str] = []
        if self.base_cmd is None:
            problems.append(f"opencode executable not found: {self.args.opencode_bin!r}")
        tasks = self.scoring.get("tasks", {})
        for task in self.tasks:
            if task not in cfg.AGENT_TASKS:
                continue
            if task not in tasks:
                problems.append(f"scoring.json has no entry for task {task!r}")
                continue
            entry = tasks[task]
            if entry.get("hidden_src"):
                hidden = cfg.ROOT / entry["hidden_src"]
                if not hidden.is_file():
                    problems.append(f"hidden test not found for {task}: {hidden}")
                if not entry.get("hidden_dest"):
                    problems.append(f"scoring.json has no hidden_dest for task {task!r}")
            fixture = cfg.fixture_dir(task)
            if fixture is None:
                if not (cfg.LMA_REPO / ".git").exists():
                    problems.append(f"LMA source repo not found: {cfg.LMA_REPO}")
                if not cfg.LMA_NODE_MODULES.is_dir():
                    problems.append(f"ui/node_modules not found: {cfg.LMA_NODE_MODULES}")
            elif not fixture.is_dir():
                problems.append(f"fixture not found for {task}: {fixture}")
            task_md = cfg.task_text_path(task)
            if not task_md.is_file():
                problems.append(f"task text not found for {task}: {task_md}")
        for task in self.tasks:
            if task in cfg.NOTOOL_TASKS:
                material = cfg.NOTOOL_TASKS[task]["material"]
                if material and not (cfg.KIT_SRC / "hata-testi" / material).is_file():
                    problems.append(f"prompt material not found for {task}: {material}")
        return problems

    def print_dry_run(self, items: list[dict[str, Any]]) -> None:
        print(f"bench root      : {cfg.BENCH}")
        print(f"run folders     : {cfg.RUNS_ROOT / '<run_id>'}")
        print(f"arms            : {', '.join(self.arms)}")
        print(f"tasks           : {', '.join(self.tasks)}")
        print(f"reps            : {self.reps}")
        timeout_text = (f"{self.args.timeout}s" if self.args.timeout is not None
                        else f"{cfg.DEFAULT_TIMEOUT}s, agent-lma {cfg.GROUP_TIMEOUTS['agent-lma']}s")
        print(f"planned runs    : {len(items)}  (parallel={self.args.parallel}, "
              f"lma<= {cfg.LMA_MAX_PARALLEL}, timeout={timeout_text})")
        print(f"inputs hash     : {self.baseline_hash}")
        print(f"opencode        : {self.base_cmd}")
        print(f"session check   : {'off' if self.args.no_session_check else 'on'}")
        print()
        if items:
            print("first 12 run_ids in execution order:")
            for item in items[:12]:
                print(f"  {item['order_index']:03d}  {item['run_id']:<24} {cfg.ARMS[item['arm']]['model']}")
            print()
        # Show one command per mode without executing anything.
        for mode, task in (("agent", next((t for t in self.tasks if t in cfg.AGENT_TASKS), None)),
                           ("notool", next((t for t in self.tasks if t in cfg.NOTOOL_TASKS), None))):
            if not task:
                continue
            if mode == "agent":
                prompt_len = len(cfg.build_agent_task_text(task))
                sample = build_command(self.base_cmd or ["opencode"], self.arms[0],
                                       f"{task}-{self.arms[0]}-r1", mode, "")
            else:
                prompt_len = len(cfg.build_no_tool_prompt(task))
                sample = build_command(self.base_cmd or ["opencode"], self.arms[0],
                                       f"{task}-{self.arms[0]}-r1", mode, "<PROMPT>")
            rendered = " ".join(sample[:-1]) + f" <prompt: {prompt_len} chars>"
            print(f"{mode} command  : {rendered}")
        print()
        for task in self.tasks:
            if task not in cfg.AGENT_TASKS:
                continue
            entry = self.scoring["tasks"].get(task)
            if not entry:
                continue
            ctx = scoring.command_context(cfg.RUNS_ROOT / f"{task}-{self.arms[0]}-r1", self.python_cmd)
            ctx["hidden_dest"] = entry.get("hidden_dest", "")
            print(f"{task} gate    : {' '.join(scoring.render_cmd(entry['gate_cmd'], ctx))}")
            if entry.get("hidden_src"):
                print(f"{task} hidden  : {' '.join(scoring.render_cmd(entry['hidden_cmd'], ctx))}")

    # -- one run
    def execute(self, item: dict[str, Any]) -> None:
        if self.stop.is_set():
            return
        if item["run_id"] in self.completed and not self.args.force:
            return
        if cfg.inputs_hash() != self.baseline_hash:
            self.stop.set()
            self.log("ABORT: kit/task fixture hash changed before run " + item["run_id"])
            return
        # At most two LMA runs at a time, regardless of --parallel.
        if item["group"] == "agent-lma":
            with self.lma_sem:
                self._execute(item)
        else:
            self._execute(item)

    def _execute(self, item: dict[str, Any]) -> None:
        run_id = item["run_id"]
        task = item["task"]
        group = item["group"]
        arm = item["arm"]
        run_dir = cfg.RUNS_ROOT / run_id
        art_dir = cfg.ARTIFACTS / run_id
        art_dir.mkdir(parents=True, exist_ok=True)
        events_path = art_dir / "events.jsonl"
        stderr_path = art_dir / "stderr.txt"
        timeout = self.timeout_for(group)
        score_timeout = self.score_timeout_for(group)
        rust = group in cfg.RUST_GROUPS
        lma_info = None

        try:
            if task in cfg.AGENT_TASKS:
                if group == "agent-lma":
                    lma_info = cfg.fresh_lma_copy(task, run_dir)
                else:
                    cfg.fresh_fixture_copy(task, run_dir)
                write_text(run_dir / "TASK.md", cfg.build_agent_task_text(task))
                mode = "agent"
                prompt = ""
            else:
                cfg.remove_tree(run_dir)
                run_dir.mkdir(parents=True)
                mode = "notool"
                prompt = cfg.build_no_tool_prompt(task)
            cfg.write_opencode_json(run_dir, mode)
        except (OSError, RuntimeError, ValueError) as error:
            self._write_failure(item, f"setup failed: {error!r}")
            return

        baseline_snapshot = cfg.snapshot_files(run_dir)
        command = build_command(self.base_cmd or ["opencode"], arm, run_id, mode, prompt)
        env = build_env(run_dir, rust=rust)
        started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        self.log(f"START {run_id} task={task} arm={arm} model={cfg.ARMS[arm]['model']}")
        start = time.time()
        timed_out = False
        start_error = None
        rc: int | None = None
        try:
            with open(events_path, "wb") as out_handle, open(stderr_path, "wb") as err_handle:
                proc = subprocess.Popen(command, cwd=str(run_dir), env=env,
                                        stdin=subprocess.DEVNULL,
                                        stdout=out_handle, stderr=err_handle)
                try:
                    rc = proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    scoring.kill_tree(proc)
                    try:
                        rc = proc.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        rc = proc.wait()
        except OSError as error:
            start_error = repr(error)
            write_text(stderr_path, start_error)
        wall = round(time.time() - start, 2)

        # Redact before anything is persisted.
        raw_events = read_text_retry(events_path)
        raw_stderr = read_text_retry(stderr_path)
        redacted_events = cfg.redact(raw_events)
        redacted_stderr = cfg.redact(raw_stderr)
        write_text(events_path, redacted_events)
        write_text(stderr_path, redacted_stderr)

        unique = evmod.dedupe_events(evmod.read_events(events_path))
        session_id = evmod.extract_session_id(unique)

        row = evmod.read_session_row(session_id) if session_id else None
        if session_id and row is None:
            time.sleep(1.0)
            row = evmod.read_session_row(session_id)

        session_check = verify_session_dir(unique, run_dir, row)
        step = evmod.parse_step_usage(unique)
        db_usage = evmod.row_usage(row)
        usage_source = "unavailable"
        if step["step_finish_events"] == 0 and db_usage:
            usage_source = "session_db"
        elif step["missing_final_step_usage"] and db_usage:
            usage_source = "session_db"
        elif step["step_finish_events"]:
            usage_source = "step_events"

        if usage_source == "session_db" and db_usage:
            tokens = db_usage
            cost_usd = db_usage.get("cost_usd")
        elif usage_source == "step_events":
            tokens = {key: step[key] for key in (
                "input_tokens", "cache_read_tokens", "cache_write_tokens",
                "output_tokens", "reasoning_tokens", "total_tokens")}
            cost_usd = step["cost_usd"]
        else:
            tokens = {key: 0 for key in (
                "input_tokens", "cache_read_tokens", "cache_write_tokens",
                "output_tokens", "reasoning_tokens", "total_tokens")}
            cost_usd = None
        cost_source = usage_source if cost_usd is not None else "unavailable"

        calls = evmod.parse_tool_calls(unique)
        tool_counts = dict(Counter(call["tool"] for call in calls))
        outside = evmod.find_outside_access(calls, run_dir)

        after_snapshot = cfg.snapshot_files(run_dir)
        changes = cfg.diff_snapshots(baseline_snapshot, after_snapshot)

        answer = evmod.answer_text(unique)
        write_text(art_dir / "answer.txt", cfg.redact(answer))

        # Last-line contract rules are checked on the final assistant message only.
        final_text = evmod.final_message_text(unique)

        # agent-lma: keep an anonymous, git-style diff of the model's changes.
        changes_diff = None
        if lma_info is not None:
            diff_text = cfg.render_changes_diff(lma_info["base_files"], cfg.snapshot_bytes(run_dir))
            write_text(art_dir / "changes.diff", cfg.redact(diff_text))
            changes_diff = str(art_dir / "changes.diff")

        gate = None
        hidden = None
        if group != "notool":
            entry = self.scoring["tasks"][task]
            gate = scoring.run_gate(entry, run_dir, score_timeout, env, self.python_cmd)
            write_text(art_dir / "gate.log", cfg.redact(gate["tail"]))
            if entry.get("hidden_src"):
                hidden = scoring.run_hidden(entry, cfg.ROOT / entry["hidden_src"], run_dir,
                                            score_timeout, env, self.python_cmd)
                write_text(art_dir / "hidden.log", cfg.redact(hidden["tail"]))

        constraints = None
        constraints_info = None
        if group == "agent-cli":
            constraints, constraints_info = cli_constraints.evaluate(task, run_dir, final_text)

        production = None
        if group == "agent-lma":
            production = cli_constraints.production_files(changes)

        auto_keyword = None
        auto_exact = None
        solved = False
        if group == "notool":
            auto_keyword = scoring.keyword_score(task, answer)
            auto_exact = auto_keyword.get("auto_exact") if isinstance(auto_keyword, dict) else None
            solved = bool(answer.strip())
        elif group == "agent-lma":
            solved = bool(gate and gate["passed"])
            if task == "lmaghost":
                # The reported bug does not exist: production code must stay untouched.
                solved = solved and not production
        else:
            solved = bool(hidden and hidden["ok"])

        errors = evmod.parse_errors(unique)
        invalid_reasons: list[str] = []
        if timed_out:
            invalid_reasons.append("timeout")
        if start_error:
            invalid_reasons.append("start_error: " + start_error[:200])
        if not unique:
            invalid_reasons.append("no_events")
        if not self.args.no_session_check:
            if session_check["verified"] is False:
                invalid_reasons.append("session_dir_mismatch")
            elif session_check["verified"] is None:
                invalid_reasons.append("session_dir_unknown")
        valid = not invalid_reasons

        result = {
            "run_id": run_id,
            "task": task,
            "group": group,
            "arm": arm,
            "model": cfg.ARMS[arm]["model"],
            "effort": cfg.ARMS[arm]["effort"],
            "rep": item["rep"],
            "order_index": item["order_index"],
            "started_at": started_at,
            "wall_seconds": wall,
            "exit_code": rc,
            "timed_out": timed_out,
            "error_events": errors,
            "steps": step["steps"],
            "tool_calls": tool_counts,
            "input_tokens": tokens["input_tokens"],
            "cache_read_tokens": tokens["cache_read_tokens"],
            "cache_write_tokens": tokens["cache_write_tokens"],
            "output_tokens": tokens["output_tokens"],
            "reasoning_tokens": tokens["reasoning_tokens"],
            "total_tokens": tokens["total_tokens"],
            "cost_usd": cost_usd,
            "cost_source": cost_source,
            "usage_source": usage_source,
            "missing_final_step_usage": step["missing_final_step_usage"],
            "session_id": session_id,
            "session_dir_verified": session_check["verified"],
            "session_dir_detail": session_check,
            "hidden_pass": hidden["pass"] if hidden else None,
            "hidden_total": hidden["total"] if hidden else None,
            "hidden_ok": hidden["ok"] if hidden else None,
            "hidden_exit_code": hidden["exit_code"] if hidden else None,
            "gate_passed": gate["passed"] if gate else None,
            "gate_exit_code": gate["exit_code"] if gate else None,
            "constraints": constraints,
            "constraints_ok": (all(constraints.values()) if constraints else None),
            "constraints_info": constraints_info,
            "production_changed": (bool(production) if production is not None else None),
            "production_changed_files": production,
            "auto_exact": auto_exact,
            "changes_diff": changes_diff,
            "lma_base_commit": lma_info["base_commit"] if lma_info else None,
            "lma_node_modules": lma_info["node_modules"] if lma_info else None,
            "files_changed": changes,
            "files_changed_count": len(changes),
            "outside_access": bool(outside),
            "outside_access_detail": outside,
            "valid": valid,
            "invalid_reasons": invalid_reasons,
            "answer_chars": len(answer),
            "auto_keyword": auto_keyword,
            "solved": solved,
            "kit_hash": self.baseline_hash,
            "artifacts": str(art_dir),
            "stderr_tail": redacted_stderr[-800:],
        }
        if usage_source == "session_db":
            result["step_usage"] = {key: step[key] for key in (
                "steps", "step_finish_events", "input_tokens", "cache_read_tokens",
                "cache_write_tokens", "output_tokens", "reasoning_tokens",
                "total_tokens", "cost_usd", "missing_final_step_usage")}
        elif db_usage:
            result["session_db_usage"] = db_usage

        self._append(result)
        self.log(f"END {run_id} rc={rc} wall={wall}s valid={valid} solved={solved} "
                 f"hidden={result['hidden_pass']}/{result['hidden_total']} "
                 f"cost={cost_usd} usage={usage_source} outside={bool(outside)}")

        try:
            changed = cfg.inputs_hash() != self.baseline_hash
        except OSError:
            changed = False
        if changed:
            self.stop.set()
            self.log("ABORT: kit/task fixture hash changed during run " + run_id)

    def _append(self, row: dict[str, Any]) -> None:
        line = json.dumps(row, ensure_ascii=False)
        with self.write_lock:
            self.runs_handle.write(cfg.redact(line) + "\n")
            self.runs_handle.flush()
            os.fsync(self.runs_handle.fileno())

    def _write_failure(self, item: dict[str, Any], reason: str) -> None:
        row = {
            "run_id": item["run_id"], "task": item["task"], "group": item["group"],
            "arm": item["arm"], "model": cfg.ARMS[item["arm"]]["model"],
            "effort": cfg.ARMS[item["arm"]]["effort"], "rep": item["rep"],
            "order_index": item.get("order_index"), "started_at": None,
            "wall_seconds": 0, "exit_code": None, "timed_out": False,
            "error_events": [], "steps": 0, "tool_calls": {},
            "input_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0,
            "output_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0,
            "cost_usd": None, "cost_source": "unavailable", "usage_source": "unavailable",
            "missing_final_step_usage": True, "session_id": None,
            "session_dir_verified": None, "session_dir_detail": None,
            "hidden_pass": None, "hidden_total": None, "hidden_ok": None,
            "hidden_exit_code": None, "gate_passed": None, "gate_exit_code": None,
            "constraints": None, "constraints_ok": None, "constraints_info": None,
            "production_changed": None, "production_changed_files": None,
            "auto_exact": None, "changes_diff": None,
            "lma_base_commit": None, "lma_node_modules": None,
            "files_changed": [], "files_changed_count": 0, "outside_access": False,
            "outside_access_detail": [], "valid": False, "invalid_reasons": [reason],
            "answer_chars": 0, "auto_keyword": None, "solved": False,
            "kit_hash": self.baseline_hash,
        }
        try:
            self._append(row)
        except OSError as error:
            self.log(f"could not append failure row for {item['run_id']}: {error!r}")
        self.log(f"RUN-FAIL {item['run_id']}: {reason}")

    def execute_safe(self, item: dict[str, Any]) -> None:
        """One broken run must not abort the rest of the batch."""
        try:
            self.execute(item)
        except Exception as error:  # noqa: BLE001 - barrier by design
            self.log(f"RUNNER ERROR {item['run_id']}: {error!r}")
            self._write_failure(item, f"runner_error: {error!r}"[:300])

    # -- batch
    def run(self) -> int:
        problems = self.validate()
        if problems:
            for problem in problems:
                print("ERROR:", problem, file=sys.stderr)
            return 2
        items = [item for item in self.build_items()
                 if self.args.force or item["run_id"] not in self.completed]
        if self.args.dry_run:
            self.print_dry_run(items)
            return 0
        if not items:
            print("nothing to do: every planned run_id is already in", self.runs_file)
            return 0
        if self.base_cmd is None:
            print("ERROR: opencode executable not found", file=sys.stderr)
            return 2

        cfg.RESULTS.mkdir(parents=True, exist_ok=True)
        cfg.ARTIFACTS.mkdir(parents=True, exist_ok=True)
        cfg.RUNS_ROOT.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log(f"BATCH START planned={len(items)} arms={','.join(self.arms)} "
                 f"tasks={','.join(self.tasks)} reps={self.reps} hash={self.baseline_hash}")
        with open(self.runs_file, "a", encoding="utf-8", newline="\n") as handle:
            self.runs_handle = handle
            with ThreadPoolExecutor(max_workers=max(1, self.args.parallel)) as pool:
                list(pool.map(self.execute_safe, items))
        self.log("BATCH END" + (" STOPPED" if self.stop.is_set() else ""))
        print("STOPPED" if self.stop.is_set() else "done")
        return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return Runner(args).run()
    except (ValueError, FileNotFoundError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
