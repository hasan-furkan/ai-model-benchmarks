import csv
import os
import tempfile
import unittest
from datetime import date

from report import load, weekly_totals, write_csv


def r(i, amount, at, status="paid", refund_of=""):
    return {"id": str(i), "status": status, "amount_cents": str(amount), "created_at": at, "refund_of": refund_of}


class Hidden(unittest.TestCase):
    def test_monday_start(self):
        t = weekly_totals([r(1, 100, "2026-03-08T12:00:00+00:00")])  # a Sunday
        self.assertEqual(t, {date(2026, 3, 2): 100})

    def test_utc_boundary(self):
        t = weekly_totals([r(1, 100, "2026-03-08T23:30:00-05:00")])  # Monday 04:30 UTC
        self.assertEqual(t, {date(2026, 3, 9): 100})

    def test_voided_excluded(self):
        t = weekly_totals([r(1, 100, "2026-03-04T12:00:00+00:00"), r(2, 999, "2026-03-04T12:00:00+00:00", "voided")])
        self.assertEqual(t, {date(2026, 3, 2): 100})

    def test_refund_goes_to_original_week(self):
        t = weekly_totals([r(1, 1000, "2026-03-04T12:00:00+00:00"), r(2, -200, "2026-03-18T12:00:00+00:00", refund_of="1")])
        self.assertEqual(t, {date(2026, 3, 2): 800})

    def test_orphan_refund_own_week(self):
        t = weekly_totals([r(2, -200, "2026-03-18T12:00:00+00:00", refund_of="77")])
        self.assertEqual(t, {date(2026, 3, 16): -200})

    def test_refund_before_sale_in_row_order(self):
        t = weekly_totals([r(2, -200, "2026-03-18T12:00:00+00:00", refund_of="1"), r(1, 1000, "2026-03-04T12:00:00+00:00")])
        self.assertEqual(t, {date(2026, 3, 2): 800})

    def test_csv_format(self):
        p = os.path.join(tempfile.mkdtemp(), "o.csv")
        write_csv({date(2026, 3, 2): 5}, p)
        with open(p, newline="", encoding="utf-8") as f:
            self.assertEqual(list(csv.reader(f)), [["week_start", "total_cents"], ["2026-03-02", "5"]])

    def test_sample_file(self):
        t = weekly_totals(load("data/sample.csv"))
        self.assertEqual(t, {date(2026, 3, 2): 1300})
