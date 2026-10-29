# Gate operator checklist — hosts without hooks

For Claude Code, hooks enforce parts of the gate. On every other host
(Antigravity, WorkBuddy, dsh, Muse, agy, …) no hook runs, so this manual
checklist is the enforcement. It is discipline plus the CI re-run, not
a runtime control — say so in any handover that relies on it.

## Before starting work

- [ ] `python3 gate/pass-gate.py status` — know what is passing, in progress, blocked.
- [ ] WIP=1: exactly one item `in_progress` at a time. `start` the item
  before writing code, never after.
- [ ] Write the verification command first: it must actually prove the
  behaviour, exit 0 on pass, and be fast and hermetic (no network, no pytest
  if the sandbox may lack it — see the known-baseline note below).
- [ ] `docs/internal/SESSION_STATE.md` names the `in_progress` item, so a
  later session can resume in about a minute (`check-clean` dimension 3a
  checks this narrative).

## While working

- [ ] Never hand-edit `gate/feature_list.json` — in short, never hand-edit
  the feature list. The only writer is
  `pass-gate.py` (`add` / `start` / `verify` / `block` / `reopen` /
  `override`). A hand edit leaves no event and is only caught by CI §3k.
- [ ] Never hand-edit `gate/events.jsonl`. It is append-only; history
  rewrites show up as diffs against the last reviewed commit.
- [ ] If stuck, `block` with a reason instead of faking a pass. An
  `override` is a logged human decision, not a passing run, and must be
  re-examined at the next breakpoint or reopened.

## Before handing off

- [ ] `python3 gate/pass-gate.py verify --id <id>` for each finished item —
  passing requires a recorded command, exit code 0, timestamp and output tail.
- [ ] `python3 gate/pass-gate.py check-clean` — read every dimension, do not
  summarise a FAIL as a pass:
  - 1 build, 2 tests, 3a narrative, 3b re-verified passing items,
    3c no placeholders, 4 no temp artefacts in `git status`, 5 start path.
  - A dimension with no command configured reports SKIP, not PASS.
- [ ] `git status --short` — no `*.tmp`, `*.bak*`, `__pycache__`, `*.log`.
- [ ] If `check-clean` dimension 2 fails only on the known sandbox baseline
  (`eval:bench-smoke-passes`, missing pytest), say exactly that — do not
  claim check-clean is fully green, and do not install pytest just to make
  the handover look green without recording the change.

## Session handoff

- [ ] Update `SESSION_STATE.md`: in-progress item (or `none`), next steps,
  blocked items, and a dated last-verification line.
- [ ] Commit `feature_list.json` and `events.jsonl` together with the work;
  they are reviewable evidence, not local telemetry (unlike the gitignored
  cost ledger).
- [ ] Never claim a PR is merged, CI is green, or a live host run passed
  until the tool output says so. Unverified items stay listed as unverified.

Origin: written during the 2026-10-29 night dogfood run, which itself ran
on Muse/agy without Claude hooks — this checklist is what that run followed.
