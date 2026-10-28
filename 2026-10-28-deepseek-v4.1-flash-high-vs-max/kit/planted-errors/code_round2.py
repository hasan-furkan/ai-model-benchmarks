import threading
import time
from collections import OrderedDict
from datetime import datetime, timezone


class LRUCache:
    """Least-recently-used cache: get() and put() both count as a use."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)


class Counter:
    """Thread-safe counter."""

    def __init__(self):
        self.n = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            current = self.n
        self.n = current + 1


def merge_intervals(intervals):
    """Merge overlapping intervals. Touching intervals like (1, 3) and (3, 5) are merged too."""
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result


def page(items, number, size):
    """Return page `number` (1-based) of `items`."""
    offset = number * size
    return items[offset:offset + size]


def retry(fn, attempts=5, base_delay=0.1, max_delay=2.0):
    """Call fn, retrying with exponential backoff capped at max_delay."""
    delay = base_delay
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(min(delay, max_delay))
            delay *= 2


def mean_of_positive(data):
    """Average of the positive numbers in data (a list)."""
    items = (x for x in data if x > 0)
    total = sum(items)
    count = len(list(items))
    return total / count if count else 0.0


def is_expired(expires_at: datetime) -> bool:
    """expires_at is stored as an aware UTC datetime."""
    return datetime.now() > expires_at


def round_half_even_cents(amount: float) -> int:
    """Banker's rounding to whole cents is required by our accounting rules."""
    return round(amount * 100)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
