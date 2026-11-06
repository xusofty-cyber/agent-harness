# Proposal — Two-track state (authoritative layer + notes layer)

Status: **accepted and implemented** (2026-11-06, DECISIONS D73):
`docs/internal/SESSION_NOTES.md` created with the header + 100-line
quote cap; SESSION_STATE header now restricts it to Track-A content;
ARCHITECTURE.md notes the split. No auto-summarisation (non-goal
stands).
Origin: D02 (Claude Code's CLAUDE.md vs auto-memory split) and D01
(summary chains), against this repo's recurring state problem:
SESSION_STATE carries both authoritative breakpoints and working
notes, which is part of why it rots (found stale twice here, and
in MedOnTime at 324 lines).

## Design

- **Track A — authoritative state** (gate-adjacent, low churn):
  `gate/feature_list.json` (gate-owned, unchanged) and
  `docs/internal/SESSION_STATE.md` restricted to breakpoint facts:
  goal, in-progress, next, blocked, last verification. The 14-day
  freshness rule (repo_checks, 2026-11-06) applies to this track.
- **Track B — working notes** (agent-writable, explicitly
  non-authoritative): a new `docs/internal/SESSION_NOTES.md`,
  append-friendly, with a hard load cap (e.g. most recent 100
  lines are what a session-start surface may quote) and a header
  stating it is not a source of truth. Anything in Track B that
  turns out to matter must be promoted into Track A, DECISIONS.md
  or a plan — promotion is a deliberate act, never automatic.
- Session-start surfaces quote Track A first; Track B is read on
  demand, never injected wholesale.

## Non-goals

No change to gate mechanics or the feature-list format. No
auto-summarisation pipeline in v1 (Pi-style summary chains are a
later candidate if Track B outgrows its cap in practice).

## Adoption path if accepted

1. Create SESSION_NOTES.md with the header + cap rule.
2. Trim SESSION_STATE guidance in its header comment to Track-A
   content only.
3. Note the split in ARCHITECTURE.md and the gate README.
