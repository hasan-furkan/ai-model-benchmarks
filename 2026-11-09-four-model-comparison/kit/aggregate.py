"""Aggregate results/runs.jsonl into results/summary.md (+ summary.json).

Success means:
  * agent tasks  -> valid run, hidden tests all pass (`solved`)
  * no-tool tasks -> valid run with a non-empty answer (`solved`), and the
    auto_keyword score is reported separately because it needs human review.

Usage:
    python kit/aggregate.py
    python kit/aggregate.py --runs kit/testdata/runs.jsonl --out kit/testdata/summary.md
"""
from __future__ import annotations

import argparse
import json
import statistics as stats
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KIT = Path(__file__).resolve().parent
BENCH = KIT.parent
DEFAULT_RUNS = BENCH / "results" / "runs.jsonl"

ARM_ORDER = ["luna", "deepseek", "mimo", "minimax"]
TASK_ORDER = ["api", "stok", "t1", "t2", "t3", "t4", "t5",
              "rc", "rand", "lma1", "lma2", "lmaghost",
              "kod1", "belge1", "kod2", "belge2", "ghost",
              "zor1", "zor2", "zor3"]
TOKEN_FIELDS = [
    ("input_tokens", "input"),
    ("cache_read_tokens", "cache read"),
    ("cache_write_tokens", "cache write"),
    ("output_tokens", "output"),
    ("reasoning_tokens", "reasoning"),
    ("total_tokens", "total"),
]


# ---------------------------------------------------------------- helpers
def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict) or not row.get("run_id"):
                continue
            key = row["run_id"]
            if key not in rows:
                order.append(key)
            rows[key] = row
    return [rows[key] for key in order]


def numeric(values: list[Any]) -> list[float]:
    return [float(value) for value in values if isinstance(value, (int, float))]


def stat_block(values: list[Any]) -> dict[str, Any]:
    vals = numeric(values)
    if not vals:
        return {"n": 0, "sum": None, "mean": None, "median": None, "min": None, "max": None}
    return {
        "n": len(vals),
        "sum": round(sum(vals), 4),
        "mean": round(stats.mean(vals), 4),
        "median": round(stats.median(vals), 4),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
    }


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.{digits}f}"
    return str(value)


def fmt_pair(block: dict[str, Any], digits: int = 0) -> str:
    if not block["n"]:
        return "-"
    return f"{fmt(block['sum'], digits)} / {fmt(block['mean'], digits)}"


def rate(numerator: int, denominator: int) -> str:
    if not denominator:
        return "-"
    return f"{numerator / denominator * 100:.0f}% ({numerator}/{denominator})"


def ratio(ok: int, total: int) -> str:
    return f"{ok}/{total}" if total else "-"


# ---------------------------------------------------------------- grouping
def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if row.get("valid")]
    success = [row for row in valid if row.get("solved")]
    timed = [row for row in rows if row.get("timed_out")]
    errored = [row for row in rows if row.get("error_events")]
    usage_rows = [row for row in valid if row.get("usage_source") != "unavailable"]
    cost_values = [row.get("cost_usd") for row in valid if row.get("cost_usd") is not None]
    wall_values = [row.get("wall_seconds") for row in valid if not row.get("timed_out")]

    tokens = {key: stat_block([row.get(key) for row in usage_rows]) for key, _ in TOKEN_FIELDS}
    cost_sum = round(sum(cost_values), 6) if cost_values else None
    cost_mean = round(stats.mean(cost_values), 6) if cost_values else None

    keyword_scores = [row["auto_keyword"]["score"] for row in valid
                      if isinstance(row.get("auto_keyword"), dict)
                      and isinstance(row["auto_keyword"].get("score"), (int, float))]

    # New fields are optional: rows written before 2026-11-09 lack them.
    constraint_rows = [row for row in valid if isinstance(row.get("constraints"), dict)]
    constraints_ok = sum(1 for row in constraint_rows if row.get("constraints_ok"))
    adherence = [sum(1 for value in row["constraints"].values() if value) / len(row["constraints"])
                 for row in constraint_rows if row["constraints"]]
    exact_rows = [row for row in rows if isinstance(row.get("auto_keyword"), dict)
                  and row["auto_keyword"].get("auto_exact") is not None]
    exact_ok = sum(1 for row in exact_rows if row["auto_keyword"].get("auto_exact"))
    production_changed = sum(1 for row in rows if row.get("production_changed"))

    return {
        "runs": len(rows),
        "valid": len(valid),
        "invalid": len(rows) - len(valid),
        "success": len(success),
        "success_rate": round(len(success) / len(valid), 4) if valid else None,
        "wall": stat_block(wall_values),
        "timeouts": len(timed),
        "errors": len(errored),
        "nonzero_exit": sum(1 for row in rows if row.get("exit_code") not in (0, None)),
        "missing_final_step_usage": sum(1 for row in rows if row.get("missing_final_step_usage")),
        "usage_unavailable": sum(1 for row in rows if row.get("usage_source") == "unavailable"),
        "outside_access": sum(1 for row in rows if row.get("outside_access")),
        "tokens": tokens,
        "cost_sum": cost_sum,
        "cost_mean": cost_mean,
        "cost_per_success": round(cost_sum / len(success), 6) if cost_sum is not None and success else None,
        "keyword_mean": round(stats.mean(keyword_scores), 4) if keyword_scores else None,
        "keyword_n": len(keyword_scores),
        "constraints_checked": len(constraint_rows),
        "constraints_ok": constraints_ok,
        "constraints_adherence": round(stats.mean(adherence), 4) if adherence else None,
        "exact_n": len(exact_rows),
        "exact_ok": exact_ok,
        "production_changed": production_changed,
        "agent_runs": sum(1 for row in rows if row.get("group") != "notool"),
        "notool_runs": sum(1 for row in rows if row.get("group") == "notool"),
    }


