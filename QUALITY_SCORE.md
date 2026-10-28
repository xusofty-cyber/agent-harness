# QUALITY_SCORE.md — first edition (2026-10-28, Phase 3)

First measured quality snapshot for agent-harness. Every number below is
either a real run in `eval/results/` or is marked **unmeasured**. Nothing
here is an upstream number quoted as our own.

## Measured baseline (full 36-run matrix, 2026-10-28)

Source: `docs/bench/baseline-2026-10.md`, `eval/results/*.json`. Bare arm
ran in the Phase 3 session; pack/gate arms ran in a fresh session the
same day (see the baseline report's Confounds — cross-arm duration gaps
are confounded by executor; only pack-vs-gate is a clean comparison).

| Task | Bare median | Pack median | Gate median | Pooled median | Completion |
|---|---|---|---|---|---|
| T1 bugfix | 6 s | 3 s | 5 s | 5 s | 9/9 |
| T2 feature | 7 s | 4 s | 7 s | 7 s | 9/9 |
| T3 cross-file | 18 s | 8 s | 5 s | 8 s | 9/9 |
| T4 docs+code | 18 s | 4 s | 5 s | 5 s | 9/9 |

Pooled: completion **36/36 (100%)**, false completions **0/36**,
interventions **0**, median duration **6.0 s**. Per arm: bare 12/12
(median 7.5 s), pack 12/12 (median 4.0 s), gate 12/12 (median 5.0 s).
Every run passed on its first verify attempt. Thresholds re-derived
from the full matrix (same formulas, still provisional — see the
baseline report): duration red-lines T1 11 s, T2 25 s, T3 56 s,
T4 59 s; completion floor 11/12 per 12-run window; any false
completion is a red-line breach.

Outcome: **no difference between arms** — 12/12 pass everywhere, 0
false completions. Ceiling effect: the tasks are too trivial to
discriminate arms on outcome. The gate's false-pass interception was
demonstrated in Phase 1 dogfood, not by this matrix. Pack-vs-gate
(clean comparison, same executor): gate costs ~1 s and +1 round
(the verify + status calls), no outcome difference.

## Unmeasured

- **Token cost: unmeasured.** No host exposes a programmatic token API
  (see `docs/internal/token-adapters.md`). Cost is tracked via Phase 2
  proxy metrics only (runs, duration, verify failures, interventions).
- **New-session rebuild cost pack vs gate: unmeasured** in this matrix
  (both executors did many runs each; the only fresh-session handover
  measurement is Phase 1 dogfood, ~1 s).
- **Arm discrimination on reliability: unmeasured.** 36/36 first-try
  passes is a ceiling effect; harder tasks (multi-step, ambiguous, or
  with a planted defect to catch) are needed before the matrix can tell
  whether the gate reduces false completions.
- **Skill-load cost (measured, v2 3-4; re-measured per profile in Phase
  4):** `eval/run-bench.sh measure-load` now reports all three profiles
  (2026-10-28). `minimal` (default): **10 skill dirs, 212,777 skills
  bytes, 700,569 deployed-total bytes**. `standard`: **18 dirs, 301,118
  skills bytes, 877,254 deployed-total bytes**. `full`: **38 dirs (heavy
  skills gated), 757,688 skills bytes, 1,790,382 deployed-total bytes**
  (Phase 3 reported 1,790,367 for the same 38 — re-measured now, 15 bytes
  difference from a deployed file changed since; the current figure is
  the one to quote). Largest SKILL.md files:
  `subagent-driven-development` (32,577 B), `openspec-bulk-archive-change`
  (22,296 B), `executing-plans` (20,405 B). Skills bytes count
  `.agents/skills/` only; deployed-total counts the whole deployed
  directory. This is a size measurement, not a token measurement.
- **Ablation (Phase 4, first run 2026-10):** `writing-skills` (107,640 B)
  ablated over 12 pack-arm runs: 12/12 pass, 0 false completions — no
  outcome regression (see `docs/ablation/ablation-2026-10-writing-skills.md`).
  Candidate for removal on bench evidence only; owner decision pending.

## Module snapshot (rubric-scored, see `eval/rubric.md`)

| Module | Score | Basis |
|---|---|---|
| Gate (`gate/`) | Accept (11/12) | Phase 1 dogfood-1 calibration round: fake pass intercepted, handover ~1 s |
| Comet adapter | Accept (11/12) | Phase 2 recovery calibration round: stateVersion preserved, auto_resume high confidence |
| Pipeline (`--strict`) | Accept | Phase 2 verification: strict FAIL exit 1 / advisory WARN exit 0, no PASS on failure |
| Hooks (5 events) | Accept | 56 + 10 + 11 + 12 hook tests pass; parse failures logged, still fail-open |
| Benchmarks (`eval/`) | Accept | 36/36 runs pass (12 per arm); thresholds re-derived from the full matrix, still provisional |
| Docs / i18n | Revise | EN/ZH current; FR/DE/ZH-TW frozen per D3; rubric not yet `stable` (no live second-judge calibration round yet) |

Module scores are judgement calls anchored to the evidence cited, not
measurements. The rubric itself is **calibrated (5 rounds, 0 divergences)**
but not `stable` — see `eval/calibration.md`.

## What changes next

1. ~~Run the `pack` and `gate` arms (24 runs) to complete the matrix.~~
   Done 2026-10-28: 36/36 runs, thresholds re-derived (still provisional).
2. One live second-person rubric calibration round → rubric `stable`.
3. ~~Re-derive thresholds from the full 36-run matrix; replace the
   provisional ones above.~~ Done (see baseline report); they stay
   provisional until a same-executor three-arm run or harder tasks
   tighten the spread.
4. Phase 4 ablation uses the skill-load numbers above as its input.
