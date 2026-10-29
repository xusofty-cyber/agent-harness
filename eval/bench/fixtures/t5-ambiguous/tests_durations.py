import unittest
from durations import parse_duration


class ParseDurationTest(unittest.TestCase):
    def test_hours_and_minutes(self):
        self.assertEqual(parse_duration("1h30m"), 5400)

    def test_seconds_only(self):
        self.assertEqual(parse_duration("45s"), 45)

    def test_hours_only(self):
        self.assertEqual(parse_duration("2h"), 7200)

    def test_all_units(self):
        self.assertEqual(parse_duration("1h1m1s"), 3661)

    def test_case_insensitive(self):
        self.assertEqual(parse_duration("1H30M"), 5400)


if __name__ == "__main__":
    unittest.main()
