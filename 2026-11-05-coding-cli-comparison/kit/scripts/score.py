"""Scores every finished run: metrics from each CLI's own data, checks rerun here in a throwaway copy.
Usage: score.py [--manifest kit/manifest.json] [--ids r01,...]  -> results/scores.json
"""
import argparse
import ast
import difflib
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

K = Path(__file__).parent
P = K.parent
B = Path(r"C:\Users\<user>\Desktop\projects\_benchmark\cli-2026-11-05")
RAW = P / "raw"
RUNS = P / "done"  # finished runs are moved here by the runner
WORKROOT = B / "runs"  # where the run was live (used for outside-path detection)
RES = P / "results"
HOME = Path(os.environ["USERPROFILE"])
IN, CACHE, OUT = 0.15, 0.003, 0.60  # USD per 1M, models.dev opencode-go/deepseek-v4.1-flash
SKIP_DIRS = {".git", "__pycache__", ".claude", ".opencode", ".dsh", ".deepseek"}
STATE_NOTE = {".claude", ".opencode", ".dsh", ".deepseek"}


def cost(unc, cr, o):
    return (unc * IN + cr * CACHE + o * OUT) / 1e6


def metrics_A(rid):
    try:
        d = json.loads((RAW / f"{rid}.out").read_text(encoding="utf-8", errors="replace"))
    except ValueError:
        d = {}
    u = d.get("usage", {})
    m = {"unc": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0), "cache": u.get("cache_read_input_tokens", 0),
         "out": u.get("output_tokens", 0), "turns": d.get("num_turns"), "own_cost": d.get("total_cost_usd"),
         "final": d.get("result") or "", "tools": [], "own_cost_note": "Claude Code list price, not Go", "api_errors": 0,
         "from_session_log": not d}
    if d.get("session_id"):
        hits = glob.glob(str(HOME / f".claude/projects/*/{d.get('session_id')}.jsonl"))
    else:  # no result JSON (timeout/kill): find the session log by the work dir slug
        slug = re.sub(r"[^A-Za-z0-9]", "-", str(WORKROOT / rid / "work"))
        hits = sorted(glob.glob(str(HOME / f".claude/projects/{slug}/*.jsonl")), key=os.path.getmtime)[-1:]
    seen, seen_msg = set(), set()
    unc = cache = out = turns = 0
    last_text = ""
    if hits:
        for line in open(hits[0], encoding="utf-8", errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("subtype") == "api_error" or e.get("isApiErrorMessage"):
                m["api_errors"] += 1
            msg = e.get("message") or {}
            if e.get("type") == "assistant" and isinstance(msg.get("content"), list):
                mid = msg.get("id")
                if mid not in seen_msg and msg.get("usage"):
                    seen_msg.add(mid)
                    uu = msg["usage"]
                    unc += uu.get("input_tokens", 0) + uu.get("cache_creation_input_tokens", 0)
                    cache += uu.get("cache_read_input_tokens", 0)
                    out += uu.get("output_tokens", 0)
                    turns += 1
                for c in msg["content"]:
                    if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id") not in seen:
                        seen.add(c.get("id"))
                        m["tools"].append((c.get("name"), c.get("input")))
                    elif isinstance(c, dict) and c.get("type") == "text":
                        last_text = c.get("text") or last_text
    if not d:
        m.update({"unc": unc, "cache": cache, "out": out, "turns": turns, "final": last_text})
    return m


def metrics_B(rid):
    tools, texts, sid = [], [], None
    for line in (RAW / f"{rid}.out").read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        sid = e.get("sessionID") or sid
        p = e.get("part") or {}
        if e.get("type") == "tool_use":
            tools.append((p.get("tool"), (p.get("state") or {}).get("input")))
            texts = []
        elif e.get("type") == "text":
            texts.append(p.get("text") or "")
    c = sqlite3.connect(str(HOME / ".local/share/opencode/opencode.db"))
    r = c.execute("select cost,tokens_input,tokens_output,tokens_reasoning,tokens_cache_read,tokens_cache_write,directory from session_v2 where id=?", (sid,)).fetchone()
    steps = len(re.findall(r'"type":"step_start"', (RAW / f"{rid}.out").read_text(encoding="utf-8", errors="replace")))
    r = r or (0, 0, 0, 0, 0, 0, "")
    return {"unc": r[1] + (r[5] or 0), "cache": r[4], "out": r[2] + r[3], "turns": steps, "own_cost": r[0], "final": "\n".join(texts), "tools": tools,
            "own_cost_note": "OpenCode session cost",
            "session_dir_ok": (r[6] or "").lower().rstrip("/") == str(WORKROOT / rid / "work").replace(chr(92), "/").lower()}


def metrics_C(rid):
    tools, final, steps, dsh_in, dsh_out = [], "", 0, 0, 0
    for line in (RAW / f"{rid}.out").read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t = e.get("type")
        if t == "tool_call":
            tools.append((e.get("name") or e.get("tool"), e.get("input") or e.get("args") or e.get("arguments")))
        elif t == "final":
            final = e.get("text") or ""
        elif t == "status" and e.get("phase") == "step_end":
            steps += 1
            u = e.get("usage") or {}
            dsh_in += u.get("inputTokens", 0)
            dsh_out += u.get("outputTokens", 0)
    unc = cache = out = 0
    allowance = list_cost = 0.0
    p = RAW / f"{rid}.usage.jsonl"
    n = 0
    dec = json.JSONDecoder()
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("{") or "prompt_tokens" not in line:
                continue
            try:
                u, _ = dec.raw_decode(line)  # tolerate trailing junk from the first proxy version
            except ValueError:
                continue
            if not isinstance(u, dict) or "prompt_tokens" not in u:
                continue
            n += 1
            oc = u.get("opencode") or {}
            allowance += oc.get("allowance") or 0
            list_cost += oc.get("list_cost") or 0
            cached = u.get("prompt_cache_hit_tokens")
            if cached is None:
                cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
            unc += u["prompt_tokens"] - cached
            cache += cached
            out += u.get("completion_tokens", 0)
    return {"unc": unc, "cache": cache, "out": out, "turns": steps, "own_cost": None, "final": final, "tools": tools,
            "own_cost_note": "dsh reports no cost", "dsh_in": dsh_in, "dsh_out": dsh_out, "proxy_usage_records": n,
            "go_allowance": round(allowance, 6), "go_list_cost": round(list_cost, 6)}


METRICS = {"A": metrics_A, "B": metrics_B, "C": metrics_C}


def walk(d):
    r = {}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".pyc"):
                continue
            p = Path(root, f)
            r[p.relative_to(d).as_posix()] = p.read_bytes()
    return r


