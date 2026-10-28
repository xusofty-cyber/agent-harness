# Merge review + optimization — feat/merge-v3 (2026-10-29)

Review of the two analyses of the merge branch (yunyi's
`~/workspace/user/files/-merge-v3-analysis.md`, 217 lines; yunkai's
`~/workspace/user/files/-merge-v3-.md`, 109 lines, signed "审计：云开"),
plus the optimization round that followed. Every verdict below was
re-verified against the merge branch and the source branches — nothing
was taken on trust from either analysis.

Branch: `feat/merge-v3`, worktree `~/workspace/agent-harness-merge`.
Base at review start: `dbe9c5f` (17 merge commits, pushed 2026-10-28).
Nothing was pushed in this round; main was not touched, no PR into
main was opened, no tag was created.

## 1. Review verdicts

### 1.1 Baseline claim (yunyi: "the plan recommended v3-yunyi, the merge picked p0")

**FALSE.** The comparison plan
(`~/workspace/your_files/agent-harness-三分支对比与合并优化方案-2026-10-28.md`)
§6.1 says explicitly "以云澈 `feat/phase0-v3` 为骨架", repeated in its
conclusion. The merge's choice of `ab8ec04` as base follows the plan.
No change made.

### 1.2 D27 attribution (merge-verification vs yunyi: who misattributes?)

**BOTH SIDES PARTLY RIGHT; the plan document itself is inconsistent.**
The plan attaches D27-labelled guard work to the yunkai side too
(comparison table, §3 discussion, §6.3 take-list "D27 Guard 合取式启发式
+ 13 个测试" under yunkai), while yunyi's DECISIONS D27 is Guard
`$(which git)` indirection with 13 tests (verified at
`origin/v3-yunyi:DECISIONS.md:53`) and yunkai's DECISIONS contain only
D-001..D-011, no D27. The merge-verification correction note (the plan's
§6.3 attribution is wrong) is substantively correct and needed no
change. The plan's internal inconsistency is recorded, not litigated
further — the merge follows the verified evidence, not the plan's labels.

### 1.3 Yunyi P0#3: "three tools are not pinned in skills-lock.json"

**FALSE as stated.** All three are in the merge branch's 42-entry lock
with pins: codegraph `pinnedCommit` + `installerSha256`, comet
`npmVersion` 0.5.1 + `pinnedCommit`, rtk `pinnedCommit` +
`installerSha256`. Deploy scripts agree with the lock (installer-pin
checks). Consequence: the merge DECISIONS sentence "all three are
pinned in `skills-lock.json`" is literally true and must NOT be
rewritten to claim the pins live only in scripts/guides. What was done
instead (commit `7f23a9f`): a precision note on the yunyi-D31 bullet —
the lock pin is real, the deploy scripts enforce the same pins at
install time, the guides document them; the one uncovered surface is
rtk's PowerShell winget channel (skeleton D13, known gap). Upstream rtk
tip measured 2026-10-29 (`7a73af1b…`) differs from both the merge pin
(`e05c7bdf…`) and yunyi's (`753a3b0e…`); a pin differing from tip is by
design (pins dated 2026-10-28), not drift — re-pinning is a
supply-chain decision, not a bug fix. The true-lock rule itself is
unchanged.

### 1.4 Yunyi: "the plan recommended yunyi's minimal profile and a two-axis (--profile + --tier) design"

**UNSUPPORTED.** The plan rejects yunyi's `skill-profiles.txt`
mechanism in favour of the skeleton's JSON source, and states the slim
template merges into the profile mechanism orthogonally to minimal 10 /
standard 18, not as a second axis. No change made. (The tier question
itself was later settled by user ruling D58 — see §3.)

### 1.5 Yunkai §4: four "established user rulings"

**ALL VERIFIED VERBATIM** in yunkai's `docs/internal/DECISIONS.md`:
D-004 template `archive_confirmation` stays `automatic` (own config
stays `required`); D-006 delete 18 FR/DE files, owner confirmed; D-007
cost ledger warns, never stops automatically; D-011 human rubric
calibration not run, rubric stays advisory-only on a standing basis.
Also verified: yunyi D23 records the user chose hard stop ON with
ceilings (single task ≤10 verifications / ≤3600 s / ≤5 retries; single
day ≤100 verifications / ≤8 h; `hard_stop_enabled=true`); skeleton D12
records the proxy ledger warns and never auto-stops. The three-way
contradiction on hard stop was real — and was settled by user ruling
D57 (see §3), not by picking a side from the documents.

### 1.6 Yunkai §5#1: QUALITY_SCORE "6/6 feature_list items passing"

**TRUE as a drift report.** The merge branch's `gate/feature_list.json`
has exactly 3 items, all passing; the 6/6 is yunkai's number carried
over. Fixed to 3/3 (commit `7f23a9f`).

### 1.7 Retest numbers (both analyses)

**ACCURATE.** Independent re-runs on the merge branch at review start:
repo_checks 662 PASS / 0 FAIL; hooks 73 + 11 + 12 + 12 = 108, plus
server 5/5 = 113 total; pytest 69 passed; bench smoke 4/4 OK. (Counts
moved during this round as checks were added; final numbers in §5.)

### 1.8 "check-thresholds only covers t4" (yunyi + original brief wording)

**IMPRECISE on both sides.** The actual run of
`eval/check-thresholds.py` covers t1–t4 (12 groups, all ok, no breach).
The real gap: t5–t8 eval JSONs are not loaded — they live in
`eval/results/bench-t5-t8-merge-round1/` under names like
`t5-ambiguous__bare__r1.json` (not the `*_{bare,pack,gate,dist-slim}_rep*.json`
glob), and they lack run-record fields (`outcome`, `verify_attempts`,
`duration_s`, `false_completion`), carrying only `accepted`,
`tests_pass`, `tests_intact`, `extras`. Fixed by wiring (commit
`aafc6a6`, see §2).

### 1.9 Yunkai: pytest-missing makes bench-smoke misreport 1 FAIL

**REPRODUCED EXACTLY.** With a python lacking pytest, `bash
eval/run-bench.sh smoke` fails at the t1 acceptance step (`python3 -m
pytest tests/test_calc.py::test_subtract -q` → "No module named pytest"
→ "smoke: acceptance fails after solution"), and repo_checks reports
only the generic `eval:bench-smoke-passes` FAIL with no diagnosis.
Fixed by a preflight + tail detail (commit `cb1f6d2`, see §2).

### 1.10 Other verified facts (used, not re-litigated)

- SESSION_STATE template drift is real: EN base 31 lines, ZH 27 lines,
  DE/FR/ZH-TW 46 lines (old format); yunyi's 11-line breakpoint format
  was not adopted. Settled by D61 (see §2).
- Yunyi's lint-rules were not ported (merge DECISIONS D54 admits partial
  adoption). Ported now (commit `b5c0c4a`, D62, see §2).
