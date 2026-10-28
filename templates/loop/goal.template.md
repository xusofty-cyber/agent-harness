# Goal — <GOAL_NAME>

> **Owner**: <who owns the goal> | **Loop**: Goal Loop (`tools/loop.py goal-loop`)
> **Created**: <YYYY-MM-DD> | **Status**: running | awaiting-approval | complete | failed
> **Rule**: the loop stops only on the conditions below. A round passes
> only when the verify command actually exits 0 — never on the maker's
> word. Run the manual baseline first, then the loop, and compare.

## Goal

- <What "done" means, in one verifiable sentence>

## Verification

- Command: `<verify command — must exit 0 on success>`
- What counts as pass: <observable condition, e.g. "test file passes and
  the fixed output contains no `1 items`">
- What counts as fail: <exit non-zero, timeout, or output mismatch>

## Stop conditions

- Max rounds: <N> (loop fails past this without the pass condition)
- Consecutive passes to stop: <N, default 2>
- Per-command timeout: <N seconds — enforced by the runner, recorded>
- Wall-clock budget: <N seconds, 0 = none>
- Human approval required: <yes/no — if yes, the loop pauses in
  `awaiting-approval` and only `loop.py approve` resumes it>

## Constraints

- <What the loop must not touch, e.g. "only gate/pass-gate.py and its test">
- <Budget / scope limits>

## Baseline (manual, run first)

- Method: <how the same goal was done by hand, no loop>
- Duration: <seconds> | Rounds: <n> | Verify attempts: <n> | Outcome: <pass/fail>

## Loop versions

- v1: <what changed in this iteration, and what the verify said>
- v2: <what changed in this iteration, and what the verify said>

## Verdict

- <Did the loop measurably help vs the baseline? Time, rounds, verify
  attempts, false completions. If it did not help, say so — the loop's
  existence is not evidence that the loop was needed.>
