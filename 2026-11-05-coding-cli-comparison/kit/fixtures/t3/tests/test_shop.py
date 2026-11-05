import unittest

from shop.cart import Cart
from shop.invoice import render_line, render_total
from shop.legacy_api import partner_price
from shop.notify import receipt_message, refund_message
from shop.utils import fmt_price


class ShopTest(unittest.TestCase):
    def test_fmt_price(self):
        self.assertEqual(fmt_price(1999), "19.99 USD")
        self.assertEqual(fmt_price(-5, "EUR"), "-0.05 EUR")

    def test_cart(self):
        c = Cart()
        c.add("pen", 150, 2)
        self.assertEqual(c.tax(), 60)
        self.assertEqual(c.summary(), "1 items, total 3.60 USD")

    def test_invoice(self):
        self.assertEqual(render_line("pen", 150), "pen: 1.50 USD")
        self.assertEqual(render_total(1000), "TOTAL 10.00 USD (tax 2.00 USD)")

    def test_notify(self):
        self.assertEqual(refund_message("Ada", 100), "Hi Ada, we refunded 1.00 USD.")
        self.assertEqual(receipt_message("Ada", 100), "Hi Ada, you paid 1.20 USD including 0.20 USD tax.")

    def test_legacy(self):
        self.assertEqual(partner_price(100), "1.00 EUR")


if __name__ == "__main__":
    unittest.main()