- The merge branch never had a real GitHub CI run (ci.yml triggers only
  on pushes to main/long-term-memory-governance and on pull requests).
  `workflow_dispatch` added (commit `7f23a9f`); a real run is still
  owed before release (see §4).
- Gate bootstrap verification covers only the test command: t5's
  DECISIONS.md topics and t6's `tests_median_extra.py` are outside gate
  acceptance (merge-verification self-reports this). Fixed by
  VERIFY_CMD (commit `f785acb`, see §2).
- Yunyi's D15 placeholder rule lives in yunyi's `gate/harness.py`
  clean-state check (FAIL when SESSION_STATE still contains unfilled
  template placeholders). The skeleton template's own unfilled markers
  are `<YYYY-MM-DD>`, `<PROJECT_NAME>`, and the phrase "What this
  session is trying to ship". Skeleton `check-clean` (five dimensions
  in `gate/pass-gate.py`) had no placeholder dimension; its own
  `docs/internal/SESSION_STATE.md` contains none of those markers.
  Adopted as dimension 3c (commit `0c03da7`, D59, see §2).

## 2. Optimization commits (one per item, in order)

| Commit | Item |
|---|---|
| `ca3013c` | policy(final): cost hard stop ON — port yunyi cost.py gate + D23 ceilings (D57, user ruling 2026-10-29) |
| `d0f7d9a` | policy(final): archive_confirmation template default back to automatic (D26, user ruling 2026-10-29) |
| `eeff670` | policy(final): delete 18 FR/DE files + clean references (D27, user ruling 2026-10-29) |
| `7e74217` | fix: drop fr/de from wizard language lists (P3 follow-up: README trio + Multi-Tool guide `-Language` lists) |
| `6f04832` | policy(final): graph/loop ship only on standard/full profiles (D58, user ruling 2026-10-29) |
| `7f23a9f` | review: QUALITY_SCORE 3/3 fix, pin-surface precision note, CI workflow_dispatch |
| `f785acb` | review: gate bootstrap verifies full acceptance (t5 DECISIONS, t6 extra tests) |
| `0c03da7` | review: adopt D47 (check-clean placeholder FAIL) + D48 in effect (D59/D60) |
| `0834664` | review: SESSION_STATE 31-line format final (D61) + i18n drift warning |
| `b5c0c4a` | review: port yunyi lint-rules (6 rules, skeleton-adapted) + repo_checks gate (D62) |
| `4ea74ce` | policy(final): rubric standing advisory-only (D28, user ruling 2026-10-29) |
| `876b5f2` | fix: eval test follows D28 advisory-only (rubric commit follow-up) |
| `cb1f6d2` | review: bench smoke preflight diagnoses missing pytest |
| `9eec6c2` | review: port yunkai pass-gate behavior suite (7 tests, skeleton-adapted) |
| `aafc6a6` | review: wire t5-t8 matrix results into check-thresholds |

