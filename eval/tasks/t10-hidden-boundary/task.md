# T10 — Hidden boundary case (B2 harder task)

| Field | Value |
|---|---|
| id | `t10-hidden-boundary` |
| kind | feature with a boundary case missing from the visible tests |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -c "from calc import power; assert power(2,3)==8 and power(2,0)==1 and power(5,-1)==0.2 and power(2,-2)==0.25"` (exit 0) AND `grep -Eq "power\([^)]*-[0-9]" tests/test_calc.py` (exit 0, i.e. the agent's own tests cover a negative exponent) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Add a `power(a, b)` function to `calc.py` that returns `a ** b`.

The visible test file already contains `test_power`
(`power(2, 3) == 8`), and that test currently fails with
`ImportError`. That visible test is NOT the whole specification:
before you claim done, identify the boundary cases yourself, write
tests for them in `tests/test_calc.py`, and verify them. In
particular, think about what `power` must do when the exponent is
zero or negative — the acceptance command checks cases that are
deliberately absent from the visible test file, so an implementation
that only handles positive integer exponents (for example a loop
that multiplies `b` times) will fail even though the visible test
passes.

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- The other failing tests at the start commit (`test_subtract`,
  `test_divide_rounding`) belong to other tasks — do not fix them,
  and do not count them against this task.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag).

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run.
