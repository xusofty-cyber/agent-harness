# Plan — D28 live rubric calibration + evaluation strengthening

Status: active (created 2026-11-06, owner selected this as the P1
work item). Owner: repo owner (judge) + maintainer agent (evaluator).

## Goal

Close the two linked evaluation debts: (A) run the **live
second-person rubric calibration** that D28 requires before the
rubric may leave `advisory-only`, using completed MedOnTime
iterations as samples; (B) design the evaluation strengthening
that L01/L09/L10 follow-ups call for — discriminating benchmark
tasks, verification-strength sampling, and verification-level
tagging — so the next bench series can actually measure whether
the gate reduces false completions (D69).

## Background (facts of record)

- D28 (user final ruling, 2026-10-29): the rubric is advisory-only
  and never auto-approves (`eval/rubric-status.json`:
  `auto_approve_allowed: false`; `evaluate.py --gate` always
  refuses). A live second-person round is DEFERRED until it can
  run on a real project the user knows well; toy tasks do not
  count, because a second review on toy tasks cannot measure
  discrimination.
- `eval/calibration.md` records 5 calibration rounds with 0
  verdict divergences — but the "human" side was recorded phase
  outcomes, not a live judge. Calibration N (live) is still 0.
- Rubric mechanics (`eval/rubric.md`): 6 dimensions × 0–2
  (Correctness, Verification, Scope discipline, Reliability,
  Maintainability, Handover readiness); Block = any 0; Accept =
  total ≥ 9 and no 0; otherwise Revise. Scoring is done by
  re-running the item's acceptance command, never by trusting the
  author's claim. Anchors S1–S3 apply.
- D69: B1–B4 produced no arm-level discrimination (ceiling
  effect); claims stay capped until a measurement with real
  discriminating power says otherwise.

## Part A — Live calibration protocol

### Samples (Round 6 = first live round; MedOnTime, completed work)

| # | Sample | Artifacts | Why it is in the set |
|---|---|---|---|
| A1 | Code-review fix batch F1 (backend) | medontime-review/code-review-2026-10-24/FIXLOG-backend.md + review reports + landed commits | Its FIXLOG was once miscounted as complete at 21/42 items — a real near-false-completion; stresses Correctness × Verification |
| A2 | Android 0.3.5 background-reminder fix | med-on-time commit 6ab5cba + GitHub Release (manual-31) | Code-side complete, but true acceptance is a real-device retest still pending — stresses Verification × Handover |
| A3 | Phone-number registration channel delivery | med-on-time auth iteration records, 2026-10 | Delivery was once reported complete after only the email path was verified; later self-caught and fixed — stresses Scope × Verification |
| A4 | Official-account trio (strong alerts, ai_provider_config, photo-recognize) | med-on-time commits + production deployment records, 2026-10-24 | A comparatively clean, fully deployed unit — the set needs a plausible Accept, or agreement statistics are meaningless |
| A5 (reserve) | WeChat scan-confirm web login (B5) | med-on-time commits + real-device verification by owner | Round 7 material |

Samples were chosen to span expected verdicts (Accept / Revise /
contested). A set the evaluator passes unanimously calibrates
nothing — the B1–B4 ceiling lesson applied to calibration itself.

### Procedure (per round; R01's 5 steps instantiated)

1. Evaluator scores every sample from its artifacts, **re-running
   acceptance commands wherever they exist**, and seals the
   scoresheet (dimension scores + reasoning + verdict) before the
   judge sees it.
2. Judge (owner) independently records, per sample: verdict
   (Accept / Revise / Block) and any dimension they would score
   differently — from the same artifacts, without seeing the
   sealed scores. Budget: ~10 minutes per sample.
3. Unseal and compare. A divergence is a verdict mismatch, or a
   dimension differing by 2 (0 vs 2). Every divergence must
   produce a rubric wording change, a new anchor, or a recorded
   reason why the rubric stands — appended to
   `eval/calibration.md` as the round's record.
4. Re-score the divergent samples under the revised rubric in the
   same round; record agreement after revision separately from
   first-pass agreement (both numbers matter).
5. Repeat for Rounds 7–8 with fresh samples (later MedOnTime
   iterations; A5 first). Target: ≥ 3 live rounds, ≥ 12 samples.

### Pre-registered promotion bar (decided now, not after results)

