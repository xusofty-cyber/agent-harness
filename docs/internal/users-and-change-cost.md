# Users and change cost — agent-harness (Phase 0, 0-10)

> **Provisional.** This page is a working hypothesis, not a finding. It is
> sourced from the repository itself (history, structure, and the Phase 0
> measurements below); there is no usage telemetry, survey, or interview
> behind it. The repo owner is the known maintainer — confirm, correct, or
> replace this portrait with the owner before treating it as a decision
> input. Do not invent users.

## Provisional user portrait

- **Maintainer / primary user: the repo owner** (github.com/xusofty-cyber).
  Single-maintainer project: 453 commits in about four weeks
  (2026-09-28–10-22), tags v0.1.0–v0.2.1, no other contributors visible
  in the history. The owner builds and dogfoods the pack across their own
  projects and AI coding tools.
- **Secondary users (assumed, unconfirmed):** developers who run several AI
  coding tools side by side — Claude Code, Codex, Antigravity, Copilot,
  Zed, Pi/OpenCode — and want one set of rules and skills deployed to all
  of them instead of maintaining per-tool copies. Evidence: the deploy
  scripts target 12 bridge tools plus 7 native AGENTS.md readers, and the
  guides are maintained in five languages (EN, ZH, ZH-TW, FR, DE).
- **What they care about (inferred from the repo's own rules):** rules that
  stay generic and portable across tools; no silent drift between the
  PowerShell and bash deploy scripts (the PARITY table in
  `tests/repo_checks.py`); numbers in docs that match the disk; nothing
  that costs tokens while idle.
- **What is NOT known:** how many people use the pack, which tools they
  actually deploy to, which skills they use, or which rules they change.
  There is no telemetry and no feedback channel in the repo. Until that
  exists, the "core ≤10 skills" list (planned for Phase 3) cannot be set
  from data — see U1 in DECISIONS.md.

## Measured cost of one rule change

Two measurements, both reproducible from this branch.

### 1. A one-number change: fixing the skill count (commit 7aadadf, 0-1)

Changing one fact — "the repo has 40 skills, not 44" — touched:

| | |
|---|---|
| Files changed | 17 (16 docs + 1 new script) |
| Insertions / deletions | 214 / 46 (of which 156 insertions are the new `tools/count-skills.py`) |
| Doc-only edits | 16 files, ~58 insertions / 46 deletions — mostly one-line number swaps |
| Languages touched | all 5 READMEs + EN/ZH Skills Usage Guide + all 5 Panorama Guides |

Takeaway: even a trivial fact lives in ~16 places because the READMEs and
guides are maintained in five languages and repeat the same numbers. This
is why Phase 0 added `tools/count-skills.py` + the repo_checks §3i
assertion: the next count change should be one edit in the script's
EXPECTED table plus the doc sweep, and CI will catch a missed copy.

### 2. Reference fan-out of one sample rule: `token-discipline`

`grep -rl token-discipline` across the repo (2026-10-28, branch
`feat/phase0-v3`):

| Category | Files |
|---|---|
| `templates/agents/` (distributable rule templates) | 5 |
| `docs/guides/` | 10 |
| `README*.md` | 5 |
| `.agents/skills/` (the skill that documents it) | 1 |
| Dated snapshots (`docs/internal/SESSION_RESUME*.md`, history) | 2 |
| **Total** | **23** |

No references in `deploy-agents.*`, `run-pipeline.*`, `tests/`, the root
`AGENTS.md`, or `.claude/` — the rule is a doc/template concern, not a
script or check concern. A rename or behaviour change to `token-discipline`
therefore means editing ~21 live files (5 templates + 10 guides + 5
READMEs + 1 skill doc), plus updating the 2 historical snapshots only if
the project decides snapshots are living documents (they are not — leave
them).

### Rule of thumb for Phase 1+

- **One fact, one place:** new facts get a single source of truth (script
  or lock file) and a CI assertion before they are quoted in docs.
- **Budget ~20 files** for a rule rename/reword that is referenced in
  templates + guides + READMEs; budget ~5 files if it only lives in the
  templates.
- **Five-language cost is the multiplier:** every user-facing sentence in
  EN/ZH costs a matching edit in ZH-TW/FR/DE unless D3's freeze is lifted
  or the sentence is EN/ZH-only by decision.