def stdlib_ok(src, local):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return True
    for n in ast.walk(tree):
        names = []
        if isinstance(n, ast.Import):
            names = [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            names = [n.module.split(".")[0]]
        for x in names:
            if x not in sys.stdlib_module_names and x not in local:
                return False
    return True


def run(cmd, cwd, timeout=400, stdout_only=False):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout if stdout_only else p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        return 99, f"TIMEOUT {e}"


def hidden(task, work):
    t = Path(tempfile.mkdtemp(prefix="bench-eval-"))
    try:
        shutil.copytree(work, t / "w", ignore=shutil.ignore_patterns(".git", "__pycache__"))
        w = t / "w"
        shutil.copy(K / "fixtures" / task / "check.ps1", w / "check.ps1")
        rc, o = run(["powershell", "-NoProfile", "-File", "check.ps1"], w, stdout_only=True)
        lines = [x for x in o.strip().splitlines() if x.strip()]
        check = bool(lines) and lines[-1].strip() == "CHECK PASSED"
        shutil.copy(K / "hidden" / f"{task}_hidden.py", w / "zz_hidden.py")
        rc2, o2 = run([sys.executable, "-m", "unittest", "zz_hidden"], w)
        m = re.search(r"Ran (\d+) test", o2)
        total = int(m.group(1)) if m else 0
        m = re.search(r"FAILED \((.*)\)", o2)
        bad = sum(int(x) for x in re.findall(r"=(\d+)", m.group(1))) if m else 0
        if rc2 and not m:
            bad = total or 1
        return check, total - bad, total
    finally:
        shutil.rmtree(t, ignore_errors=True)


def defs(path):
    tree = ast.parse(path)
    return tree, {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def sig(fn):
    a = fn.args
    return [x.arg for x in a.posonlyargs + a.args]


def test_count(src):
    return len(re.findall(r"^\s*def test", src, re.M))


def regression_catches_bug(work):
    """Worker's regression test run against the original buggy module must fail."""
    t = Path(tempfile.mkdtemp(prefix="bench-reg-"))
    try:
        shutil.copy(K / "fixtures/t2/inventory.py", t / "inventory.py")
        shutil.copy(Path(work) / "test_inventory.py", t / "test_inventory.py")
        rc, o = run([sys.executable, "-m", "unittest", "-k", "test_concurrent_reserve_no_oversell", "test_inventory"], t)
        return rc != 0 and "Ran 1 test" in o or (rc != 0 and re.search(r"Ran [1-9]", o) is not None)
    finally:
        shutil.rmtree(t, ignore_errors=True)


def constraints(task, work, final, files, base):
    changed = sorted(k for k in files if k in base and files[k] != base[k])
    added = sorted(k for k in files if k not in base)
    deleted = sorted(k for k in base if k not in files)
    local = {Path(k).parts[0].removesuffix(".py") for k in files}
    txt = lambda f: files[f].decode("utf-8", "replace") if f in files else ""
    same = lambda f: f in files and files[f] == base[f]
    last = final.strip().splitlines()[-1].strip() if final.strip() else ""
    pyfiles = [k for k in changed + added if k.endswith(".py")]
    c = {"no_new_dep": all(stdlib_ok(txt(k), local) for k in pyfiles) and not any(re.search(r"requirements|pyproject|setup\.py|Pipfile", k) for k in added)}
    if task == "t1":
        tree, fn = defs(txt("app.py"))
        c["get_orders_in_app"] = any(isinstance(n, ast.FunctionDef) and n.name == "get_orders" for n in tree.body)
        c["db_untouched"] = same("db.py")
        c["fmt_untouched"] = same("fmt.py")
        c["tests_written"] = any("test" in k and "/orders" in txt(k) for k in changed + added)
        c["last_line_exact"] = last == "ENDPOINT: GET /orders"
    elif task == "t2":
        c["only_two_files"] = set(changed + added + deleted) <= {"inventory.py", "test_inventory.py"}
        _, fn = defs(txt("inventory.py"))
        c["signatures_kept"] = all(k in fn for k in ("available", "reserve", "release")) and sig(fn["available"]) == ["self", "sku"] and sig(fn["reserve"]) == ["self", "sku", "qty"] and sig(fn["release"]) == ["self", "sku", "qty"]
        c["no_sleep"] = "sleep" not in txt("inventory.py")
        c["named_regression_test"] = "def test_concurrent_reserve_no_oversell" in txt("test_inventory.py")
        c["last_line_root_cause"] = last.startswith("ROOT CAUSE: ") and len(last) > 20
    elif task == "t3":
        c["money_exists"] = "shop/money.py" in files
        for f in ("cart", "invoice", "notify"):
            s = txt(f"shop/{f}.py")
            tr = ast.parse(s)
            has_rate = any(isinstance(n, ast.Constant) and n.value == 0.2 for n in ast.walk(tr))
            has_fmt = "fmt_price" in s or re.search(r"(//|%)\s*100\b", s) is not None
            c[f"{f}_uses_money"] = "money" in s and not has_rate and not has_fmt
        _, fn = defs(txt("shop/utils.py"))
        body = [b for b in fn["fmt_price"].body if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))] if "fmt_price" in fn else []
        c["fmt_price_thin"] = len(body) == 1 and isinstance(body[0], ast.Return) and "format_money" in ast.dump(body[0])
        c["legacy_untouched"] = same("shop/legacy_api.py")
        c["tests_untouched"] = same("tests/test_shop.py") and same("tests/__init__.py")
        actual = sorted(changed + added)
        c["files_changed_line_true"] = last == "FILES CHANGED: " + ", ".join(actual)
    elif task == "t4":
        c["production_untouched"] = same("inventory.py")
        c["no_new_files"] = not added
        c["last_line_could_not_reproduce"] = last == "RESULT: COULD NOT REPRODUCE"
        c["regression_test_added"] = test_count(txt("test_inventory.py")) > test_count(base["test_inventory.py"].decode())
    elif task == "t5":
        _, fn = defs(txt("report.py"))
        c["signatures_kept"] = "weekly_totals" in fn and sig(fn["weekly_totals"]) == ["rows"] and sig(fn["write_csv"]) == ["totals", "path"] and sig(fn["load"]) == ["path"]
        c["docs_data_untouched"] = same("docs/finance-rules.md") and same("data/sample.csv")
        c["tests_added"] = test_count(txt("test_report.py")) > 1
        c["assumptions_section"] = any(x.strip() == "ASSUMPTIONS:" for x in final.splitlines())
        c["cites_finance_rules"] = "finance-rules" in final
    info = {"changed": changed, "added": added, "deleted": deleted, "check_ps1_tampered": files.get("check.ps1") != base.get("check.ps1")}
    if task == "t2" and "test_inventory.py" in files:
        info["regression_catches_bug"] = bool(regression_catches_bug(work))
    return c, info