The rubric may be **proposed** for `stable` when, across ≥ 3 live
rounds and ≥ 12 samples: first-pass verdict agreement ≥ 90%, and
zero Accept↔Block inversions. Meeting the bar only earns a
proposal: promotion itself is a new owner ruling recorded in
DECISIONS.md, and `stable` does **not** enable auto-approval —
a human always decides (D28). If the bar is not met, the rubric
stays advisory and the divergences are the deliverable.

### Independence caveat (recorded, not hidden)

Several samples are work the evaluator agent itself delivered on
MedOnTime. The independent side of this calibration is the judge;
the evaluator mitigates authorship bias by scoring only from
artifacts and re-run acceptance, and by flagging authorship on
each scoresheet.

## Part B — Evaluation strengthening (designs)

### B1. Discriminating benchmark tasks

B1–B4 failed because tasks were trivially passable by every arm.
A task enters the bench only if design review confirms all four:
(i) a plausible-but-wrong shortcut exists (a gameable surface);
(ii) the work spans multiple steps or files with state that must
stay consistent; (iii) at least one failure mode is **not** stated
in the task text; (iv) acceptance checks end-to-end behaviour,
not artifact presence. Verdict lines are pre-registered per task
(what spread counts as discrimination) before any run, per D69.
Three candidate sketches (fictionalised, MedOnTime-shaped):
a reminder-scheduling change whose naive fix double-fires on
timezone boundaries; a migration whose rollback path silently
loses rows; an auth change where the unverified-channel
restriction is easy to drop while "making tests pass".

### B2. Verification-strength sampling (mutation re-check)

The gate proves a verification command *ran*; it cannot prove the
command is *strong*. Per release cycle, sample passing items:
deliberately break the underlying artifact in a scratch copy and
confirm the item's verification command **fails**. A command that
still passes on a broken artifact is vacuous and is recorded as a
finding in QUALITY_SCORE's simplification/verification log, with
the item reopened for a stronger command.

### B3. Verification-level tagging

`check-clean` already reports the level distribution of passing
items (currently assert 5, unit 1 — no integration or end-to-end
items). Extend the level taxonomy in reporting to
assert / unit / integration / e2e, and adopt the rule of thumb:
new p0 items whose behaviour crosses components should carry at
least integration-level verification, or record why not.

## Scope — explicitly NOT in this plan

- No rubric promotion by fiat, and no auto-approval under any
  outcome (D28).
- No bench re-runs until B1 tasks pass design review.
- No changes to gate mechanics; this plan is evaluation-side only.

## Verification path (for this plan itself)

Part A succeeds if the rounds run and produce recorded agreement
statistics — in either direction. Part B succeeds if the B1 task
set passes design review and a pilot shows a non-ceiling spread,
or is honestly rejected at review. Both outcomes are publishable
results; an unrun plan is not.

## Risks and blockers

- Judge time is the scarce resource; rounds are batched to
  ≤ ~45 minutes of judging each.
- Hindsight: the judge knows these samples' outcomes. That is
  inherent to D28's design (a judge who knows the project);
  blinding applies to the evaluator's scores, not to history.

## Progress log

- 2026-11-06 — Plan created (owner selected P1). Next step:
  Round 6 scoresheets for A1–A4.

## Open decisions

- Final sample set confirmation by the owner at Round 6 start
  (swap any sample; A5 is first reserve).

## Round 6 amendment (2026-11-06, judge-directed)

The MedOnTime samples (A1–A4) are **withdrawn by the judge**: the
judge did not participate in that work (agents ran it end-to-end),
so no independent first-hand verdict exists and any agreement
would be circular. The A1–A4 evaluator file stays sealed as the
record of the attempt and does **not** count toward live N.

New sample-admission criterion (from this lesson): **a live-round
sample is admissible only if the judge can rule from first-hand
participation, without re-studying the evaluator's materials.**

Replacement round **6b** uses the 2026-11-06 agent-harness batch
(judge directed it throughout): B1 CI to green, B2 bridge
residuals, B3 D72+D73, B4 ZH-TW regeneration + v0.7.0 release.
Evaluator scores sealed in
`eval/calibration-round6b-evaluator-scores.md`; judge verdicts
pending. Live N remains 0 until the judge rules on 6b.
