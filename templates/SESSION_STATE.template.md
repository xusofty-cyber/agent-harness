# SESSION_STATE — session breakpoint

> **Updated**: <YYYY-MM-DD> | **Project**: <PROJECT_NAME>
> **Feature list**: `gate/feature_list.json` (status via `python3 gate/pass-gate.py status`)
> **Rule**: one page max. If this file grows past one page, move finished
> work to `CHANGELOG.md` and keep only the breakpoint here. History is not
> state.

## Goal

- <What this session is trying to ship, in one line>

## In progress

- `<feature_list id>`: <one-line state> (or: none — run `pass-gate.py start --id <id>`)

## Next

- [ ] <Next concrete step>
- [ ] <Next concrete step>

## Blocked

- <Blocker, or "none">

## Last verification

- <Last command run and its result, or "none yet">
- Evidence lives in `gate/feature_list.json` (the `evidence` field) and
  `gate/events.jsonl` — not in prose here. If the prose here and the
  feature list disagree, the feature list wins.
