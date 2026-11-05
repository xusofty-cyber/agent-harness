# Phase 4 verification record (2026-10-28)

Branch: `feat/phase0-v3`. Executor: Muse Spark, this VM. All numbers below
were measured on this branch unless marked otherwise.

## 4-1 — Skill tiers

- `skills-profiles.json` is the single source of truth; `deploy-agents.sh`
  (`--profile`) and `deploy-agents.ps1` (`-Profile`) read it.
- Measured deploys to empty target dirs (`eval/run-bench.sh measure-load`,
  2026-10-28):

  | Profile | Skill dirs | Skills-only bytes | Deployed-total bytes |
  |---|---|---|---|
  | minimal (default) | 10 | 212,777 | 700,569 |
  | standard | 18 | 301,118 | 877,254 |
  | full | 38 (heavy gated) | 757,688 | 1,790,382 |
  | full + `--include-heavy-skills` | 40 | 1,960,329 (disk sum) | — |

  Full deployed-total re-measured at 1,790,382 vs Phase 3's 1,790,367
  (15 bytes, a deployed file changed since — current figure is the one
  to quote). Skills-only bytes count `.agents/skills/` on disk;
  deployed-total counts the whole deployed directory. No token claim is
  made from either number.
- Bad profile exits 2 (`--profile bogus`); `--profile=standard` works;
  default (no flag) deploys 10.
- Core-10 selection basis: reference counts below (measured), sizes
  (measured), bench task-type affinity (provisional), no usage telemetry
  (U1). Full rationale per skill: `docs/internal/skill-tiers.md`.

### Reference counts (2026-10-28, EN+ZH sources only)

Columns: `tmpl` = files under `templates/agents/` (EN+ZH) referencing the
skill; `faq` = FAQ guide (EN+ZH); `multi` = Multi-Tool guide (EN+ZH);
`guide` = Skills Usage Guide (EN+ZH, listing baseline = 2 for every
skill). 16 skills have `tmpl` > 0 (triggered by a rule template); 24 are
guide listings only.

| Skill | tmpl | faq | multi | guide | Bytes |
|---|---|---|---|---|---|
| brainstorming | 2 | 1 | 0 | 2 | 73,946 |
| caveman | 2 | 0 | 1 | 2 | 6,574 |
| codegraph | 2 | 1 | 1 | 2 | 1,388 |
| comet | 2 | 0 | 1 | 2 | 6,299 |
| cross-tool-memory | 0 | 1 | 0 | 2 | 2,413 |
| diagnosing-superpowers | 0 | 0 | 0 | 2 | 40,841 |
| dispatching-parallel-agents | 0 | 1 | 0 | 2 | 6,078 |
| docx | 0 | 0 | 2 | 2 | 1,128,695 |
| engineering-docs | 2 | 0 | 0 | 2 | 61,174 |
| executing-plans | 0 | 0 | 0 | 2 | 23,060 |
| finishing-a-development-branch | 2 | 0 | 0 | 2 | 7,781 |
| git-advanced | 0 | 0 | 0 | 2 | 5,580 |
| living-documentation | 2 | 0 | 0 | 2 | 39,685 |
| open-code-review | 2 | 1 | 1 | 2 | 24,627 |
| openspec-apply-change | 0 | 0 | 0 | 2 | 11,159 |
| openspec-archive-change | 0 | 0 | 0 | 2 | 16,570 |
| openspec-bulk-archive-change | 0 | 0 | 0 | 2 | 22,296 |
| openspec-continue-change | 0 | 0 | 0 | 2 | 9,786 |
| openspec-explore | 0 | 0 | 0 | 2 | 22,797 |
| openspec-ff-change | 0 | 0 | 0 | 2 | 11,174 |
| openspec-new-change | 0 | 0 | 0 | 2 | 5,870 |
| openspec-onboard | 0 | 0 | 0 | 2 | 18,406 |
| openspec-propose | 0 | 0 | 0 | 2 | 16,239 |
| openspec-sync-specs | 0 | 0 | 0 | 2 | 15,755 |
| openspec-update-change | 0 | 0 | 0 | 2 | 10,994 |
| openspec-verify-change | 0 | 0 | 0 | 2 | 18,345 |
| option-review | 2 | 0 | 0 | 2 | 6,163 |
| pdf | 0 | 0 | 2 | 2 | 58,692 |
| ponytail | 2 | 0 | 1 | 2 | 3,492 |
| receiving-code-review | 0 | 0 | 0 | 2 | 6,203 |
| requesting-code-review | 2 | 1 | 0 | 2 | 9,423 |
| rtk | 2 | 0 | 2 | 2 | 1,333 |
| subagent-driven-development | 0 | 0 | 0 | 2 | 59,739 |
| systematic-debugging | 2 | 1 | 1 | 2 | 40,842 |
| test-driven-development | 2 | 1 | 1 | 2 | 17,846 |
| using-git-worktrees | 0 | 0 | 0 | 2 | 6,813 |
| using-superpowers | 0 | 0 | 0 | 2 | 20,630 |
| verification-before-completion | 2 | 1 | 0 | 2 | 3,646 |
| writing-plans | 2 | 0 | 0 | 2 | 10,335 |
| writing-skills | 0 | 0 | 0 | 2 | 107,640 |

