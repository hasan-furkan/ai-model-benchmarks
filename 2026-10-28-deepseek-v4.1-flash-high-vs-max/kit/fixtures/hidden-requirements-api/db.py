"""In-memory data. Timestamps are stored in the shop's local time (Europe/Warsaw, UTC+1/+2)."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

WARSAW_SUMMER = timezone(timedelta(hours=2))
WARSAW_WINTER = timezone(timedelta(hours=1))

CUSTOMERS = [
    {"id": 1, "name": "Ada", "city": "Warsaw", "balance": Decimal("12.5"), "created_at": datetime(2026, 7, 1, 10, 0, tzinfo=WARSAW_SUMMER)},
    {"id": 2, "name": "Bob", "city": "Krakow", "balance": Decimal("0"), "created_at": datetime(2026, 1, 15, 9, 30, tzinfo=WARSAW_WINTER)},
    {"id": 3, "name": "Cem", "city": "Warsaw", "balance": Decimal("7.05"), "created_at": datetime(2026, 3, 2, 18, 45, tzinfo=WARSAW_WINTER)},
]

ORDERS = [
    {"id": 101, "customer_id": 1, "total": Decimal("19.9"), "created_at": datetime(2026, 10, 20, 0, 30, tzinfo=WARSAW_SUMMER)},
    {"id": 102, "customer_id": 1, "total": Decimal("5"), "created_at": datetime(2026, 10, 27, 12, 0, tzinfo=WARSAW_WINTER)},
    {"id": 103, "customer_id": 3, "total": Decimal("120.00"), "created_at": datetime(2026, 9, 1, 8, 15, tzinfo=WARSAW_SUMMER)},
]
