"""Output conventions shared by every endpoint."""
from datetime import timezone
from decimal import Decimal, ROUND_HALF_UP


def iso_utc(dt):
    """2026-07-01T08:00:00Z: always UTC, ISO-8601, 'Z' suffix."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def money(value: Decimal) -> str:
    """Money is a string with exactly two decimals: Decimal('12.5') -> '12.50'."""
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