Detail per optimization item:

- **QUALITY_SCORE drift (O1):** 6/6 → 3/3 (3 items, all passing).
- **Pin precision (O2):** D31 bullet note; true-lock rule untouched.
- **Gate bootstrap extras (O3, preferred option):** `eval/bench/prep.py`
  gains VERIFY_CMD — t5 = unit tests + DECISIONS.md ≥5/6 topic groups
  (same groups as `evaluate.py`), t6 = unit tests +
  `tests_median_extra`; t7/t8 unchanged. `clean-state.json`
  build/test/start stay TEST_CMD. New
  `tests/bench_bootstrap_verify_test.py` 4/4 (command-content +
  behavioral gate runs: solution without the extra FAILs verify, with
  it PASSes). The fallback option (documenting "gate only checks test
  commands") was NOT needed.
- **SESSION_STATE format (O4, D61):** skeleton 31-line EN format is
  final (D29-consistent); yunyi's 11-line format NOT adopted.
  `tools/i18n-check.py` gains a warning-only drift check (>5 lines,
  mirroring LINT-006): ZH-TW SESSION_STATE (46 vs 31) prints a [drift]
  reminder, exit still 0; ZH (27 vs 31) within tolerance;
  PROJECT_CONTEXT variants aligned (63/63/63).
- **Lint-rules port (O5, D62):** `tools/lint-rules.py` + repo_checks
  `lint-rules:exit-0` (CI runs repo_checks, so CI is covered) +
  `tests/lint_rules_test.py` 3/3 (yunyi's test file had zero test
  functions; written fresh). Rule-by-rule: LINT-001 entry presence —
  NEW coverage, ENTRY_FILES adapted (yunyi's `gate/harness.py` and
  `templates/feature_list.template.json` do not exist here, dropped);
  LINT-002 hook wiring — overlaps the skeleton's five-event settings
  check, extended to the six hook files; LINT-003 schema parse —
  adapted to `gate/feature_list.schema.json` (a JSON Schema document:
  version const 1, items array — the first draft wrongly required a
  feature_list instance shape and failed on the real schema, fixed)
  plus non-empty state templates, NEW coverage; LINT-004 placeholder
  residue — NEW scope (skeleton's placeholder check covers only
  docs/internal/*.md with angle-bracket markers); the first run caught
  LINT-004 residue in the new 3c code itself, so the 3c pattern is now
  assembled from parts (same trick lint-rules uses); LINT-005 dead
  refs — equivalent coverage already exists in repo_checks Phase 0,
  port kept for defense in depth; LINT-006 translation drift — NEW
  alert, overlaps the i18n-check drift warning by design (linter view
  vs translation-tracker view).
- **D47/D48 (O6, D59/D60):** D47 ADOPTED — new check-clean dimension
  3c in `gate/pass-gate.py` (skeleton-adapted markers; any FAIL
  dimension keeps exit 1; missing file is SKIP for 3c) +
  `tests/check_clean_test.py` 4/4. D48 ADOPTED IN EFFECT, no code
  change — repo_checks has no check requiring a gitignored file;
  confirmed by the fresh-clone run (§5).
- **pytest hidden dependency (O7):** `run-bench.sh smoke` preflight
  fails fast with an explicit diagnosis + install line when pytest is
  missing (verified with a stub python); repo_checks
  `eval:bench-smoke-passes` detail now includes the smoke tail.
- **Pass-gate behavior suite (O8):** yunkai's 7 tests ported into
  `tests/pass_gate_test.py` (3 plural tests kept; 10/10 pass). Mapping
  is documented in the file header: verify-success (evidence
  exit_code 0 + output_sha256, event `verified`), verify-failure
  (start first, BAD → exit 1, in_progress, evidence None,
  `verify_failed` event with exit 3), passing-irreversible (re-verify
  exits 1 "cannot verify"), reopen --reason (in_progress, evidence
  None, verified + reopened events preserved), WIP enforced at start
  (start/start refusal, WIP=1), status rejects claimed completion and
  empty verification. No new gate features invented.
- **check-thresholds t5–t8 (O9):** `_load_records` also loads
  `bench-t5-t8-merge-round1/*.json`, normalizing `accepted` → outcome
  and task/arm from filenames; median/false-completion checks skip
  those groups (no data). Real data: t1–t4 12 groups ok, t5–t8 13
  groups "no conclusion" (1 record each), no breach. Docstring states
  the acceptance-only limitation; 2 new threshold tests.
- **CI trigger (O10):** `workflow_dispatch:` added to ci.yml `on:`
  only; push/PR triggers unchanged, no automatic runs.
- **Graph/loop tier (O11):** decided by user ruling D58, not by
  analysis — see §3.
- **Fresh-clone + deploy matrix (O12):** see §5.

## 3. Policy items decided by user final ruling 2026-10-29 (landed)

- **Hard stop ON (D57):** yunyi `cost.py` check gate + D23 ceilings
  ported (`eval/cost.py`, `eval/cost-budget.json`,
  `tests/cost_test.py` 5/5); `eval/cost-ledger.jsonl` gitignored;
  repo_checks `cost-gate:*` guards. `tools/cost-ledger.py` stays
  warn-only — two ledgers, two roles — so skeleton D12 and yunkai
  D-007 stand for their own tools while branch policy for verification
  runs is ON. The provisional OFF ruling is replaced, not deleted.
- **archive_confirmation template default automatic (D26):**
  `templates/comet.config.yaml:54` required → automatic; D4 kept as
  Phase 0 history, superseded for the template going forward; deployed
  projects untouched (deploy copies the template only when the target
  lacks it); this repo has no own `.comet/config.yaml` (removed in
  Phase 0 dedup).
- **FR/DE deletion (D27):** 18 files deleted + references cleaned
  (repo_checks §3h 3×3 languages + link roots, i18n-check GENERATED
  ZH-TW only, i18n-status rows, README/guide switchers, deploy +
  pipeline language menus and mappings with fr/de inputs falling back
  to EN, CONTRIBUTING table, count-skills LIVE_DOCS, wizard language
  lists). ZH-TW stays frozen. One i18n side effect fixed in the same
  change: the Multi-Tool zh-tw row flipped in-sync → stale after the
  EN link cleanup (the tool's own rule). CHANGELOG history mentions
  stay untouched. repo_checks walk, measured at each step: 662 (merge)
  → 666 (cost-gate +4, `ca3013c`) → 660 (this commit: −6 template
  checks) → 669 (tier: +8 net §3t + 1 PARITY) → 670 (lint-rules check)
  → 671 (rubric-advisory-only check). Every step explained; no silent
  drift.
- **Graph/loop tier standard+ (D58):** minimal ships the gate itself
  only (no `gate/graph.py`, no `tools/loop.py`, no `templates/loop/`);
  standard/full keep them. Deploy scripts (sh+ps1, `TierGateGraphLoop`
  PARITY row) gate copying on the profile; re-deploying with minimal
  over a project that already has graph/loop files backs each file up
  (`.bak.` timestamp) and removes it (templates/loop/ dir remains if
  it still holds the backups). Docs: skill-tiers tier table + migration
  note, README EN/ZH profile paragraphs, release draft upgrade notes.
  Migration sentence, verbatim: previously minimal-deployed projects
  that already have graph/loop files will have those files removed on
  re-deploy with minimal (backed up first); to keep them, re-deploy
  with `--profile standard`. Loop/graph implementations untouched —
  distribution only. repo_checks §3t asserts per-tier file sets.
- **Rubric standing advisory-only (D28):** `eval/rubric-status.json`
  status provisional → advisory-only, `confirmation_round_required`
  true → false; `--gate` still refuses (exit 2) — behavior unchanged,
  docstring + refusal message reworded. D28 rewritten in place to
  user-final; yunkai D-011 marked SETTLED; D16/D21 bullet updated.
  Future trigger, recorded in D28 and the status file: a live second
  review is DEFERRED, not owed — it runs only when conditions mature,
  and it must run on a real project the user knows well (bench toy
  tasks do not count: a second review on toy tasks cannot measure
  discrimination). Only if such a round actually runs and consistency
  meets the bar may `stable` and auto-approval be reconsidered. Until
  then, nothing is owed on this item. Release draft + QUALITY_SCORE
  rubric wordings synced to "advisory opinions only, never
  auto-approves". repo_checks `eval:rubric-advisory-only` pins the
  ruling. Follow-up fix `876b5f2`: the old eval test asserting
  provisional was updated to advisory-only (pytest 94/94 after).

## 4. Still awaiting user ruling (nothing else is open)

- **VERSION switch + tag (D35):** VERSION 0.2.1 → 0.3.0 + tag `v0.3.0`.
  Prepared only: `tools/check-release.py` passes on 0.2.1 today
  (VERSION/CHANGELOG/lock consistent, 42 lock entries);
  `docs/internal/release-checklist.md` carries the procedure (PR to
  main needs explicit user approval; main is frozen). NOT executed in
  this round: no VERSION change, no tag, no push, no PR, no merge.

## 5. Verification (final numbers, this round)

- `python3 tests/repo_checks.py`: **671 PASS / 0 FAIL** (worktree).
  Count walk: 662 (merge) → 666 (cost-gate +4) → 660 (P3: −6 template
  checks) → 669 (tier: +8 net §3t + 1 PARITY) → 670 (lint-rules check)
  → 671 (rubric-advisory-only check). Every step explained; no silent
  drift.
- Fresh clone (`git clone ~/workspace/agent-harness-phase0 -b
  feat/merge-v3 /tmp/fresh-merge-v3`, HEAD `aafc6a6`): clean tree,
  repo_checks **671 PASS** — also confirms D48/D60 (no check requires
  a gitignored file).
- Hook tests: **73 + 12 + 11 + 12 = 108**, server **5/5**.
- pytest: **94 passed** (69 at merge + 5 cost + 4 bootstrap-verify + 4
  check-clean + 3 lint-rules + 7 pass-gate behavior + 2 threshold
  normalization = 94; arithmetic checks out).
- Bench smoke: **OK** (`bash eval/run-bench.sh smoke`); missing-pytest
  path verified separately (PREFLIGHT FAILED + install line, exit 1).
- Deploy matrix (from the fresh clone): minimal / standard / full /
  `--comet-init` all exit 0; minimal ships gate without graph.py, no
  loop.py, 0 loop templates; standard and full ship graph.py +
  loop.py + 6 loop templates; minimal-over-standard migration removes
  graph/loop with `.bak.` backups; all shipped runners `--help` exit 0.
- `python3 tools/check-release.py`: OK (VERSION 0.2.1, CHANGELOG
  newest 0.2.1, lock 42 entries).
- Negative tests: true-lock guard present (repo_checks §5c); VERSION
  mismatch would fail check-release (not exercised by changing VERSION
  — the switch is user-gated, see §4).
- `python3 tools/lint-rules.py`: 5 PASS + LINT-006 WARN (expected
  SESSION_STATE zh-tw drift), exit 0.
- `python3 eval/check-thresholds.py`: t1–t4 12 groups ok, t5–t8 13
  groups no conclusion, no breach.
- `python3 tools/i18n-check.py`: pass (5 reminders + 1 [drift]).

## 6. Pre-release checklist (what remains, in order)

1. **VERSION switch + tag (D35)** — user approval required (see §4).
2. **Real CI run** — trigger `workflow_dispatch` on this branch from
   GitHub Actions; must include the Windows `ps-analyzer` job (this VM
   has no PowerShell; ps1 changes in this round are statically
   verified only: syntax mirrored from the sh logic, CRLF+BOM
   preserved, PARITY markers present). CI has never run for this
   branch; local runs mirror its steps but are not a substitute.
3. **Discriminating bench round (evidence item, NOT a tool-availability
   item)** — per-arm independent implementations × 3 rounds for
   t5–t8 (and t1–t4 if re-baselined). The existing matrices suffer a
   ceiling effect (tasks too easy; one implementation reused across
   arms), so they cannot prove the gate reduces false completions.
   This round deliberately did NOT run it: it needs fresh executors
   and is a pre-release special, not a code change.
4. **PR into main + merge** — only with the user's explicit approval
   (main frozen since 2026-10-28; note the revert-the-revert
   requirement: main's revert commit `1d3ecb7`/`88c8b79` must be
   reverted first before feat/merge-v3 content can land).
5. **Release notes final numbers** — re-verify on release day
   (repo_checks count, check-release, deploy smoke); do not copy the
   numbers from this document.

## 7. Deliberately NOT changed in this round

- No push, no merge to main, no PR into main, no tag (per standing
  rule + this task's explicit instruction).
- No change to loop/graph implementations (tier change is distribution
  only).
- No change to the true-lock rule, the cost-ledger warn-only tool, or
  the deploy profile skill membership (skills-profiles.json untouched).
- No switch to yunyi's 11-line SESSION_STATE format; no adoption of
  yunyi's all-2 Accept rule, auto-approve, or PIN_EXEMPT.
- No re-pinning of codegraph/comet/rtk to upstream tips.
- No discriminating bench round (see §6.3).
