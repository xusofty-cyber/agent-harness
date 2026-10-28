# Goal — fix pass-gate status pluralization

> **Owner**: repo owner (user) | **Loop**: Goal Loop (`tools/loop.py goal-loop`)
> **Created**: 2026-10-28 | **Status**: running
> **Rule**: the loop stops only on the conditions below. A round passes
> only when the verify command actually exits 0 — never on the maker's
> word. Run the manual baseline first, then the loop, and compare.

## Goal

- `gate/pass-gate.py status` prints "1 item" for one item (not "1 items"),
  and a regression test covers 0/1/2 items.

## Verification

- Command: `bash docs/internal/phase5/verify-goal.sh`
- What counts as pass: status on a 1-item gate prints "(1 item)" and never
  "(1 items)"; `tests/pass_gate_test.py` exists and passes.
- What counts as fail: exit non-zero, timeout, or output mismatch.

## Stop conditions

- Max rounds: 5
- Consecutive passes to stop: 2
- Per-command timeout: 60 seconds
- Wall-clock budget: 600 seconds
- Human approval required: no

## Constraints

- Only `gate/pass-gate.py` and `tests/pass_gate_test.py` may change.
- No other behaviour of `status` may change (JSON mode untouched).

## Baseline (manual, run first)

- Method: <filled in after the manual run>
- Duration: <seconds> | Rounds: <n> | Verify attempts: <n> | Outcome: <pass/fail>

## Loop versions

- v1: <round 1 — pluralization fix; verify says …>
- v2: <round 2 — regression test; verify says …>

## Verdict

- <filled in after the loop run — did the loop measurably help vs baseline?>
