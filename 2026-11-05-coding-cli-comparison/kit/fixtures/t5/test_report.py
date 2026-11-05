import unittest
from datetime import date

from report import weekly_totals


class ReportTest(unittest.TestCase):
    def test_single_sale_midweek(self):
        rows = [{"id": "1", "status": "paid", "amount_cents": "1000", "created_at": "2026-03-04T10:00:00+00:00", "refund_of": ""}]
        self.assertEqual(sum(weekly_totals(rows).values()), 1000)
        self.assertEqual(len(weekly_totals(rows)), 1)
        self.assertIsInstance(next(iter(weekly_totals(rows))), date)


if __name__ == "__main__":
    unittest.main()
