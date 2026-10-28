# Phase 5 loops — verification record

Date: 2026-10-28. Branch: `feat/phase0-v3`. Runner: `tools/loop.py`
(stdlib only). Both demo loops ran in separate git worktrees (detached
HEAD `7661bb5`), fanned in under merge rule "all must pass" — both final
verifies passed before any result was committed. Raw state + events are
kept under `docs/internal/phase5/goal-run/` and `docs/internal/phase5/mc-run/`.

Entry-gate honesty up front: the Phase 5 entry assessment
(`agent-harness-phase5-entry-assessment-2026-10-28.md`, in the author's
working notes) concluded the gates were NOT fully met — benchmark tasks
too simple to show loop need, no review-bandwidth bottleneck — and the
user decided to proceed anyway. This record therefore judges the loops
on measured effect, not on the fact that they exist.

## Goal Loop — status pluralization

Goal: `gate/pass-gate.py status` prints "1 item" (not "1 items") and a
regression test covers 0/1/2 items. Goal file:
`docs/internal/phase5/goal-goal.md`. Runner: max rounds 5, consecutive
passes 2, timeout 60 s, budget 600 s, no approval required.

### Manual baseline (worktree `/tmp/phase5-wt-goal`)

| Attempt | Result | Time | Verify attempts | Note |
|---|---|---|---|---|
| 1 | FAIL | ~2 s | 1 | Verify caught a wrong assumption: `pass-gate init` seeds 3 example items, so init+add can never yield a 1-item gate |
| 2 | FAIL | ~0.8 s | 1 | `--root` is the project root; pass-gate appends `gate/` itself |
| 3 (comparable) | PASS | 1364 ms | 1 | Fix + test written by hand, verify OK |

The fix itself was right from attempt 1; the two failures were in the
verification harness — the verify did its job. Comparable baseline:
**1364 ms, 1 round, 1 verify, pass.**

### Loop run (same worktree, fix reverted first)

| Round | Maker did | Verify said | Outcome |
|---|---|---|---|
| 1 | Pluralization fix applied | FAIL — regression test file missing (round 1 only fixes code) | fail |
| 2 | Regression test written | PASS | pass |
| 3 | No-op | PASS again | pass → 2 consecutive, complete |

Total: **2052 ms, 3 rounds, 3 verify attempts (1 fail, 2 pass)**.
State + events: `docs/internal/phase5/goal-run/` (init, round ×3, complete).

### Verdict

No measurable improvement on this task: the loop took ~1.5× the
comparable manual time (2052 ms vs 1364 ms) and 3× the verify attempts.
On a 1-line fix the loop's overhead dominates. What it added is process
assurance, not speed: verification enforced every round, a single pass
could not stop the loop, and the full audit trail exists. The loop's
value would show on tasks where a single-pass claim is unreliable —
not here. Recorded honestly; the loop's existence is not evidence it
was needed.

## Maker-Checker Loop — graph template

Goal: `templates/loop/graph.template.md` passes every checker item
(graph-validate OK, ≥6 node rows, timeout ≤ 300 s, merge rule
"all must pass"). Goal file: `docs/internal/phase5/goal-mc.md`.
Runner: max rounds 5, consecutive passes 2, timeout 60 s, budget 600 s,
**human approval required**. Worktree `/tmp/phase5-wt-mc`.

| Round | Maker did | Checker found | Outcome |
|---|---|---|---|
| 1 | Draft: nodes/edges/shared state/routing only | FAIL — graph-validate, timeout-value, merge-rule | fail |
| 2 | Timeout rule (60 s) added | FAIL — graph-validate, merge-rule | fail |
| 3 | Approval node completed | FAIL — graph-validate, merge-rule | fail |
| 4 | Fan-out merge rule ("all must pass") added | PASS — all items | pass |
| 5 | No-op | PASS — all items | pass → 2 consecutive, awaiting approval |

Total: **1437 ms, 5 rounds, 5 checker attempts (3 fail, 2 pass)**.
Each round's failure list genuinely shrank (3 → 2 → 2 → 0 items) — the
checker drove real revisions, not planted failures.

### Isolation (verified, not asserted)

- Checker dir contained exactly one file: `graph.template.md` (copied
  fresh each round; `artifacts_copied` events seq 1/3/5/7/9).
- Maker dir contained only the same artifact. The checker never saw
  the maker's notes or the loop state.

### Approval

- Pass condition met at round 5 → state `awaiting-approval`,
  `approval_requested` event (seq 11).
- Approved by owner via `loop.py approve` (note: "graph template
  adopted: 5 rounds, checker clean twice, adopting into
  templates/loop/") → `approved` event, status `complete`.

### Template vs loop output (diffed, not assumed)

The committed `templates/loop/graph.template.md` is the loop's round-4
output plus template framing only. Diffed 2026-10-28: the only
differences are the header (`<LOOP_NAME>` / `<goal.md path>` placeholders
and a contract note), owner names generalized to `<maker>`/`<approver>`,
approval text generalized to placeholders, wall-clock budget `<N>`
instead of 600, and added guidance prose (node-kind definitions).
Both files pass `graph-validate`. One prose inaccuracy in the loop
artifact: its approval text says "pass condition at round 4" — the
pass condition was actually met at round 5 (rounds 4 and 5 passed);
the maker script text was corrected to "round 5" in the fan-in commit
and noted here, not silently rewritten in the run record.

## Timeout rule — verified by triggering it

- Verify `sleep 30`, timeout 2 s: killed at **2.005 s**, rc=124,
  `timed_out=True`, round outcome `timeout`, loop failed (max rounds 1).
  State + events: `docs/internal/phase5/timeout-demo/`.
- Budget: maker `sleep 5` with wall-clock budget 1 s → status
  `budget-exceeded`, `budget_exceeded` event, exit 1 — **even though the
  round's verify passed**. Found during this demo: the first version of
  `_check_stop` checked the pass condition before the budget, so the
  loop completed despite exceeding budget; the order was fixed
  (budget → pass → max rounds) and the demo re-run to confirm.
  State + events: `docs/internal/phase5/budget-demo/`.

## Fan-out / fan-in

- Two worktrees, one base commit (`7661bb5`), no shared files.
- Merge rule "all must pass": Goal Loop complete (round 3/5) and
  Maker-Checker complete (round 5/5 + approval) — both final verifies
  re-run in the main clone before fan-in.
- Fan-in commits: `phase5(5-1)` (Goal Loop) and `phase5(5-2)`
  (Maker-Checker). Worktrees removed after fan-in.

## What the loops did NOT prove

- Neither loop shows a task where a single pass is unreliable: both
  demos passed on the first fully-formed attempt (Goal Loop round 2,
  Maker-Checker round 4). The consecutive-pass rule and the audit trail
  are the demonstrated benefits; speed and false-completion reduction
  are not demonstrated by these runs.
- The 36-run bench matrix (Phase 3) still cannot distinguish arms
  (ceiling effect); these loops do not change that. Harder benchmark
  tasks remain the missing evidence for whether Loop is needed at all.
