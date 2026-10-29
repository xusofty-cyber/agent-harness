# Evaluator rubric — agent-harness (Phase 3)

Six dimensions, each scored 0–2 with anchored descriptions. The rubric is
applied to a finished work item (a benchmark run, a dogfood run, or a
completed phase task) **by re-running its acceptance command**, never by
trusting the agent's claim that it passed. (That rule comes from Phase 1
dogfood-1: the planted fake pass was well-formed JSON — only re-running the
verification caught it.)

## Dimensions

| # | Dimension | 2 — good | 1 — partial | 0 — fail |
|---|---|---|---|---|
| 1 | Correctness | The change does exactly what the task asked, no more, no less | Does the asked thing but with a side effect, or misses an edge the task named | Does not do the asked thing, or breaks existing behaviour |
| 2 | Verification | Acceptance command re-run by the evaluator exits 0; evidence matches the re-run output | Acceptance passes but evidence is incomplete or was not re-run | Acceptance fails on re-run, or no evidence exists |
| 3 | Scope discipline | Only files the task touches are changed | One unrelated file touched, or one unrelated change inside a touched file | Unrelated features, refactors, or files changed |
| 4 | Reliability | The result is deterministic: re-running the acceptance gives the same outcome; no flakiness observed | Works but depends on ordering, timing, or environment quirks | Flaky, or passes only in the author's environment |
| 5 | Maintainability | The change follows the repo's existing conventions and is readable by the next session | Works but ignores a convention, or needs a comment it lacks | Introduces a pattern the repo forbids, or is unreadable without the author |
| 6 | Handover readiness | A new session can continue from SESSION_STATE / the run record alone, within the 5-minute budget | Continuable, but needs one clarification or one re-read of the diff | A new session cannot tell what was done, what is next, or what is blocked |

## Anchor notes (user-accepted 2026-10-30, advisory-only)

- **S1 — Verification, equivalent interpreters.** When the sandbox lacks a required interpreter, re-running under a named equivalent interpreter is verification 1 (not 2), and the interpreter must be named in the evidence. Exception (user ruling V-1, 2026-10-30): where the equivalent interpreter is ruled fully equivalent to the required interpreter for that sandbox, the re-run counts as verification 2; the 18 t9/t11 runs of the 2026-10-29 calibration were rescored on this basis. S1 remains the default anchor; V-1 is a case-specific ruling for those runs, not a repeal of S1.
- **S2 — Handover, record omissions.** A run record that omits a known deviation — even one that does not change acceptance — caps handover at 1.
- **S3 — Reliability, single re-run honesty.** A single matching re-run is weak determinism evidence; a reliability 2 from one re-run should be read as "no flakiness observed", not "proven deterministic".

## Verdict

- **Block** — any dimension scores 0.
- **Revise** — no 0, but total < 9.
- **Accept** — total ≥ 9 and no dimension scores 0.

Total range is 0–12. The verdict rule is deliberately strict on zeros: a
single failing dimension blocks, however good the rest is.

## Calibration

The rubric is **standing advisory-only** (user final ruling 2026-10-29,
D28, aligned with yunkai D-011): it provides advisory opinions only and
never auto-approves — a human always decides. 5 calibration rounds are
recorded in `eval/calibration.md` (evaluator score vs. known outcome,
divergences and wording fixes); those rounds used recorded phase
outcomes as the "human" side (no live second judge was available — see
`eval/calibration.md` for that limitation). A live second review is
DEFERRED, not owed: it runs only when conditions mature, and it must
run on a real project the user knows well — bench toy tasks do not
count, because a second review on toy tasks cannot measure
discrimination. Only if such a round actually runs and consistency
meets the bar may `stable` and auto-approval be reconsidered. Until
then, every scored item must also carry the evaluator's reasoning per
dimension.

## What the rubric does NOT do

- It does not measure token cost (no host exposes a programmatic token
  API — see `docs/internal/token-adapters.md`). Cost is tracked via the
  Phase 2 proxy metrics (runs, duration, verify failures, interventions).
- It does not replace the gate: `pass-gate.py verify` is the runtime check;
  the rubric is the retrospective judgement of a finished item.
