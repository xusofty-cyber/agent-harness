# QUALITY_SCORE.md — first edition (2026-10-28, Phase 3)

First measured quality snapshot for agent-harness. Every number below is
either a real run in `eval/results/` or is marked **unmeasured**. Nothing
here is an upstream number quoted as our own.

## Measured baseline (bare arm, 12 runs)

Source: `docs/bench/baseline-2026-10.md`, `eval/results/*.json`.

| Task | Median duration | Range | Completion |
|---|---|---|---|
| T1 bugfix | 6 s | 6–8 s | 3/3 |
| T2 feature | 7 s | 7–8 s | 3/3 |
| T3 cross-file | 18 s | 7–32 s | 3/3 |
| T4 docs+code | 18 s | 7–32 s | 3/3 |

Pooled: completion **12/12 (100%)**, false completions **0/12**,
interventions **0**. Thresholds derived from this baseline (provisional,
see the baseline report for formulas): duration red-lines T1 10 s, T2 9 s,
T3 46 s, T4 46 s; completion floor 11/12 per 12-run window; any false
completion is a red-line breach.

## Unmeasured

- **`pack` arm: unmeasured** (0/12 runs). **`gate` arm: unmeasured**
  (0/12 runs). The 3-arm comparison does not exist yet; do not quote one.
- **Token cost: unmeasured.** No host exposes a programmatic token API
  (see `docs/internal/token-adapters.md`). Cost is tracked via Phase 2
  proxy metrics only (runs, duration, verify failures, interventions).
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
| Benchmarks (`eval/`) | Accept | 12/12 bare runs pass; thresholds derived from variance, not invented |
| Docs / i18n | Revise | EN/ZH current; FR/DE/ZH-TW frozen per D3; rubric not yet `stable` (no live second-judge calibration round yet) |

Module scores are judgement calls anchored to the evidence cited, not
measurements. The rubric itself is **calibrated (4 rounds, 0 divergences)**
but not `stable` — see `eval/calibration.md`.

## What changes next

1. Run the `pack` and `gate` arms (24 runs) to complete the matrix.
2. One live second-person rubric calibration round → rubric `stable`.
3. Re-derive thresholds from the full 36-run matrix; replace the
   provisional ones above.
4. Phase 4 ablation uses the skill-load numbers above as its input.
