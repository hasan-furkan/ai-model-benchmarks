"""Benchmark runner. Usage: run_bench.py --manifest kit/manifest.json [--tasks t0] [--ids r01,r02] [--jobs 3]"""
import argparse
import http.client
import http.server
import json
import os
import random
import re
import shutil
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

K = Path(__file__).parent
P = K.parent  # private: kit, raw logs, finished runs, out of the workers' reach
B = Path(r"C:\Users\<user>\Desktop\projects\_benchmark\cli-2026-11-05")
RUNS = B / "runs"
RAW = P / "raw"
DONE = P / "done"
SCRIPT = Path(os.environ["USERPROFILE"]) / ".claude/scripts/deepseek-agent.ps1"
NODE = B / "_tools/node24/node.exe"
DSH = B / "_tools/dsh/node_modules/@deepseek-ai/dsh/lib/bin.js"
TIMEOUT = 1800
QUOTA = re.compile(r"\b429\b|rate.?limit|quota|insufficient", re.I)
stop = threading.Event()
log_lock = threading.Lock()


def rules():
    s = SCRIPT.read_text(encoding="utf-8-sig")
    m = re.search(r"\$rules = @'\r?\n(.*?\r?\n)'@", s, re.S)
    return m.group(1)


def go_key():
    k = os.environ.get("OPENCODE_GO_API_KEY")
    if not k:
        k = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "[Environment]::GetEnvironmentVariable('OPENCODE_GO_API_KEY','User')"],
            capture_output=True, text=True).stdout.strip()
    assert k, "no Go key"
    return k


KEY = go_key()


def clean_env():
    """B and C do not inherit this session's Claude/Anthropic variables."""
    e = {k: v for k, v in os.environ.items() if not re.match(r"(CLAUDE|ANTHROPIC|DEEPSEEK_WORKER)", k, re.I)}
    return e


# ---- Usage-recording pass-through proxy for arm C: dsh's own logs drop the cache split.
# Forwards bytes unchanged; records only the provider's `usage` objects. Authorization is never logged.
class Proxy(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def _fwd(self):
        parts = self.path.lstrip("/").split("/", 1)
        rid, rest = parts[0], "/" + (parts[1] if len(parts) > 1 else "")
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else None
        hdrs = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "accept-encoding", "connection")}
        hdrs["Accept-Encoding"] = "identity"
        c = http.client.HTTPSConnection("opencode.ai", timeout=600)
        c.request(self.command, rest, body, hdrs)
        r = c.getresponse()
        self.send_response(r.status)
        for k, v in r.getheaders():
            if k.lower() not in ("transfer-encoding", "connection", "content-length", "content-encoding"):
                self.send_header(k, v)
        self.send_header("Connection", "close")
        self.end_headers()
        buf = b""
        with open(RAW / f"{rid}.usage.jsonl", "a", encoding="utf-8") as lg:
            lg.write(json.dumps({"req": rest, "status": r.status, "t": time.time()}) + "\n")
            while True:
                chunk = r.read1(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if b'"usage"' in line:
                        s = line.decode("utf-8", "replace")
                        m = re.search(r'"usage"\s*:\s*(?=\{)', s)
                        u = None
                        if m:
                            try:
                                u, _ = json.JSONDecoder().raw_decode(s, m.end())
                            except ValueError:
                                u = None
                        lg.write(json.dumps(u) + "\n")
                        lg.flush()
        c.close()

    do_POST = do_GET = _fwd


def start_proxy():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


PROXY_PORT = None


def log(msg):
    with log_lock:
        with open(RAW / "runner.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def prepare(rid, task):
    d = RUNS / rid / "work"
    if d.parent.exists():
        shutil.rmtree(d.parent, ignore_errors=True)
    d.mkdir(parents=True)
    src = K / "fixtures" / task
    if src.exists():
        shutil.copytree(src, d, dirs_exist_ok=True)
    def g(*a):
        subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "user.name=bench", "-c", "user.email=bench@example.invalid", *a],
                       cwd=d, check=True, capture_output=True)
    g("init", "-q")
    g("config", "core.autocrlf", "false")
    g("add", "-A")
    g("commit", "-q", "--allow-empty", "-m", "base")
    return d


