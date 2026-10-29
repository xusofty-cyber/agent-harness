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

## Verdict

- **Block** — any dimension scores 0.
- **Revise** — no 0, but total < 9.
- **Accept** — total ≥ 9 and no dimension scores 0.

Total range is 0–12. The verdict rule is deliberately strict on zeros: a
single failing dimension blocks, however good the rest is.

## Calibration

The rubric is **provisional** until 3–5 calibration rounds are recorded in
`eval/calibration.md` (evaluator score vs. known outcome, divergences and
wording fixes). Only after calibration may the rubric be marked `stable`;
before that, every scored item must also carry the evaluator's reasoning
per dimension. Calibration rounds in this session used recorded phase
outcomes as the "human" side (no live second judge was available — see
`eval/calibration.md` for that limitation).

## What the rubric does NOT do

- It does not measure token cost (no host exposes a programmatic token
  API — see `docs/internal/token-adapters.md`). Cost is tracked via the
  Phase 2 proxy metrics (runs, duration, verify failures, interventions).
- It does not replace the gate: `pass-gate.py verify` is the runtime check;
  the rubric is the retrospective judgement of a finished item.
