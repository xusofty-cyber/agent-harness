# Python Review Rules

## Correctness

- Mutable default arguments (`def f(x=[])`).
- Bare `except:` or `except Exception:` that swallows errors silently.
- `None` handling: attribute access / subscript on values that may be `None`.
- Integer division vs float division where it matters (`//` vs `/`).
- Datetime: naive vs aware mixing; `datetime.now()` without timezone in
  distributed contexts.

## Resource & concurrency

- Files / connections / locks opened without context managers.
- Unbounded growth: lists/dicts appended in loops without size consideration.
- Thread-safety: shared mutable state across threads without locks;
  `asyncio` code calling blocking I/O.

## Error handling

- Errors logged but not propagated where the caller needs to know.
- Retry loops without backoff or max attempts.
- **Do NOT report**: missing type hints as a defect (style-level only).

## Maintainability

- Functions longer than ~50 lines doing more than one thing.
- Duplicated logic across 3+ sites (suggest extraction).
- Magic numbers/strings without named constants.

## Do NOT report

- "Could use a dataclass" for simple 2-field structures.
- Import order nits (that's a linter's job).
- Performance micro-concerns without evidence of hot-path impact.
