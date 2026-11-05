"""Public API used by external partners. FROZEN: partners vendor this file by checksum."""
from shop.utils import fmt_price


def partner_price(cents):
    return fmt_price(cents, "EUR")
