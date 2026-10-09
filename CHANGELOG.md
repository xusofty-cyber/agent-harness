# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Releases are tagged `vX.Y.Z` from `main` by the maintainer.

## [Unreleased]

### Added
- `tools/doc-impact.py`: living-documentation impact analysis — matches changed
  files against doc `modules` globs, walks `depends_on` upward, and reports
  staleness via `last_verified_commit` (🔴 must-update / 🟡 review / 🟢 in-sync);
  advisory only, wired into comet Verify/Archive gates.
- `tests/repo_checks.py`: `doc-frontmatter` check — `docs/{specs,architecture,
  reference,guides,adr}/` markdown files must declare valid traceability
  frontmatter (`id`/`type`/`status`/`modules`), with `type` matching its tier.
- New local skill `living-documentation` (`version: 0.1.1`): 4-tier living documentation suite (`docs/{specs,architecture,reference,guides}`) with YAML frontmatter-based code-doc bidirectional traceability (`modules`, `depends_on`), L0/L1/L2 change impact thresholds, and deep integration with Comet change lifecycle (Open/Build/Verify/Archive) and OpenSpec workflows.
- Four production-grade templates under `.agents/skills/living-documentation/templates/`: `srs.template.md`, `architecture.template.md`, `reference.template.md`, and `guide.template.md`.
- Two reference guides under `.agents/skills/living-documentation/references/`: `comet-integration.md` and `traceability-matrix.md`.
- `deploy-agents.sh` and `deploy-agents.ps1`: initialized living documentation scaffold (`docs/{specs,architecture,reference,guides,adr}`) on deployment; added `LivingDocScaffold` parity check in `tests/repo_checks.py`.
- Updated `Project AGENTS.md` and `.agents/rules/engineering-spec.md` with living documentation and code-doc traceability gates.
- `deploy-agents.sh` and `deploy-agents.ps1`: added `-m` / `--ai-memory-init` (`-AiMemoryInit`) flag to optionally initialize `.ai-memory.toml` for target projects (inferring `workspace` and `project`), and sync `.ai-memory.toml.example` as reference.
- New local skill `option-review` (`version: 0.1.1`): pre-decision review of
  multiple candidate approaches. Fans out isolated reviewers across five
  dimensions (security, engineering, reversibility, simplicity, cross-tool)
  and returns a decision matrix; includes single-agent CoT fallback when subagents
  are unavailable, and impact thresholding to avoid over-triggering on minor code choices;
  complements `requesting-code-review` (which reviews completed work).
- `VERSION` file (single source of truth for the release version);
  `tests/repo_checks.py` checks it matches the newest `CHANGELOG.md` version.
- `tests/repo_checks.py`: `skill-version` check — in-repo-authored skills must
  declare semver `version:` in `SKILL.md` frontmatter, matching `skills-lock.json`.
- `cross-tool-memory` skill: `version: 0.1.0` (first versioned skill).

### Changed
- Synced 41 native skills count and in-repo skills descriptions across
  `README.md`, `README_zh.md`, root `AGENTS.md`, and the bilingual
  `Tools Practical Usage and Skills Panorama Guide` pairs.

### Fixed
- `setup-ai-memory.sh` / `.ps1`: pass `--no-skills` to
  `ai-memory install-instructions` — this repo curates `cross-tool-memory`
  as its only memory skill; upstream managed skills must not be dropped
  into `.agents/skills/` (they would break the `skills-lock.json`
  consistency check and leak into downstream deploys).
- `tests/repo_checks.py`: new `exec-bit` guard asserting `deploy-agents.sh`
  and `setup-ai-memory.sh` are `100755` in the git index — the GitHub
  contents API resets the exec bit to `100644` on every content push, so
  restore locally with `git update-index --chmod=+x` after API-driven PRs.
- `docs/internal/SESSION_STATE.md`: updated from the stale
  pre-merge state to the `v0.1.0` closed state.

## [0.1.0] - 2026-10-08

First tagged release.

### Added
- GitHub Actions CI (`.github/workflows/ci.yml`): markdownlint, shellcheck,
  `node --check`, hook behavior tests, repo static checks, and a
  `deploy-agents.sh` smoke test on ubuntu; PSScriptAnalyzer (Error gate) on Windows.
- `tests/hooks.test.mjs`: 12 black-box tests driving `.claude/hooks/guard.mjs`
  through the Claude Code PreToolUse stdin JSON protocol.
- `tests/repo_checks.py`: JSON/TOML validity, `SKILL.md` frontmatter
  (`name`/`description`), `deploy-agents.ps1`/`.sh` feature-parity markers,
  and `skills-lock.json` ↔ skill directory consistency.
- `tests/repo_checks.py`: bilingual `##` section-count parity check for the
  EN/ZH guide pairs.
- `setup-ai-memory.sh` / `setup-ai-memory.ps1`: pin the validated ai-memory
  version (currently `2.6.0`); refuse to configure on mismatch unless
  `AI_MEMORY_ALLOW_OTHER_VERSION=1` is set.
- `CONTRIBUTING.md`: bilingual doc sync policy, template-genericity rule,
  dual-script parity rule.
- `docs/internal/`: home for this repository's own dev notes
  (`PROJECT_CONTEXT.md`, `SESSION_STATE.md`, `SESSION_RESUME.md`), moved out of
  the distribution root.
- Root `AGENTS.md`: dogfood entry point describing this repository for tools
  that auto-load it.
- `skills-lock.json`: added missing `cross-tool-memory` entry.

### Changed
- Chinese guide filenames are now ASCII with a `.zh.md` suffix
  (`Multi-Tool Deployment and Configuration Guide.zh.md`,
  `Tools Practical Usage and Skills Panorama Guide.zh.md`); all cross-references updated.
- Removed the two `docs/BRANCH_COMPARISON*` documents: the branches are merged,
  and their content is summarized in this changelog.
- Merged `long-term-memory-governance`: cross-tool memory governance
  (`cross-tool-memory` skill, optional local ai-memory backend),
  safe global-rule sync (preserve by default, timestamped backup on `-Update`),
  Codex global support, Antigravity 2.0/CLI/IDE dual entry, and Honest Limits.
- `.claude/hooks/guard.mjs`: fixed `git add .` never matching
  (`(-A|\.)\b` has no word boundary after `.`); `rm` guard now covers `-R`
  and `-r` at end-of-command, without flagging files like `rm -report`.
- `.agents/rules/git-workflow.md`: trunk branch is now a `<DEFAULT_BRANCH>`
  placeholder instead of hardcoded `develop`.
- README skill count corrected to the actual number of skill directories.

### Fixed
- 4 broken table-of-contents anchors, 10 fenced code blocks missing language
  tags, duplicate headings, and list-style inconsistencies found by markdownlint.
- 2 shellcheck warnings in `deploy-agents.sh` (SC2034 unused `line`, SC2155
  `local` masking return value).
