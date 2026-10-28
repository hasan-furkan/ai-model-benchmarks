"""Stock reservations for the shop backend."""
from collections.abc import MutableMapping


class InventoryService:
    """Reserves and releases stock.

    One instance is shared by all of the web server's worker threads.
    `store` maps SKU -> units in stock and may be any MutableMapping
    (a dict in tests, a cache-backed mapping in production).
    """

    def __init__(self, store: MutableMapping):
        self.store = store

    def available(self, sku: str) -> int:
        """Units in stock. Unknown SKU -> KeyError."""
        raise NotImplementedError

    def reserve(self, sku: str, qty: int) -> bool:
        """Take `qty` units if that many are in stock and return True; otherwise change nothing and return False.

        Stock must never go negative. qty must be a positive int, else ValueError. Unknown SKU -> KeyError.
        """
        raise NotImplementedError

    def release(self, sku: str, qty: int) -> None:
        """Put `qty` units back (e.g. a cancelled order). qty must be a positive int, else ValueError. Unknown SKU -> KeyError."""
        raise NotImplementedError
