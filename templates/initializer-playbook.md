# Initializer playbook — the first session only sets up (course L06)

Initialization and implementation are different jobs. The first
session on a gated project does **no feature work**: it produces a
trustworthy starting state that later sessions can build on. If you
are the initializer, stop after the acceptance checklist passes.

## 1. Opening questions (ask before writing anything)

- What is this project, in one sentence? Who uses it?
- What does "done" mean for the first milestone — which commands
  prove it (build / test / start)?
- What is explicitly out of scope for now?
- Which paths are sensitive (secrets, data, production config)?
- What already exists: repo state, failing tests, known debt?

Record the answers in `PROJECT_CONTEXT.md` and `DECISIONS.md` — in
the repo, not in chat (course L03).

## 2. Scaffold and prove the starting state

1. Run the deploy/init path for this repo (`gate/init.template.sh`
   or `python3 gate/pass-gate.py init`).
2. Fill `gate/clean-state.json` with the project's real build, test
   and start commands from step 1 — placeholders do not count.
3. Run each command once. A starting state that does not build is
   the first feature-list item, not a footnote.

## 3. Write the feature list (the initializer's main product)

For each item, in this order:

1. **Verification command first** — the command whose exit 0 proves
   the behaviour, plus its `level` (`assert` / `unit` /
   `integration` / `e2e`, D66). If you cannot write the command,
   the item is not understood yet; split it or ask.
2. **User-visible behaviour** — what a user or the next session can
   observe when it is done. No behaviour, no item.
3. Title, area, priority — last, and briefly.

Use `pass-gate.py add` (never hand-edit `feature_list.json`).
Order items so the riskiest assumption is tested earliest.

## 4. Initialization acceptance checklist

- [ ] `pass-gate.py status` validates with zero errors
- [ ] `pass-gate.py check-clean` passes (or every FAIL is itself
      filed as a feature-list item)
- [ ] `SESSION_STATE.md` names the goal and the first item to start
- [ ] No item is left `in_progress` by the initializer — starting
      work is the next session's first act
- [ ] Sensitive paths and out-of-scope areas are written down

Only then is the project ready for implementation sessions.
