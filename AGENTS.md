# AGENTS.md — agents-living (this repository)

> This file describes **the agents-living repository itself** for tools that
> auto-load a root `AGENTS.md` (Antigravity, Codex, Zed). The *distributable
> rule templates* live in `Global AGENTS.md`, `Project AGENTS.md`,
> `Directory AGENTS.md` and `.agents/rules/` — this file is not one of them.

## What this repo is

Reusable AI coding-rule templates, Claude Code hooks, 40 native skill
directories, and one-click deployment scripts (`deploy-agents.ps1` / `.sh`)
for Claude Code, Codex, Antigravity, Copilot and Zed. MIT licensed.

## Working in this repo

- **Templates stay generic**: never hardcode a specific project's architecture,
  branch names, or business facts into `Global/Project/Directory AGENTS.md` or
  `.agents/rules/`. See `CONTRIBUTING.md`.
- **Two scripts, one feature set**: `deploy-agents.ps1` and `deploy-agents.sh`
  must stay in sync — extend the `PARITY` table in `tests/repo_checks.py`
  when adding a feature.
- **Bilingual docs**: guides come in EN/ZH pairs; change both sides in one PR.
- **Checks**: `node tests/hooks.test.mjs`, `python3 tests/repo_checks.py`;
  CI also runs markdownlint, shellcheck and a deploy smoke test. Keep `main` green.
- **This repo's own notes** live in `docs/internal/` (not the distribution root).
- Changelog entries go under `[Unreleased]` in `CHANGELOG.md`.

## Key paths

- `.agents/rules/` — modular sub-rules (engineering, git, security, tokens)
- `.agents/skills/` — 40 skill directories (openspec ×16, superpowers ×15, …)
- `.claude/hooks/guard.mjs` — Claude Code PreToolUse Bash guard
- `docs/internal/` — this repo's own dev notes (not deployed)

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
