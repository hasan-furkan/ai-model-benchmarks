"""Aggregates scores.json (+ blind review results) into results/summary.json and results/summary.md."""
import json
import statistics as st
from pathlib import Path

K = Path(__file__).parent
P = K.parent
RES = P / "results"


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"n": len(xs), "mean": round(st.mean(xs), 4), "median": round(st.median(xs), 4), "min": round(min(xs), 4),
            "max": round(max(xs), 4), "sd": round(st.stdev(xs), 4) if len(xs) > 1 else 0}


def main():
    rows = json.loads((RES / "scores.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in rows}
    counted = [r for r in rows if r["id"] + "b" not in ids and r["task"] not in ("t0", "t0b") and r.get("status") != "not_run"]
    first_fail = {r["id"]: r for r in rows if r["id"] + "b" in ids}
    review = {}
    mp = RES / "review_map.json"
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))
        for f in RES.glob("review_t*.json"):
            task = f.stem.split("_")[1]
            for o in json.loads(f.read_text(encoding="utf-8")):
                rid = m.get(f"{task}/{o.get('label')}")
                if rid:
                    review[rid] = o
    # Go quota ratio measured on arm C (provider-reported allowance vs uniform list cost).
    cs = [r for r in rows if r["arm"] == "C" and r.get("go_allowance")]
    ratio = sum(r["go_allowance"] for r in cs) / max(sum(r["cost_uniform"] for r in cs), 1e-9) if cs else 0.6
    out = {"go_ratio": round(ratio, 4), "arms": {}, "cells": {}}
    for arm in "ABC":
        a = [r for r in counted if r["arm"] == arm]
        rv = [review[r["id"]] for r in a if r["id"] in review]
        allruns = [r for r in rows if r["arm"] == arm and r["task"] not in ("t0", "t0b") and r.get("status") != "not_run"]
        out["arms"][arm] = {
            "runs": len(a),
            "solved": sum(bool(r.get("solved")) for r in a),
            "all_constraints": sum(bool(r.get("all_constraints")) for r in a),
            "solved_and_all_constraints": sum(bool(r.get("solved")) and bool(r.get("all_constraints")) for r in a),
            "adherence": stats([r.get("adherence") for r in a]),
            "cost_uniform_per_run": stats([r.get("cost_uniform") for r in a]),
            "cost_uniform_total_incl_retries": round(sum(r.get("cost_uniform") or 0 for r in allruns), 4),
            "wall_s": stats([r.get("wall_s") for r in a]),
            "turns": stats([r.get("turns") for r in a]),
            "tools": stats([r.get("n_tools") for r in a]),
            "tokens_unc": stats([r.get("unc") for r in a]), "tokens_cache": stats([r.get("cache") for r in a]),
            "tokens_out": stats([r.get("out") for r in a]),
            "failed_first_attempt": sum(1 for x in first_fail.values() if x["arm"] == arm),
            "failed_counted": sum(bool(r.get("failed")) for r in a),
            "timeouts": sum(bool(r.get("timed_out")) for r in allruns),
            "api_errors": sum(r.get("api_errors") or 0 for r in allruns),
            "outside_runs": sum(1 for r in allruns if r.get("outside")),
            "outside_sensitive_runs": sum(1 for r in allruns if any(o.get("sensitive") for o in r.get("outside", []))),
            "check_ps1_tampered": sum(bool(r.get("check_ps1_tampered")) for r in a),
            "t4_production_changed": sum(1 for r in a if r["task"] == "t4" and not (r.get("constraints") or {}).get("production_untouched", True)),
            "review_n": len(rv),
            "review_right_problem_yes": sum(1 for o in rv if o.get("right_problem") == "yes"),
            "review_correct_yes": sum(1 for o in rv if o.get("correct") == "yes"),
            "review_quality": stats([o.get("quality") for o in rv if isinstance(o.get("quality"), (int, float))]),
        }
        for t in sorted({r["task"] for r in a}):
            c = [r for r in a if r["task"] == t]
            out["cells"][f"{t}/{arm}"] = {
                "solved": f"{sum(bool(r.get('solved')) for r in c)}/{len(c)}",
                "all_constraints": f"{sum(bool(r.get('all_constraints')) for r in c)}/{len(c)}",
                "adherence": stats([r.get("adherence") for r in c]),
                "cost": stats([r.get("cost_uniform") for r in c]), "wall": stats([r.get("wall_s") for r in c]),
                "failed_constraints": sorted({k for r in c for k, v in (r.get("constraints") or {}).items() if not v}),
                "review_quality": [review[r["id"]].get("quality") for r in c if r["id"] in review],
                "review_right": [review[r["id"]].get("right_problem") for r in c if r["id"] in review],
            }
    (RES / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
