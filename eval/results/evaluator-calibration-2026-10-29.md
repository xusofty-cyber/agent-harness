# Evaluator calibration — night extension (2026-10-29)

> **Status banner — read first.** This report does NOT claim a live
> human second review. **实时二审仍欠用户复核**: no live second judge
> scored any sample in this round, and nothing in this report should be
> cited as "reviewed by a human second judge". What was done instead is
> a recorded-outcome calibration extension (see §1–§2 for exactly what
> the "human side" is and is not). The rubric stays **advisory-only**
> (D28, user final ruling 2026-10-29); `evaluate.py --gate` still
> refuses unconditionally (§6); `eval/rubric-status.json`,
> `eval/rubric.md`, `eval/calibration.md` and `eval/evaluate.py` were
> **not changed** by this work. Rubric wording suggestions in §5 are
> proposals for the user to decide, not applied changes.

## 1. Ground truth — what was actually found (and what does not exist)

Searched 2026-10-29 night, in this clone of main `5fd31c7`:

- `eval/results/*.json` — 72 bench records (t1–t4, t9–t12, 3 arms × 3
  reps), 12 ablation records, 13 t5–t8 merge-round records, plus
  `eval/results/b1-2026-10-29.md` and `eval/results/b2-2026-10-29.md`.
- `eval/calibration.md` — the 5 existing calibration rounds.
- `docs/internal/phase1-dogfood.md`, `docs/internal/phase2-verification.md`,
  `DECISIONS.md` (D15, D28), `eval/rubric-status.json`.
- Repository-wide search for scorecard JSONs, second-reviewer records,
  manual per-dimension scores: **none found** (no `*scorecard*` file
  exists in the repo; no human per-dimension score exists anywhere in
  `eval/` or `docs/`).

**Ground-truth inventory, stated plainly:**

