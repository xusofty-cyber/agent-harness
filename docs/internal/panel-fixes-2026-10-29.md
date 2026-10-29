# Panel P0+P1 fix record — 2026-10-29 (branch `feat/merge-v3`)

> **Scope:** independent expert panel's P0 (3) + P1 (12) on `feat/merge-v3`
> only. P2 (11 items) is out of scope and was NOT done. All work on branch
> `feat/merge-v3` in `~/workspace/agent-harness-merge`.
> **Red lines honoured:** only `feat/merge-v3` pushed; no push to main, no
> PR into main, no merge into main, no tag. Remote main stayed `88c8b79`
> throughout. VERSION stays `0.2.1`.
>
> **Heads:** fixes landed at `e0dc2e8` (pushed, CI-tested); this record
> itself is the only commit on top of it. The record commit is docs-only
> and changes no code, but strictly the pushed HEAD after this record
> has no CI run of its own — the CI record below covers `e0dc2e8`.

## Per-item fixes (one commit each) and verification

- **P0-1 — event log tolerance** — `0b7e73c`.
  `gate/pass-gate.py` gained `EventsLogError`; `_read_events` raises it
  with line number + preview instead of a raw traceback; `_append_event`
  uses max integer seq + 1 (tolerates missing/non-integer seq); `main()`
  pre-validates the log for mutating commands (exit 2, clean message,
  no state change), read-only commands keep working for inspection.
  `gate/comet_adapter.py` writes full gate-format events
  (seq/ts/actor=`comet_adapter`/event/item_id/detail) and fails before
  mutating on a corrupt log. `.claude/hooks/stop-gate.mjs` scans max seq
  across the whole log and skips unparseable lines (§3k flags them).
  Verified in /tmp with the panel's probes: legacy seq-less last event
  no longer crashes start/verify; real comet import writes a complete
  event and later commands work; a bad line yields exit 2 with a clean
  message and the item provably stays `in_progress`. Regression tests:
  `tests/pass_gate_test.py` EventsLogToleranceTest (3),
  `tests/comet_adapter_test.py` (5).
- **P0-2 + P1-6 — graph fan-in return codes + result-branch protection** —
  `c3f386c` (same file, same class of problem, fixed together).
  `gate/graph.py` fan-in now refuses `--result` equal to `main`, `--base`,
  or the checked-out branch, refuses an already-existing result branch
  unless `--force` is given, and checks return codes for `branch -D`
  (only when rebuilding with `--force`), `checkout -b`, and each `merge`
  (on merge failure it records `blocked` with `stop_reason`
  `merge_conflict`, prints conflicted files, leaves the repo mid-merge
  for inspection, and never emits `merged`/`done`). New `--force` flag
  - docstring. Verified: `tests/graph_test.py` 7 pass, including a
  merge-conflict case that blocks without merged/done and leaves
  `UU shared.txt`, and result-protection cases (main refused with
  main's log still 1 commit; existing branch refused without `--force`,
  rebuilt with it).
- **P1-1 — terminate system requires runtime evidence** — `efe7109`.
  `gate/pass-gate.py` `cmd_terminate` system stage now requires evidence
  to exist, have `exit_code == 0`, and match the item's CURRENT
  verification command (otherwise `termination_failed` + exit 1, status
  unchanged); static and runtime successes each append a
  `termination_stage` event so a forged record is distinguishable from
  a real run. Verified: `tests/pass_gate_terminate_test.py` 14 pass,
  including forged termination (hand-written static+runtime true,
  verification `false`, no evidence) → exit 1, stays `in_progress`,
  and stale evidence after a command change → refused.
- **P1-2 — guard bypass closure** — `2843a86`.
  `.claude/hooks/guard.mjs`: `resolveProg` now skips sudo/env/timeout/
  nice options (value-options `-u/-g/-C/-D/-R/-t/-p/-U`, env
  `-u/-C/-S`, timeout `-s/-k` plus the duration operand, nice `-n`),
  with non-executing modes (`sudo -l/-v/-k`, `command -v/-V`,
  `--help/--version`) returning null instead of false positives;
  `-c alias.*` definitions now deny outright (was warn-only); xargs /
  find `-exec`/`-execdir` words are analysed as their own command;
  same-command variables are tracked at argv[0] / eval-argument
  positions (`G=$(which git); $G ...`, `x='git ...'; eval $x`); nested
  resolvers expand recursively (`$(echo $(which git))`). Also fixed
  `rawSegments` double-counting `$(` depth, which had left every later
  `;`/`&`/`|` treated as nested. Documented residuals (unchanged):
  cross-call variables, PATH shims, shell functions/aliases, eval of
  runtime-built strings — server-side branch protection is the
  boundary. Verified probe-by-probe: 11 new bypass DENY cases + 6
  harmless ALLOW cases; the alias test updated warn → deny; extra
  probes (`env -u`, `sudo -i`, `sudo --user=root`,
  `timeout --signal=KILL 5`, `command git`, `xargs -I{}`, `find
  -execdir`) all deny on force variants, allow on non-force variants.
  Hook suite: 90/90 in `tests/hooks.test.mjs`.
