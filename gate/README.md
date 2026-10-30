# gate/ — the self-owned verification gate (Phase 1)

The gate is the part of agent-harness that makes "done" checkable. It is
small on purpose: a JSON state machine, one stdlib-only Python script, two
Claude Code hooks, and an append-only log. It does not run your model
loop, schedule work, or call any vendor CLI. Comet is an optional adapter
elsewhere in this repo; the gate works with or without it (D1).

## Files

| File | What it is |
|---|---|
| `feature_list.schema.json` | JSON Schema for the feature list: statuses, required fields, allowed transitions, WIP=1, evidence-required-for-passing |
| `pass-gate.py` | The gate. Stdlib only. Reads the list, runs verification commands, moves items, writes evidence, appends events |
| `init.template.sh` | Scaffold a project for the gate (feature list, clean-state config, SESSION_STATE, DECISIONS) + one smoke run |
| `feature_list.json` | **This repo's own list** (dogfood). Per-project state; deployed targets create their own via `init` — deploy never copies this file |
| `clean-state.json` | Build/test/start commands for `check-clean` (this repo's own) |
| `events.jsonl` | Append-only event log. Every transition lands here |

The schema lives in `gate/`; the human template lives in
`templates/feature_list.template.json`.

## The loop

```console
pass-gate.py add --id <id> --title "..." --behavior "..." --command "<verify>"
pass-gate.py start --id <id>        # WIP=1: one item in_progress at a time
... do the work ...
pass-gate.py verify --id <id>       # runs the command; exit 0 -> passing + evidence
pass-gate.py verify --all           # verify everything in_progress
pass-gate.py block --id <id> --reason "..."   # stuck? say so, don't fake it
pass-gate.py reopen --id <id> --reason "..."  # passing was wrong; reason required
pass-gate.py status                 # what is where
pass-gate.py check-clean            # five-dimension handover check
pass-gate.py events --last 20       # what happened
```

An item may enter `passing` only with evidence: the command that ran,
its exit code (0), when it ran, and the tail of its output. `passing` is
irreversible except through `reopen`, which clears the evidence and
requires a reason. The verification command is the definition of done —
if it does not actually prove the behaviour, the gate is a ritual, not a
check. Write the command first, then the code.

**Verification level (v0.4.1, D66).** `verification.level` optionally
records how strong the proof is: `assert` (text/existence assertion) <
`unit` < `integration` < `e2e`. It is descriptive, never a gate —
`check-clean` dimension 3d reports the passing mix by level (this repo
currently reads `assert 5, unit 1`, which is honest for docs changes
and a warning sign for feature work), and `pass-gate.py add --level`
sets it at creation. An item without a level is reported as
`unspecified`. The point is visibility: a `passing` proved by `grep`
must not look identical to one proved end-to-end (course L10).

## Clean-state (handover check)

`check-clean` runs the five course dimensions; the progress dimension
has two checks (3a narrative, 3b machine-readable truth):

1. **build** passes — `gate/clean-state.json: build`
2. **tests** pass — `clean-state.json: test`
3. **progress recorded** — (a) `SESSION_STATE.md` names the in_progress
   item; (b) every `passing` item's verification still exits 0 on re-run
4. **temp artefacts cleaned** — no `*.tmp` / `*.bak*` / `__pycache__` /
   `*.log` in `git status`
5. **standard start path works** — `clean-state.json: start`

A dimension with no command configured reports SKIP, not PASS. Any FAIL
means: do not hand off yet.

## Anti-tamper: defence in depth, not a guarantee

An agent can always rewrite a JSON file. The gate does not pretend
otherwise. Three legs raise the cost of faking a pass and leave a trace:

1. **PreToolUse hook** (`.claude/hooks/guard-feature-list.mjs`): direct
   Write/Edit to any `feature_list.json` is denied (exit 2). The only
   writer is `pass-gate.py`, invoked through Bash. **Claude Code only** —
   other hosts have no such hook; on them this leg does nothing.
2. **CI second check** (`tests/repo_checks.py` §3k): for every `passing`
   item, CI re-runs the verification command and requires exit 0 *now*,
   and requires a `verified`/`override` event for the item. A hand-edited
   evidence block with invented output is caught here. This leg runs at
   review time, not at run time.
3. **Event log** (`gate/events.jsonl`): every transition is appended with
   a monotonic sequence number and committed to git, so rewriting history
   shows up as a diff. It cannot stop a rewrite; it makes one visible.

Known gaps (recorded honestly, not fixed by pretending):

- A direct edit through Bash (`sed`, `python`, heredoc) bypasses leg 1
  entirely and leaves no event — leg 2 is the only catch, and only at CI
  time. This was demonstrated in dogfooding: a fake pass planted by
  hand-edit had no event; CI §3k caught it anyway.
- Leg 2 re-runs verification commands, so a slow or flaky command makes
  CI slow or flaky. Keep verification commands fast and hermetic.
- `events.jsonl` seq numbers are monotonic, not gapless; a deleted line
  is detectable only by a missing seq number, which CI flags as
  "seq not increasing" only if the order breaks — a clean deletion of the
  *last* lines is not detectable from the file alone. Git history is the
  backstop: compare against the last reviewed commit.

## Session lifecycle hooks (Phase 2, 2-3)

Besides the gate hooks above, two lifecycle hooks complete the set
(all five Claude Code hook events are now wired in `.claude/settings.json`):

- **SessionStart** (`.claude/hooks/session-start.mjs`): when a session
  starts in a project with a gate, it prints a compact resume — item
  counts, in_progress/blocked items, and the first lines of
  `SESSION_STATE.md`. No gate state means silence, never an error.
- **PostToolUse** (`.claude/hooks/post-tool-use.mjs`): appends one JSON
  line per tool call to `gate/cost-ledger.jsonl` (tool name + timestamp) —
  the raw material for the cost ledger's proxy metrics
  (`tools/cost-ledger.py`). It only records when `gate/` exists, and
  `COST_LEDGER=0` disables it entirely. The ledger is local telemetry and
  is gitignored (unlike `feature_list.json`/`events.jsonl`, which are
  reviewable evidence and committed per D8).
- **Stop** (`.claude/hooks/stop-gate.mjs`, Phase 1): blocks stopping while
  any item is `in_progress`, with the logged human override channel.

All three are Claude Code only — other hosts have no hook events, so on
them these legs do nothing. Every hook is fail-open: a parse failure or
an unreadable state file logs to stderr and exits 0.

## Cost ledger (Phase 2, 2-5)

The ledger records deterministic **proxy metrics** — it is not a token
ledger (no host exposes a programmatic token API; see
`docs/internal/token-adapters.md`):

- `gate/cost-ledger.jsonl`: one line per PostToolUse tool call (hook) and
  one line per pipeline stage (`run-pipeline.sh`/`.ps1`, only when the
  target has a `gate/`). Local telemetry, **gitignored**.
- `gate/cost-budget.json`: per-day caps (runs, tool calls, verify
  failures, overrides) + a per-stage duration cap. Created by
  `python3 tools/cost-ledger.py init-budget` (never overwrites). This file
  is policy, so it **is** committed with the project.
- `python3 tools/cost-ledger.py summary [--json]`: aggregates the ledger
  plus `gate/events.jsonl` (verify_failed / override counts).
- `python3 tools/cost-ledger.py check-budget`: exit 0 within budget;
  exit 1 over budget — prints the exceeded limits to stderr and records
  one `budget_exceeded` event in `gate/events.jsonl` (deduped per day).
  Over-budget **never auto-stops a run**: budget semantics for auto-stop
  are not defined yet.

## Human override (no deadlocks)

Two logged escape hatches, both visible in the evidence and the log:

- `pass-gate.py override --id <id> --reason "..." [--by NAME]` — marks
  the item passing with `evidence.override` (exit_code −1 = "no passing
  run"). A reviewer sees it was an override, not a passing run.
- The Stop hook (`.claude/hooks/stop-gate.mjs`) blocks stopping while
  any item is `in_progress`. Set `GATE_ALLOW_STOP=1` with a non-empty
  `GATE_STOP_REASON` to stop now; the hook appends a `stop_override`
  event first. An override without a reason is not an override.
  If the hook already blocked the same stop once, Claude Code sets
  `stop_hook_active` and a second attempt is allowed (blocking again
  would loop forever); the allowance is logged as
  `stop_allowed_hook_active`.

**Audit responsibility for overrides.** An override is a human decision,
not a passing run: `check-clean` never re-verifies an overridden item
(3b skips override items by design), so nothing else will catch a bad
override. The person who overrides owns the follow-up: every override
must be re-examined at the next session breakpoint (SESSION_STATE
review) and either verified for real or reopened
(`pass-gate.py reopen`). An override older than one session without
re-examination must be treated as an open item again.
`pass-gate.py status` and `events` list overrides explicitly so a
reviewer can find them.

## Deploy

`deploy-agents.sh` / `.ps1` copy the gate *code* (`pass-gate.py`,
`graph.py`, `feature_list.schema.json`, `init.template.sh`, this README) to the
target's `gate/`. They never copy `feature_list.json`, `events.jsonl`,
or `clean-state.json` — those are per-project state. A target project
runs `sh gate/init.template.sh --name <project> --verify "<cmd>" --start
"<cmd>"` to create its own state, or `python3 gate/pass-gate.py init`.

Note: `pass-gate.py init` looks for `templates/feature_list.template.json`
next to the repo; in a deployed target that directory does not exist, so
init falls back to an empty list and `add` is the way items are created.
That is intentional — the examples are repo documentation, not a default.

## Dogfood

Phase 1 was dogfooded twice; the record is
`docs/internal/phase1-dogfood.md`. In short: this repo's own
`SESSION_STATE.md` migration went through the gate (fake pass planted,
caught by CI §3k, hook denied a direct write, real verify passed), and
a second small project (`/tmp/tinycalc`, a CLI calculator) went
failing → passing on a real feature with a second intercept caught by
`check-clean` dimension 3b. Both handovers were timed at ~1s of reading.
