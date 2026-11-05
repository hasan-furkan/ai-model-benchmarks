import unittest

from shop.cart import Cart
from shop.invoice import render_total
from shop.money import format_money, tax_for
from shop.notify import receipt_message
from shop.utils import fmt_price


class Hidden(unittest.TestCase):
    def test_format_money(self):
        self.assertEqual(format_money(1999), "19.99 USD")
        self.assertEqual(format_money(-5, "EUR"), "-0.05 EUR")
        self.assertEqual(format_money(0), "0.00 USD")

    def test_tax_for(self):
        self.assertEqual(tax_for(1000), 200)
        self.assertEqual(tax_for(1000, 0.1), 100)

    def test_alias(self):
        self.assertEqual(fmt_price(-1999, "EUR"), "-19.99 EUR")

    def test_behaviour_kept(self):
        self.assertEqual(render_total(-1000), "TOTAL -10.00 USD (tax -2.00 USD)")
        self.assertEqual(receipt_message("A", 333), "Hi A, you paid 4.00 USD including 0.67 USD tax.")
        c = Cart()
        c.add("x", 100, 500)
        self.assertEqual(c.subtotal(), 9900)
