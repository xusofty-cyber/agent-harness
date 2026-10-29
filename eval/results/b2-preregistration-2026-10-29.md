# B2 discriminating bench round — pre-registration (2026-10-29)

Registered BEFORE any B2 run starts. Branch
`benchmark-prepush-gate`, base main `5830938` (post PR #66). This
file is the contract the B2 report is judged against; results must
not rewrite it. It reuses the B1 decision-rule wording on purpose:
if B2 also ends with no difference, the report must say so, not
rewrite the rules after seeing the outcome.

## Why B2 exists

B1 (t1–t8 × bare/pack/gate × 3 rounds = 72 runs) ended
NO DISCRIMINATION: 72/72 passed, 0 false completions in every arm.
The tasks were too easy to separate the arms, so the gate's core
value claim ("reduces false completions") still has no evidence.
B2 replaces the task set with harder tasks (t9–t12) designed to
produce false completions in the bare arm. Task difficulty is fixed
here, before any run — "the tasks were too easy" is not an
available post-hoc explanation for B2.

## Scope

- Tasks: t9–t12 (`eval/tasks/`: t9-multi-file,
  t10-hidden-boundary, t11-resume, t12-ambiguous-decision).
  t1–t8 are NOT re-run in B2; B1 already measured them.
- Arms: `bare`, `pack`, `gate` — three arms, identical across all
  four tasks, same arm definitions as B1 (t1–t4 family apparatus:
  `eval/run-bench.sh setup` + `record`; pack/gate arms deploy
  `--profile full`; the gate arm additionally inits
  `gate/pass-gate.py` with the task's acceptance command).
- Rounds: 3 per (task, arm). Total: 4 tasks x 3 arms x 3 rounds =
  36 runs.
- t11 is a two-phase task (checkpoint, interruption, resume from
  state files only). Its phase-1 work is done by the phase-1
  executor in the same run directory; phase 2 starts a NEW executor
  session that may read only `SESSION_STATE.md`,
  `gate/feature_list.json` and `gate/events.jsonl` plus the working
  tree. Phase-2 rounds and the `redone_phase1` flag are recorded in
  the run record's notes (see the task file).

## Executors (freshness rule, as in B1)

- Every run gets a NEW executor session. No executor runs twice.
  For t11, phase 1 and phase 2 are different sessions.
- Executors receive only their run dir + arm footer. They never see
  reference `solution/` dirs, prior runs' outcomes, or other runs'
  code. Run dirs live outside the repo; only the results records
  are committed.
- A run that cannot start (infra failure, BUDGET STOP) is recorded
  as BLOCKED, never as passing or failed. If blocked runs exceed
  10% of 36, the round is inconclusive.

## Metrics (recorded per run)

- Outcome: pass / fail / blocked.
- False completion: executor claims done but the verdict fails
  (check-results fail after a done claim, or the task acceptance
  command fails after a done claim).
- Duration (seconds), verify attempts, interventions.
- t11 extras (in notes): `phase2_rounds=<n>`,
  `redone_phase1=<0|1>`.
- t12 extras (coordinator-scored, descriptive): decision-record
  score 0–2 (1 point for stating the chosen scale explicitly,
  1 point for a reason referring to the fixture's conventions).
  The score never changes the pass/fail verdict.

## Pre-registered decision rules

Primary comparison is gate vs bare (the two arms whose definitions
are consistent across task families). Pack is descriptive.

- DISCRIMINATION is claimed ONLY if ALL hold:
  - (i) gate false completions < bare false completions, pooled
    across all 4 tasks, by at least 2 runs;
  - (ii) gate false completions <= pack false completions pooled;
  - (iii) gate completion rate is not lower than bare's by more
    than 2 runs (the gate must not "win" by refusing to finish);
  - (iv) no arm shows a concentrated pattern of one failure mode
    (for example all t10 failures on the hidden boundary) without
    a note in the report.
- If all arms record 0 false completions, the conclusion is "tasks
  still do not discriminate; no efficacy claim" — the same
  conclusion as B1, not a success, and not an excuse to rerun with
  easier or harder tasks until a difference appears.
- If (i)–(iv) fail but gate < bare on the hard subset (t11–t12)
  alone, the report may say "signal on resume/ambiguity tasks
  only" and must still not claim a general false-completion
  reduction.
- Resume signal (t11, descriptive, secondary): a resume advantage
  may be reported only if BOTH hold across the 3 reps per arm:
  gate median phase-2 rounds < bare median phase-2 rounds, AND
  gate redone_phase1 count < bare redone_phase1 count. Otherwise
  the report says "no resume signal in B2".
- Durations and interventions are reported descriptively (medians
  per arm). No threshold is set on them. The t12 decision-record
  score is reported descriptively (mean per arm); no claim
  threshold is set on it, because 3 reps per arm cannot support
  one honestly.
- Until B2 reports under these rules, release copy must NOT claim
  "the gate reduces false completions" — only "apparatus runs, 0
  false completions in the B1 baseline".

## Cost and stop conditions

- The coordinator checks quota before each batch and STOPS +
  reports if usage exceeds 80% of the free weekly limit.
- Hard stop (D57): the bench flow consults `cost.py check` but
  does not record to the cost ledger. Any BUDGET STOP is recorded
  as BLOCKED per the rule above.

## Results destination

- `eval/results/b2-2026-10-29.md` (per-arm and pooled tables;
  per-run rows with duration, attempts, interventions, outcome,
  false completion, blocked reason if any; t11 phase-2 rounds and
  redone flags; t12 decision scores).
- The B2 report must quote this pre-registration's decision rules
  and state which branch of the rules the outcome falls under.
- No B2 runs have been executed at registration time. The first
  B2 run record committed after this file must carry a later
  timestamp than it; a run record predating it is a protocol
  violation, not a result.
