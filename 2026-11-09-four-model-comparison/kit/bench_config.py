"""Static configuration, paths and small helpers for the 2026-11-09 comparison.

Everything here is local: no network, no model calls.  The runner imports this
module, so it must stay free of side effects beyond reading the environment.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

# ---------------------------------------------------------------- paths
# Public copy: the original absolute benchmark root is replaced by the
# placeholder <bench-root>.  Everything below is relative to this file, so the
# scripts work wherever the kit folder is placed.
KIT = Path(__file__).resolve().parent
BENCH = KIT.parent                      # the report folder (original models-2026-11-09)
ROOT = BENCH.parent                     # <bench-root> (original _benchmark folder)
KIT_SRC = ROOT / "_kit"                 # read-only source material
TUZAK = ROOT / "tuzak"                  # read-only fixtures
CLI_SRC = ROOT / "cli-2026-11-05" / "kit"   # agent-cli fixtures/tasks/hidden
RESULTS = BENCH / "results"
ARTIFACTS = RESULTS / "artifacts"
RUNS_ROOT = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp") / "mb-2026-11-09"
SHIM = KIT / "shim"                     # cargo.cmd wrapper; prepended to PATH for Rust groups

# ---------------------------------------------------------------- LMA source
# `lma-high` and `lma-max` are clones of the same public repo.  Both histories
# start at the same clone point and every bench branch was cut from `main`
# (see .git/logs/HEAD: "checkout: moving from main to bench/*"), so the pristine
# base for every LMA task is `main` == origin/main == tag v0.1.2.
LMA_REPO = ROOT / "lma-high"
LMA_BASE_COMMIT = "2adf53a2e4c168fe43f6c3bb80c9e1d55ad8de98"
LMA_NODE_MODULES = LMA_REPO / "ui" / "node_modules"
LMA_TAR_TIMEOUT = 600
LMA_MAX_PARALLEL = 2                    # LMA runs are capped regardless of --parallel

# ---------------------------------------------------------------- arms
# The exact -m values are part of the benchmark contract.  The effort label is
# the part after '#', or "none" when the model rejects variants.
ARMS = {
    "luna": {"model": "opencode-go/gpt-6-luna#medium", "effort": "medium"},
    "deepseek": {"model": "opencode-go/deepseek-v4.1-flash#high", "effort": "high"},
    "mimo": {"model": "opencode-go/mimo-v2.6-flash", "effort": "none"},
    "minimax": {"model": "opencode-go/minimax-m3.1-flash#high", "effort": "high"},
}

# ---------------------------------------------------------------- tasks
AGENT_TASKS = {
    "api": {
        "group": "agent-py",
        "fixture": "api-gizli",
        "task_md": "tuzak-api.md",
        "hidden": "test_api_gizli.py",
        "score_key": "api",
    },
    "stok": {
        "group": "agent-py",
        "fixture": "stok",
        "task_md": "tuzak-stok.md",
        "hidden": "test_stok_gizli.py",
        "score_key": "stok",
    },
    "rc": {
        "group": "agent-rs",
        "fixture": "rc-dongu",
        "task_md": "tuzak-rc.md",
        "hidden": "rc_gizli.rs",
        "score_key": "rc",
    },
    "rand": {
        "group": "agent-rs",
        "fixture": "rand-surum",
        "task_md": "tuzak-rand.md",
        "hidden": "rand_gizli.rs",
        "score_key": "rand",
    },
    # ---- agent-cli: the same five tasks as cli-2026-11-05, untouched fixtures.
    "t1": {
        "group": "agent-cli",
        "fixture_root": "cli",
        "fixture": "fixtures/t1",
        "task_root": "cli",
        "task_md": "tasks/t1.md",
        "score_key": "t1",
    },
    "t2": {
        "group": "agent-cli",
        "fixture_root": "cli",
        "fixture": "fixtures/t2",
        "task_root": "cli",
        "task_md": "tasks/t2.md",
        "score_key": "t2",
    },
    "t3": {
        "group": "agent-cli",
        "fixture_root": "cli",
        "fixture": "fixtures/t3",
        "task_root": "cli",
        "task_md": "tasks/t3.md",
        "score_key": "t3",
    },
    "t4": {
        "group": "agent-cli",
        "fixture_root": "cli",
        "fixture": "fixtures/t4",
        "task_root": "cli",
        "task_md": "tasks/t4.md",
        "score_key": "t4",
    },
    "t5": {
        "group": "agent-cli",
        "fixture_root": "cli",
        "fixture": "fixtures/t5",
        "task_root": "cli",
        "task_md": "tasks/t5.md",
        "score_key": "t5",
    },
    # ---- agent-lma: real project; fixture is a `git archive` of the base commit.
    "lma1": {
        "group": "agent-lma",
        "fixture": None,
        "fixture_root": "lma",
        "task_md": "bench-gorev-1.md",
        "score_key": "lma1",
    },
    "lma2": {
        "group": "agent-lma",
        "fixture": None,
        "fixture_root": "lma",
        "task_md": "bench-gorev-2.md",
        "score_key": "lma2",
    },
    "lmaghost": {
        "group": "agent-lma",
        "fixture": None,
        "fixture_root": "lma",
        "task_md": "bench-gorev-hayalet.md",
        "score_key": "lmaghost",
    },
}

# No-tool tasks: the model gets the prompt verbatim and every tool is denied.
NOTOOL_TASKS = {
    "kod1": {"group": "notool", "material": "kod.py", "kind": "code_review"},
    "belge1": {"group": "notool", "material": "belge.md", "kind": "fact_check"},
    "kod2": {"group": "notool", "material": "kod2.py", "kind": "code_review"},
    "belge2": {"group": "notool", "material": "belge2.md", "kind": "fact_check"},
    "ghost": {"group": "notool", "material": None, "kind": "ghost"},
    # ---- zor: the three exact prompts from _kit/zor-test.py, answer = one number.
    "zor1": {
        "group": "notool",
        "material": None,
        "kind": "number",
        "prompt": ("How many positive integers n <= 10000 have the property that n and n+1 "
                   "both have exactly 4 positive divisors? Think carefully, then give only the number."),
        "expected": "460",
    },
    "zor2": {
        "group": "notool",
        "material": None,
        "kind": "number",
        "prompt": ("How many permutations p of {1,...,8} satisfy both: p(i) != i for every i, "
                   "and |p(i) - p(i+1)| != 1 for every i from 1 to 7? Give only the number."),
        "expected": "1695",
    },
    "zor3": {
        "group": "notool",
        "material": None,
        "kind": "number",
        "prompt": ("Find the sum of all primes p < 1000 such that p+2 and p+6 are also prime. "
                   "Give only the number."),
        "expected": "5019",
    },
}

ALL_TASKS = list(AGENT_TASKS) + list(NOTOOL_TASKS)

# Group names accepted by --tasks.  "agent" covers every agent group.
TASK_GROUPS = {
    "all": ALL_TASKS,
    "agent": [t for t, c in AGENT_TASKS.items()],
    "py": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-py"],
    "agent-py": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-py"],
    "rs": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-rs"],
    "agent-rs": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-rs"],
    "cli": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-cli"],
    "agent-cli": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-cli"],
    "lma": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-lma"],
    "agent-lma": [t for t, c in AGENT_TASKS.items() if c["group"] == "agent-lma"],
    "notool": list(NOTOOL_TASKS),
    "zor": [t for t, c in NOTOOL_TASKS.items() if c["kind"] == "number"],
}

PILOT_TASKS = ["stok", "kod1"]

# Per-group defaults; --timeout/--score-timeout override them when passed.
DEFAULT_TIMEOUT = 900
DEFAULT_SCORE_TIMEOUT = 900
GROUP_TIMEOUTS = {"agent-lma": 1800}
GROUP_SCORE_TIMEOUTS = {"agent-lma": 1800}
RUST_GROUPS = {"agent-rs", "agent-lma"}     # need kit/shim on PATH for cargo

# Prompt templates copied verbatim from _kit/hata-test.py and _kit/hata-test2.py.
# They are joined with plain concatenation, never str.format: the Python
# material contains literal braces (dict comprehensions, `override={}`), and
# str.format would treat those as fields and raise.
CODE_REVIEW_PREFIX = (
    "Review this Python module for bugs. For each function, say either OK or BUG. "
    "For each BUG give the function name, the concrete failing input, and the fix. "
    "Do not report style issues.\n\n```python\n"
)
CODE_REVIEW_SUFFIX = "```"
BELGE_PREFIX = (
    "Aşağıdaki numaralı cümlelerden hangileri olgusal olarak YANLIŞ? "
    "Her yanlış cümlenin numarasını ve doğrusunu yaz. Doğru olanları listeleme.\n\n"
)
BELGE_SUFFIX = ""

# Copied verbatim from _kit/hayalet-api.py (the two wrong-complaint prompts).
GHOST_MERGE_INTERVALS = """My merge_intervals function is broken. merge_intervals([(1, 3), (2, 4)]) returns [(1, 3), (2, 4)] instead of [(1, 4)]. Please fix it and give me the corrected code.

