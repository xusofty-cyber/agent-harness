# Phase 2 verification record (2026-10-28)

How each Phase 2 Go-gate item was verified, with the actual commands and
outputs. Fixtures live under `/tmp` (ephemeral); re-run them from the
repo root when in doubt.

## 1. Fake green is eliminated from the pipeline

Stale-doc fixture `/tmp/docimpact-fixture` (a doc whose
`last_verified_commit` is behind `src/foo.py`):

```console
$ python3 tools/doc-impact.py --root /tmp/docimpact-fixture --strict
exit=1
🔴 docs/specs/foo.md [SPEC-FOO] (direct, 2 commits behind)
    ↳ src/foo.py

$ python3 tools/doc-impact.py --root /tmp/docimpact-fixture
exit=0   # advisory default: reports, does not fail

$ python3 tools/sync-skills.py --check --strict
exit=0   # all vendored skills in sync with their upstreams today
```

Pipeline on the same fixture, stage 4 only:

```console
$ bash run-pipeline.sh /tmp/docimpact-fixture --stages docs --strict --non-interactive
✖ 阶段 4 出现错误（退出码 1，--strict）
[✖ FAIL]  活体文档影响分析与质检 (doc-impact) : doc-impact.py 返回非零退出码 1（有文档 must-update）（--strict）
pipeline exit=1

$ bash run-pipeline.sh /tmp/docimpact-fixture --stages docs --non-interactive
⚠ 阶段 4 未完全成功（退出码 1），记为 WARN（默认 advisory 模式；--strict 会记为 FAIL）
[! WARN]  活体文档影响分析与质检 (doc-impact) : doc-impact.py 返回非零退出码 1（有文档 must-update）（advisory）
pipeline exit=0
```

The `stty` / trap terminal-restore `|| true` lines were deliberately left
alone — they restore terminal state, they record no PASS. Clean target
`/tmp/clean-target` with `--strict` passes (exit 0).

## 2. Comet is pinned and interrupt recovery was tested once

Pin measured at implementation time (never hardcoded in a plan doc):

```console
$ npm view @rpamis/comet version
0.5.1
$ comet --version
0.5.1
```

`tools/check-comet.py` passes on this machine; negative demos in
`/tmp/comet-mismatch` (wrong pin 9.9.9 → exit 1; wrong schema v9 →
exit 1). `install_pinned_script` was tested end-to-end with a harmless
local installer: correct hash → exit 0 and the installer ran; wrong
hash → exit 1 and the installer did NOT run; download failure → exit 1.
No `| sh` / `| iex` remains in either deploy script.

Interrupt-recovery test (native workflow, scratch project
`/tmp/comet-recovery`, seeded with the repo's own
`templates/comet.config.yaml` — bare `comet init` is interactive and
needs a platform selection, so the state-machine path was driven
directly with the CLI):

```console
$ comet native new demo-change --json
exitCode 0 — active change, phase shape, stateVersion 1
$ comet native next demo-change --summary ... --expected-state-version 1 \
    --expected-action prepare-shape-confirmation --project-root /tmp/comet-recovery
# first attempt failed honestly: brief.md sections were empty (shape
# validation). After filling the brief, the same command advanced the
# state to stateVersion 2 (verified via status).
```

Simulated interruption — fresh shell, no state touched:

```console
$ comet native status demo-change --project-root /tmp/comet-recovery --json
phase shape | stateVersion 2 | status await-user   # identical, not reset
$ comet resume-probe --utterance "continue demo-change" --json /tmp/comet-recovery
action: auto_resume, confidence: high, changeName: demo-change,
reasonCode: native-change-named, candidate selected: true
$ comet native doctor demo-change --project-root /tmp/comet-recovery --json
Diagnostics passed: no problems found.
```

State files are portable: `docs/comet/changes/demo-change/comet-state.yaml`
uses relative refs only; `.comet/current-change.json` carries no machine
paths. The `~/.comet/workspaces/<hash>/...` runtime directory named in
comet's JSON envelope is not materialised on disk (lazy) — no
machine-path contamination was observed in any file a project would
commit. This settles D8's open caveat U2.

Honest scope limit: advancing past Shape confirmation requires an
interactive user confirmation by design (and an independent Verifier
session for Build), so a non-interactive CLI test cannot complete the
full loop. A malformed `next` attempt (missing required inputs, exit 64)
left the confirmation stale; the guard behaved as designed and the
state was preserved (v2, await-user) — recovery is via the normal
revise/confirm loop, not data loss.

