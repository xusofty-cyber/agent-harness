# T2 — Single feature

| Field | Value |
|---|---|
| id | `t2-feature` |
| kind | single feature |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_power -q` (exit 0) AND `python3 -c "from calc import power; assert power(2,3)==8"` (exit 0) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Add a `power(a, b)` function to `calc.py` that returns `a ** b`. The test
`test_power` already exists in the fixture and currently fails with
`ImportError`.

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
