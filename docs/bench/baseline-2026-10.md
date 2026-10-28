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
- Executor: Muse Spark on this VM, same executor for all 12 runs.
- Runs are recorded by `eval/run-bench.sh record` with duration, rounds
  (tool calls), verify attempts, interventions, outcome, false-completion.

## Measured results — bare arm (12/12 pass)

| Task | rep1 | rep2 | rep3 | Median | Min–Max | Rounds (median) | Verify attempts |
|---|---|---|---|---|---|---|---|
| T1 bugfix | 6 s | 6 s | 8 s | 6 s | 6–8 s | 4 | 1, 1, 1 |
| T2 feature | 7 s | 7 s | 8 s | 7 s | 7–8 s | 4 | 1, 1, 1 |
| T3 cross-file | 32 s | 18 s | 7 s | 18 s | 7–32 s | 3 | 1, 1, 1 |
| T4 docs+code | 32 s | 18 s | 7 s | 18 s | 7–32 s | 5 | 1, 1, 1 |

Pooled (12 runs): median duration **7.5 s**, completion **12/12 (100%)**,
false completions **0/12**, interventions **0**, every run passed on its
first verify attempt.

## Unmeasured cells

| Arm | Runs done | Status |
|---|---|---|
| `pack` | 0/12 | **unmeasured** — framework ready (`run-bench.sh setup --arm pack` tested once for T1 gate setup, not as a scored run) |
| `gate` | 0/12 | **unmeasured** — setup path tested once (T1 gate, item `in_progress`), not as a scored run |

The full 3-arm × 4-task × 3-rep matrix is 36 runs; 12 are done. The
remaining 24 are follow-up work, not claimed here.

## Thresholds — derived from baseline variance (provisional)

No threshold below is invented. Each is computed from the bare-arm numbers
above; the formula is stated so anyone can recompute it. All thresholds
are **provisional** (n=3 per task, single executor) and must be re-derived
after the full matrix.

- **Duration red-line per task** = median + 2 × (max − median).
  With n=3, (max − median) is the only spread estimate available; doubling
  it leaves headroom for one more slow run without flagging normal
  learning-curve variation.
  - T1: 6 + 2×(8−6) = **10 s**
  - T2: 7 + 2×(8−7) = **9 s**
  - T3: 18 + 2×(32−18) = **46 s**
  - T4: 18 + 2×(32−18) = **46 s**
- **Rounds red-line per task** = max + 2 (one extra read+verify cycle).
  - T1: **6**, T2: **6**, T3: **6**, T4: **8**
- **Completion-rate floor** = 11/12 in any 12-run window. Baseline is
  12/12; one more failure than baseline trips it.
- **False-completion red-line** = any false completion (>0 in any window).
  Baseline is 0/12; a false pass contradicts the gate's core promise.
- **Verify-attempts flag** = 3+ attempts on a single run (two failed
  verifies before a pass) → flag for review, not an automatic fail.

## Confounds — read before quoting any number

1. **Same executor, learning effect.** One executor did all 12 reps.
   Durations fell across reps (T3/T4: 32 → 18 → 7 s) because the executor
   already knew the fixture. Independent-session reps would show larger
   variance; the thresholds above are lower bounds on variance, not
   estimates of it.
2. **Trivial tasks.** Each task is a 1–3 line change. Absolute durations
   (6–32 s) reflect task triviality plus fixture familiarity, not
   real-world task cost. The comparative signal across arms is the point
   of this benchmark, not the absolute seconds.
3. **n=3 per task.** Medians from three runs are fragile. Do not use
   these thresholds to claim a regression on a single run; use them on
   12-run windows as defined above.
4. **Rep-3 shortcut.** In rep 3 of T1/T2/T4 the executor skipped re-reading
   fixture files it already knew, so rep-3 rounds are one lower than a
   fresh session would need. This is recorded in the run notes; it
   slightly understates rounds/durations for rep 3.

## What this baseline does NOT show

- Whether the pack or the gate arm is faster, slower, or more reliable:
  both are unmeasured.
- Any token number: no host exposes a programmatic token API (see
  `docs/internal/token-adapters.md`). Cost is tracked via Phase 2 proxy
  metrics only.
- Any comparison with upstream token-reduction claims: those numbers are
  not ours, are not reproduced here, and are not used as thresholds.
