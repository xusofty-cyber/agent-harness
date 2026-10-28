# Quality Score — merged edition (2026-10-28, feat/merge-v3)

Per-module scores for the merged branch (`feat/phase0-v3` skeleton +
`v3-yunyi` + `v3-yunkai`), with the evidence behind each. Scores are
0–10, deliberately un-generous: a score claims only what the cited
evidence shows. Re-issued when the evidence changes (monthly,
alongside benchmark baselines). Format merged from `v3-yunkai`; the
skeleton's baseline numbers are kept as an appendix below.

| Module | Score | Evidence |
|---|---|---|
| Gate layer (`gate/`) | 8 | 23 unit tests (pass-gate 3 + terminate/handoff/run 11 + graph 5 + comet_adapter 4) + repo_checks §3k gate validation (662 PASS total); dogfooded on this repo (6/6 feature_list items passing with gate evidence, Phase 1); bench gate arm left verifiable evidence in 24/24 runs across rounds 3–5; terminate/handoff/run, Graph executor, and comet_adapter all landed in this merge. Not 10: graph/comet-adapter paths are young (5 and 4 tests); pass-gate.py itself has only 3 unit tests — most of its coverage is repo_checks §3k and dogfood. |
| Pipeline & deploy | 7 | Strict gates real since Phase 2 (drift fixtures prove exit codes); comet pinned 0.5.1 + state backup verified end-to-end (this merge); deploy dir creation tested; three profiles measured (minimal 10 skills / 212,777 B, standard 18 / 301,118 B, full 38 / 757,688 B); slim Project template ships with minimal/standard (D-009, this merge). Not higher: ps1 paths are review-verified, not execution-verified on Windows. |
| Hooks & guard | 7 | 108 hook tests green (hooks 73 + write 12 + gate 11 + lifecycle 12) + 5 server tests; guard expands substitutions recursively, enforces the D27 resolver conjunction (13 tests), logs parse failures to guard-alerts.jsonl and still fails open; yunkai's nested-substitution hardening tests added in this merge. Not higher: guard remains a guardrail, not a sandbox (documented); Stop hook has no soak time yet. |
| Distribution (templates + 40 skills) | 5 | Counts machine-guarded (skills-lock: 36 github entries pinned, CI `--check --strict`); licensing inventoried; template-size ablation done — slim Project template adopted for minimal/standard tiers (D-009). Still: ~99K tokens of SKILL.md for 40 skills with zero per-skill usage evidence and known overlaps (e.g. two debugging skills); the skill catalog is the ablation cadence's next target. |
| Numbers & claims hygiene | 6 | Repo's own stale figures fixed in Phase 0 and now CI-guarded (repo_checks 662 PASS); upstream figures (comet skill) dispositioned in the 2026-10-28 bench baseline; this merge's numbers are all re-measured (see verification record). Not higher: the upstream text still ships un-annotated in the synced skill (cannot edit without breaking sync). |
| Evaluation | 4 | t1–t4: 36-run matrix, 36/36 pass, 0 false completions (but ceiling effect — tasks too trivial to discriminate arms); t5–t8: fixtures smoke-green (pristine rejected, reference accepted, 4/4) with an objective evaluator (hidden probes, test-intact checks), but no completed t5–t8 runs yet at the time of writing — the one-round matrix is the merge's remaining verification; rubric calibrated 5 rounds, still not `stable` (no live second-judge round); thresholds provisional. But tasks are minutes-scale and arms are same-model — scores here measure provability and cost, not capability deltas. |

Overall posture: the enforcement and measurement spine is real; the
distribution bulk is unproven value and the evaluation is young.
Subtraction (Phase 4, driven by these numbers) is where the
distribution score is supposed to move — by shrinking, not growing.

## What changes next

1. Complete the t5–t8 one-round matrix (4 tasks × 3 arms + dist-slim
   arm) and record it in `docs/internal/merge-verification.md`; if the
   hard tasks separate the arms, the Evaluation score moves.
2. One live second-person rubric calibration round → rubric `stable`.
3. Monthly ablation continues (next run 2026-11); `writing-skills`
   removal still awaits owner sign-off.
4. Re-issue this scorecard when the evidence above changes.

## Appendix — skeleton baseline numbers (Phase 3, kept verbatim)

Source: `docs/bench/baseline-2026-10.md`, `eval/results/*.json`. Bare
arm ran in the Phase 3 session; pack/gate arms ran in a fresh session
the same day (see the baseline report's Confounds — cross-arm duration
gaps are confounded by executor; only pack-vs-gate is a clean
comparison).

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

### Unmeasured (from the skeleton edition)

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

### Module snapshot, rubric-scored (skeleton edition, see `eval/rubric.md`)

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
