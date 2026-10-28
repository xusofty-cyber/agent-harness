# Skill tiers — deploy profiles (Phase 4, 4-1)

> **Provisional.** The tier lists below are a first cut from evidence the
> repo actually has. There is **no usage telemetry** (U1 in DECISIONS.md):
> nobody has measured which skills anyone invokes. Every selection below
> is tagged with the kind of evidence behind it; anything tagged
> `provisional` is a judgement call to be re-tested, not a finding.
> Re-selection is scheduled after the 36-run bench matrix completes
> (pack/gate arms, Phase 3 follow-up); review date **2026-11-28**.

## The profiles

Single source of truth: `skills-profiles.json` at the repo root.
`deploy-agents.sh` / `deploy-agents.ps1` read it; `tests/repo_checks.py`
§3r asserts it. Edit membership there, never in the scripts or guides.

| Profile | Skills | Skills-only bytes (measured 2026-10-28) | Default? |
|---|---|---|---|
| `minimal` | 10 | 212,777 | **yes** (`--profile` unset) |
| `standard` | 18 | 301,118 | no |
| `full` | 40 | 1,960,329 | no |

`full` without `--include-heavy-skills` / `-IncludeHeavySkills` deploys 38
skills (docx + brainstorming stay out; Phase 0, 0-9). Skills-only bytes
count `.agents/skills/<name>/` on disk; the deployed project directory is
larger (rules, templates, hooks) — Phase 3 `measure-load` reported the
deployed directory at 1,790,367 bytes for the old 38-skill default. Do not
compare the two numbers as if they measured the same thing.

## What each tier ships beyond skills (D58, user final ruling 2026-10-29)

Skills are only half the deploy. The gate/loop layers follow the same tiers:

| Profile | Gate itself | Orchestration (graph + loop) |
|---|---|---|
| `minimal` (default) | yes — `pass-gate.py`, `comet_adapter.py`, schema, init template | **no** — `gate/graph.py`, `tools/loop.py`, `templates/loop/` are not shipped |
| `standard` | yes | yes |
| `full` | yes | yes |

In short: minimal = the gate itself; standard = the gate + orchestration;
full = everything. This is distribution only — the loop/graph
implementations are untouched. Guarded by `tests/repo_checks.py` §3t
(per-tier file-set assertions) and the `TierGateGraphLoop` PARITY row.

**Migration:** a project previously deployed with `minimal` that already
has graph/loop files will have those files **removed** on re-deploy with
`minimal` (each file is backed up with a timestamped `.bak.` copy by the
deploy scripts first). To keep them, re-deploy with `--profile standard`
(`-SkillProfile standard`).

**No token-saving claim is made here.** Bytes are bytes, not tokens; no
host exposes a programmatic token API (see
`docs/internal/token-adapters.md`). If a future measurement shows a token
difference, it will be recorded with its method, not asserted from bytes.

## Minimal (default) — 10 skills

Basis tags: `[measured]` = a real run or a real wiring in this repo;
`[dependency]` = the skill is referenced by a distributable rule template
(`templates/agents/` EN+ZH sources, counted 2026-10-28);
`[provisional]` = judgement call, no usage data.

| Skill | Bytes | Basis |
|---|---|---|
| `verification-before-completion` | 3,646 | [measured] Phase 1 dogfood: the gate's verify discipline; the rubric requires re-running acceptance, never trusting the claim. [dependency] Referenced by Project AGENTS template + FAQ guide. |
| `systematic-debugging` | 40,842 | [dependency] Project AGENTS template + FAQ + Multi-Tool guide. [provisional] Task-type affinity: T1 bugfix. |
| `test-driven-development` | 17,846 | [dependency] Project AGENTS template + FAQ + Multi-Tool guide. [provisional] Task-type affinity: T2 feature. |
| `living-documentation` | 39,685 | [measured] `tools/doc-impact.py` is wired to it (dual-copy sync, §3e). [dependency] Project AGENTS template. [provisional] Task-type affinity: T4 docs+code sync. |
| `writing-plans` | 10,335 | [dependency] Project AGENTS template. |
| `executing-plans` | 23,060 | [provisional] Completes the pair with `writing-plans`; a plan skill without its execution half is a dead end. Guide-listed only. |
| `using-git-worktrees` | 6,813 | [provisional] The P01 isolation method the benchmarks use is worktree-based; the harness's own evaluation depends on it. Guide-listed only. |
| `subagent-driven-development` | 59,739 | [provisional] Sub-agents are one of the L13 six primitives; the largest single SKILL.md in the repo (32,577 B) — kept despite its size, flagged for the first ablation review. Guide-listed only. |
| `requesting-code-review` | 9,423 | [dependency] Project AGENTS template + FAQ guide. |
| `codegraph` | 1,388 | [measured] Hook integration: `.claude/settings.json` runs `codegraph prompt-hook`. [dependency] Project AGENTS template. |

