# Baseline report — Phase 3 benchmarks (2026-10-28)

First measured numbers for agent-harness. Everything below is a real run
(`eval/results/*.json`); unmeasured cells are marked **unmeasured**, not
filled in. No upstream numbers are quoted here as our own results.

## Method

- Fixture: `eval/fixture/` (tinycalc), fixed start commit
  `2e583970fb952158ad83617fe436534abd38295d` (deterministic: fixed author,
  dates, message; the runner refuses to run on a different hash).
- Arms: `bare` (fixture only), `pack` (distribution pack deployed),
  `gate` (pack + `gate/` workflow). Isolation: P01 English independent
  directory method — one fresh directory per run, no shared files.
- Executor: bare arm — Muse Spark, Phase 3 session, this VM.
  Pack/gate arms — Muse Spark, a fresh session (this run), same VM.
  **The arms were run by different executor sessions** — see Confounds.
- Runs are recorded by `eval/run-bench.sh record` with duration, rounds
  (tool calls), verify attempts, interventions, outcome, false-completion.

## Measured results — full 36-run matrix (2026-10-28)

All three arms measured. Pooled median is the median of all 9 runs for
the task (3 arms × 3 reps); it is the value `eval/check-results.py`
recomputes from `eval/results/*.json`.

| Task | Bare reps | Pack reps | Gate reps | Pooled median | Pooled range | Rounds (median, pooled) | Verify attempts |
|---|---|---|---|---|---|---|---|
| T1 bugfix | 6, 6, 8 | 4, 3, 3 | 5, 4, 5 | 5 s | 3–8 s | 3 | 1 (all 9 runs) |
| T2 feature | 7, 7, 8 | 7, 4, 4 | 4, 16, 7 | 7 s | 4–16 s | 3 | 1 (all 9 runs) |
| T3 cross-file | 32, 18, 7 | 10, 8, 4 | 9, 5, 4 | 8 s | 4–32 s | 3 | 1 (all 9 runs) |
| T4 docs+code | 32, 18, 7 | 5, 4, 4 | 9, 5, 5 | 5 s | 4–32 s | 3 | 1 (all 9 runs) |

Per arm (12 runs each):

| Arm | Completion | False completions | Interventions | Median duration | Range | Median rounds |
|---|---|---|---|---|---|---|
| bare | 12/12 (100%) | 0/12 | 0 | 7.5 s | 6–32 s | 4 |
| pack | 12/12 (100%) | 0/12 | 0 | 4.0 s | 3–10 s | 3 |
| gate | 12/12 (100%) | 0/12 | 0 | 5.0 s | 4–16 s | 4 |

Pooled (36 runs): completion **36/36 (100%)**, false completions
**0/36**, interventions **0**, median duration **6.0 s**, every run
passed on its first verify attempt.

## Three-arm conclusions — read before quoting any comparison

1. **Outcome: no difference between arms.** All three arms are 12/12
   pass, 0 false completions, 0 interventions, first-verify pass every
   time. The tasks are too trivial to discriminate the arms on outcome —
   this is a ceiling effect, not evidence that the arms are equivalent
   on real work. The gate's ability to catch a false pass was **not**
   demonstrated by this matrix (no false pass occurred); it was
   demonstrated separately in Phase 1 dogfood-1, where a planted fake
   `passing` was intercepted by CI §3k.
2. **Duration: pack/gate look faster than bare, but that gap is not a
   clean arm effect.** Bare was run by the Phase 3 executor session;
   pack/gate by a fresh session that had already read the whole fixture
   and all four task specs before its first run. The bare executor's
   T3/T4 rep-1 runs took 32 s each (first-exposure discovery); this
   session's first T3/T4 runs took 10 s / 9 s. Do not quote "pack is
   faster than bare" — the executor changed between arms.
3. **Pack vs gate (the one clean comparison).** Both arms were run by
   the same executor in this session, with arm order alternated per task
   (T1/T3 started pack, T2/T4 started gate) so first-exposure advantage
   is balanced. Pack median 4.0 s vs gate median 5.0 s; pack median
   rounds 3 vs gate 4. The +1 s / +1 round on gate is the gate's own
   workflow (pass-gate verify + status check), not extra rework — every
   gate run passed on its first verify, and `status` confirmed
   `passing` with evidence in all 12 gate runs. No outcome difference.
4. **Failure attribution: none possible.** Zero failures in 36 runs, so
   there is nothing to attribute to the five diagnostic layers. The
   matrix cannot answer "does the gate reduce false completions or
   rebuild cost" — it can only say neither arm produced a failure on
   these tasks.
5. **Rebuild cost (new-session rebuild): not measured by this matrix.**
   Both executors did many runs each; a fresh-session handover was
   measured in Phase 1 dogfood (~1 s) and not re-measured here.

## Thresholds — re-derived from the full matrix (still provisional)

Re-derived with the same formulas as the bare-only provisional
thresholds, now from the pooled 9 runs per task (36 runs total).
Recomputation is stated so anyone can re-derive it from
`eval/results/*.json`. Thresholds stay **provisional**: the pooled spread
is dominated by the bare executor's first-rep learning (32 s outliers)
and one 16 s inter-call-latency outlier (T2 gate rep2, see Confounds),
so the re-derived duration red-lines are looser than the provisional
ones. Do not use them to claim a regression on a single run; use them on
12-run windows as defined below.

