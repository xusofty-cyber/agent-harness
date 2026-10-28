import unittest

from textkit import slugify, truncate_middle, word_wrap


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_empty(self):
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("---"), "")


class TestTruncateMiddle(unittest.TestCase):
    def test_short_text_unchanged(self):
        self.assertEqual(truncate_middle("hello", 10), "hello")
        self.assertEqual(truncate_middle("hello", 5), "hello")

    def test_truncates_to_exact_length(self):
        self.assertEqual(truncate_middle("abcdefghij", 5), "ab…ij")
        self.assertEqual(truncate_middle("abcdef", 4), "ab…f")
        self.assertEqual(truncate_middle("abcdef", 3), "a…f")
        self.assertEqual(truncate_middle("abcdefghij", 2), "a…")

    def test_max_len_one(self):
        self.assertEqual(truncate_middle("hello", 1), "…")

    def test_invalid_max_len(self):
        with self.assertRaises(ValueError):
            truncate_middle("hello", 0)


class TestWordWrap(unittest.TestCase):
    def test_greedy_packing(self):
        self.assertEqual(word_wrap("the quick brown fox", 5),
                         "the\nquick\nbrown\nfox")
        self.assertEqual(word_wrap("hello world", 5), "hello\nworld")

    def test_long_word_hard_split(self):
        self.assertEqual(word_wrap("aaa bbbbbbbb cc", 4),
                         "aaa\nbbbb\nbbbb\ncc")

    def test_empty(self):
        self.assertEqual(word_wrap("", 5), "")

    def test_invalid_width(self):
        with self.assertRaises(ValueError):
            word_wrap("hello", 0)


if __name__ == "__main__":
    unittest.main()
