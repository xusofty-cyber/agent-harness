# tinycalc

A tiny calculator used as the agent-harness benchmark fixture.

## Operations

- `add(a, b)` — returns `a + b`.
- `subtract(a, b)` — returns `a - b`.
- `multiply(a, b)` — returns `a * b`.
- `divide(a, b)` — returns the exact quotient of `a / b`.

## CLI

```sh
python3 cli.py add 2 3        # prints: Result: 5.0
python3 cli.py multiply 2 3   # prints: Result: 6.0
```

## Tests

```sh
python3 -m pytest -q
```
