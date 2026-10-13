# Glossary（术语表）

AI coding assistant infrastructure terms used across agent-harness docs.

| Term | Definition |
|---|---|
| **PreToolUse** | Claude Code hook event fired before a tool (e.g. Bash) executes; used for security interception. |
| **Progressive Disclosure** | Loading rules/skills on-demand instead of all at once, to save context tokens. |
| **frontmatter** | YAML metadata block at the top of a markdown file (`---` delimited), with `name`/`description`/`version`. |
| **TUI** | Terminal User Interface — interactive CLI wizard (here: `pipeline.sh` / `tools/tui.py`). |
| **Comet** | Versioned workflow state machine skill (`.comet/config.yaml`), for phased tasks. |
| **OpenSpec** | Spec-driven development skill family (proposal → tasks → implementation). |
| **Superpowers** | Agent methodology skill family (obra/superpowers): TDD, debugging, etc. |
| **CodeGraph** | Code intelligence index (`.codegraph/`), for semantic code navigation. |
| **L0/L1/L2** | Living-documentation tiers: L0=inline, L1=file-level, L2=project-level. |
| **worktree** | Git worktree — multiple working directories from one repo (used for parallel branches). |
| **refspec** | Refspec — `git push` source:destination mapping (e.g. `main:main`, `+main` for force). |
| **--no-ff** | Merge strategy that always creates a merge commit (preserves branch history). |
| **--ff-only** | Merge only if fast-forward possible (fails otherwise, no merge commit). |
| **Protected branch** | `develop`/`master`/`main`/`release*`/`staging` — direct commits prohibited. |
| **Iron Laws** | The 4 non-negotiable Git safety rules (see `.agents/rules/git-workflow.md` §2). |
| **Skill** | On-demand capability package (`SKILL.md` + scripts), loaded when triggered. |
| **Hook** | Automated check intercepting tool calls (Claude Code PreToolUse) or file writes. |
