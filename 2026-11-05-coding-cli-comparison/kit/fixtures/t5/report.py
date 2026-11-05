"""Weekly revenue report."""
import csv
from datetime import datetime, timedelta


def weekly_totals(rows):
    """rows: dicts with id, status, amount_cents, created_at (ISO 8601), refund_of (id or '').

    Returns {week_start date: total cents}.
    """
    totals = {}
    for row in rows:
        day = datetime.fromisoformat(row["created_at"]).date()
        # Weeks start on Sunday.
        week = day - timedelta(days=(day.weekday() + 1) % 7)
        amount = abs(int(row["amount_cents"]))
        totals[week] = totals.get(week, 0) + amount
    return totals


def write_csv(totals, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["week_start", "total_cents"])
        for week in sorted(totals):
            w.writerow([week.isoformat(), totals[week]])


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
