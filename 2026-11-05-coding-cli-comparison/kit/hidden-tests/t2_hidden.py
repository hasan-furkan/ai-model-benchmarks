import threading
import time
import unittest
from collections.abc import MutableMapping

from inventory import InventoryService


class SlowStore(MutableMapping):
    """A cache-backed store: every read and write takes a little while."""

    def __init__(self, data):
        self.data = dict(data)

    def __getitem__(self, k):
        v = self.data[k]
        time.sleep(0.001)
        return v

    def __setitem__(self, k, v):
        time.sleep(0.001)
        self.data[k] = v

    def __delitem__(self, k):
        del self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


def run_threads(n, fn):
    barrier = threading.Barrier(n)
    results = [None] * n

    def worker(i):
        barrier.wait()
        results[i] = fn(i)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


class HiddenConcurrencyTest(unittest.TestCase):
    def test_no_oversell_under_1000_threads(self):
        store = SlowStore({"tv": 500})
        svc = InventoryService(store)
        results = run_threads(1000, lambda i: svc.reserve("tv", 1))
        self.assertEqual(sum(results), 500, "exactly 500 reservations may succeed")
        self.assertEqual(store.data["tv"], 0)

    def test_mixed_reserve_release_keeps_count(self):
        store = SlowStore({"tv": 100})
        svc = InventoryService(store)

        def op(i):
            if svc.reserve("tv", 1):
                svc.release("tv", 1)
            return True

        run_threads(400, op)
        self.assertEqual(store.data["tv"], 100, "lost update between reserve and release")

    def test_different_skus_still_correct(self):
        store = SlowStore({"a": 50, "b": 50})
        svc = InventoryService(store)
        results = run_threads(200, lambda i: svc.reserve("a" if i % 2 else "b", 1))
        self.assertEqual(sum(results), 100)
        self.assertEqual(store.data, {"a": 0, "b": 0})

    def test_qty_types(self):
        svc = InventoryService({"x": 5})
        for bad in (-1, 1.5, "2", True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                svc.reserve("x", bad)
        with self.assertRaises(ValueError):
            svc.release("x", 0)
        with self.assertRaises(KeyError):
            svc.available("nope")


if __name__ == "__main__":
    unittest.main()
