# T4 — Docs + code sync

| Field | Value |
|---|---|
| id | `t4-docs-sync` |
| kind | docs + code sync |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_divide_rounding -q` (exit 0) AND `grep -qi "round" README.md` (exit 0) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Change `divide(a, b)` in `calc.py` so it returns the quotient rounded to
2 decimal places (`divide(10, 3) == 3.33`), and update `README.md` so the
documented behaviour of `divide` matches the code (it must mention rounding).

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- The other failing tests at the start commit (`test_subtract`,
  `test_power`) belong to other tasks — do not fix them, and do not count
  them against this task.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag).

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run.
