# Quality Score — v0.5.1 edition (2026-10-30)

Re-issued for v0.5.1 (including D67 event hash chain, D68 skill-usage telemetry, D69 B1–B4 conclusion, and the v0.5.2 audit fixes). Scores are
0–10, deliberately un-generous: a score claims only what the cited
evidence shows. The 2026-10-28 merged edition is kept verbatim below
as history.

| Module | Score | Evidence |
|---|---|---|
| Gate layer (`gate/`) | 8 | Unchanged core, still the strongest module: this repo's feature list now carries 6/6 passing items with evidence; v0.4.1 adds `verification.level` (D66) and check-clean dimension 3d, which reports this repo's passing mix as `assert 5, unit 1` — visible, and a standing warning for feature work. Not higher: real-world soak time is still short and every passing item here is docs-scale. |
| Host bridges (Antigravity / WorkBuddy / dsh) | 4 | New module, scored by `docs/internal/host-verification-matrix.md` tiers: Antigravity CLI `partial-live` (one live agy 1.4.10 run found and fixed a real cwd bug), Antigravity IDE / WorkBuddy / dsh `protocol-only` (payloads assumed, no live run). Protocol suites pass (20 + 16 + 19 tests). v0.4.1 discharges one owed check: `tsc --noEmit` on the dsh plugin passes (TypeScript 5.9.3, exit 0). Not higher: no bridge has run a full gate flow on its live host. |
| Pipeline & deploy | 7 | As the merged edition, plus: v0.4.1 adds a Windows CI execution smoke for `deploy-agents.ps1` (the ps-analyzer job now also runs the deploy and asserts the core file set). Not higher until that job has actually run green in CI — at re-issue time it is committed, not yet observed. |
| Hooks & guard | 7 | Claude suites unchanged and green (90 + 12 + 11 + 12); total hook-related tests including bridges: 168, all passing locally 2026-10-30. Guard is still a guardrail, not a sandbox (documented); Stop hook soak time still short. |
| Distribution (templates + 39 skills) | 6 | v0.5.1 lands D68 skill-usage telemetry (`.claude/skill-usage.jsonl` + `tools/skill-usage-report.py`, extended in v0.5.2 to capture on-demand `SKILL.md` reads and bridge payloads), and wires `gate/pass-gate.py` directly into `Project AGENTS.md`. Score moves further when the 2026-11 monthly ablation trims zero-load skills. |
| Numbers & claims hygiene | 7 | Up from 6: README's enforcement wording now matches the host-verification matrix in EN and ZH (nothing below `live-verified` is worded as enforced); this scorecard is re-issued on evidence change as promised; repo_checks now classifies missing-environment failures (e.g. no pytest) as `[ENV-SKIP]`, distinct from repository failures. Not higher: the ZH-TW Multi-Tool guide remains knowingly stale (explicitly recorded in `docs/internal/i18n-status.md`), and upstream comet-skill figures still ship un-annotated. |
| Evaluation | 4 | Still 4, deliberately — and the open question this row waited on is now answered as far as the current bench design can answer it. B3 (real project, 2026-10-30) found nonzero but arm-identical false completions (no arm-level discrimination); B3.1 confirmed the pattern after process fixes (SEGMENTED); B4 (real host, enforcement dimensions) returned NULL under its pre-registered verdict lines. The claim that the gate reduces false completions is recorded as **not established by B1–B4 measurement** (D69), and the benchmark series is sealed (re-test only the affected dimension after a material host/mechanism change). Token cost remains unmeasured (no host exposes a token API — proxy metrics only). |

Overall posture (v0.5.1): the gate and its evidence spine are real;
the bridge layer is broad but shallow (deployed, not live-verified);
the evaluation still cannot say whether any of it improves outcomes
on real work. The next score movement is expected from subtraction
and B3 evidence, not from new surface.

---

## Quality Score — merged edition (2026-10-28, feat/merge-v3) [history]

Per-module scores for the merged branch (`feat/phase0-v3` skeleton +
`v3-yunyi` + `v3-yunkai`), with the evidence behind each. Scores are
0–10, deliberately un-generous: a score claims only what the cited
evidence shows. Re-issued when the evidence changes (monthly,
alongside benchmark baselines). Format merged from `v3-yunkai`; the
skeleton's baseline numbers are kept as an appendix below.

