# Graph — Maker-Checker demo, graph template (Phase 5)

> **Loop**: maker-checker | **Goal**: `docs/internal/phase5/goal-mc.md`
> **Run**: 2026-10-28, worktree `/tmp/phase5-wt-mc` (detached HEAD `7661bb5`)
> **Result**: complete at round 5/5, 2 consecutive passes, human approval
> recorded. State + events: `docs/internal/phase5/mc-run/`.
> This is the worked example of `templates/loop/graph.template.md` — the
> template with this run's real values filled in.

## Nodes

| Node | Kind | Owner | Description |
|---|---|---|---|
| maker | agent | loop-maker (scripted: `maker-graph.py`) | Revises the graph template, one round at a time |
| verify | deterministic | runner (`tools/loop.py`) | Runs the checker command, exit 0 = pass |
| timeout-enforcer | deterministic | runner | Kills a command past its timeout, records a timeout event |
| event-log | deterministic | runner | Appends one event per round/transition, never rewrites |
| approval | human | owner | Decides adopt vs send back (see Approval) |
| merge | deterministic | runner | Fan-in: only after the merge rule is met |

## Edges

| From | To | Condition |
|---|---|---|
| maker | verify | maker exits 0 |
| maker | maker | maker fails — next round revises |
| verify | approval | verify passes 2 consecutive rounds |
| verify | maker | verify fails or times out — next round revises |
| approval | merge | human approves |
| approval | maker | human rejects — next round revises |
| verify | human-escalation | max rounds (5) reached without the pass condition |

## Shared state fields

- `loop-state.json`: kind=maker-checker, goal_id=mc-graph-template,
  status, round, consecutive_passes, max_rounds=5, timeout_s=60,
  max_seconds=600, rounds[] (10 records: maker+verify per round)
- `loop-events.jsonl`: append-only, monotone seq 0–12 (init,
  artifacts_copied ×5, round ×5, approval_requested, approved)
- `maker/` and `checker/`: working directories; the checker only ever
  saw `graph.template.md`, copied fresh each round (verified: the
  checker dir contained exactly that one file)

## Routing rules

- A round passes only on checker exit 0; a timeout is a fail, recorded.
- Stop on 2 consecutive passes, on max rounds (5), or on wall-clock
  budget (600 s) — whichever comes first. Stopping on max rounds or
  budget is a failure, not a completion.
- The maker never writes the checker's verdict; the checker never edits
  the artifact.

## Approval

- What happened: the loop reached its pass condition at round 5
  (rounds 4 and 5 both passed the checker)
- What changed: `templates/loop/graph.template.md` (content refined over
  5 rounds) and the loop record in `docs/internal/phase5/mc-run/`
- Why human: adopting a new template into the repo needs a person — the
  runner can verify shape, not whether the graph is the right contract
- Approve: the graph template is adopted; fan-in proceeds (recorded as
  `approved` by owner, round 5)
- Reject: the loop returns to the maker; the rejection is recorded as an event

## Timeout

- Per-command timeout: 60 seconds (runner-enforced; a timeout kills the
  command and records a `timeout` event). Verified separately: a verify
  command of `sleep 30` with timeout 2 was killed at 2.005 s, rc=124,
  `timed_out=True`, round outcome `timeout` — see `docs/internal/phase5-loops.md`.
- Wall-clock budget: 600 seconds; exceeding it records a
  `budget_exceeded` event and fails the loop even if the round just
  passed (verified: maker `sleep 5` with budget 1 s → `budget-exceeded`,
  exit 1 — the budget check runs before the pass check).

## Fan-out / fan-in

- Fan-out: two independent loop demos ran in parallel in separate git
  worktrees (detached HEAD `7661bb5`): Goal Loop in `/tmp/phase5-wt-goal`,
  Maker-Checker in `/tmp/phase5-wt-mc`. Isolated directories, no shared
  files; both worktrees started from the same base commit.
- Merge rule: all must pass — both loops' final verify had to pass
  before fan-in (Goal Loop: complete round 3/5; Maker-Checker: complete
  round 5/5 + approval).
- Fan-in: each worktree's changed files were copied into the main clone,
  re-verified (`verify-goal.sh`, `pass_gate_test.py`, `graph-validate`,
  `loop.py status` on both runs), then committed per branch:
  `phase5(5-1)` (Goal Loop) and `phase5(5-2)` (Maker-Checker).
  Worktrees removed after fan-in.
