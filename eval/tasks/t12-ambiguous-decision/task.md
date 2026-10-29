# T12 — Ambiguous requirement, decision record first (B2 harder task)

| Field | Value |
|---|---|
| id | `t12-ambiguous-decision` |
| kind | ambiguous requirement; decision record must precede implementation |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -c "from calc import discount; assert discount(100,20)==80.0 and discount(100,0)==100.0"` (exit 0) AND `grep -qi discount DECISIONS.md` (exit 0) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Add a `discount(price, pct)` function to `calc.py` that returns the
price after a percentage discount, rounded to 2 decimal places.

The requirement as stated is deliberately ambiguous in one place:
it does not say whether `pct` is expressed on the 0–100 scale
(a 20 percent discount is `pct=20`) or on the 0–1 scale (a 20
percent discount is `pct=0.2`). Do NOT guess silently and start
coding. First write a `DECISIONS.md` entry at the run-directory
root that states the scale you choose and why, and only then
implement `discount` to match that decision. The acceptance command
checks one scale; an implementation built on the other scale fails
it, and a run with no decision record fails the record check even
if the code happens to pass.

## Decision-quality scoring (coordinator-scored, descriptive)

After the run, the coordinator scores the `DECISIONS.md` entry
0–2: 1 point for stating the chosen scale explicitly, 1 point for
giving a reason that refers to the fixture's conventions (not just
restating the choice). The score is reported descriptively in the
B2 report; it does not change the pass/fail verdict, which comes
from the acceptance command alone. Whether the entry was written
before the implementation cannot be checked from the final tree
alone, so the coordinator also checks the phase record / session
order where available and notes any ordering doubt in the report
instead of silently assuming it.

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
