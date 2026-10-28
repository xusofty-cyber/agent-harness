# Loop state — <LOOP_NAME>

> **Kind**: maker-checker | **Goal**: `<goal.md path>`
> **Status**: running | awaiting-approval | complete | failed
> **Rule**: one row per round, written by the runner — never edited by
> hand. The checker sees only the listed artifacts, copied fresh each
> round into `checker/`; it never sees the maker's notes. A round passes
> only when the checker command actually exits 0.

## Goal

- <One line: what the loop is producing>

## Rounds

| Round | Maker did | Checker found | Outcome | Next action |
|---|---|---|---|---|
| 1 | <what the maker changed> | <what the checker found> | pass / fail / timeout | <next step, or "—" if stopped> |

## Consecutive passes

- <n> / <required> — stop at <required>, or max rounds <N>

## Approval

- Requested: <round, or "—"> | Approved by: <name, or "—"> | Note: <text>

## Last verification

- <Last checker command and its result, or "none yet">
- Full record: `loop-state.json` (rounds) and `loop-events.jsonl`
  (append-only events). If this prose and the JSON disagree, the JSON wins.