| Source | N | What the "human side" actually is | Usable as |
|---|---|---|---|
| Existing calibration rounds 1–5 (`eval/calibration.md`) | 5 | Recorded phase outcomes / acceptance results (Phase 1 Go-gate pass, Phase 2 Go-gate item pass, t3 acceptance pass ×2, v1 diagnosis "not a harness" as the negative control). The file itself says: recorded outcomes, "no live second judge was available". | Verdict-level comparison only |
| B2 runs t9–t12, all arms/reps (this round's new sample) | 36 | Recorded acceptance outcome (`outcome: pass`, `false_completion: 0`) from `eval/results/t9*–t12*.json`, independently re-verified by the B2 coordinator per the B2 report. **Not a human judgement** — it is a machine acceptance verdict plus a coordinator re-verification note. | Verdict-level comparison only |
| t12 decision-record scores (B2 report, coordinator-scored, descriptive) | 9 | Coordinator score 2/2 for every t12 run's `DECISIONS.md` (1 pt scale stated + 1 pt reason referring to fixture conventions). This is the closest thing in the repo to a human-scored number — but it scores the decision record, **not** any rubric dimension, so it cannot be used as rubric ground truth. Reported here for completeness, not folded into any agreement rate. | Corroboration only, not agreement |
| B1 runs t1–t8 (pooled report) | 72 | Acceptance verdicts: 24/24 pass per arm, 0 false completions. Not re-scored here: t1–t4 run dirs are not preserved in this sandbox and t5–t8 run dirs are gone, so rubric scoring (which requires re-running acceptance and inspecting diffs) cannot be done honestly from records alone. | Not scored; cited as context |
| Independent live human per-dimension scores | **0** | Do not exist. | — |

**Consequence, stated once and applied everywhere below:** a
per-dimension "agreement rate with human judgement" **cannot be
computed** from this repository, because the human side of that
fraction is empty. Any report that printed one would be fabricating
it. What IS computed is (a) verdict agreement against recorded
outcomes, and (b) the evaluator's own dimension-score distribution —
two different things, never merged into a single "human consistency"
number.

## 2. Method — new sample (36 B2 runs)

Sample: all 36 B2 runs (t9-multi-file, t10-hidden-boundary,
t11-resume, t12-ambiguous-decision × bare/pack/gate × rep1–3).
These were chosen because, unlike B1, their run directories are
still preserved under `/tmp/bench/<task>/<arm>/rep<n>`, so the rubric's
own first rule — re-run acceptance, never trust the claim — could
actually be followed.

Per run, the evaluator (this night session) did:

1. **Re-ran the task acceptance command** inside the preserved run
   dir, exactly as written in `eval/tasks/<task>/task.md`, with ONE
   documented substitution: system `python3` has no pytest in this
   sandbox, so pytest steps ran under `/tmp/bench-venv/bin/python`
   — the same equivalent interpreter the B2 report itself cites.
   No acceptance command was otherwise altered.
2. **Diffed task-relevant files** against the pristine fixture
   (`eval/fixture/`): t9 = calc.py, cli.py, README.md,
   tests/test_calc.py; t10 = calc.py, tests/test_calc.py; t11 =
   calc.py, SESSION_STATE.md; t12 = calc.py, DECISIONS.md. Added /
   removed lines were scanned and manually reviewed for unrelated
   changes inside a touched file (the t3-bare-rep1 scope-1 pattern
   from calibration round 3). For bare arms the full run-dir file
   tree was also compared with the fixture: no extra files except
   the task's own SESSION_STATE.md / DECISIONS.md. Pack/gate run
   dirs additionally contain deploy scaffolding (AGENTS.md, docs/,
   gate/, templates/, etc.); that scaffolding is setup artefact
   deployed before the executor ran, not executor scope, and is
   excluded from the scope judgement — the scope claim below is
   therefore a claim about task-relevant files, not a full-tree
   claim for pack/gate arms.
3. **Read the run record** (`eval/results/<task>_<arm>_rep<n>.json`)
   for outcome, false-completion flag, verify attempts,
   interventions and notes, and the B2 report's caveats.
4. **Scored all six dimensions** with per-dimension evidence, then
   computed the verdict with `eval/evaluate.py`'s rule (Accept =
   total ≥ 9 and no 0; Block = any 0; else Revise). Verdicts were
   never hand-chosen. All 36 scorecards are saved as machine-
   checkable JSON under
   `eval/results/evaluator-calibration-2026-10-29-scorecards/` and
   all 36 pass `python3 eval/evaluate.py check`.

**Scoring rules fixed before scoring (uniform, no post-hoc fitting):**

- Correctness 2 iff the evaluator's acceptance re-run passes every
  step; 0 iff any step fails. (No partial-pass case occurred, so
  the 1 anchor was defined but unused.)
- Verification 2 iff the re-run used the literal acceptance commands
  (system python3 / grep) and the B2 report states every run was
  independently re-verified by the coordinator; 1 iff a pytest step
  ran under the equivalent venv interpreter (evidence does not
  match the literal command verbatim). This is the single systematic
  judgement call in this round, and it is applied to all 18 pytest
  runs alike, not tuned per run.
- Scope 2 iff task-relevant diffs contain only the task change;
  1 iff one unrelated change inside a touched file; 0 iff unrelated
  features/files. (No 1 or 0 occurred — see §4.)
- Reliability 2 iff the re-run outcome matches the recorded outcome
  with interventions 0 and no flakiness note. Single re-run only:
  this weakly tests determinism (see limitations).
- Maintainability 2 iff the diff follows fixture conventions. The
  fixture's functions are bare one-liners and only `divide` carries
  a docstring, so a new function without a docstring is NOT a
  convention breach; t12 docstrings and the t11 divide-docstring
  update are consistent additions.
- Handover 2 iff task spec + run record (+ SESSION_STATE.md /
  DECISIONS.md where the task requires one) suffice for a new
  session to continue; 1 iff the record omits a known deviation
  (exactly one case: §4, item D-1).