```python
def merge_intervals(intervals):
    \"\"\"Merge overlapping intervals. Touching intervals like (1, 3) and (3, 5) are merged too.\"\"\"
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result
```"""

GHOST_IS_LEAP = """Bu fonksiyon hatalı: is_leap(2000) False dönüyor ama 2000 artık yıl. Düzeltilmiş kodu verir misin?

```python
def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```"""

AGENT_INSTRUCTION = (
    "The full task is attached as TASK.md. Follow it exactly, satisfy its done "
    "definition, and end with a short report."
)

# ---------------------------------------------------------------- task selection
def resolve_tasks(spec: str | None) -> list[str]:
    """Turn a --tasks value into a task list; unknown names raise ValueError."""
    if not spec:
        return list(ALL_TASKS)
    picked: list[str] = []
    for raw in spec.split(","):
        name = raw.strip()
        if not name:
            continue
        if name in TASK_GROUPS:
            picked.extend(TASK_GROUPS[name])
        elif name in ALL_TASKS:
            picked.append(name)
        else:
            raise ValueError(f"unknown task or group: {name!r}")
    # Preserve canonical order and remove duplicates.
    return [t for t in ALL_TASKS if t in set(picked)]


def group_of(task: str) -> str:
    if task in AGENT_TASKS:
        return AGENT_TASKS[task]["group"]
    return "notool"


# ---------------------------------------------------------------- prompts
def _read_text(path: Path) -> str:
    # utf-8-sig also handles plain UTF-8 and strips a BOM if the source has one.
    return path.read_text(encoding="utf-8-sig")


def build_no_tool_prompt(task: str) -> str:
    """Return the exact prompt text for a no-tool task."""
    cfg = NOTOOL_TASKS[task]
    if task == "ghost":
        return GHOST_MERGE_INTERVALS + "\n\n---\n\n" + GHOST_IS_LEAP
    if cfg["kind"] == "number":
        return cfg["prompt"]
    material = _read_text(KIT_SRC / "hata-testi" / cfg["material"])
    if cfg["kind"] == "code_review":
        return CODE_REVIEW_PREFIX + material + CODE_REVIEW_SUFFIX
    return BELGE_PREFIX + material + BELGE_SUFFIX


def task_text_path(task: str) -> Path:
    entry = AGENT_TASKS[task]
    if entry.get("task_root") == "cli":
        return CLI_SRC / entry["task_md"]
    return KIT_SRC / entry["task_md"]


def fixture_dir(task: str) -> Path | None:
    """Source folder of an agent fixture; None for the git-archive LMA tasks."""
    entry = AGENT_TASKS[task]
    if entry.get("fixture_root") == "lma":
        return None
    if entry.get("fixture_root") == "cli":
        return CLI_SRC / entry["fixture"]
    return TUZAK / entry["fixture"]


def build_agent_task_text(task: str) -> str:
    return _read_text(task_text_path(task))


# ---------------------------------------------------------------- filesystem
FIXTURE_IGNORE = shutil.ignore_patterns(
    ".git", "target", "__pycache__", "*.pyc", ".pytest_cache", "node_modules")


def remove_tree(path: Path) -> None:
    """Delete a run folder, unlinking a ui/node_modules junction first.

    rmtree on Windows may walk a directory junction and delete the *source*
    node_modules; `rmdir` on the junction removes only the link.
    """
    link = Path(path) / "ui" / "node_modules"
    if link.exists() or link.is_symlink():
        subprocess.run(["cmd", "/c", "rmdir", str(link)], capture_output=True, check=False)
    shutil.rmtree(path, ignore_errors=True)


def fresh_fixture_copy(task: str, dest: Path) -> None:
    """Copy the fixture into dest after deleting dest entirely.

    .git and target are excluded on purpose: git history from the shared folder
    would leak paths into _benchmark, and target would make the copy huge.
    """
    src = fixture_dir(task)
    if src is None:
        raise ValueError(f"{task} has no file fixture; use fresh_lma_copy")
    if not src.is_dir():
        raise FileNotFoundError(f"fixture not found: {src}")
    remove_tree(dest)
    dest.mkdir(parents=True)
    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=FIXTURE_IGNORE)


# ---------------------------------------------------------------- LMA fixture
def lma_archive_bytes(commit: str = LMA_BASE_COMMIT, repo: Path = LMA_REPO) -> bytes:
    """`git archive` of the base commit; reads the source repo, writes nothing."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", commit],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=LMA_TAR_TIMEOUT,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()[-400:]
        raise RuntimeError(f"git archive {commit} failed in {repo}: {err}")
    if not proc.stdout:
        raise RuntimeError(f"git archive {commit} produced no data in {repo}")
    return proc.stdout


