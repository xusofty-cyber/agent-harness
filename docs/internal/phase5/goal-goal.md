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

- Method: edit `gate/pass-gate.py` + write `tests/pass_gate_test.py`
  by hand, run `verify-goal.sh` after each attempt.
- Attempt 1: FAIL, ~2 s, 1 verify — verify caught a wrong assumption:
  `pass-gate init` seeds 3 example items, so init+add can never yield
  a 1-item gate. Attempt 2: FAIL, ~0.8 s, 1 verify — `--root` is the
  project root, not the gate dir. Attempt 3 (comparable): PASS, 1364 ms,
  1 round, 1 verify. The fix itself was right from attempt 1; the two
  failures were in the verification harness — the verify did its job.
- Comparable baseline: 1364 ms | Rounds: 1 | Verify attempts: 1 | Outcome: pass

## Loop versions

- v1 (round 1): pluralization fix applied; verify FAIL — regression test
  file missing (as designed: round 1 only fixes the code).
- v2 (round 2): regression test written; verify PASS.
- v3 (round 3): maker no-op; verify PASS again — 2 consecutive passes,
  loop complete. Total: 2052 ms, 3 rounds, 3 verify attempts (1 fail,
  2 pass). State + events in `docs/internal/phase5/goal-run/`.

## Verdict

- No measurable improvement on this task: the loop took ~1.5× the
  comparable manual time (2052 ms vs 1364 ms) and 3× the verify attempts.
  On a 1-line fix the loop's overhead dominates. What it added is process
  assurance, not speed: verification enforced every round, a single pass
  could not stop the loop (2 consecutive passes required), and the full
  audit trail (state + events) exists. The loop's value would show on
  tasks where a single-pass claim is unreliable — not here. Recorded
  honestly; the loop's existence is not evidence it was needed.
