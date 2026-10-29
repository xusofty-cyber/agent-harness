# Task: implement parse_duration

Implement `parse_duration(text)` in `durations.py`: parse a duration
string into total seconds (int). The specified behavior:

- units `h`, `m`, `s` with integer amounts, combined in h/m/s order
  (e.g. "1h30m" -> 5400, "45s" -> 45, "1h1m1s" -> 3661);
- case-insensitive.

The spec is deliberately silent about several inputs you will meet
in real data: whitespace inside the string, repeated units, invalid
input, empty input, bare numbers without a unit, and decimals. For
each of those, choose a reasonable behavior, implement it
consistently, and document every choice in a new file `DECISIONS.md`
in the project root — one short section per topic.

Rules:
- Do not modify the tests (`tests_durations.py`).
- Done means: `python3 -m unittest tests_durations -v` passes AND
  `DECISIONS.md` documents your choices for all six topics above.