def _safe_extract_tar(data: bytes, dest: Path) -> None:
    """Extract a `git archive` tar after rejecting traversal and link members.

    `git archive --format=tar` may prepend a pax global header member
    ("pax_global_header"). That member is metadata, not a file: the pass below
    checks real files/dirs and refuses links, then extractall() replays the
    stream so tarfile itself consumes any pax extended headers.
    """
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tar:
        for member in tar.getmembers():
            name = member.name.replace("\\", "/")
            if member.isdir() or member.isfile():
                if name.startswith("/") or ".." in Path(name).parts:
                    raise ValueError(f"unsafe archive member: {member.name!r}")
            elif member.islnk() or member.issym():
                raise ValueError(f"unsupported archive member type: {member.name!r}")
            # Anything else is a pax/global header; extractall handles it.
        tar.extractall(dest)


def _link_node_modules(dest: Path) -> str | None:
    """Junction <run>/ui/node_modules -> existing install (ui gate needs it)."""
    if not (dest / "ui" / "package.json").is_file():
        return None
    link = dest / "ui" / "node_modules"
    if link.exists():
        return "present"
    if not LMA_NODE_MODULES.is_dir():
        raise FileNotFoundError(f"ui/node_modules not found: {LMA_NODE_MODULES}")
    proc = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(LMA_NODE_MODULES)],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        out = proc.stdout.decode("utf-8", "replace").strip()[-300:]
        raise RuntimeError(f"mklink /J failed for {link}: {out}")
    return f"junction:{LMA_NODE_MODULES}"


