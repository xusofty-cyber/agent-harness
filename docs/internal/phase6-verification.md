# Phase 6 verification record (2026-10-28)

Branch `feat/phase0-v3`, HEAD after Phase 6: see commit list in the final
report. Base: Phase 5 HEAD `8313378`. All verification below was run on
this branch, unpushed, never merged to main.

## 1. repo_checks — 655 PASS, 0 FAIL

`python3 tests/repo_checks.py` → "All repo checks passed." (Phase 5: 599.)
New checks added in Phase 6 (+56):

| Section | Checks | What |
|---|---|---|
| §5c | 38 | every github entry 40-hex pinnedCommit; meta entries pin+note |
| §3m1 ocr-pin | 3 | lock npmVersion/pinnedAt/pinnedFrom; scripts agree with lock; no bare install |
| §3m1b docs-pin | 4 | EN+ZH Panorama Guide: no bare npm install, no piped curl\|sh / irm\|iex |
| §3c2 release | 1 | `tools/check-release.py` exits 0 |
| §3t loop-deploy | 8 | empty-dir deploy: 6 templates + runner land, runner executes |
| parity loop | 1 | `LoopDeploy` / `loop-deploy` in both scripts |
| (import fix) | — | `import shutil` for §3t cleanup (NameError found by the run itself) |

## 2. Hook tests — 89 pass, 0 fail

| File | Pass | Fail |
|---|---|---|
| tests/hooks.test.mjs | 56 | 0 |
| tests/hooks-gate.test.mjs | 10 | 0 |
| tests/hooks-lifecycle.test.mjs | 12 | 0 |
| tests/hooks-write.test.mjs | 11 | 0 |
| tests/pass_gate_test.py | OK | — |

## 3. True-lock negative tests (6-1)

- Break a pin (`codegraph.pinnedCommit = "not-a-real-commit"`) + empty a
  meta note → repo_checks fails with `[FAIL] lock-pin:codegraph`,
  `[FAIL] lock-pin:meta-openspec` (and the pre-existing
  `installer-pin:codegraph-lock`). Lock restored; checks pass again.
- Note: an all-zero 40-char string IS valid hex — the first negative-test
  attempt used `'0'*40` and (correctly) did not fail. Retested with a
  non-hex value.
- `python3 tools/sync-skills.py --check --strict` (online, the CI step):
  exit 0 in ~34 s, all skills in-sync vs pins. (Run once during Phase 6
  investigation; CI will run it on every push/PR.)

## 4. OCR pin negative test (6-2a)

- Unpin the ps1 install (bare `npm install -g @alibaba-group/open-code-review`)
  → `[FAIL] ocr-pin:no-bare-install`. Restored from backup copy (not
  `git checkout`, which would have reverted the intended uncommitted sh
  edits — lesson recorded in the final report). Checks pass again.

## 5. Docs-pin negative test (6-2b)

- Reintroduce bare `npm install -g @rpamis/comet` in the EN Panorama Guide
  → `[FAIL] docs-pin:EN-no-bare-npm`. Guide restored from backup. Checks
  pass again. `i18n:status-check` passes with 12 reminders (the stale
  rows, by design).

## 6. Release-gate negative tests (6-3)

- `VERSION` = 9.9.9 → `check-release.py` fails (exit 1):
  `VERSION='9.9.9' != CHANGELOG newest='0.2.1'`. Restored.
- Add a `**Breaking**` bullet without a `Migration:` note to CHANGELOG
  [Unreleased] → `check-release.py` fails (exit 1) AND repo_checks §3c2
  fails (`release:check-release-passes`). Restored. Checks pass again.
- `python3 tools/check-release.py` on the clean tree: exit 0
  ("VERSION 0.2.1, CHANGELOG newest 0.2.1, lock 42 entries").

## 7. Deploy

- `bash deploy-agents.sh /tmp/smoke-loop < /dev/null` → exit 0;
  `templates/loop/` contains all 6 templates; `tools/loop.py` present.
- repo_checks §3t (same deploy in a temp dir, inside the suite): all 8
  checks pass, including running the deployed `loop.py --help`.
- `bash -n deploy-agents.sh` syntax OK. deploy-agents.ps1 edited with
  CRLF + BOM preserved (verified with `file`).

## 8. What was NOT done

- No tag created; VERSION stays 0.2.1 (needs separate user approval).
- FR/DE/ZH-TW Panorama Guide translations of the pinned instructions:
  rows marked `stale`, translation not done (tracked debt, D19).
- Vendored comet skill's unversioned install line: left as-is (D23).
- RTK winget pin: no version pin available (D13).
- No push, no merge to main (per task red lines; see §9).

## 9. Branch state

- Branch: `feat/phase0-v3` only. Local main untouched at `88c8b79`
  (never checked out). `v3-yunyi` / `v3-yunkai` never fetched, checked
  out, or merged. Nothing pushed.