- **P1-3 — hard-stop enforcement point** — `8655fa7`.
  `eval/run-bench.sh` `setup` now calls `cost.py check` BEFORE any
  destructive work: exit 0 proceeds, exit 2 (BUDGET STOP) refuses with
  exit 2 and no dest dir created, any other gate exit also refuses
  (fail closed). Smoke goes through setup, so it is covered.
  `COST_LEDGER` / `COST_BUDGET` env overrides added as a test seam.
  Docs state the honest scope: `pass-gate.py verify` does NOT consult
  this gate, and the plain local JSONL ledger can be emptied/renamed
  around — policy gate, not tamper-proof enforcement
  (`eval/cost-budget.json` note + D57 implementation note; ruling
  unchanged). Verified: allow path proceeds (BUDGET OK, dest created);
  ceiling ledger (10 verifications) refuses exit 2 with no dest dir;
  corrupt budget JSON refuses exit 2 (gate-unavailable path).
- **P1-4 — cost.py self-crash** — `3eccc3a`.
  New shared `read_ledger()`: blank lines skipped, non-JSON and
  non-object lines counted, warned on stderr with line number +
  preview, and skipped — never a traceback. Sums use `_num(.get(...,
  0))`. `check` now writes `budget_stop` lines with
  duration_ms/verifications/retries = 0. Verified: panel probes (ledger
  with a `budget_stop` line + a non-JSON line) now return BUDGET OK
  with stderr warnings instead of KeyError/JSONDecodeError; cost tests
  7/7 (was 5/5).
- **P1-5 — validate crash + schema drift** — `df91d14`.
  `gate/pass-gate.py` `validate()`: type guard before the
  evidence-command comparison (non-dict verification no longer
  `AttributeError`s); `timeout_seconds` enforced 1..3600 (99999 used to
  pass); evidence objects require command/exit_code/ran_at/output_tail
  with correct types, plus override by/reason/at when present;
  `additionalProperties:false` enforced at top, item, verification,
  evidence, override and external_evidence levels; non-string ids now
  error instead of risking an unhashable lookup. The drift ran both
  ways: verify/terminate write `output_sha256` into evidence but the
  schema omitted it, so `gate/feature_list.schema.json` gains
  `output_sha256` (optional string; required list unchanged) instead
  of weakening the validator to reject the tool's own output. The
  never-referenced `ALLOWED` table was deleted (transitions are
  enforced per-command by status checks; noted where the table was).
  Verified: panel crash probe returns a clean error list, no crash;
  drift probe (timeout 99999 + missing ran_at/output_tail) now errors;
  extra-key probe errors; the tool's own evidence shape and the repo's
  own `gate/feature_list.json` validate clean. New
  `ValidateSchemaDriftTest` (4 tests). Note the fix itself caught a
  real second drift mid-work: strengthening the validator first broke
  one existing test, because verify/terminate write `output_sha256`
  and the schema omitted it — fixed by correcting the schema (above),
  not by weakening the validator. Gate tests after this commit: 43
  (pass-gate 17 + terminate 14 + graph 7 + comet_adapter 5).
- **P1-8 — DECISIONS donor table** — `d1442c2`. D47/D48/D54 rows now
  read "Superseded by D59/D60/D62" with the adopted scope, instead of
  "not adopted / not ported". No ruling changed.
- **P1-9 — D25 tier qualifier** — `2b83c3a`. D25 gained a note: the
  "both deploy scripts ship" sentence is qualified by D58 — graph/loop
  ship only on standard/full; minimal is the gate only.
- **P1-10 — D15/D28 contradiction** — `7508baa`. D15's "still owed"
  gained a footnote: superseded by D28 (live second review DEFERRED,
  not owed; runs only when conditions mature, on a real project the
  user knows well). D15 text otherwise unchanged.
- **P1-11 — release draft hard stop** — `e2dd194`.
  `docs/internal/release-v0.3.0.md`: the Phase 2 bullet now names the
  proxy ledger (warn-only per D12) as such, and a new D57 bullet states
  the accurate position — ceilings, exit-2 refusal of new verification
  runs, never killing in-flight runs, the run-bench.sh setup enforcement
  point (P1-3), and the ledger's tamper limit. Numbers left for P1-7.
