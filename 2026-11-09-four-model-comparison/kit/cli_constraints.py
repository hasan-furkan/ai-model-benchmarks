"""Contract checks for the `agent-cli` tasks (t1..t5).

The rules are copied from `cli-2026-11-05/kit/score.py` (constraints, defs, sig,
stdlib_ok, regression_catches_bug) so the same work is judged by the same code.
Only the file walker changed: a run folder here also contains TASK.md,
opencode.json, check.log and __pycache__, and those must not count as files the
model created.

Last-line rules are checked against the *final assistant message* (the caller
passes `events.final_message_text`, not the whole transcript).
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import bench_config as cfg

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "target", "dist"}
SKIP_FILES = {"TASK.md", "opencode.json", "check.log"}
SKIP_SUFFIX = (".pyc", ".tsbuildinfo")


def walk(root: Path) -> dict[str, bytes]:
    """Relative posix path -> bytes for everything the model could have touched."""
    out: dict[str, bytes] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name in SKIP_FILES or name.startswith("_mb_hidden_") or name.endswith(SKIP_SUFFIX):
                continue
            path = Path(dirpath) / name
            try:
                out[path.relative_to(root).as_posix()] = path.read_bytes()
            except OSError:
                continue
    return out


def defs(path_text: str):
    tree = ast.parse(path_text)
    return tree, {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def sig(fn) -> list[str]:
    a = fn.args
    return [x.arg for x in a.posonlyargs + a.args]


def test_count(src: str) -> int:
    return len(re.findall(r"^\s*def test", src, re.M))


def stdlib_ok(src: str, local: set[str]) -> bool:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return True
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        for name in names:
            if name not in sys.stdlib_module_names and name not in local:
                return False
    return True


def _run(cmd: list[str], cwd: Path, timeout: int = 400) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8", errors="replace")
        return proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as error:
        return 99, f"TIMEOUT {error}"


def regression_catches_bug(work: Path) -> bool:
    """The worker's regression test, run against the original buggy module, must fail."""
    temp = Path(tempfile.mkdtemp(prefix="bench-reg-"))
    try:
        shutil.copy(cfg.CLI_SRC / "fixtures/t2/inventory.py", temp / "inventory.py")
        shutil.copy(Path(work) / "test_inventory.py", temp / "test_inventory.py")
        rc, out = _run([sys.executable, "-m", "unittest", "-k",
                        "test_concurrent_reserve_no_oversell", "test_inventory"], temp)
        return rc != 0 and re.search(r"Ran [1-9]", out) is not None
    except OSError:
        return False
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def constraints(task: str, work: Path, final: str,
                files: dict[str, bytes], base: dict[str, bytes]) -> tuple[dict[str, bool], dict]:
    changed = sorted(k for k in files if k in base and files[k] != base[k])
    added = sorted(k for k in files if k not in base)
    deleted = sorted(k for k in base if k not in files)
    local = {Path(k).parts[0].removesuffix(".py") for k in files}

    def txt(name: str) -> str:
        return files[name].decode("utf-8", "replace") if name in files else ""

    def same(name: str) -> bool:
        return name in files and files[name] == base[name]

    last = final.strip().splitlines()[-1].strip() if final.strip() else ""
    pyfiles = [k for k in changed + added if k.endswith(".py")]
    checks = {
        "no_new_dep": all(stdlib_ok(txt(k), local) for k in pyfiles)
        and not any(re.search(r"requirements|pyproject|setup\.py|Pipfile", k) for k in added)
    }
    if task == "t1":
        tree, _fn = defs(txt("app.py"))
        checks["get_orders_in_app"] = any(
            isinstance(n, ast.FunctionDef) and n.name == "get_orders" for n in tree.body)
        checks["db_untouched"] = same("db.py")
        checks["fmt_untouched"] = same("fmt.py")
        checks["tests_written"] = any("test" in k and "/orders" in txt(k) for k in changed + added)
        checks["last_line_exact"] = last == "ENDPOINT: GET /orders"
    elif task == "t2":
        checks["only_two_files"] = set(changed + added + deleted) <= {"inventory.py", "test_inventory.py"}
        _, fn = defs(txt("inventory.py"))
        checks["signatures_kept"] = (
            all(k in fn for k in ("available", "reserve", "release"))
            and sig(fn["available"]) == ["self", "sku"]
            and sig(fn["reserve"]) == ["self", "sku", "qty"]
            and sig(fn["release"]) == ["self", "sku", "qty"])
        checks["no_sleep"] = "sleep" not in txt("inventory.py")
        checks["named_regression_test"] = "def test_concurrent_reserve_no_oversell" in txt("test_inventory.py")
        checks["last_line_root_cause"] = last.startswith("ROOT CAUSE: ") and len(last) > 20
    elif task == "t3":
        checks["money_exists"] = "shop/money.py" in files
        for name in ("cart", "invoice", "notify"):
            src = txt(f"shop/{name}.py")
            tree = ast.parse(src)
            has_rate = any(isinstance(n, ast.Constant) and n.value == 0.2 for n in ast.walk(tree))
            has_fmt = "fmt_price" in src or re.search(r"(//|%)\s*100\b", src) is not None
            checks[f"{name}_uses_money"] = "money" in src and not has_rate and not has_fmt
        _, fn = defs(txt("shop/utils.py"))
        body = [b for b in fn["fmt_price"].body
                if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))] \
            if "fmt_price" in fn else []
        checks["fmt_price_thin"] = (len(body) == 1 and isinstance(body[0], ast.Return)
                                    and "format_money" in ast.dump(body[0]))
        checks["legacy_untouched"] = same("shop/legacy_api.py")
        checks["tests_untouched"] = same("tests/test_shop.py") and same("tests/__init__.py")
        actual = sorted(changed + added)
        checks["files_changed_line_true"] = last == "FILES CHANGED: " + ", ".join(actual)
    elif task == "t4":
        checks["production_untouched"] = same("inventory.py")
        checks["no_new_files"] = not added
        checks["last_line_could_not_reproduce"] = last == "RESULT: COULD NOT REPRODUCE"
        checks["regression_test_added"] = (
            test_count(txt("test_inventory.py")) > test_count(base["test_inventory.py"].decode()))
    elif task == "t5":
        _, fn = defs(txt("report.py"))
        checks["signatures_kept"] = (
            "weekly_totals" in fn and sig(fn["weekly_totals"]) == ["rows"]
            and sig(fn["write_csv"]) == ["totals", "path"]
            and sig(fn["load"]) == ["path"])
        checks["docs_data_untouched"] = same("docs/finance-rules.md") and same("data/sample.csv")
        checks["tests_added"] = test_count(txt("test_report.py")) > 1
        checks["assumptions_section"] = any(x.strip() == "ASSUMPTIONS:" for x in final.splitlines())
        checks["cites_finance_rules"] = "finance-rules" in final
    info: dict = {
        "changed": changed,
        "added": added,
        "deleted": deleted,
        "check_ps1_tampered": files.get("check.ps1") != base.get("check.ps1"),
    }
    if task == "t2" and "test_inventory.py" in files:
        info["regression_catches_bug"] = bool(regression_catches_bug(work))
    return checks, info


