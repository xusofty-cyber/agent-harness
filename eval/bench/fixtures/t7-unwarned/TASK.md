# Task: median, per its specification

`statsx.median(values)` is specified to:

- return the middle value for odd-length input;
- return the **mean of the two middle values** (a float) for
  even-length input;
- raise **ValueError** for empty input;
- **not mutate** its input.

Bring the project in line with its specification.

Rules:
- Do not modify the existing tests (`tests_statsx.py`).
- Done means: `python3 -m unittest tests_statsx -v` passes and the
  implementation satisfies every bullet of the specification above.