Note: the ablation dependency gate (`tools/ablation.py check`) uses a
stricter match than this table (it also catches path references like
`.agents/skills/<name>`), so `cross-tool-memory` is BLOCKED there even
though this table shows `tmpl` 0 for it. The gate, not this table, decides
ablatability.

## 4-2 — i18n

- Old §6 16-pair H2 symmetric hard check removed; replaced by EN/ZH
  parity (4 pairs, hard) + `tools/i18n-check.py` (status file).
- `i18n-check.py` run 2026-10-28: exit 0, 9 reminders (README ×3,
  Skills Usage Guide ×3, Global AGENTS ×3 — all `stale`, source moved
  after last sync; shas from git archaeology, see
  `docs/internal/i18n-status.md`). 12 rows `in-sync`.
- `--spot-check 2 --seed 7` ran: samples print, but sections are matched
  by index and translations do not always share the source's section
  order (e.g. target §7 "Décisions clés" vs source §7 "Constraints").
  Known limitation: spot-check shows both sides for a human to judge; it
  does not assert section alignment.
- History note: the 4-1d commit (guide tier sections) was red on the old
  §6 check (EN `##` 12→13, FR/DE/ZH-TW still 12) until 4-2 landed. The
  old check correctly caught the drift; 4-2 is the response, not a
  bypass.

## 4-3 — sh/ps1 decision

- D17 recorded: keep dual, sh-first, review 2027-04-28, with three
  revisit triggers. Cost data: deploy 1,592 + 1,483 lines, pipeline
  1,136 + 1,058 lines (5,269 total), 54 PARITY markers. U3 settled.

## 4-4 — Ablation, first run (`writing-skills`, 2026-10)

- Dependency gate: CLEAR (no template/hook references). Gate verified
  non-trivial: `systematic-debugging` and `ponytail` both BLOCKED
  (Project AGENTS template references); `cross-tool-memory` BLOCKED (path
  reference).
- 12 pack-arm runs (4 tasks × 3 reps), component removed from
  `.agents/skills` and `.claude/skills` in each run dir (verified absent
  after every prepare): **12/12 pass, 0 false completions, all first-try,
  verify attempts 1, rounds 1**. Records:
  `eval/results/ablation/*_pack-no-writing-skills_rep*.json`.
- Duration caveat (read before quoting any duration): three timing
  conventions were used — T1 batched (24/25/26 s, includes batch-prepare
  latency; breaches the 10 s red-line as an artifact), T2 rep1 interleaved
  (2 s), the other 8 single-invocation (0–1 s at 1-second resolution,
  shell-execution time only). Duration and rounds are therefore NOT the
  verdict basis for this run. Verdict rests on outcome + false
  completion: NO REGRESSION. Full analysis in the report's operator
  correction section.
- Recommendation: CANDIDATE FOR REMOVAL (bench only). Human decision:
  PENDING (owner). Size at stake: 107,640 bytes.
- Also verified during this run: no deployed skill file contains
  `multiply`, so the T3 pack-arm acceptance is achievable (checked in a
  pack run dir before running T3).

## Validation (final tree, 2026-10-28)

- `python3 tests/repo_checks.py`: **554 PASS, 0 FAIL** (Phase 3: 544).
- Hook tests: `hooks.test.mjs` 56 pass, `hooks-gate.test.mjs` 10 pass,
  `hooks-write.test.mjs` 11 pass, `hooks-lifecycle.test.mjs` 12 pass.
- Python unit tests: `sync_skills_test.py`, `doc_impact_test.py`,
  `cost_ledger_test.py` all OK.
- Deploy smoke: minimal/standard/full/default/bad-profile verified above;
  `eval/run-bench.sh smoke` passes.
- `bash -n` passes on both shell scripts; `node --check` on hooks.
- NOT verified locally: `shellcheck` / `markdownlint` (not installed —
  CI is authoritative, as in Phases 0–3); PowerShell changes are static
  only (no `pwsh` on this VM; PARITY marker + `ConvertFrom-Json` usage
  checked by reading, not by running).

## Phase 4 Go gate (v2 acceptance criteria)

| # | Criterion | Result |
|---|---|---|
| 4-1 | Default deploy ≤10 skills; Skills Usage Guide rewritten per tier | ✅ PASS — default deploys 10; EN+ZH guides have tier sections, CI §3r asserts them against `skills-profiles.json`. |
| 4-2 | Symmetric hard check removed; CI time/failure-rate clearly down; EN/ZH still strictly synced | ⚠️ PARTIAL — check removed, EN/ZH parity kept and passing; "CI time/failure-rate down" is **not measured** (no CI run observed from here). The mechanism is in place; the CI effect needs a CI run to confirm. |
| 4-3 | Decision + review date in DECISIONS.md | ✅ PASS — D17, review 2027-04-28, three triggers. |
| 4-4 | Monthly ablation process; ≥6 recorded ablations in 12 months | ⚠️ PROCESS LANDED — tooling + first run + queue + report all exist; the "≥6 in 12 months" cadence cannot be complete on day one. Next run due 2026-11 (`diagnosing-superpowers`). |

**Go-gate conclusion: Phase 4 is done as a phase of work; two items stay
open as tracked follow-ups, not as blockers:** (1) confirm the CI
time/failure effect of the 4-2 change on the next CI run; (2) the ablation
cadence (next run 2026-11). Neither blocks merging the branch. The
provisional core-10 list is explicitly marked for re-selection after the
bench matrix completes (review 2026-11-28, D18).