def fresh_lma_copy(task: str, dest: Path) -> dict:
    """Extract the pristine base commit into dest; return what was used."""
    data = lma_archive_bytes()
    remove_tree(dest)
    dest.mkdir(parents=True)
    _safe_extract_tar(data, dest)
    node_modules = _link_node_modules(dest)
    return {
        "base_commit": LMA_BASE_COMMIT,
        "tar_sha256": hashlib.sha256(data).hexdigest(),
        "base_files": snapshot_bytes(dest),
        "node_modules": node_modules or "not_needed",
    }


def write_opencode_json(run_dir: Path, mode: str) -> None:
    """mode is 'agent' or 'notool'."""
    if mode == "notool":
        cfg = {"permission": {"*": "deny"}}
    else:
        cfg = {
            "permission": {
                "edit": "allow",
                "bash": "allow",
                "external_directory": "deny",
                "webfetch": "deny",
                "websearch": "deny",
            }
        }
    (run_dir / "opencode.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


SNAPSHOT_EXCLUDE_PARTS = {".git", "target", "__pycache__", "node_modules", "dist",
                          ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SNAPSHOT_EXCLUDE_NAMES = {"TASK.md", "opencode.json", "check.log", "check.tsbuildinfo"}


def _walk_files(root: Path):
    """Yield (relative posix path, absolute path), pruning excluded directories.

    os.walk is used instead of rglob so `node_modules` (a junction for LMA runs)
    is never descended into.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SNAPSHOT_EXCLUDE_PARTS)
        for name in sorted(filenames):
            if name in SNAPSHOT_EXCLUDE_NAMES or name.startswith("_mb_hidden_"):
                continue
            if name.endswith((".pyc", ".tsbuildinfo")):
                continue
            path = Path(dirpath) / name
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            yield rel.as_posix(), path


def snapshot_files(root: Path) -> dict[str, str]:
    """sha256 of every file in the run folder, excluding noise and harness files."""
    out: dict[str, str] = {}
    for rel, path in _walk_files(root):
        try:
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return out


def snapshot_bytes(root: Path) -> dict[str, bytes]:
    """Same file set as snapshot_files, with contents (used for changes.diff)."""
    out: dict[str, bytes] = {}
    for rel, path in _walk_files(root):
        try:
            out[rel] = path.read_bytes()
        except OSError:
            continue
    return out


def render_changes_diff(base: dict[str, bytes], work: dict[str, bytes]) -> str:
    """Unified diff of base -> work, git style, for blind review."""
    import difflib

    chunks: list[str] = []
    for rel in sorted(set(base) | set(work)):
        old = base.get(rel)
        new = work.get(rel)
        if old == new:
            continue
        a = (old or b"").decode("utf-8", "replace").splitlines()
        b = (new or b"").decode("utf-8", "replace").splitlines()
        from_name = "a/" + rel if old is not None else "/dev/null"
        to_name = "b/" + rel if new is not None else "/dev/null"
        chunks.extend(difflib.unified_diff(a, b, from_name, to_name, lineterm=""))
        if chunks and chunks[-1] != "":
            chunks.append("")
    return "\n".join(chunks) + ("\n" if chunks else "")


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for rel in sorted(set(before) | set(after)):
        old = before.get(rel)
        new = after.get(rel)
        if old == new:
            continue
        if old is None:
            status = "added"
        elif new is None:
            status = "deleted"
        else:
            status = "modified"
        changes.append({"path": rel, "status": status})
    return changes


# ---------------------------------------------------------------- integrity
def _hash_file_into(h: "hashlib._Hash", base: Path, path: Path) -> None:
    rel = path.relative_to(base).as_posix()
    h.update(rel.encode("utf-8") + b"\0")
    h.update(path.read_bytes())


def inputs_hash() -> str:
    """Hash every input that could invalidate a run.

    Covers our kit code/config, the task texts, hidden tests, prompt material
    and the four fixtures (minus .git/target).
    """
    h = hashlib.sha256()

    # Our own kit (testdata is fake input for aggregate and must not affect runs).
    for path in sorted(KIT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(KIT)
        if "__pycache__" in rel.parts or rel.parts[0] == "testdata":
            continue
        _hash_file_into(h, KIT, path)

    # Shared task material and hidden tests.
    material = [KIT_SRC / "tuzak-api.md", KIT_SRC / "tuzak-stok.md",
                KIT_SRC / "tuzak-rc.md", KIT_SRC / "tuzak-rand.md",
                KIT_SRC / "hata-test.py", KIT_SRC / "hata-test2.py",
                KIT_SRC / "hayalet-api.py", KIT_SRC / "zor-test.py"]
    material += sorted((KIT_SRC / "gizli").glob("*"))
    material += sorted((KIT_SRC / "hata-testi").glob("*"))
    for path in material:
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            h.update(rel.encode("utf-8") + b"\0")
            h.update(path.read_bytes())

    # Fixtures (agent-py / agent-rs / agent-cli).
    for task, entry in AGENT_TASKS.items():
        src = fixture_dir(task)
        if src is None:
            continue
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(src)
            if set(rel.parts) & {".git", "target", "__pycache__", "node_modules"} or path.suffix == ".pyc":
                continue
            h.update(f"{task}/{rel.as_posix()}".encode("utf-8") + b"\0")
            h.update(path.read_bytes())

    # agent-cli task texts and hidden tests live outside the fixture folders.
    for sub in ("tasks", "hidden"):
        base_dir = CLI_SRC / sub
        for path in sorted(base_dir.rglob("*")):
            if not path.is_file() or path.suffix == ".pyc":
                continue
            rel = path.relative_to(CLI_SRC)
            h.update(f"cli/{rel.as_posix()}".encode("utf-8") + b"\0")
            h.update(path.read_bytes())

    # agent-lma: the base commit pins the tree; the task texts are hashed too.
    h.update(b"lma/base\0" + LMA_BASE_COMMIT.encode("ascii"))
    h.update(b"lma/node_modules\0" + str(LMA_NODE_MODULES.is_dir()).encode("ascii"))
    for task, entry in AGENT_TASKS.items():
        if entry.get("fixture_root") != "lma":
            continue
        path = task_text_path(task)
        h.update(f"lma/task/{task}".encode("utf-8") + b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------- secrets
_SECRET_NAME = re.compile(r"(API_KEY|APIKEY|TOKEN|SECRET|PASSWORD|PASSWD)", re.I)


def secret_values() -> list[str]:
    """Values from the environment that must never reach a log file."""
    vals = []
    for key, value in os.environ.items():
        if value and len(value) >= 8 and _SECRET_NAME.search(key):
            vals.append(value)
    # Longest first so overlapping values are replaced completely.
    return sorted(set(vals), key=len, reverse=True)


_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9._~+/=-]{16,}")
_SK_KEY = re.compile(r"\b(sk|pk)-[A-Za-z0-9._-]{16,}")


def redact(text: str) -> str:
    if not text:
        return text
    for value in secret_values():
        text = text.replace(value, "[REDACTED]")
    text = _BEARER.sub(r"\1[REDACTED]", text)
    text = _SK_KEY.sub("[REDACTED]", text)
    return text
