"""Builds blind review packets: per task, every scored run's diff + final message labelled X1.. in random order.
Packets go to B/_review/<task>/ (reviewer's work dir); the label->run mapping stays private in P/results/review_map.json.
Usage: build_review.py --scores scores.json
"""
import argparse
import json
import random
import shutil
from pathlib import Path

K = Path(__file__).parent
P = K.parent
B = Path(r"C:\Users\<user>\Desktop\projects\_benchmark\cli-2026-11-05")
RES = P / "results"
OUT = B / "_review"

PROMPT = """You are a blind code reviewer. Do not modify any file. Do not run commands.

Folder contents:
- TASK.md: the exact task that was given to several anonymous coding agents.
- fixture/: the starting code every agent received.
- X1.diff, X1.final.txt, X2.diff, ...: for each anonymous submission, the unified diff it made and its final message.

For EACH submission judge only from these files:
1. right_problem: did it solve the problem the task actually asks for (not a different or easier one)? yes / partly / no
2. correct: is the change logically correct for the stated requirements? yes / partly / no
3. constraint_violations: list any explicit task rule it broke (file limits, names, last-line format, forbidden edits), or "none".
4. quality: 1-5 (5 = what a careful senior engineer would merge).
5. note: one sentence, the most important reason.

Answer with ONLY a JSON array, one object per submission, in label order:
[{"label":"X1","right_problem":"yes","correct":"yes","constraint_violations":"none","quality":4,"note":"..."}, ...]
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default="scores.json")
    a = ap.parse_args()
    rows = json.loads((RES / a.scores).read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    rng = random.Random(4242)
    mapping = {}
    for task in sorted({r["task"] for r in rows if r["task"].startswith("t") and r["task"] not in ("t0", "t0b")}):
        ids = {r["id"] for r in rows}
        # Only the counted attempt per item: the retry when one exists.
        runs = [r for r in rows if r["task"] == task and r.get("status") != "not_run" and r["id"] + "b" not in ids
                and (RES / "diffs" / f"{r['id']}.diff").exists()]
        rng.shuffle(runs)
        d = OUT / task
        shutil.copytree(K / "fixtures" / task, d / "fixture")
        (d / "TASK.md").write_text((K / "tasks" / f"{task}.md").read_text(encoding="utf-8"), encoding="utf-8")
        (d / "REVIEW.md").write_text(PROMPT, encoding="utf-8")
        for i, r in enumerate(runs, 1):
            lab = f"X{i}"
            mapping[f"{task}/{lab}"] = r["id"]
            shutil.copy(RES / "diffs" / f"{r['id']}.diff", d / f"{lab}.diff")
            shutil.copy(RES / "diffs" / f"{r['id']}.final.txt", d / f"{lab}.final.txt")
    (RES / "review_map.json").write_text(json.dumps(mapping, indent=1), encoding="utf-8")
    print(len(mapping), "submissions")


if __name__ == "__main__":
    main()