**Original-5 audit (not re-scored):** the cited sources for
calibration rounds 1–5 were re-read (phase1-dogfood PASS chains and
handover test, phase2-verification Go-gate verification, t3 bare
rep1 / gate rep1 records both `pass` with `false_completion 0`).
Nothing contradicted the recorded verdicts, so the existing 5/5
stands as recorded; re-scoring them would add no new evidence
because their evidence is unchanged since 2026-10-28/29 and no new
human side exists for them either.

## 3. Results — agreement numbers (with their exact denominators)

### Verdict agreement vs recorded outcomes (the only agreement rate this data supports)

| Sample | Evaluator verdicts | Recorded outcome | Verdict agreement |
|---|---|---|---|
| New: B2 t9–t12 (36 runs) | 36 × Accept | 36 × pass | **36/36 = 100%** |
| Existing: calibration rounds 1–5 | 4 × Accept, 1 × Block | Go-gate pass, Go-gate pass, acceptance pass, "not a harness", acceptance pass | **5/5 = 100%** |
| Independent live human per-dimension scores | — | — | **not computable (N = 0)** |

Totals in the new sample: 17 runs at 12/12, 19 runs at 11/12
(18 × verification-1, 1 × handover-1, no overlap — t10 pack rep2 is
12 on verification and 11 overall via handover). Zero verdict
divergences, zero dimension scores of 0.

### Evaluator dimension-score distribution, new sample (NOT an agreement rate)

216 dimension scores total (36 runs × 6):

| Dimension | 2 | 1 | 0 |
|---|---|---|---|
| Correctness | 36 | 0 | 0 |
| Verification | 18 | 18 | 0 |
| Scope discipline | 36 | 0 | 0 |
| Reliability | 36 | 0 | 0 |
| Maintainability | 36 | 0 | 0 |
| Handover readiness | 35 | 1 | 0 |
| **Total** | **197** | **19** | **0** |

Per-arm totals (descriptive only): t9 11/12 in all 9 runs; t10 12/12
except pack rep2 at 11/12; t11 11/12 in all 9 runs; t12 12/12 in all
9 runs. No arm effect is claimed: the t9/t11 11s come from the
interpreter substitution, which is an environment property, not an
arm property (it hits bare, pack and gate alike).

### Sample table (full 36 rows; per-run evidence is in the scorecard JSONs)

| Task | Arm | Rep | Corr | Verif | Scope | Reliab | Maint | Handover | Total | Evaluator verdict | Recorded outcome | Agree? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t10-hidden-boundary | bare | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | bare | rep2 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | bare | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | gate | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | gate | rep2 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | gate | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | pack | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t10-hidden-boundary | pack | rep2 | 2 | 2 | 2 | 2 | 2 | 1 | 11/12 | Accept | pass | yes |
| t10-hidden-boundary | pack | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t11-resume | bare | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | bare | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | bare | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | gate | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | gate | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | gate | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | pack | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | pack | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t11-resume | pack | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t12-ambiguous-decision | bare | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | bare | rep2 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | bare | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | gate | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | gate | rep2 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | gate | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | pack | rep1 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | pack | rep2 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t12-ambiguous-decision | pack | rep3 | 2 | 2 | 2 | 2 | 2 | 2 | 12/12 | Accept | pass | yes |
| t9-multi-file | bare | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | bare | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | bare | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | gate | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | gate | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | gate | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | pack | rep1 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | pack | rep2 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |
| t9-multi-file | pack | rep3 | 2 | 1 | 2 | 2 | 2 | 2 | 11/12 | Accept | pass | yes |

## 4. Divergence analysis — what actually diverged, and what did not

**Verdict divergences: none.** All 36 evaluator verdicts match the
recorded acceptance outcome, and all 5 existing rounds match their
recorded outcomes. There is no verdict-divergence list to show,
because there is no verdict divergence in either sample.

**Dimension-level departures from full marks: 19 of 216 scores are 1,
0 are 0.** They fall into two systematic groups plus one single case:

- **V-group (18 runs, verification 1):** every t9 and t11 run. Cause
  is environmental, not executor quality: system python3 lacks
  pytest, so the evaluator's re-run (like the B2 coordinator's)
  used `/tmp/bench-venv/bin/python`. The acceptance itself passes
  under the equivalent interpreter; the 1 records that the evidence
  does not match the literal acceptance command verbatim. If the
  user judges the venv interpreter fully equivalent, all 18 become
  2 and every run in the sample is 12/12 except D-1 — that is a
  user decision, not something this report assumes. **Review item
  V-1 for the user.**
- **D-1 (1 run, handover 1): t10-hidden-boundary pack rep2.**
  Scorecard: `t10-hidden-boundary_pack_rep2.scorecard.json`,
  total 11/12, verdict Accept. Evidence: B2 report caveat 3 states
  this run skipped a docs-sync DoD step outside the task's scope,
  and that deviation is NOT in the run record's notes. A new
  session continuing from the record alone cannot learn it, which
  is the rubric's handover-1 anchor ("needs one clarification").
  Acceptance is unaffected and the verdict does not change.
  **Review item D-1 for the user:** confirm the handover-1, or
  rule that a skipped out-of-scope DoD step should not cap
  handover.
- **t11 gate-arm caveat (not scored down further):** in all 3 t11
  gate runs the code passes acceptance (evaluator re-run, venv
  interpreter) but `gate/feature_list.json` still shows t11-resume
  `in_progress`, because `pass-gate.py verify` fails only on the
  missing system pytest (B2 report caveat 1). This is already
  reflected in the verification-1 above; it is not double-counted
  as a second penalty, and it must be stated whenever t11 gate
  passes are cited (as the B2 report itself requires).

**Divergences that could NOT be assessed (honest gaps, not hidden):**

- **Unattributed t10 deviation:** B2 report caveat 3 also says one
  t10 executor read the repository's general AGENTS.md, but does
  not say which arm/rep. It cannot be scored against any specific
  run without guessing, so no run was scored down for it. If the
  user (or the B2 coordinator's notes) can attribute it, that run's
  scorecard should be revisited — most plausibly on scope/handover
  notes, not on correctness or verdict.
- **No failing runs in the sample:** all 36 recorded outcomes are
  pass, all 36 re-runs pass, 0 false completions, 0 interventions.
  The rubric's Block and Revise verdicts are therefore untested by
  this round; the only Block evidence remains calibration round 4
  (the pre-Phase-0 retrospective). A sample with zero failures
  cannot show whether the evaluator would catch a failure.
- **Reliability is the weakest-measured dimension here:** one
  re-run matching the recorded outcome is consistent with
  determinism, not proof of it. No run showed flakiness, but no run
  was re-run twice either.
- **t12 decision ordering:** whether each DECISIONS.md entry was
  written before the implementation cannot be checked from the
  final tree alone (B2 report says the same). Handover scores for
  t12 rest on the record's presence and content, not on ordering
  proof.

**Classification of the 19 non-2 scores:** 18 environmental
(interpreter substitution) + 1 record-completeness (D-1) + 0
executor-quality failures. That classification is itself a finding:
in this ceiling sample, the evaluator's deductions say more about
the sandbox and the record-keeping than about executor quality.

## 5. Rubric — does it need a tweak? (advisory-side suggestions only, NOT applied)

**Recommendation: no change to the verdict rule, no change to
advisory-only status, no change to `eval/rubric-status.json`.**
Nothing in this round justifies moving the rubric toward `stable`
or auto-approval: the sample is all-pass toy tasks, there is no
live second judge, and D28 explicitly says bench toy tasks do not
count toward `stable`. The suggestions below are wording
clarifications on the advisory side only, for the user to accept or
reject; none was applied to `eval/rubric.md` in this PR.

- **S1 — Verification anchor, equivalent interpreters.** Add one
  sentence to the verification-1 anchor: when the sandbox lacks a
  required interpreter, re-running under a named equivalent
  interpreter is verification 1 (not 2), and the interpreter must
  be named in the evidence. This codifies the judgement actually
  used for the 18 t9/t11 runs, so a future evaluator does not have
  to re-decide it silently.
- **S2 — Handover anchor, record omissions.** Add to the
  handover-1 anchor: a run record that omits a known deviation —
  even one that does not change acceptance — caps handover at 1.
  This codifies D-1 (t10 pack rep2) and gives record-keepers a
  reason to note deviations in the record itself.
- **S3 — Reliability anchor, single re-run honesty.** Add a note
  (not a score change) that a single matching re-run is weak
  determinism evidence; a reliability 2 from one re-run should be
  read as "no flakiness observed", not "proven deterministic".

If the user rejects S1 (i.e. rules the venv interpreter fully
equivalent), the mechanical consequence is: 18 verification scores
become 2, and the sample becomes 35 runs at 12/12 and 1 run (D-1)
at 11/12, verdicts unchanged. If the user rejects S2, D-1 becomes
12/12 and the sample is uniform except for the interpreter question.
Either way, no verdict in this report moves.

## 6. Gate and checks evidence (this round)

- `evaluate.py --gate` on a valid 12/12 Accept scorecard:
  **exit 2, GATE REFUSED** — "rubric is advisory-only (D28, user
  final ruling 2026-10-29); it provides advisory opinions only and
  never auto-approves — a human decides." The check step on the
  same card exits 0 (`scorecard valid ... -> Accept (total 12/12)`).
  `eval/evaluate.py` was not modified.
