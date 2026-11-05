# Reliability — how this repo proves it is healthy

Summary document. Normative detail lives in `gate/README.md`,
`docs/internal/release-checklist.md` and the CI workflow; this file
states the standard paths and the rules that bind them.

## Standard paths

- Unit tests: `python3 -m unittest discover -s tests -p "*_test.py"`
- Guard suite: `python3 tests/repo_checks.py`
- Hook behavior tests: the `node tests/*.test.mjs` set run in CI
- Gate state: `python3 gate/pass-gate.py status`
- Clean-state check: `python3 gate/pass-gate.py check-clean`
  (five dimensions; run before claiming any work round complete)

## Required signals

- The gate's hash-chained event log (every state transition is
  recorded and tamper-evident).
- This repo dogfoods its own gate: `gate/feature_list.json` carries
  this repo's items with recorded evidence.
- CI (`.github/workflows/ci.yml`) runs the checks above plus
  markdownlint, shellcheck and a deploy smoke test.

## Rules

- `main` stays green; a red check is fixed before new feature work
  starts on top of it.
- Work is not complete if the repository cannot be restarted
  cleanly: standard startup and verification paths must run from a
  fresh checkout (`check-clean` dimension coverage).
- A failure must be locatable from repo-local signals (gate log,
  test output, check reports). If it is not, the missing signal is
  itself a defect to record in
  `docs/exec-plans/tech-debt-tracker.md`.
- Recurring failure modes get a benchmark case or a guardrail, not
  a prose warning.
