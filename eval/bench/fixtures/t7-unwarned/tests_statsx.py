import unittest
from statsx import median


class MedianTest(unittest.TestCase):
    def test_single(self):
        self.assertEqual(median([7]), 7)

    def test_odd_unsorted(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_odd_five(self):
        self.assertEqual(median([5, 1, 9, 3, 7]), 5)


if __name__ == "__main__":
    unittest.main()
