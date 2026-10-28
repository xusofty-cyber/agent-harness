# Merge verification — `feat/merge-v3` (2026-10-28)

Merge of `feat/phase0-v3` (skeleton, base `ab8ec04`) + `v3-yunyi`
(`35a42f7`) + `v3-yunkai` (`65de843`), per
`agent-harness-三分支对比与合并优化方案-2026-10-28.md`. No merge to
main, no PR into main, no modification of the three source branches.
Branch pushed to `origin/feat/merge-v3` only.

## Commits (base `ab8ec04` → HEAD)

| # | Commit | Step |
|---|---|---|
| 1 | `ec952e5` | Step 1 pre-fix: Stop-hook `stop_hook_active` deadlock guard + override audit note in gate/README.md |
| 2 | `b3f4c6c` | yunyi `gate/graph.py` executor + 5 tests (per-command `--timeout`, `--state` default `<repo>/graph-state.jsonl`) |
| 3 | `75572b5` | yunyi terminate/handoff/run as pass-gate subcommands + 11 tests (atomic termination.json, corrupt = fatal, reopen clears, handoff atomic, run `--branch`) |
| 4 | `bb4c770` | yunyi rubric `eval/evaluate.py` + gate, `eval/check-thresholds.py` + 5 eval + 7 threshold tests (skeleton verdict rule; all-2 NOT adopted; `--gate` refuses, provisional) |
| 5 | `c8b070b` | graph wired into deploy (sh+ps1, PARITY, repo_checks §3t); repo_checks 655 → 658 |
| 6 | `8986639` | yunyi guard-alerts.jsonl graded policy + D27 resolver rule (resolver must be argv[0]) + 13 guard tests + 1 guard-write test |
| 7 | `852acef` | yunyi D32 brainstorming server safety doc + 5 server tests (docs only; server unchanged) |
| 8 | `3b3b956` | yunkai bench t5–t8 + objective evaluator into `eval/bench/` (fixtures, prep, evaluate, smoke, README) |
| 9 | `9268dfa` | yunkai `gate/comet_adapter.py` + schema `external_evidence` + 4 tests; ships with the gate layer |
| 10 | `c5a1451` | yunkai `.comet` state backup before `comet init` (sh+ps1 + PARITY) |
| 11 | `b018a57` | yunkai slim Project template for minimal/standard tiers (D-009; sh+ps1 + PARITY) |
| 12 | `eda666f` | yunkai guard hardening tests (4 additive: nested depth-2, echo-wrapped, benign `--version`) |
| 13 | `69892b1` | `QUALITY_SCORE.md` rewritten in yunkai's scorecard format; skeleton baseline as appendix |
| 14 | `06b9c2d` | DECISIONS D26–D56 + CHANGELOG merge entry (step 6 docs closeout) |
| 15 | `2543caa` | lint: markdownlint clean (1 merge-introduced MD025 + 4 pre-existing) |

## Verification checklist (plan §6.7)