def task_sort_key(task: str) -> tuple[int, str]:
    try:
        return (TASK_ORDER.index(task), task)
    except ValueError:
        return (len(TASK_ORDER), task)


def arm_sort_key(arm: str) -> tuple[int, str]:
    try:
        return (ARM_ORDER.index(arm), arm)
    except ValueError:
        return (len(ARM_ORDER), arm)


# ---------------------------------------------------------------- markdown
def markdown(rows: list[dict[str, Any]], source: Path) -> str:
    arms = sorted({row.get("arm", "?") for row in rows if row.get("arm")}, key=arm_sort_key)
    tasks = sorted({row.get("task", "?") for row in rows if row.get("task")}, key=task_sort_key)

    lines: list[str] = []
    lines.append("# Model comparison 2026-11-09")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}  ")
    lines.append(f"Source: `{source}` ({len(rows)} unique run_ids)  ")
    lines.append("")
    lines.append("Success = valid run **and** all hidden tests pass (agent tasks), or a non-empty "
                 "answer (no-tool tasks). Invalid runs are excluded from success rates and from "
                 "time/token/cost statistics but are counted in their own column.")
    lines.append("")
    lines.append("No-tool scores come from `auto_keyword` heuristics and **require human review**; "
                 "they are not model quality claims.")
    lines.append("")
    lines.append("`constraints ok` = agent-cli runs whose contract checks all passed. "
                 "`exact` = zor runs whose last number matched the expected value. "
                 "`prod changed` = runs that touched non-test code (must be 0 for `lmaghost`).")
    lines.append("")
    lines.append("Token cells are `sum / mean` over valid runs with available usage. "
                 "Cost is exactly what OpenCode reported (step events or its session DB).")
    lines.append("")

    # -------- per arm
    lines.append("## Per arm")
    lines.append("")
    header = ["arm", "model", "effort", "runs", "valid", "invalid", "success", "success rate",
              "median s", "min s", "max s", "timeouts", "errors",
              "constraints ok", "exact", "prod changed",
              "input", "cache read", "cache write", "output", "reasoning", "total",
              "cost $ sum", "cost $ mean", "cost/success", "outside", "missing final usage"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    overall = {}
    for arm in arms:
        arm_rows = [row for row in rows if row.get("arm") == arm]
        summary = summarize(arm_rows)
        overall[arm] = summary
        model = next((row.get("model") for row in arm_rows if row.get("model")), "-")
        effort = next((row.get("effort") for row in arm_rows if row.get("effort")), "-")
        cells = [
            arm, f"`{model}`", effort, summary["runs"], summary["valid"], summary["invalid"],
            summary["success"], rate(summary["success"], summary["valid"]),
            fmt(summary["wall"]["median"]), fmt(summary["wall"]["min"]), fmt(summary["wall"]["max"]),
            summary["timeouts"], summary["errors"],
            ratio(summary["constraints_ok"], summary["constraints_checked"]),
            ratio(summary["exact_ok"], summary["exact_n"]),
            summary["production_changed"],
        ]
        cells += [fmt_pair(summary["tokens"][key], 0) for key, _ in TOKEN_FIELDS]
        cells += [
            fmt(summary["cost_sum"], 4), fmt(summary["cost_mean"], 4),
            fmt(summary["cost_per_success"], 4), summary["outside_access"],
            summary["missing_final_step_usage"],
        ]
        lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
    lines.append("")

    # -------- per arm x task
    lines.append("## Per arm x task")
    lines.append("")
    header = ["arm", "task", "group", "runs", "valid", "invalid", "success", "success rate",
              "median s", "min s", "max s", "timeouts", "errors",
              "input", "cache read", "cache write", "output", "reasoning", "total",
              "cost $ sum", "cost $ mean", "cost/success", "gate pass",
              "constraints ok", "exact", "prod changed", "keyword mean"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    cells_out = {}
    for arm in arms:
        for task in tasks:
            cell_rows = [row for row in rows if row.get("arm") == arm and row.get("task") == task]
            if not cell_rows:
                continue
            summary = summarize(cell_rows)
            cells_out[f"{arm}/{task}"] = summary
            gate_rows = [row for row in cell_rows if row.get("gate_passed") is not None]
            gate_pass = sum(1 for row in gate_rows if row["gate_passed"])
            cells = [
                arm, task, cell_rows[0].get("group", "-"), summary["runs"], summary["valid"],
                summary["invalid"], summary["success"], rate(summary["success"], summary["valid"]),
                fmt(summary["wall"]["median"]), fmt(summary["wall"]["min"]), fmt(summary["wall"]["max"]),
                summary["timeouts"], summary["errors"],
            ]
            cells += [fmt_pair(summary["tokens"][key], 0) for key, _ in TOKEN_FIELDS]
            cells += [
                fmt(summary["cost_sum"], 4), fmt(summary["cost_mean"], 4),
                fmt(summary["cost_per_success"], 4),
                f"{gate_pass}/{len(gate_rows)}" if gate_rows else "-",
                ratio(summary["constraints_ok"], summary["constraints_checked"]),
                ratio(summary["exact_ok"], summary["exact_n"]),
                summary["production_changed"],
                fmt(summary["keyword_mean"], 3) if summary["keyword_mean"] is not None else "-",
            ]
            lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
    lines.append("")

    # -------- no-tool detail
    lines.append("## No-tool answers (auto_keyword, needs human review)")
    lines.append("")
    lines.append("| arm | task | valid answers | exact | keyword mean |")
    lines.append("|---|---|---|---|---|")
    for arm in arms:
        for task in tasks:
            cell_rows = [row for row in rows if row.get("arm") == arm and row.get("task") == task
                         and row.get("group") == "notool"]
            if not cell_rows:
                continue
            scores = [row["auto_keyword"]["score"] for row in cell_rows
                      if isinstance(row.get("auto_keyword"), dict)
                      and isinstance(row["auto_keyword"].get("score"), (int, float))]
            exact_rows = [row for row in cell_rows if isinstance(row.get("auto_keyword"), dict)
                          and row["auto_keyword"].get("auto_exact") is not None]
            exact_ok = sum(1 for row in exact_rows if row["auto_keyword"].get("auto_exact"))
            answers = sum(1 for row in cell_rows if row.get("valid") and row.get("answer_chars"))
            mean = f"{stats.mean(scores):.3f}" if scores else "-"
            lines.append(f"| {arm} | {task} | {answers} | "
                         f"{ratio(exact_ok, len(exact_rows))} | {mean} |")
    lines.append("")

    invalid_rows = [row for row in rows if not row.get("valid")]
    if invalid_rows:
        lines.append("## Invalid runs")
        lines.append("")
        lines.append("| run_id | reasons |")
        lines.append("|---|---|")
        for row in invalid_rows:
            lines.append(f"| {row.get('run_id')} | {', '.join(row.get('invalid_reasons') or ['?'])} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", default=str(DEFAULT_RUNS))
    parser.add_argument("--out", default=str(BENCH / "results" / "summary.md"))
    parser.add_argument("--json-out", default=str(BENCH / "results" / "summary.json"))
    args = parser.parse_args(argv)

    source = Path(args.runs)
    if not source.is_file():
        print(f"ERROR: runs file not found: {source}")
        return 2
    rows = load_rows(source)
    if not rows:
        print(f"ERROR: no usable rows in {source}")
        return 2

    arms = sorted({row.get("arm", "?") for row in rows if row.get("arm")}, key=arm_sort_key)
    tasks = sorted({row.get("task", "?") for row in rows if row.get("task")}, key=task_sort_key)
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(source),
        "rows": len(rows),
        "arms": {arm: summarize([row for row in rows if row.get("arm") == arm]) for arm in arms},
        "cells": {
            f"{arm}/{task}": summarize([row for row in rows if row.get("arm") == arm
                                        and row.get("task") == task])
            for arm in arms for task in tasks
            if any(row.get("arm") == arm and row.get("task") == task for row in rows)
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown(rows, source), encoding="utf-8")

    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {out_path}")
    print(f"wrote {json_path}")
    for arm in arms:
        summary = data["arms"][arm]
        print(f"{arm:<9} valid={summary['valid']}/{summary['runs']} "
              f"success={summary['success']}/{summary['valid']} "
              f"median={fmt(summary['wall']['median'])}s cost={fmt(summary['cost_sum'], 4)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
