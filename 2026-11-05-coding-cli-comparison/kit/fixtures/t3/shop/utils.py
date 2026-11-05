"""Shared helpers."""


def fmt_price(cents, currency="USD"):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d} {currency}"


def clamp(value, low, high):
    return max(low, min(value, high))
