"""Shopping cart."""
from . import utils


class Cart:
    def __init__(self):
        self.lines = []

    def add(self, name, cents, qty=1):
        self.lines.append((name, cents, utils.clamp(qty, 1, 99)))

    def subtotal(self):
        return sum(cents * qty for _, cents, qty in self.lines)

    def tax(self):
        return round(self.subtotal() * 0.2)

    def summary(self):
        total = self.subtotal() + self.tax()
        return f"{len(self.lines)} items, total {utils.fmt_price(total)}"