- All 36 new scorecards pass `python3 eval/evaluate.py check`
  (verdicts recompute correctly under the rubric rule).
- `python3 tests/repo_checks.py`: see PR checks section below;
  the only accepted baseline deviation is the known sandbox-missing-
  pytest failure, if it appears (same baseline as prior rounds).

## 7. Review pack for the user (for tomorrow morning, no live review claimed)

**实时二审仍欠用户复核.** Nothing below has been second-reviewed
by a live judge. To make tomorrow's review a single pass, the user
is asked to confirm or overturn exactly these items (everything
else in this report is mechanical re-run/diff evidence):

1. **V-1:** verification 1 (not 2) for all 18 t9/t11 runs because
   pytest ran under `/tmp/bench-venv/bin/python` instead of system
   python3 — or rule the venv interpreter fully equivalent (then
   18 scores become 2, verdicts unchanged).
2. **D-1:** handover 1 for t10 pack rep2 (record omits the skipped
   docs-sync DoD step, B2 report caveat 3) — or rule it should not
   cap handover.
3. **Attribution (if known):** which t10 arm/rep read the repo's
   general AGENTS.md (B2 caveat 3, unattributed)? If attributable,
   that run's scorecard needs a note.
4. **S1–S3:** accept or reject the three advisory-side rubric
   wording suggestions in §5 (none applied yet).
5. **Scope of this calibration:** confirm that a 36-run all-pass
   toy-task sample with no live second judge does NOT advance any
   `stable` / auto-approval claim — the standing advisory-only
   status is unchanged by this PR.

**Review materials (all in this PR, no separate bundle needed):**

- This report: `eval/results/evaluator-calibration-2026-10-29.md`
- Per-run evaluator scorecards with per-dimension evidence:
  `eval/results/evaluator-calibration-2026-10-29-scorecards/`
  (36 JSON files, one per B2 run; each passes
  `eval/evaluate.py check`)
- Sources for every claim: run records
  `eval/results/t9-multi-file_*_rep*.json`,
  `t10-hidden-boundary_*_rep*.json`, `t11-resume_*_rep*.json`,
  `t12-ambiguous-decision_*_rep*.json`; task specs
  `eval/tasks/<task>/task.md`; fixture `eval/fixture/`; preserved
  run dirs `/tmp/bench/<task>/<arm>/rep<n>` (outside the repo;
  re-run evidence was collected from them this night); B2 report
  `eval/results/b2-2026-10-29.md` (caveats 1–3); existing
  calibration `eval/calibration.md` (rounds 1–5).

