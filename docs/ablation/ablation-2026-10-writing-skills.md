# Ablation 2026-10 — `writing-skills`

Component: `writing-skills` (107640 bytes on disk). Dependency gate: CLEAR (no template/hook references; checked 2026-10-28).

Method: pack-arm bench runs with `writing-skills` removed from the run directory (`.agents/skills` and `.claude/skills`). Baseline thresholds recomputed from the bare arm with the Phase 3 formulas (duration red-line = median + 2×(max−median); rounds red-line = max+2; completion floor 11/12; any false completion is a breach).

## Runs (12)

| Task | Rep | Duration | Rounds | Outcome | False completion | Status |
|---|---|---|---|---|---|---|
| t1-bugfix | 1 | 24 s (red-line 10) | 1 (red-line 6) | pass | 0 | REGRESSION |
| t1-bugfix | 2 | 25 s (red-line 10) | 1 (red-line 6) | pass | 0 | REGRESSION |
| t1-bugfix | 3 | 26 s (red-line 10) | 1 (red-line 6) | pass | 0 | REGRESSION |
| t2-feature | 1 | 2 s (red-line 9) | 1 (red-line 6) | pass | 0 | ok |
| t2-feature | 2 | 0 s (red-line 9) | 1 (red-line 6) | pass | 0 | ok |
| t2-feature | 3 | 0 s (red-line 9) | 1 (red-line 6) | pass | 0 | ok |
| t3-cross-file | 1 | 0 s (red-line 46) | 1 (red-line 6) | pass | 0 | ok |
| t3-cross-file | 2 | 1 s (red-line 46) | 1 (red-line 6) | pass | 0 | ok |
| t3-cross-file | 3 | 0 s (red-line 46) | 1 (red-line 6) | pass | 0 | ok |
| t4-docs-sync | 1 | 1 s (red-line 46) | 1 (red-line 8) | pass | 0 | ok |
| t4-docs-sync | 2 | 0 s (red-line 46) | 1 (red-line 8) | pass | 0 | ok |
| t4-docs-sync | 3 | 1 s (red-line 46) | 1 (red-line 8) | pass | 0 | ok |

## Verdict

REGRESSION — keep the component.

## Recommendation

KEEP — regression observed; do not remove.

> Superseded by the operator correction below: the only breaches are the
> three T1 durations, which are a batching artifact (see "Operator
> correction"). Corrected recommendation: CANDIDATE FOR REMOVAL (bench
> only), owner sign-off still required.

## Operator correction — the T1 duration breach is a measurement artifact, not a regression (2026-10-28)

The mechanical verdict above says REGRESSION, driven entirely by the three
T1 durations (24/25/26 s vs the 10 s red-line). All 12 outcomes are `pass`,
false completions are 0, and rounds (1) are far under every red-line. The
T1 durations are not comparable to the baseline, for a documented reason:

- The 12 run directories were prepared in one batch first (all 12
  `prepare` calls), then the tasks were performed. The T1 `started`
  timestamps (1793183112/3112/3113) cluster at prepare time; the work
  happened at 1793183136–3139. The 24–26 s therefore measures batch
  latency, not task time.
- The same agent doing the same one-line T1-class fix in the interleaved
  T2 rep1 run took 2 s, and single-invocation runs took 0–1 s (1-second
  resolution). The skill's absence cannot plausibly add ~20 s to a
  one-line fix; the difference tracks the execution pattern, not the
  component.
- Three timing conventions were used across the 12 runs, and the report
  records which: T1 batched (durations inflated), T2 rep1 interleaved
  (2 s), the other 8 single-invocation (0–1 s, shell-execution time only,
  reasoning time before the invocation excluded). Duration and rounds are
  therefore not the verdict basis for this run.

**Corrected verdict: NO REGRESSION on outcome (12/12 pass, 0 false
completions).** The duration signal is inconclusive for this run and must
not be quoted as a regression. The mechanical table above is left intact;
this section is the correction, not a rewrite.

## Recommendation (corrected)

CANDIDATE FOR REMOVAL (bench only — these four tasks do not exercise
every skill; `writing-skills` is about authoring skills, which no bench
task does). Removal still needs the owner's sign-off below, plus the
guide / `skills-profiles.json` / `skills-lock.json` updates in the same
change. Size at stake: 107,640 bytes (5.5% of the 1,960,329-byte full
profile, skills-only).

## Human decision

PENDING — owner. Removal requires the owner to fill in this line (remove / keep + reason + date). The script never removes anything itself.
