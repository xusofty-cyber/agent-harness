#!/usr/bin/env python3
"""Round-based maker for the Phase 5 Maker-Checker demo (docs/internal/phase5).

The artifact is templates/loop/graph.template.md, built up round by round
in the maker's working directory (cwd — the loop runner sets it to
<loop-root>/maker). Each round applies one real revision; the checker
fails the round until its findings are addressed:
  round 1 — draft: nodes / edges / shared state / routing only
             (timeout, approval detail, merge rule all TBD)
  round 2 — timeout rule (60 s) + routing rules
  round 3 — approval node completed
  round 4 — fan-out / fan-in merge rule ("all must pass")
  round 5+ — no-op (checker re-runs; consecutive passes stop the loop)

Edits are exact-string replacements (asserted), so a round that cannot
apply its revision fails loudly instead of silently passing.
"""

import os
import sys

DRAFT = """# Graph — Maker-Checker demo (graph template under construction)

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

TBD

## Timeout

TBD

## Fan-out / fan-in

TBD
"""

ROUND2 = ("## Timeout\n\nTBD",
          "## Timeout\n\n- Per-command timeout: 60 seconds (runner-enforced; a timeout kills\n"
          "  the command and records a `timeout` event).\n"
          "- Wall-clock budget: 600 seconds (0 = none); exceeding it records a\n"
          "  `budget_exceeded` event and fails the loop.")

ROUND3 = ("## Approval\n\nTBD",
          "## Approval\n\n- What happened: the loop reached its pass condition at round 4\n"
          "- What changed: templates/loop/graph.template.md (this file)\n"
          "- Why human: adopting a new template into the repo needs a person —\n"
          "  the runner can verify shape, not whether the graph is the right contract\n"
          "- Approve: the graph template is adopted; fan-in proceeds\n"
          "- Reject: the loop returns to the maker; the rejection is recorded as an event")

ROUND4 = ("## Fan-out / fan-in\n\nTBD",
          "## Fan-out / fan-in\n\n- Fan-out: this graph template was built by a Maker-Checker loop whose\n"
          "  maker and checker ran in isolated directories; the sibling Goal Loop\n"
          "  ran in a separate git worktree\n"
          "- Merge rule: all must pass — every branch's final verify must pass\n"
          "  before fan-in\n"
          "- Fan-in: copy each branch's changed files into the main clone, re-run\n"
          "  repo_checks, commit per branch")


def main():
    rnd = int(os.environ.get("LOOP_ROUND", "1"))
    path = os.path.join(os.getcwd(), "graph.template.md")
    if rnd == 1:
        with open(path, "w", encoding="utf-8") as f:
            f.write(DRAFT)
        print("maker-graph: round 1 — draft written (timeout/approval/fan-out TBD)")
    elif rnd == 2:
        text = open(path, encoding="utf-8").read()
        assert ROUND2[0] in text, "round 2 anchor missing"
        open(path, "w", encoding="utf-8").write(text.replace(ROUND2[0], ROUND2[1], 1))
        print("maker-graph: round 2 — timeout rule added")
    elif rnd == 3:
        text = open(path, encoding="utf-8").read()
        assert ROUND3[0] in text, "round 3 anchor missing"
        open(path, "w", encoding="utf-8").write(text.replace(ROUND3[0], ROUND3[1], 1))
        print("maker-graph: round 3 — approval node completed")
    elif rnd == 4:
        text = open(path, encoding="utf-8").read()
        assert ROUND4[0] in text, "round 4 anchor missing"
        open(path, "w", encoding="utf-8").write(text.replace(ROUND4[0], ROUND4[1], 1))
        print("maker-graph: round 4 — fan-out merge rule added")
    else:
        print(f"maker-graph: round {rnd} — no-op (nothing left to change)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