## 8. Limitations (read before citing any number from this report)

1. No live second judge; no independent human per-dimension scores
   exist in the repo (N = 0). "100% verdict agreement" here means
   agreement with recorded acceptance outcomes, not with human
   judgement.
2. Ceiling sample: 36/36 pass, 0 false completions, 0
   interventions. Block/Revise discrimination is untested by this
   round.
3. Toy tasks (tinycalc) on a sandbox without system pytest. Per
   D28 this sample cannot support a `stable` claim, and this report
   makes none.
4. Reliability rests on a single re-run per run; scope for pack/gate
   arms rests on task-relevant files (deploy scaffolding excluded
   by design); t12 decision ordering is unprovable from the final
   tree; one t10 deviation is unattributed.
5. Durations were not used in scoring (B2 report caveat 2: not
   comparable across tasks) and no cost/token claim is made.
6. B2 run dirs live in `/tmp/bench/` and may not survive a VM
   replacement; the scorecards + this report are the durable
   record, but a future re-run of acceptance from scratch would
   need those dirs (or a fresh bench run).

## 9. Verification note — independent second pass, same night (no new scores)

This report was drafted during the paused night session and left
uncommitted on branch `night/eval-calibration`. Before this PR was
opened, a second pass re-checked it against the repo rather than
trusting the draft:

- Recomputed from the 36 scorecard JSONs: dimension distribution
  (correctness 36×2; verification 18×2/18×1; scope 36×2;
  reliability 36×2; maintainability 36×2; handover 35×2/1×1),
  totals (17×12, 19×11), verdicts (36×Accept), and agreement
  against each scorecard's `source_record` (36/36 pass with
  `false_completion` 0). No scorecard was changed.
- Re-ran acceptance independently for 4 sample runs:
  t10 bare rep1 (literal commands, pass), t9 bare rep1 (venv
  pytest + remaining literal steps, pass — the `remainder 10 0`
  step fails as required), t11 gate rep1 (venv pytest, 3 passed;
  `gate/feature_list.json` still shows t11-resume `in_progress`,
  matching B2 caveat 1), t12 pack rep1 (literal commands, pass).
- Diffed t9 bare rep1 against `eval/fixture/`: only the task
  change (README, calc.py, cli.py, tests/test_calc.py) — scope 2
  confirmed for that run; t12 pack rep1's DECISIONS.md carries the
  scale reasoning the report cites.
- Confirmed B2 caveats 1, 3 and 4 verbatim in
  `eval/results/b2-2026-10-29.md` (t11 gate `in_progress`,
  t10 pack rep2 docs-sync deviation + unattributed AGENTS.md read,
  system python3 lacks pytest), and the inventory counts
  (72 bench records, 12 ablation, 13 t5–t8 merge-round records).
- `python3 eval/evaluate.py check` passes on all 36 scorecards;
  `evaluate.py --gate` on a 12/12 card exits 2 with GATE REFUSED
  (advisory-only, D28). `python3 tests/repo_checks.py` fails only
  on the known sandbox baseline `eval:bench-smoke-passes`
  (system python3 lacks pytest); no other check fails with these
  files added. `eval/evaluate.py`, `eval/rubric.md`,
  `eval/rubric-status.json` and `eval/calibration.md` are
  unmodified in this PR (only the two new paths below are added).
- Usage guardrail at start of this pass: 32% of the free weekly
  limit (resets Nov 1, 6:08 PM CST), below the 85% stop line.

What this second pass did NOT do: it did not re-score all 36 runs
from scratch, did not run a live second-judge round, and did not
apply rubric suggestions S1–S3. Those remain open for the user
(§7).