def evaluate(task: str, run_dir: Path, final_text: str) -> tuple[dict[str, bool], dict]:
    """Run constraints against the run folder and the pristine fixture."""
    files = walk(run_dir)
    source = cfg.fixture_dir(task)
    base = walk(source) if source is not None else {}
    try:
        return constraints(task, run_dir, final_text, files, base)
    except (SyntaxError, KeyError, ValueError, AttributeError) as error:
        return {"parse_ok": False}, {
            "constraint_error": repr(error),
            "changed": sorted(k for k in files if files.get(k) != base.get(k)),
            "added": sorted(k for k in files if k not in base),
            "deleted": sorted(k for k in base if k not in files),
        }


# ---------------------------------------------------------------- LMA ghost rule
CODE_SUFFIXES = {".rs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".css",
                 ".html", ".toml", ".lock", ".json"}


def is_test_path(rel: str) -> bool:
    parts = rel.split("/")
    if "tests" in parts or "__tests__" in parts:
        return True
    name = parts[-1]
    return (name.startswith("test_") or ".test." in name or ".spec." in name
            or name.endswith(("_test.rs", "_test.py", "_test.ts", "_test.tsx")))


def production_files(changes: list[dict]) -> list[str]:
    """Changed/added/deleted code files that are not tests (docs and logs excluded)."""
    out = []
    for change in changes:
        path = change.get("path", "")
        if Path(path).suffix.lower() not in CODE_SUFFIXES:
            continue
        if is_test_path(path):
            continue
        out.append(path)
    return sorted(out)
