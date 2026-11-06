# SESSION_NOTES — working notes (NON-AUTHORITATIVE)

> **This file is not a source of truth.** It is the Track-B working
> notes layer of the two-track state design
> (`docs/design-docs/proposal-state-two-track.md`, adopted 2026-11-06,
> DECISIONS D73). Facts live in Track A: `gate/feature_list.json` and
> `docs/internal/SESSION_STATE.md`. Anything here that turns out to
> matter must be **promoted** into Track A, `DECISIONS.md`, or a plan
> document — promotion is a deliberate act, never automatic.

Rules:
- Append-friendly; newest entries at the top.
- Only the most recent **100 lines** of this file are what a
  session-start surface may quote; older material is archive, read on
  demand only, never injected wholesale.
- Never record gate state here (status, evidence, blockers of record) —
  that is Track A's job, and a second copy will drift.

## Notes

- 2026-11-06 — CI first run lesson: an unpinned linter in CI is a
  time bomb — markdownlint-cli >=0.33 changed MD024/MD004 semantics
  and reddened a repo that was green under 0.32.2. Pin tool versions
  in workflows; treat "CI was never run" debt as compounding.
- 2026-11-06 — File created with the two-track adoption. First use:
  parking spot for observations during the v0.7.0 release round that
  do not yet deserve a plan entry.