## 3. Guard bypass coverage (before → after)

Probed by feeding PreToolUse stdin JSON to `.claude/hooks/guard.mjs`:

| Command | Before (2-4) | After |
|---|---|---|
| `$(git push --force origin main)` | 2 (denied) | 2 |
| `$(which git) push --force origin main` | 0 (bypass) | 2 |
| `` `which git` push --force origin main `` | 0 (bypass) | 2 |
| `$(command -v git) push --force origin main` | 0 (bypass) | 2 |
| `eval "git push --force origin main"` | 0 (bypass) | 2 |
| `sh -c 'git push --force origin main'` | 0 (bypass) | 2 |
| `bash -c "git push --force origin main"` | 0 (bypass) | 2 |
| `sudo $(which git) push --force origin main` | 0 (bypass) | 2 |
| `FOO=$(git rev-parse HEAD) git push --force origin main` | 2 | 2 |
| `echo $(git rev-parse HEAD)` | 0 (must stay) | 0 |
| `echo $(which git) push --force origin main` | 0 (must stay) | 0 |
| `x=$(which git) push --force origin main` | 0 (must stay) | 0 |
| `echo '$(which git) push --force origin main'` | 0 (must stay) | 0 |
| `git status` / `git push origin main` | 0 | 0 |

All 14 cases are now tests in `tests/hooks.test.mjs` (56 pass, 0 fail).
Remaining known gap: `xargs` / `find -exec` indirection is not expanded.

## 4. Cost ledger (proxy metrics, no token ledger)

Pipeline → ledger end-to-end (`/tmp/ledger-demo`, target with `gate/`):

```console
$ bash run-pipeline.sh /tmp/ledger-demo --stages deploy --non-interactive
pipeline exit=0
$ cat /tmp/ledger-demo/gate/cost-ledger.jsonl
{"ts": "2026-10-28T09:51:16Z", "kind": "stage", "run_id": "20261028095115-22685",
 "stage": "阶段 1", "status": "pass", "duration_ms": 1000}
$ python3 tools/cost-ledger.py summary --gate-dir /tmp/ledger-demo/gate
runs today: 1, tool calls today: 0, stages today: 1 (fail 0, warn 0)
$ python3 tools/cost-ledger.py check-budget --gate-dir /tmp/ledger-demo/gate
within budget (2026-10-28): runs 1, tool calls 0, verify failures 0, overrides 0
exit=0
```

Over-budget demo (budget tightened to `max_tool_calls_per_day: 1`, three
hook-style tool-call lines appended):

```console
$ python3 tools/cost-ledger.py check-budget --gate-dir /tmp/ledger-demo/gate
COST BUDGET EXCEEDED (2026-10-28): max_tool_calls_per_day: 3 > 1
Alert only — the run is NOT auto-stopped (budget semantics for auto-stop are not defined yet).
recorded budget_exceeded event (seq 1) in /tmp/ledger-demo/gate/events.jsonl
exit=1
$ python3 tools/cost-ledger.py check-budget --gate-dir /tmp/ledger-demo/gate   # again
budget_exceeded event already recorded today; not duplicated
exit=1
```

## 5. Full verification (end of Phase 2)

```console
$ python3 tests/repo_checks.py
All repo checks passed. — 508 PASS
$ node tests/hooks.test.mjs            — pass 56, fail 0
$ node tests/hooks-gate.test.mjs       — pass 10, fail 0
$ node tests/hooks-write.test.mjs      — pass 11, fail 0
$ node tests/hooks-lifecycle.test.mjs  — pass 12, fail 0
$ python3 tests/cost_ledger_test.py   — Ran 6 tests, OK
$ python3 tests/doc_impact_test.py    — Ran 11 tests, OK
$ python3 tests/sync_skills_test.py   — Ran 17 tests, OK
$ bash deploy-agents.sh /tmp/smoke-p2c < /dev/null
deploy exit=0 — new hooks (session-start, post-tool-use) deployed,
settings.json wires SessionStart/PostToolUse, .gitignore carries
gate/cost-ledger.jsonl
```

Not verified locally (honest gaps): shellcheck / markdownlint are not
installed on this VM — CI is the authority for those; `run-pipeline.ps1`
and `deploy-agents.ps1` changes were verified statically only (no
`pwsh` / `powershell` on this VM — parity checks + careful reading).
