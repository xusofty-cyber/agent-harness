import unittest
from statsx import median


class MedianExtraTest(unittest.TestCase):
    def test_even_length_mean_of_middles(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_even_unsorted(self):
        self.assertEqual(median([4, 1, 3, 2]), 2.5)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            median([])

    def test_input_not_mutated(self):
        data = [3, 1, 2]
        median(data)
        self.assertEqual(data, [3, 1, 2])


if __name__ == "__main__":
    unittest.main()