- **P1-12 — D26 check guard** — `a8a5cb6`. repo_checks gained
  `archive-template-default`: `templates/comet.config.yaml` must set
  `archive_confirmation: automatic` (D26). Only the template is pinned
  (a project's own `.comet/config.yaml` may choose `required`).
  Negative test verified: template flipped to `required` →
  `[FAIL] archive-template-default`; restored → `[PASS]`.
- **P1-7 — release-facing numbers** — `31c6555` (done LAST, from the
  final measurements below, not copied from older numbers).
  QUALITY_SCORE.md: repo_checks 662 → 672, gate tests 23 (pass-gate 3 +
  terminate 11 + graph 5 + comet_adapter 4) → 43 (17 + 14 + 7 + 5),
  hook tests 108 → 125, stale "pass-gate has only 3 unit tests"
  rationale rewritten. Release draft: repo_checks 599 → 672, hooks
  56 + 10 + 12 → 125 (90 + 12 + 11 + 12, + 5 server tests), pytest 109
  added, deploy smoke now covers all three profiles. Scores unchanged.
- **Docs (repo convention)** — `e0dc2e8`. CHANGELOG `[Unreleased]`
  entry for this round. `check-release.py` OK (VERSION 0.2.1, lock 42
  entries).

## Final verification (all measured, not copied)

- `python3 tests/repo_checks.py`: **672 PASS, 0 fail** (was 671; +1 =
  `archive-template-default`).
- Hook tests: **125 pass** (`hooks.test.mjs` 90 + `hooks-write` 12 +
  `hooks-gate` 11 + `hooks-lifecycle` 12; was 108) + server 5/5.
- `python3 -m pytest tests/`: **109 passed** (was 94; +15 = P0-1 4,
  P0-2 2, P1-1 3, P1-5 4, P1-4 2). Gate tests within it: **43**
  (pass-gate 17 + terminate 14 + graph 7 + comet_adapter 5).
- Three-tier deploy smoke: minimal / standard / full all exit 0;
  minimal correctly ships no `gate/graph.py`, `tools/loop.py`, or
  `templates/loop/` (D58); standard/full ship them.
- Worktree clean at push; every fix in its own commit (see list above).

## Real CI (P0-3) — run links and dual-task conclusions

- **Run:** <https://github.com/xusofty-cyber/agent-harness/actions/runs/40792827823>
  — workflow `CI`, `workflow_dispatch` on `feat/merge-v3` at `e0dc2e8`
  (triggered with `gh workflow run CI --ref feat/merge-v3` after pushing
  only that branch).
- **ps-analyzer (Windows): SUCCESS.** First real Windows run on this
  branch: the PowerShell scripts pass PSScriptAnalyzer. This closes the
  "ps1 never executed or analysed" half of P0-3.
- **lint-and-test (Ubuntu): FAILURE at the Markdown-lint step.**
  Cause (verified, not assumed): 45× MD004 list-style errors in TWO
  files, none of them from this round —
  `docs/internal/merge-review-optimization-2026-10-29.md` (44×, dash
  where plus expected; last touched `a76430b`, prior round) and
  `DECISIONS.md:927` (1×, plus where dash expected; the D62 `+`
  continuation line from commit `b5c0c4a`, prior round). This round's
  own markdown edits add no new list markers (release draft and
  CHANGELOG use `-` consistently with their files; DECISIONS edits are
  table cells and footnote prose; QUALITY_SCORE edits are table rows),
  so no error in the log originates from this round. Because later
  steps (ShellCheck, hook tests, repo checks, deploy smoke) were
  skipped after the lint failure, CI has NOT yet validated those steps
  on the runner — they pass locally (see final verification above).
- **Handling per the task rule:** the failure is unrelated to this
  round's changes, so it was NOT fixed-and-retriggered (the rule allows
  at most one re-trigger, and only for failures this round caused).
  Reported honestly instead. **Follow-up for a green CI record:** fix
  the 45 pre-existing MD004 lines (or normalise the two files' list
  styles) and re-trigger `workflow_dispatch`; that is a lint-debt
  cleanup outside this round's P0+P1 scope, not a fix-round defect.
- P0-3 status: **partially closed** — a real CI run now exists for this
  branch for the first time (both jobs ran; Windows passed), but the
  run is red on pre-existing lint debt, so "CI green" is NOT claimed.

## Not fixed (with reasons)

- **P2 (11 items, P2-1 – P2-11):** out of scope for this round by the
  task's red line; deliberately not done opportunistically. Includes
  Stop second-release authentication, decorative evidence hashing,
  minimal-overlay backup prompting, init placeholder false-rejects,
  event-seq locking, D19/D23/D55 superseded footnotes, FR/DE workflow
  mentions, D35 characterisation, offline lock-pin tampering, and the
  bare-`pytest` fixture mis-collection note.
- **P0-3 "CI green":** not achieved — see the CI section above. The red
  is pre-existing lint debt, not this round's code, and re-triggering
  without fixing that debt would reproduce the same red run.
- **Discriminating bench round (per-arm independent implementations × 3
  rounds) and rtk pin upstream recheck:** pre-release specials from the
  panel's path advice, not P0/P1 items; still owed, not done here.
- **VERSION switch + tag:** still waiting for merge-to-main approval
  as part of the release action (user ruling 2026-10-29); not done.

## Confirmation

- Merged to main: **no.** PR into main opened: **no.** Tag created:
  **no.** Branches pushed: **`feat/merge-v3` only** (`dbe9c5f` →
  `e0dc2e8`, plus this record commit). Remote main verified unchanged
  at `88c8b79` after the push. Local main untouched (still `52df27b`,
  stale, never pulled, never modified).
