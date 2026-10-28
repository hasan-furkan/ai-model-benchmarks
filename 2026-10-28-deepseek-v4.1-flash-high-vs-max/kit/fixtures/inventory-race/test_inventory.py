import unittest

from inventory import InventoryService


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.svc = InventoryService({"apple": 5})

    def test_reserve_and_available(self):
        self.assertTrue(self.svc.reserve("apple", 3))
        self.assertEqual(self.svc.available("apple"), 2)

    def test_reserve_too_many_changes_nothing(self):
        self.assertFalse(self.svc.reserve("apple", 6))
        self.assertEqual(self.svc.available("apple"), 5)

    def test_release(self):
        self.svc.reserve("apple", 2)
        self.svc.release("apple", 2)
        self.assertEqual(self.svc.available("apple"), 5)

    def test_bad_qty(self):
        with self.assertRaises(ValueError):
            self.svc.reserve("apple", 0)

    def test_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.svc.reserve("pear", 1)


if __name__ == "__main__":
    unittest.main()
