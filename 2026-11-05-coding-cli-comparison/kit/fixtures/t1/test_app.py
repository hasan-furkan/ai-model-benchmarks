import unittest

from app import handle


class CustomersTest(unittest.TestCase):
    def test_list_uses_utc_and_money_strings(self):
        status, body = handle("GET", "/customers", {})
        self.assertEqual(status, 200)
        ada = body[0]
        self.assertEqual(ada["created_at"], "2026-07-01T08:00:00Z")
        self.assertEqual(ada["balance"], "12.50")

    def test_filter_with_no_match_is_empty_200(self):
        self.assertEqual(handle("GET", "/customers", {"city": "Gdansk"}), (200, []))

    def test_unknown_customer_is_404(self):
        self.assertEqual(handle("GET", "/customers/99", {}), (404, {"error": "customer not found"}))

    def test_bad_id_is_400(self):
        self.assertEqual(handle("GET", "/customers/abc", {})[0], 400)


if __name__ == "__main__":
    unittest.main()
