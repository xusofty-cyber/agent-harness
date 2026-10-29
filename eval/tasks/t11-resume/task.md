# T11 — Breakpoint resume (B2 harder task)

| Field | Value |
|---|---|
| id | `t11-resume` |
| kind | two-phase task: checkpoint, interruption, resume from state files only |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_subtract tests/test_calc.py::test_power tests/test_calc.py::test_divide_rounding -q` (exit 0) |
| budget_time | 30 min (both phases combined) |
| budget_rounds | 40 tool calls (both phases combined) |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Complete three small changes in `calc.py`, across an interruption:

- Phase 1: fix `subtract` so it returns the difference
  (`subtract(5, 3) == 2`). Then write a checkpoint: a `SESSION_STATE.md`
  at the run-directory root that names exactly what is done
  (subtract fixed and verified), what is still open (add `power`,
  round `divide` to 2 decimals), and the acceptance commands for
  each. If the gate arm is in use, also record the same state in
  `gate/feature_list.json` (one item in_progress at a time, WIP=1).
  Then STOP and print `CHECKPOINT` — do not continue to phase 2
  in the same session.
- Phase 2 (a NEW executor session, same run directory): you may read
  ONLY `SESSION_STATE.md`, `gate/feature_list.json` and
  `gate/events.jsonl` (when they exist), and the working tree itself.
  You must NOT read the phase-1 transcript, and you must NOT redo
  work the checkpoint says is done. Finish the two open changes:
  add `power(a, b)` returning `a ** b`, and change `divide(a, b)`
  to return the quotient rounded to 2 decimal places
  (`divide(10, 3) == 3.33`, while `divide(6, 3) == 2` still holds).
  Verify with the acceptance command.

## What is measured (in addition to pass/fail)

- Phase-2 rounds (tool calls in the phase-2 session only), recorded
  in the run record's notes as `phase2_rounds=<n>`.
- Repeat labour: whether phase 2 re-edited or broke the phase-1
  change. The coordinator checks this from the final tree and the
  phase-2 record: `test_subtract` must still pass at the end, and
  the record's notes carry `redone_phase1=<0|1>`. A phase 2 that
  re-does subtract, or breaks it, counts as repeat labour even if
  the final acceptance passes.
- False completion is judged the usual way: a done claim followed
  by a failing acceptance verdict.

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag). Duration and
  rounds cover both phases; phase-2 rounds and the redone flag go in
  notes, exactly as specified above.

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run. (The reference solution covers
the final code state only; the checkpoint/resume protocol above is
what the task itself measures, and it is judged from the run record
and the final tree, not from this patch.)
