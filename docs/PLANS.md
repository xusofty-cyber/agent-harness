# Plans — lifecycle rules

Execution plans for this repository live in `docs/exec-plans/`:

- `active/` — plans currently being executed (one clear current step
  each; a plan file is updated as work proceeds, not written once as
  static prose).
- `completed/` — finished plans, moved here on completion and kept
  for their historical context.
- `tech-debt-tracker.md` — deferred work with an explicit reason and
  a named re-trigger condition.

## When a plan is required

A plan file is required when any of these holds: the work spans
multiple sessions; it touches multiple subsystems; its verification
or release risk is non-trivial; or it carries an open decision.

## Minimum contents

Goal; scope including what is explicitly **not** in scope;
verification path; risks and blockers; a progress log; open
decisions. On completion, record the verification evidence (or a
link to it) before moving the plan to `completed/`.

## Relation to older records

Development records written before 2026-11-06 were migrated here
from `docs/internal/` on 2026-11-06 (owner decision), with every
inbound reference — docs, tests and tools — updated in the same
change and the full check suite re-run. Two exceptions stay in
`docs/internal/`: `phase1-dogfood.md` and
`dogfood-2026-10-29.md`, whose paths are asserted by live gate
verification commands and cited in the gate's hash-chained event
log; moving them would require rewriting gate evidence. New plans
and verification reports are written under `docs/exec-plans/`.
The gate's own feature list (`gate/feature_list.json`) remains the
machine-readable tracker for gate-scoped items; plans here cover
the wider work around it.
