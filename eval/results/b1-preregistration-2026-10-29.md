# B1 discriminating bench round — pre-registration (2026-10-29)

Registered BEFORE any B1 run starts. Branch `feat/merge-v3`, user
scope decision 2026-10-29: full t1–t8. This file is the contract the
B1 report is judged against; results must not rewrite it.

## Scope

- Tasks: t1–t4 (`eval/tasks/`: t1-bugfix, t2-feature, t3-cross-file,
  t4-docs-sync) and t5–t8 (`eval/bench/fixtures/`).
- Arms: `bare`, `pack`, `gate` — three arms, identical across all
  eight tasks. The t5–t8 `dist-slim` arm is EXCLUDED from B1: t1–t4
  have no dist-slim arm, so including it would break cross-task arm
  comparability. It may run as a follow-up.
- Rounds: 3 per (task, arm). Total: 8 tasks x 3 arms x 3 rounds =
  72 runs.
- Apparatus per family, unchanged from the merge round:
  - t1–t4: `eval/run-bench.sh setup` + `record`; verdicts from
    `eval/check-results.py`.
  - t5–t8: `eval/bench/prep.py` (run dir + CLAIM footer + manifest)
    - `eval/bench/evaluate.py` (JSON verdict: `tests_pass`,
    `tests_intact`, per-task extras).
  - Pack definition differs by family (t1–t4 pack deploys
    `--profile full`; t5–t8 pack installs the 3-skill kit) — see
    `eval/bench/README.md`. Pack numbers are therefore reported per
    family, never pooled across families.

## Executors (freshness rule)

- Every run gets a NEW executor session. No executor runs twice.
- Executors receive only their run dir + arm footer. They never see
  reference `solution/` dirs, prior runs' outcomes, or other runs'
  code. Run dirs live outside the repo
  (`~/workspace/b1-runs-2026-10-29/`); only the results record below
  is committed.
- A run that cannot start (infra failure, BUDGET STOP) is recorded
  as BLOCKED, never as passing or failed. If blocked runs exceed
  10% of 72, the round is inconclusive.

## Metrics (recorded per run)

- Outcome: pass / fail / blocked.
- False completion: executor claims done but the verdict fails
  (t1–t4: check-results fail after a done claim; t5–t8: evaluator
  `tests_pass` false after a done claim, or `tests_intact` false).
- Duration (seconds), verify attempts, interventions.

## Pre-registered decision rules

Primary comparison is gate vs bare (the two arms whose definitions
are consistent across both task families). Pack is descriptive.

- DISCRIMINATION is claimed ONLY if ALL hold:
  - (i) gate false completions < bare false completions, pooled
    across all 8 tasks, by at least 2 runs;
  - (ii) gate false completions <= pack false completions pooled;
  - (iii) gate completion rate is not lower than bare's by more
    than 2 runs (the gate must not "win" by refusing to finish);
  - (iv) no arm shows concentrated `tests_intact` failures without
    a note in the report.
- If all arms record 0 false completions, the conclusion is "tasks
  still do not discriminate; no efficacy claim" — the same
  conclusion as the t1–t4 baseline, not a success.
- If (i)–(iv) fail but gate < bare on the hard subset (t5–t8)
  alone, the report may say "signal on hard tasks only" and must
  still not claim a general false-completion reduction.
- Durations and interventions are reported descriptively (medians
  per arm, per family). No threshold is set on them.
- Until B1 reports under these rules, release copy must NOT claim
  "the gate reduces false completions" — only "apparatus runs, 0
  false completions in the baseline".

## Cost and stop conditions

- Quota at registration: 23% of the free weekly limit (resets Nov 4
  21:48 CST). The coordinator checks quota before each batch and
  STOPS + reports if usage exceeds 80%.
- Hard stop (D57): the bench flow consults `cost.py check` but does
  not record to the cost ledger, and the ledger is currently empty,
  so no BUDGET STOP is expected. Any BUDGET STOP is recorded as
  BLOCKED per the rule above.

## Results destination

- `eval/results/b1-2026-10-29.md` (per-arm, per-family, and pooled
  tables; per-run rows with duration, attempts, interventions,
  outcome, false completion, blocked reason if any).
- The B1 report must quote this pre-registration's decision rules
  and state which branch of the rules the outcome falls under.