| Module | Score | Evidence |
|---|---|---|
| Gate layer (`gate/`) | 8 | 43 unit tests (pass-gate 17 + terminate 14 + graph 7 + comet_adapter 5) + repo_checks §3k gate validation (672 PASS total); dogfooded on this repo (3/3 feature_list items passing with gate evidence, Phase 1); bench gate arm left verifiable evidence in 24/24 runs across rounds 3–5; terminate/handoff/run, Graph executor, and comet_adapter all landed in this merge. Not 10: graph/comet-adapter paths are still young (7 and 5 tests); the gate's real-world soak time is still short. |
| Pipeline & deploy | 7 | Strict gates real since Phase 2 (drift fixtures prove exit codes); comet pinned 0.5.1 + state backup verified end-to-end (this merge); deploy dir creation tested; three profiles measured (minimal 15 skills / 280,960 B, standard 20 / 321,898 B, full 37 / 650,048 B); slim Project template ships with minimal/standard (D-009, this merge). Not higher: ps1 paths are review-verified, not execution-verified on Windows. |
| Hooks & guard | 7 | 125 hook tests green (hooks 90 + write 12 + gate 11 + lifecycle 12) + 5 server tests; guard expands substitutions recursively, enforces the D27 resolver conjunction (13 tests), logs parse failures to guard-alerts.jsonl and still fails open; yunkai's nested-substitution hardening tests added in this merge; the P1-2 closure (wrapper options, alias deny, xargs/find, same-command variables) added 17 more. Not higher: guard remains a guardrail, not a sandbox (documented); Stop hook has no soak time yet. |
| Distribution (templates + 39 skills) | 5 | Counts machine-guarded (skills-lock: 36 github entries pinned, CI `--check --strict`); licensing inventoried; template-size ablation done — slim Project template adopted for minimal/standard tiers (D-009). Still: ~99K tokens of SKILL.md for 39 skills with zero per-skill usage evidence and known overlaps (e.g. two debugging skills); the skill catalog is the ablation cadence's next target. |
| Numbers & claims hygiene | 6 | Repo's own stale figures fixed in Phase 0 and now CI-guarded (repo_checks 672 PASS); upstream figures (comet skill) dispositioned in the 2026-10-28 bench baseline; this merge's numbers are all re-measured (see verification record). Not higher: the upstream text still ships un-annotated in the synced skill (cannot edit without breaking sync). |
| Evaluation | 4 | t1–t4: 36-run matrix, 36/36 pass, 0 false completions (but ceiling effect — tasks too trivial to discriminate arms); t5–t8: one-round matrix 13/13 accepted, 0 false completions (this merge, `eval/results/bench-t5-t8-merge-round1.md`), but the executor reused one implementation per task across arms, so no arm discrimination was measured; rubric calibrated 5 rounds, standing advisory-only (D28, user final ruling 2026-10-29; live second review deferred, not owed); thresholds provisional. But tasks are minutes-scale and arms are same-model — scores here measure provability and cost, not capability deltas. |

Overall posture: the enforcement and measurement spine is real; the
distribution bulk is unproven value and the evaluation is young.
Subtraction (Phase 4, driven by these numbers) is where the
distribution score is supposed to move — by shrinking, not growing.

## What changes next

1. ~~Complete the t5–t8 one-round matrix (4 tasks × 3 arms + dist-slim
   arm) and record it in `docs/internal/merge-verification.md`; if the
   hard tasks separate the arms, the Evaluation score moves.~~ Done
   2026-10-28 in this merge: 13/13 accepted, 0 false completions —
   but one implementation per task was reused across arms, so no arm
   separation was measured; the score stays 4 until independent
   per-run executions (or harder tasks) separate the arms.
2. Live second-person rubric calibration round — DEFERRED, not owed (D28): only on a real project the user knows well, when conditions mature; only then revisit `stable`/auto-approval.
3. Monthly ablation continues (next run 2026-11); `writing-skills`
   was removed 2026-10-29 by owner decision (D65), so the 2026-11 run
   moves on to another component.
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
  (2026-10-28). `minimal` (default): **15 skill dirs, 280,960 skills
  bytes, 789,323 deployed-total bytes** (re-measured 2026-10-29
  after the D31 adjustment). `standard`: **20 dirs, 321,898
  skills bytes, 912,560 deployed-total bytes** (re-measured 2026-10-29
  after the D30 adjustment). `full`: **38 dirs (heavy
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
| Hooks (5 events) | Accept | 125 hook tests pass (90 + 12 + 11 + 12); parse failures logged, still fail-open |
| Benchmarks (`eval/`) | Accept | 36/36 runs pass (12 per arm); thresholds re-derived from the full matrix, still provisional |
| Docs / i18n | Revise | EN/ZH current; FR/DE deleted per D27; ZH-TW frozen per D3; rubric standing advisory-only (D28) |

Module scores are judgement calls anchored to the evidence cited, not
measurements. The rubric itself is **calibrated (5 rounds, 0 divergences)**
but standing advisory-only, not `stable` — see D28 and
`eval/calibration.md`.
