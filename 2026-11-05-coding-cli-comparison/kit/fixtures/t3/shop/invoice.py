"""Invoice rendering."""
from .utils import fmt_price


def render_line(name, cents, currency="USD"):
    return f"{name}: {fmt_price(cents, currency)}"


def render_total(cents, currency="USD"):
    sign = "-" if cents < 0 else ""
    amount = abs(cents)
    tax = round(cents * 0.2)
    return f"TOTAL {sign}{amount // 100}.{amount % 100:02d} {currency} (tax {fmt_price(tax, currency)})"