def command(arm, rid, task, env):
    taskfile = K / "tasks" / f"{task}.md"
    text = taskfile.read_text(encoding="utf-8")
    if arm == "A":
        return (["powershell", "-NoProfile", "-File", str(SCRIPT), "-TaskFile", str(taskfile), "-Dir", str(RUNS / rid / "work"),
                 "-Provider", "go", "-Model", "deepseek-reasoner", "-Mode", "bypassPermissions", "-Json"], None, dict(os.environ))
    full = rules() + text
    if arm == "B":
        return (["cmd", "/c", "opencode", "run", "--standalone", "-m", "opencode-go/deepseek-v4.1-flash#high", "--auto",
                 "--format", "json", "--title", f"bench-{rid}"], full, clean_env())
    # C
    patch = (K / "config/dsh-go.patch.tmpl.yml").read_text(encoding="utf-8").replace("__SESSION__", str(uuid.uuid4())).replace(
        "https://opencode.ai/inference", f"http://127.0.0.1:{PROXY_PORT}/{rid}/inference")
    pf = RAW / f"{rid}.patch.yml"
    pf.write_text(patch, encoding="utf-8")
    e = clean_env()
    e["DSH_HOME"] = str(P / "dshhome")
    e["OPENCODE_GO_API_KEY"] = KEY
    return ([str(NODE), str(DSH), "--profile", "headless", "--patch", str(pf), "--json", "--permission-mode", "workspace-write",
             "--approval-policy", "never", "-"], full, e)


def scrub(p):
    if p.exists():
        b = p.read_bytes()
        if KEY.encode() in b:
            p.write_bytes(b.replace(KEY.encode(), b"[REDACTED]"))


def failed(arm, out, err, rc, timed_out):
    if timed_out or rc != 0:
        return True
    if arm == "A":
        try:
            return bool(json.loads(out).get("is_error"))
        except Exception:
            return True
    if arm == "B":
        return not re.search(r'"type":"text"', out) or bool(re.search(r'^\{"type":"error"', out, re.M))
    return '"completed"' not in out


