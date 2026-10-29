# Token adapters — inventory (Phase 2, 2-5)

Why there is no unified token ledger yet: a token ledger needs at least
one host that exposes **per-session token usage through a script-consumable
source** (CLI flag, local file, or API). As of 2026-10-28, none of the five
supported hosts does. This page is the inventory; when a host ships such a
source, add its adapter here first, then build the ledger on top of it.

## Inventory

| Host | Script-consumable token source? | Adapter status |
|---|---|---|
| Claude Code | None identified (usage is visible in the vendor dashboard / account page, not consumable by a script) | None — deferred |
| Codex | None identified | None — deferred |
| Antigravity | None identified | None — deferred |
| Copilot | None identified | None — deferred |
| Zed | None identified | None — deferred |

## What exists instead (proxy metrics)

`tools/cost-ledger.py` records deterministic proxy metrics that need no
token API: tool-call counts (PostToolUse hook), pipeline stage runs
(run-pipeline.sh/.ps1), verify failures and human overrides
(`gate/events.jsonl`). Budget caps live in `gate/cost-budget.json`; over
budget only alerts and records a `budget_exceeded` event — it never
auto-stops a run.

## Not an adapter

The usage guard's `subscription-status status` measures **this agent's own**
weekly Muse quota. It is not a per-project, per-host token feed and cannot
serve as a ledger adapter for target projects.

## Re-review trigger

Revisit this page when any host ships a script-consumable token source
(CLI `--usage`-style output, a local usage file, or a documented API), or
when a new host is added to the support matrix. Until then, the unified
token ledger stays deferred by design, not by omission.
