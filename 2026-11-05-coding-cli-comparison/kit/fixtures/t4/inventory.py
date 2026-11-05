"""Stock reservations for the shop backend."""
import threading
from collections.abc import MutableMapping


class InventoryService:
    """Reserves and releases stock.

    One instance is shared by all of the web server's worker threads.
    `store` maps SKU -> units in stock and may be any MutableMapping
    (a dict in tests, a cache-backed mapping in production).
    """

    def __init__(self, store: MutableMapping):
        self.store = store
        self._lock = threading.Lock()

    @staticmethod
    def _check_qty(qty) -> None:
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError(f"qty must be a positive int, got {qty!r}")

    def available(self, sku: str) -> int:
        """Units in stock. Unknown SKU -> KeyError."""
        with self._lock:
            return int(self.store[sku])

    def reserve(self, sku: str, qty: int) -> bool:
        """Take `qty` units if that many are in stock and return True; otherwise change nothing and return False."""
        self._check_qty(qty)
        with self._lock:
            current = int(self.store[sku])
            if current < qty:
                return False
            self.store[sku] = current - qty
            return True

    def release(self, sku: str, qty: int) -> None:
        """Put `qty` units back (e.g. a cancelled order)."""
        self._check_qty(qty)
        with self._lock:
            self.store[sku] = int(self.store[sku]) + qty
