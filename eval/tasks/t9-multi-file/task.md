# T9 — Multi-file change with docs sync (B2 harder task)

| Field | Value |
|---|---|
| id | `t9-multi-file` |
| kind | multi-file change + docs sync + cross-file consistency |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_remainder -q` (exit 0) AND `python3 -c "from calc import remainder; assert remainder(10,3)==1"` (exit 0) AND `python3 cli.py remainder 10 3` prints `Result: 1.0` AND `grep -qi remainder README.md` (exit 0) AND `grep -q remainder cli.py` (exit 0) AND `python3 cli.py remainder 10 0` fails (exit non-zero) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Add a `remainder(a, b)` operation that returns `a % b`, and wire it
through every surface where an operation appears:

- `calc.py`: implement `remainder(a, b)`.
- `cli.py`: import it, add the `remainder` subcommand, and update the
  usage string so it names `remainder`.
- `README.md`: document `remainder` in the operations list and in the
  CLI example.
- `tests/test_calc.py`: add a test for `remainder` (at minimum
  `remainder(10, 3) == 1`).

## Why this task discriminates

A fix that touches only one file looks done from that file alone and
fails: `calc.py` only leaves the CLI and docs stale; `calc.py` +
`cli.py` only leaves the docs check failing; a CLI that swallows the
divide-by-zero error (returning 0 instead of failing) fails the
`remainder 10 0` check. The acceptance command checks all four
surfaces, so a partial change cannot pass by claiming done early.

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- The other failing tests at the start commit (`test_subtract`,
  `test_power`, `test_divide_rounding`) belong to other tasks — do not fix
  them, and do not count them against this task.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag).

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run.
