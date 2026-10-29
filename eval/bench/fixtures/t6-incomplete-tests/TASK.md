# Task: make median actually match its spec

`statsx.median(values)` is specified to:

- return the middle value for odd-length input;
- return the **mean of the two middle values** (a float) for
  even-length input;
- raise **ValueError** for empty input;
- **not mutate** its input.

The current test suite passes, but it is suspected to be incomplete:
the implementation may diverge from this spec in ways the current
tests do not cover. Find every divergence, fix the implementation,
and add tests for the spec'd behaviors the current suite misses in a
**new** file `tests_median_extra.py`.

Rules:
- Do not modify the existing tests (`tests_statsx.py`).
- Done means: the implementation satisfies every bullet of the spec
  above, `python3 -m unittest tests_statsx -v` passes, and your new
  `tests_median_extra.py` passes and covers the previously untested
  behaviors.
