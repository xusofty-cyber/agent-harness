# T1 — Small bug fix

| Field | Value |
|---|---|
| id | `t1-bugfix` |
| kind | small bug fix |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_subtract -q` (exit 0) |
| budget_time | 15 min |
| budget_rounds | 20 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

`subtract(5, 3)` currently returns `8`. Fix `calc.py` so it returns `2`.

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag).

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run.