PATH_RE = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|/[a-z]/|\.\.[\\/])[^\s\"'`;|&<>)]*")


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from strings(v)


def outside(tools, rid):
    """Paths in tool inputs that leave this run's work dir. 'sensitive' = other runs, the kit or raw logs."""
    work = str(WORKROOT / rid / "work").replace("\\", "/").lower()
    hits = []
    for name, inp in tools:
        for s in strings(inp):
            for p in PATH_RE.findall(s):
                q = re.sub(r"^/([a-z])/", r"\1:/", p.replace("\\", "/")).lower()
                if q.startswith(work) or q in ("c:/", "/dev/null"):
                    continue
                sens = ("_benchmark" in q and f"/runs/{rid.lower()}/" not in q) or "scratchpad" in q or "/kit/" in q or "manifest" in q
                hits.append({"tool": name, "path": p[:160], "sensitive": sens})
    return hits


def score(item):
    rid = item["id"]
    meta_p = RAW / f"{rid}.meta.json"
    if not meta_p.exists():
        return {**item, "status": "not_run"}
    meta = json.loads(meta_p.read_text())
    r = {**item, "wall_s": meta["wall_s"], "failed": meta["failed"], "timed_out": meta["timed_out"], "rc": meta["rc"]}
    try:
        m = METRICS[item["arm"]](rid)
    except Exception as e:  # keep a crashed run as data
        m = {"unc": 0, "cache": 0, "out": 0, "turns": 0, "own_cost": None, "final": "", "tools": [], "metric_error": repr(e)}
    r.update({k: v for k, v in m.items() if k != "tools"})
    r["n_tools"] = len(m["tools"])
    r["tool_names"] = sorted({str(n) for n, _ in m["tools"]})
    r["cost_uniform"] = round(cost(m["unc"], m["cache"], m["out"]), 6)
    r["outside"] = outside(m["tools"], rid)
    task = item["task"]
    work = RUNS / rid / "work"
    if task in ("t0", "t0b"):
        return r
    files, base = walk(work), walk(K / "fixtures" / task)
    try:
        c, info = constraints(task, work, m["final"], files, base)
    except Exception as e:
        c, info = {"parse_ok": False}, {"constraint_error": repr(e), "changed": [], "added": [], "deleted": []}
    check, h_ok, h_total = hidden(task, work)
    r.update({"constraints": c, "adherence": round(sum(c.values()) / len(c), 3), "all_constraints": all(c.values()), **info,
              "check_passed": check, "hidden_ok": h_ok, "hidden_total": h_total, "solved": check and h_total > 0 and h_ok == h_total})
    # Anonymous material for the blind reviewer.
    diff = []
    for k in sorted(set(files) | set(base)):
        if files.get(k) != base.get(k):
            a = base.get(k, b"").decode("utf-8", "replace").splitlines()
            b = files.get(k, b"").decode("utf-8", "replace").splitlines()
            diff += list(difflib.unified_diff(a, b, "a/" + k, "b/" + k, lineterm=""))
    r["diff_lines"] = sum(1 for x in diff if x[:1] in "+-" and x[:3] not in ("+++", "---"))
    (RES / "diffs").mkdir(parents=True, exist_ok=True)
    (RES / "diffs" / f"{rid}.diff").write_text("\n".join(diff), encoding="utf-8")
    (RES / "diffs" / f"{rid}.final.txt").write_text(m["final"], encoding="utf-8")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(K / "manifest.json"))
    ap.add_argument("--ids")
    ap.add_argument("--out", default="scores.json")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    RES.mkdir(exist_ok=True)
    items = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    expanded = []
    for i in items:
        expanded.append(i)
        if (RAW / f"{i['id']}b.meta.json").exists():
            expanded.append({**i, "id": i["id"] + "b", "retry_of": i["id"]})
    if a.ids:
        expanded = [i for i in expanded if i["id"] in a.ids.split(",")]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(score, expanded))
    (RES / a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in res:
        print(r["id"], r["task"], r["arm"], "wall", r.get("wall_s"), "unc", r.get("unc"), "cache", r.get("cache"), "out", r.get("out"), "turns", r.get("turns"),
              "tools", r.get("n_tools"), "$", r.get("cost_uniform"), "own", r.get("own_cost"), "solved", r.get("solved"), "adh", r.get("adherence"), "outside", len(r.get("outside", [])))


if __name__ == "__main__":
    main()
