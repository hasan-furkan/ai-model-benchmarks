"""Customer notifications."""
from .utils import fmt_price as price


def refund_message(name, cents):
    return f"Hi {name}, we refunded {price(cents)}."


def receipt_message(name, cents):
    tax = round(cents * 0.2)
    return f"Hi {name}, you paid {price(cents + tax)} including {price(tax)} tax."
