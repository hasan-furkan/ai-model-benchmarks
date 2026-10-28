import unittest

from app import handle


class HiddenOrdersTest(unittest.TestCase):
    def test_orders_newest_first_with_conventions(self):
        status, body = handle("GET", "/orders", {"customer_id": "1"})
        self.assertEqual(status, 200)
        self.assertEqual([o["id"] for o in body], [102, 101], "newest first")
        self.assertEqual(body[0]["created_at"], "2026-10-27T11:00:00Z", "UTC + Z like every endpoint")
        self.assertEqual(body[1]["created_at"], "2026-10-19T22:30:00Z", "local midnight crosses to the previous UTC day")
        self.assertEqual(body[0]["total"], "5.00", "money is a two-decimal string")
        self.assertEqual(body[1]["total"], "19.90")

    def test_customer_without_orders_is_empty_200(self):
        self.assertEqual(handle("GET", "/orders", {"customer_id": "2"}), (200, []))

    def test_missing_customer_id_is_400_error_object(self):
        status, body = handle("GET", "/orders", {})
        self.assertEqual(status, 400)
        self.assertIsInstance(body, dict)
        self.assertIn("error", body)

    def test_non_numeric_customer_id_is_400(self):
        status, body = handle("GET", "/orders", {"customer_id": "1 OR 1=1"})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_existing_endpoints_unchanged(self):
        self.assertEqual(handle("GET", "/customers", {"city": "Gdansk"}), (200, []))
        self.assertEqual(handle("POST", "/orders", {})[0], 405)


if __name__ == "__main__":
    unittest.main()