def kit_hash():
    import hashlib
    h = hashlib.sha256()
    for sub in ("fixtures", "hidden", "tasks"):
        for p in sorted((K / sub).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                h.update(p.relative_to(K).as_posix().encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


KIT_HASH = kit_hash()


def _force(func, path, _exc):
    os.chmod(path, 0o666)  # git object files are read-only on Windows
    func(path)


def move_run(run_id):
    # Copy once, verify, then only ever retry deleting the source. Never touch dst after a good copy
    # (the old loop deleted the good copy and re-copied a half-deleted source when a file was locked).
    src, dst = RUNS / run_id, DONE / run_id
    if dst.exists():
        log(f"{run_id} MOVE FAILED, done/ already exists; left in runs/")
        return
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        log(f"{run_id} MOVE FAILED (copy): {e!r}; left in runs/")
        return
    n_src = sum(1 for _ in src.rglob("*"))
    n_dst = sum(1 for _ in dst.rglob("*"))
    if n_src != n_dst:
        log(f"{run_id} MOVE FAILED, copy incomplete {n_dst}/{n_src}; left in runs/")
        return
    for _ in range(12):
        try:
            shutil.rmtree(src, onerror=_force)
            return
        except OSError as e:
            log(f"{run_id} source delete retry: {e!r}")
            time.sleep(10)
    log(f"{run_id} copied to done/, source left in runs/ (locked)")


def run_one(item):
    try:
        _run_one(item)
    except Exception as e:  # one broken run must not stop the batch
        log(f"{item['id']} RUNNER ERROR {e!r}")


def _run_one(item):
    rid, task, arm = item["id"], item["task"], item["arm"]
    if stop.is_set():
        log(f"{rid} skipped (stop)")
        return
    for attempt in (1, 2):
        run_id = rid if attempt == 1 else rid + "b"
        d = prepare(run_id, task)
        cmd, stdin_text, env = command(arm, run_id, task, env=None)
        # OpenCode takes its project dir from PWD, not the process cwd: pin it (and drop shell leftovers) for every arm.
        env = {k: v for k, v in env.items() if k.upper() not in ("PWD", "OLDPWD", "INIT_CWD")}
        env["PWD"] = str(d)
        out_p, err_p = RAW / f"{run_id}.out", RAW / f"{run_id}.err"
        t0 = time.time()
        log(f"{run_id} start {task} {arm}")
        with open(out_p, "wb") as o, open(err_p, "wb") as e:
            p = subprocess.Popen(cmd, cwd=d, env=env, stdout=o, stderr=e, stdin=subprocess.PIPE if stdin_text else subprocess.DEVNULL)
            if stdin_text:
                try:
                    p.stdin.write(stdin_text.encode("utf-8"))
                    p.stdin.close()
                except OSError:
                    pass
            timed_out = False
            try:
                rc = p.wait(TIMEOUT)
            except subprocess.TimeoutExpired:
                timed_out = True
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                rc = p.wait()
        wall = time.time() - t0
        scrub(out_p)
        scrub(err_p)
        out = out_p.read_text(encoding="utf-8", errors="replace")
        err = err_p.read_text(encoding="utf-8", errors="replace")
        bad = failed(arm, out, err, rc, timed_out)
        meta = {"id": run_id, "item": rid, "task": task, "arm": arm, "attempt": attempt, "rc": rc, "wall_s": round(wall, 1),
                "timed_out": timed_out, "failed": bad, "t_start": t0}
        (RAW / f"{run_id}.meta.json").write_text(json.dumps(meta), encoding="utf-8")
        log(f"{run_id} end rc={rc} wall={wall:.0f}s failed={bad}")
        if kit_hash() != KIT_HASH:
            stop.set()
            log(f"{run_id} STOP: kit fixtures/hidden/tasks changed during the batch")
        move_run(run_id)
        if not bad:
            return
        # Only a failed run is searched: task output can legitimately contain these words.
        if QUOTA.search(err) or QUOTA.search(out[-4000:]):
            stop.set()
            log(f"{run_id} STOP: quota/limit pattern in failed run")
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(K / "manifest.json"))
    ap.add_argument("--tasks")
    ap.add_argument("--ids")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    global PROXY_PORT
    PROXY_PORT = start_proxy()
    RAW.mkdir(exist_ok=True)
    RUNS.mkdir(exist_ok=True)
    m = Path(a.manifest)
    if not m.exists():
        items = [{"task": t, "arm": arm, "rep": r} for t in ("t1", "t2", "t3", "t4", "t5") for arm in "ABC" for r in (1, 2, 3)]
        random.Random(20261105).shuffle(items)
        for i, it in enumerate(items, 1):
            it["id"] = f"r{i:02d}"
        items += [{"task": "t0", "arm": arm, "rep": r, "id": f"o{arm}{r}"} for arm in "ABC" for r in (1, 2)]
        m.write_text(json.dumps(items, indent=1), encoding="utf-8")
    items = json.loads(m.read_text(encoding="utf-8"))
    if a.tasks == "all":
        pass
    elif a.tasks:
        items = [i for i in items if i["task"] in a.tasks.split(",")]
    else:
        items = [i for i in items if i["task"] != "t0"]
    if a.ids:
        items = [i for i in items if i["id"] in a.ids.split(",")]
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(run_one, items))
    log("batch end" + (" STOPPED" if stop.is_set() else ""))
    print("STOPPED" if stop.is_set() else "done")


if __name__ == "__main__":
    main()