- **Duration red-line per task** = pooled median + 2 × (pooled max −
  pooled median).
  - T1: 5 + 2×(8−5) = **11 s** (provisional was 10 s)
  - T2: 7 + 2×(16−7) = **25 s** (provisional was 9 s; the 16 s is the
    T2 gate rep2 latency outlier, not a slow task)
  - T3: 8 + 2×(32−8) = **56 s** (provisional was 46 s)
  - T4: 5 + 2×(32−5) = **59 s** (provisional was 46 s)
- **Rounds red-line per task** = pooled max + 2 (one extra read+verify cycle).
  - T1: **6**, T2: **6**, T3: **6**, T4: **8** (unchanged from provisional)
- **Completion-rate floor** = 11/12 in any 12-run window (per arm).
  Baseline is 12/12 per arm; one more failure than baseline trips it.
- **False-completion red-line** = any false completion (>0 in any window).
  Baseline is 0/36; a false pass contradicts the gate's core promise.
- **Verify-attempts flag** = 3+ attempts on a single run (two failed
  verifies before a pass) → flag for review, not an automatic fail.

## Confounds — read before quoting any number

1. **Different executors per arm.** Bare was run by the Phase 3
   session; pack/gate by this session. Cross-arm duration gaps
   (bare 7.5 s vs pack 4.0 s vs gate 5.0 s medians) are confounded by
   executor, not attributable to the arms. Only the pack-vs-gate gap
   (same executor, alternating order) is a clean arm comparison.
2. **Within-session learning.** Durations fell across reps in both
   sessions (bare T3/T4: 32 → 18 → 7 s; this session T3 pack:
   10 → 8 → 4 s, T3 gate: 9 → 5 → 4 s). Arm order was alternated so
   first-exposure advantage is balanced between pack and gate, but
   rep-3 numbers understate what a fresh session would need.
3. **Inter-call latency inside durations.** Duration is wall-clock from
   setup to verify and includes the executor's latency between tool
   calls. T2 gate rep2 (16 s) is the outlier: the verify itself passed
   first try in under a second; the 16 s is the gap between the
   executor's calls in that turn sequence. The same applies to the
   bare arm's numbers. At this task size, duration is a noisy
   executor-latency measure, not a precise task-cost measure.
4. **Rounds reflect batching style.** This session batched shell
   commands in later reps (T3 pack rep2/3 = 2 rounds vs rep1 = 4),
   so rounds fell as the session learned the fixture — same pattern
   as the bare executor's rep-3 shortcut. Cross-executor rounds
   comparisons are weak; the robust metrics are outcome,
   verify attempts, and false completions. Within this session, gate
   runs cost +1 round vs pack (the `status` confirmation call).
5. **Trivial tasks, ceiling effect.** Each task is a 1–3 line change;
   36/36 first-try passes. Absolute durations reflect task triviality
   plus fixture familiarity, not real-world task cost. Harder tasks
   (multi-step, ambiguous, or with a planted defect to catch) are
   needed before the matrix can discriminate arms on reliability.
6. **n=3 per arm-cell.** Medians from three runs are fragile. Same host
   and model (Muse Spark, this VM) for all 36 runs; no cross-host or
   cross-model variance measured.
7. **No batch setup.** Each run directory was set up immediately before
   its run (no batch preparation), so `started` timestamps are not
   polluted the way the Phase 4 ablation run's were.

## What this baseline does NOT show

- Whether the gate reduces false completions or rebuild cost on real
  work: no failure occurred in 36 runs, so there is nothing to compare.
- Any token number: no host exposes a programmatic token API (see
  `docs/internal/token-adapters.md`). Cost is tracked via Phase 2 proxy
  metrics only. Token cost remains **unmeasured**.
- Any comparison with upstream token-reduction claims: those numbers are
  not ours, are not reproduced here, and are not used as thresholds.
- New-session rebuild cost for pack vs gate: **unmeasured** in this
  matrix (see conclusion 5 above).

## Addendum (Phase 4, 2026-10-28) — pack/gate arms pinned to `--profile full`

`eval/run-bench.sh setup` for the `pack` and `gate` arms now passes
`--profile full` to `deploy-agents.sh`. Reason: Phase 4 changed the deploy
default to `minimal` (10 skills); without the pin, the pack arm would no
longer be the distribution pack Phase 3 designed the comparison around
(38 skills). The pack arm was never measured before this change (0/12), so
no measured data is redefined by pinning it now. The bare-arm numbers above
are unaffected.

## Addendum (full matrix, 2026-10-28) — pack/gate arms completed

Pack and gate arms run by a fresh Muse Spark session on this VM
(24 runs, 2026-10-28). Records in `eval/results/*_pack_rep*.json` and
`*_gate_rep*.json`; commits `bench(t1)`–`bench(t4)`. Gate runs verified
via `pass-gate.py verify` with `status` confirming `passing` with
evidence in all 12 gate runs. No runner or task-spec change was needed
to run the matrix (no bug found in `run-bench.sh` or the task specs).
