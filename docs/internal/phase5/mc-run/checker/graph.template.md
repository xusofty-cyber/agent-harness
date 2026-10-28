# Graph — Maker-Checker demo (graph template under construction)

> **Loop**: maker-checker | **Goal**: `docs/internal/phase5/goal-mc.md`

## Nodes

| Node | Kind | Owner | Description |
|---|---|---|---|
| maker | agent | loop-maker | Revises the graph template |
| verify | deterministic | runner | Runs the checker command, exit 0 = pass |
| timeout-enforcer | deterministic | runner | Kills a command past its timeout, records a timeout event |
| event-log | deterministic | runner | Appends one event per round/transition, never rewrites |
| approval | human | owner | Decides adopt vs send back (see Approval) |
| merge | deterministic | runner | Fan-in: only after the merge rule is met |

## Edges

| From | To | Condition |
|---|---|---|
| maker | verify | maker exits 0 |
| maker | maker | maker fails — next round revises |
| verify | approval | verify passes N consecutive rounds |
| verify | maker | verify fails or times out — next round revises |
| approval | merge | human approves |
| approval | maker | human rejects — next round revises |
| verify | human-escalation | max rounds reached without the pass condition |

## Shared state fields

- `loop-state.json`: kind, goal_id, status, round, consecutive_passes,
  max_rounds, timeout_s, max_seconds, rounds[] (one record per round)
- `loop-events.jsonl`: append-only, monotone seq; the audit trail
- `maker/` and `checker/`: working directories; the checker only ever
  sees the listed artifacts, copied fresh

## Routing rules

- A round passes only on verify exit 0; a timeout is a fail, recorded.
- Stop on N consecutive passes, on max rounds, or on wall-clock budget —
  whichever comes first. Stopping on max rounds or budget is a failure,
  not a completion.
- The maker never writes the checker's verdict; the checker never edits
  the artifact.

## Approval

- What happened: the loop reached its pass condition at round 4
- What changed: templates/loop/graph.template.md (this file)
- Why human: adopting a new template into the repo needs a person —
  the runner can verify shape, not whether the graph is the right contract
- Approve: the graph template is adopted; fan-in proceeds
- Reject: the loop returns to the maker; the rejection is recorded as an event

## Timeout

- Per-command timeout: 60 seconds (runner-enforced; a timeout kills
  the command and records a `timeout` event).
- Wall-clock budget: 600 seconds (0 = none); exceeding it records a
  `budget_exceeded` event and fails the loop.

## Fan-out / fan-in

- Fan-out: this graph template was built by a Maker-Checker loop whose
  maker and checker ran in isolated directories; the sibling Goal Loop
  ran in a separate git worktree
- Merge rule: all must pass — every branch's final verify must pass
  before fan-in
- Fan-in: copy each branch's changed files into the main clone, re-run
  repo_checks, commit per branch
