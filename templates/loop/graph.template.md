# Graph — <LOOP_NAME>

> **Loop**: <goal-loop | maker-checker> | **Goal**: `<goal.md path>`
> **Rule**: this graph is the contract. The runner enforces the timeout
> and stop conditions; a human enforces the approval node. If the graph
> and the runner disagree, the runner's event log wins — fix the graph.

## Nodes

| Node | Kind | Owner | Description |
|---|---|---|---|
| maker | agent | <maker> | Produces or revises the artifact |
| verify | deterministic | runner | Runs the verify/checker command, exit 0 = pass |
| timeout-enforcer | deterministic | runner | Kills a command past its timeout, records a timeout event |
| event-log | deterministic | runner | Appends one event per round/transition, never rewrites |
| approval | human | <approver> | Decides adopt vs send back (see Approval) |
| merge | deterministic | runner | Fan-in: only after the merge rule is met |

Kinds: `agent` (makes judgement calls), `deterministic` (same input,
same output — commands, checks, logs), `human` (approval only).

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
- `maker/` and `checker/`: working directories (maker-checker kind);
  the checker only ever sees the listed artifacts, copied fresh

## Routing rules

- A round passes only on verify exit 0; a timeout is a fail, recorded.
- Stop on N consecutive passes, on max rounds, or on wall-clock budget —
  whichever comes first. Stopping on max rounds or budget is a failure,
  not a completion.
- The maker never writes the checker's verdict; the checker never edits
  the artifact.

## Approval

- What happened: <the loop reached its pass condition at round N>
- What changed: <files the loop produced or modified>
- Why human: <why this needs a person, not the runner — e.g. "adopting a
  new repo check into the branch">
- Approve: <consequence — e.g. "fan-in proceeds, results are committed">
- Reject: <consequence — e.g. "loop returns to the maker, rejection is
  recorded as an event">

## Timeout

- Per-command timeout: 60 seconds (default — adjust to your loop;
  runner-enforced; a timeout kills the command and records a `timeout`
  event — verified by running a `sleep` longer than the timeout, see
  the phase record).
- Wall-clock budget: <N> seconds (0 = none); exceeding it records a
  `budget_exceeded` event and fails the loop.

## Fan-out / fan-in

- Fan-out: <parallel branches, each in its own git worktree, isolated
  directories, no shared files>
- Merge rule: <all must pass | any one passes> — every branch's final
  verify must pass before fan-in (all must pass), or one passing branch
  is enough (any one passes).
- Fan-in: <how branch results are merged back — e.g. "copy each branch's
  changed files into the main clone, re-run repo_checks, commit per branch">