| Check | Result |
|---|---|
| repo_checks ≥ 655 PASS | **662 PASS / 0 FAIL** (`python3 tests/repo_checks.py`) — 655 base + 2 comet-adapter deploy checks + 2 PARITY rows (Backup-CometState, TIER_SLIM_TEMPLATE) + 3 from earlier merge steps |
| hooks four files | **73 + 12 + 11 + 12, all pass** (hooks / hooks-write / hooks-gate / hooks-lifecycle); server.test.mjs 5/5 |
| pytest | **69 passed** (`python3 -m pytest tests/ -q`) — base + graph 5 + threshold 7 + comet_adapter 4 + terminate 11 + eval 5 + others |
| Python unit tests (CI list) | sync_skills 17 OK, doc_impact 11 OK, cost_ledger 6 OK, pass_gate 3 OK |
| deploy smoke (CI form) | **exit 0** — CI's exact smoke commands (incl. `--comet-init` variant, `.comet/config.yaml` lands); all 12 expected files land: gate/pass-gate.py, gate/graph.py, gate/comet_adapter.py, gate/feature_list.schema.json, gate/init.template.sh, tools/loop.py, 6 loop templates; deployed graph/comet_adapter/loop `--help` all exit 0 |
| bench smoke | **4/4 OK** (`python3 eval/bench/smoke.py` — pristine rejected, reference accepted for t5–t8) |
| t8 gate prep | block/start/verify flow works; evaluate pristine gate run: accepted=False (correct — stubs unimplemented), slugify_unchanged=True |
| dist-slim arm | prep materializes with the shipped slim template + 3-skill kit; deploy minimal lands slim, `--profile full` lands full text |
| comet backup | exercised on a scratch dir: snapshot created with the state file, no recursive `backups/` |
| true-lock negative test | corrupting one github pin → repo_checks **1 check failed** (turns red correctly); lock restored clean |
| version negative test | VERSION=9.9.9 → check-release.py **FAIL exit 1**; restored, OK |
| check-release.py | **OK** (VERSION 0.2.1, CHANGELOG newest 0.2.1, lock 42 entries) |
| count-skills.py --check | **OK** (40 dirs, counts agree; no README/AGENTS count change needed) |
| i18n-check.py | **passed** (12 pre-existing stale reminders, none new) |
| sync-skills.py --check --strict | **exit 0** (all skills in-sync; network) |
| markdownlint `**/*.md` | **exit 0** (shellcheck 0.9.0 + markdownlint-cli newly installed locally to run this) |
| shellcheck `-S warning ./*.sh` | **exit 0** |
| node --check (6 hook files) | **all OK** |
| Guard regression | D27 13 tests + skeleton Guard tests + yunkai 4 hardening tests all green; new false-positive case (`echo $(git --version)` allowed) and new false-negative case (nested depth-2 denied) both present |
| ps1 changes | **statically verified only** (no pwsh on this VM); BOM+CRLF preserved (`file` check after every ps1 edit) |
| CI (GitHub) | **No run exists for this branch push** — `ci.yml` triggers only on push to main/long-term-memory-governance and on pull_request; no PR into main was opened (red line). The lint-and-test steps were run locally in their CI form (see above). ps-analyzer (Windows) cannot run on this VM. |

## Bench runs (t5–t8 matrix) — PENDING

A subagent is running the one-round matrix: t5–t8 × bare/pack/gate
(12 runs) + t5 dist-slim (1 run), in
`/tmp/agent-harness-bench-merge1`, with CLAIM lines and
`evaluate.py` JSON verdicts recorded to
`eval/results/bench-t5-t8-merge-round1.md` (+ JSONs in
`bench-t5-t8-merge-round1/`). This section will be updated with the
results when they arrive; the merge is not declared complete until
the matrix is recorded here with 0 false completions (or the
failures are honestly listed).

## Known gaps / honest notes

- The bench `evaluate.py` `project_files_changed` list includes
  `setup.py` for t8 (prep deliberately excludes it from run dirs, so
  it always reads as "changed"). Informational only; `accepted` does
  not depend on it. Faithful to yunkai's original.
- For t5–t8 the pack arm installs yunkai's 3-skill dist kit, while
  the t1–t4 baseline's pack arm deployed `--profile full`. The two
  pack definitions are NOT the same apparatus — do not compare t1–t4
  pack numbers with t5–t8 pack numbers without noting that (recorded
  in `eval/bench/README.md` and `eval/bench/prep.py`).
- `pass-gate.py` has only 3 unit tests; most of its coverage is
  repo_checks §3k + dogfood (noted in QUALITY_SCORE.md).
- `eval/bench/README.md` in yunkai said "Four fixture tasks / Three
  arms" — rewritten for 4 tasks (t5–t8) / 4 arms.
- Yunkai's `gate/bench/results/` run data (72 runs) was NOT imported;
  only the machinery + fixtures were ported. The merged branch's own
  t5–t8 runs are the matrix above.
- Yunkai's `tools/cost-ledger.py` (145 lines) was NOT taken (weaker
  than the skeleton's 318-line version). Yunkai's Stop override via
  env var without a reason was NOT taken (skeleton's reason-required
  rule stands).
- The plan's §6.3 attribution of "D27 Guard + 13 tests" to yunkai is
  wrong (D27 is yunyi's — verified); corrected in DECISIONS.md. The
  plan's claim that the skeleton's `eval/` has an `evaluate.py`
  clashing with yunkai's is also wrong (no such file existed).
- `gh` push used the existing `xusofty-cyber` login (device-flow
  auth from 2026-10-28 17:09, scopes incl. `workflow`).