What minimal deliberately leaves out: the whole OpenSpec family (12 skills,
a complete workflow, not a core discipline), the Comet adapter (the gate is
self-owned; Comet is an optional runtime — D1), document processing
(docx/pdf), and the superpowers meta-family. If a project needs one of
those, that is what `standard` / `full` are for.

## Standard — minimal + 8

| Skill | Bytes | Basis |
|---|---|---|
| `comet` | 6,299 | [dependency] Project AGENTS template. [measured] Phase 2: Comet CLI pinned to 0.5.1, interrupt-recovery verified. Standard is where the optional runtime lives (v2 4-1). |
| `openspec-new-change` | 5,870 | [provisional] Entry point of the OpenSpec change loop. |
| `openspec-propose` | 16,239 | [provisional] Change-loop step. |
| `openspec-apply-change` | 11,159 | [provisional] Change-loop step. |
| `openspec-verify-change` | 18,345 | [provisional] Change-loop step; pairs with the gate's verify discipline. |
| `openspec-archive-change` | 16,570 | [provisional] Change-loop close-out. |
| `finishing-a-development-branch` | 7,781 | [dependency] Project AGENTS template. |
| `dispatching-parallel-agents` | 6,078 | [dependency] FAQ guide. Pairs with `subagent-driven-development`. |

The other 7 OpenSpec skills (`explore`, `continue-change`,
`update-change`, `sync-specs`, `ff-change`, `onboard`,
`bulk-archive-change`) stay in `full` only: they extend the loop, they are
not the loop.

## Full — all 40

Everything on disk, including the OpenSpec remainder, the superpowers
family (`using-superpowers`, `diagnosing-superpowers`), `engineering-docs`,
`open-code-review`, `option-review`, `writing-skills`, `git-advanced`,
`receiving-code-review`, `cross-tool-memory`, `caveman`, `ponytail`, `rtk`,
`pdf`, and the two heavy skills (gated by the heavy flag).

## How the reference counts were produced (reproducible)

2026-10-28, branch `feat/phase0-v3`, script in the Phase 4 work log:
count backticked/mention references per skill in `templates/agents/` (EN+ZH
sources only), the FAQ guide (EN+ZH), the Multi-Tool guide (EN+ZH), and
the Skills Usage Guide (EN+ZH). Result: 16 skills are referenced by a rule
template (Project AGENTS), 24 appear only as guide listings. The full table
is in the Phase 4 verification record
(`docs/internal/phase4-verification.md`).

## Re-selection method (after the bench matrix completes)

1. Run the pack and gate arms (24 runs) — the missing Phase 3 cells.
2. For each skill, record: (a) was it invoked during a bench run (agent
   self-report + `gate/cost-ledger.jsonl` tool-call log where present);
   (b) does a bench task fail without it (ablation, see
   `tools/ablation.py`); (c) template-reference count (re-run the count
   above); (d) size.
3. A skill stays in minimal only if it meets at least one of: invoked in a
   bench run, required by a bench ablation, or referenced by a rule
   template. Everything else is a candidate for demotion to `standard` or
   `full`, decided by the owner — not by the script.
4. Review date: **2026-11-28**. If the matrix is still unmeasured then,
   the review re-runs the reference count and defers the usage-based
   re-selection again, in writing, rather than inventing usage data.
