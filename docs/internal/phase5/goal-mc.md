# Goal — graph template that passes the checker

> **Owner**: repo owner (user) | **Loop**: Maker-Checker (`tools/loop.py maker-checker`)
> **Created**: 2026-10-28 | **Status**: running
> **Rule**: the maker revises `templates/loop/graph.template.md` one round
> at a time; the checker sees only the artifact, copied fresh each round
> into `checker/`. A round passes only when the checker command actually
> exits 0. After the pass condition is met the loop pauses for human
> approval — adopting a new template needs a person.

## Goal

- `templates/loop/graph.template.md` passes every checker item:
  graph-validate OK, ≥6 node rows, timeout ≤ 300 s, merge rule
  "all must pass".

## Verification

- Command: `python3 docs/internal/phase5/checker-graph.py`
  (run by the runner in the isolated checker directory)
- What counts as pass: all four checker items print PASS.
- What counts as fail: any item FAIL, timeout, or missing artifact.

## Stop conditions

- Max rounds: 5
- Consecutive passes to stop: 2
- Per-command timeout: 60 seconds
- Wall-clock budget: 600 seconds
- Human approval required: yes — after the pass condition, the loop
  pauses in `awaiting-approval`; `loop.py approve` resumes it.

## Constraints

- The maker only revises the graph template artifact; it never writes
  the checker's verdict. The checker never edits the artifact.
- The final template must match `templates/loop/graph.template.md`
  structure (nodes / edges / shared state / routing / approval /
  timeout / fan-out).

## Rounds

- (filled in from `loop-state.json` after the run — see
  `docs/internal/phase5-loops.md`)
