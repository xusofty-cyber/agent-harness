# AI Memory Integration Implementation Plan

## Goal

Integrate exactly one free, local-first long-term memory backend (`ai-memory`) into this repository, with a safe opt-in workflow for coding, research, documentation, and design work across Claude Code, Codex CLI/desktop, Antigravity CLI/IDE, and a manual ChatGPT web handoff. Preserve the already completed rule-template and deployment fixes on `long-term-memory-governance`, and do not touch unrelated local configuration.

## Architecture

- `ai-memory` is the only optional memory backend. Its local Markdown wiki is the durable memory store; repository source, canonical docs, current user instructions, and reproducible evidence remain authoritative.
- Use the upstream installer for host config and its merge/ownership markers. The repository does not install a binary, start a service, provision credentials, or write user-global settings during normal deployment.
- Configure capture in allowlist mode. No `.ai-memory.toml` marker is committed, so a project is not opted in by cloning this repository. Provide an ignored/local marker example or documented opt-in step based on the verified upstream marker schema.
- Keep global and directory AGENTS templates normative and generic. Keep the backend-specific recall/retain workflow in one shared Agent Skill, with host-specific limitations documented separately.
- Windows users install/configure ai-memory in the same environment where the agent runs (WSL2 or native Windows); hook/policy support can differ by client/platform. ChatGPT web uses a human-mediated Markdown handoff unless a future user chooses an eligible remote MCP setup.

## Stack

- Existing Markdown templates and guides.
- Existing PowerShell and Bash deployment scripts, changed only where an explicit, opt-in memory integration can safely delegate to the official `ai-memory` CLI.
- ai-memory upstream merge-aware commands for hooks, MCP, instructions, skills, and uninstall. No custom config merger and no required API key/provider.
- Static validation only; do not add or run automated tests under the existing user-approved constraint.

## Spec

Approved design: `docs/superpowers/specs/2026-10-07-cross-tool-memory-governance-design.md`.

Upstream behavior used by this plan is documented in [ai-memory install guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) and [marker-file reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md): allowlist capture is selected at hook installation, marker presence opts in a repository, `install-instructions` maintains delimited blocks and managed skills, and host installers are merge-aware. Re-check exact supported flags against the installed CLI version before documenting commands as copy/paste-ready.

## Global Constraints

- Preserve `.claude/settings.json` and all pre-existing user files/configuration, including untracked local configs. Existing Claude `PreToolUse` security hooks must remain separate from memory hooks.
- Do not run `git add .`/`git add -A` or modify protected branches. The user has separately authorized committing and pushing this work to its feature branch; do not create a PR.
- Do not install ai-memory, Docker images, models, or dependencies; do not activate user-global hooks or MCP configuration as part of this repository change.
- Never claim automatic free ChatGPT web access to a loopback-only service. Distinguish Codex CLI and desktop behavior; state which integration is upstream-supported and which is inferred from current host docs.
- Do not capture or retain secrets, private keys, unrelated personal data, or full transcripts. Do not commit an active capture marker or machine-specific memory database.
- Keep the Chinese and English guides consistent. Update `PROJECT_CONTEXT.md` and `SESSION_STATE.md` when implementation is complete.
- No tests are to be added or run. Use syntax/encoding checks, static searches, and diff review only.

## Review Focus

- Is capture truly opt-in on a fresh clone, including when scripts are run?
- Do setup helpers reject script/Docker hook wrappers before changing any client configuration?
- Do wrappers rely on the official CLI's merge-aware behavior and preserve unrelated hook/MCP/settings entries?
- Are the listed capabilities accurate separately for Claude Code, Codex CLI, Codex desktop, Antigravity CLI, Antigravity IDE, and ChatGPT web?
- Are no-key/no-paid-service defaults explicit without implying optional provider features are required?
- Can users opt in, inspect, disable, uninstall, and delete their local data without affecting normal agent use?
- Are global rules generic and directory-level constraints still canonical in `Directory AGENTS.md`?

## Tasks

### 1. Add the shared memory workflow Skill

**Files:** `.agents/skills/cross-tool-memory/SKILL.md`

- [x] Describe when to recall memory before coding, research, documentation, or design work and when source/docs must be checked first.
- [x] Describe what to retain: verified durable decisions, architecture, constraints, design rationale, lessons, and actionable handoffs.
- [x] Exclude secrets, raw transcripts, unverified assumptions, ephemeral details, and duplicated canonical docs.
- [x] Require concise records with provenance/canonical links and stale-memory correction/deletion.
- [x] Include the no-service fallback and explain that the skill does not imply automatic capture or global memory.

### 2. Update governance templates and safe local opt-in

**Files:** `Global AGENTS.md`, `Project AGENTS.md`, `Directory AGENTS.md`, `.gitignore` (only if needed), optional `.ai-memory.toml.example`

- [x] Keep global rules generic; add a short optional-backend reference and never make user-level personal capture the default.
- [x] Make project guidance describe ai-memory as optional, project-scoped, source-checked, and unavailable without blocking normal work.
- [x] Keep directory-specific instructions as the source of normative local constraints; do not create nested stores by default.
- [x] Add a safe local opt-in example only after confirming valid upstream marker syntax; ensure the real `.ai-memory.toml` is ignored and no example silently activates capture.
- [x] Verify no committed file enables capture by default.

### 3. Provide explicit, reversible setup guidance/scripts

**Files:** `deploy-agents.ps1`, `deploy-agents.sh` and/or a dedicated setup helper only if needed

- [x] Keep ordinary template deployment independent of ai-memory and its service state.
- [x] Add an explicit opt-in setup path that first verifies `ai-memory` is already available, then calls only supported upstream installation commands with allowlist capture. Do not download/install or start anything.
- [x] Use official merge-aware hook/MCP/instruction/skill installers; never hand-edit JSON hook configuration or overwrite existing Claude security handlers.
- [x] Limit setup helpers to upstream-supported CLI targets; document Antigravity IDE's manual MCP path.
- [x] Document the matching upstream uninstall commands and local-data deletion/backup controls; do not silently remove memory data on uninstall.
- [x] If one or more upstream commands cannot safely cover a host, document its manual steps instead of writing a second installer.

### 4. Align host support documentation

**Files:** `Multi-Tool Deployment and Configuration Guide.md`, `Tools Practical Usage and Skills Panorama Guide.md`, `多工具部署配置指南.md`, `各工具实战使用与技能全景指南.md`

- [x] Replace the “three optional candidates” comparison/recommendation with one selected backend: ai-memory.
- [x] Document local zero-LLM/zero-API-key operation, allowlist opt-in, local storage, backup/deletion, and normal-use fallback.
- [x] Separate Claude Code, Codex CLI, Codex desktop, Antigravity CLI, Antigravity IDE, and ChatGPT web integration boundaries.
- [x] Explain ChatGPT web manual handoff under the free/local setup and avoid requiring tunnels, hosted services, or paid features.
- [x] Document upstream-supported WSL2 and native Windows modes and the same-environment requirement.
- [x] Keep command examples aligned across English and Chinese versions and mark commands that require an already-installed server/CLI.

### 5. Update project state and review the complete diff

**Files:** `PROJECT_CONTEXT.md`, `SESSION_STATE.md`, all files changed above

- [x] Record ai-memory as the selected optional integration, supported boundaries, and no-key default; remove stale “candidate” language.
- [x] Record branch, touched files, actual static checks, and any unresolved upstream/client limitation in `SESSION_STATE.md`.
- [x] Review the full diff, preserving unrelated user changes and avoiding accidental inclusion of local configs.
- [x] Run only static/syntax/encoding checks and `git diff --check`; do not add or run tests.

## Verification Evidence to Capture

- PowerShell parse/encoding validation for changed PowerShell files.
- Bash syntax validation for changed shell files when a Bash runtime is available.
- Static search showing no committed active `.ai-memory.toml`, hard-coded API keys, automatic download/start commands, or stale multi-backend recommendation.
- `git diff --check` and a focused review of each changed file, especially `.claude/settings.json` (which must remain untouched by this integration).

## Plan Self-Review

- One backend is selected, and free/no-key behavior is the default.
- Setup remains opt-in, explicit, and reversible; memory service installation is out of scope.
- Setup helpers verify a native executable/platform mode before they write MCP or hook configuration, so script fallback cannot bypass allowlist capture.
- Codex, Antigravity IDE/CLI, and ChatGPT web distinctions are included.
- Existing local configuration and the earlier uncommitted work are protected.
- No tests or pull request are included; feature-branch commit/push follows the user's explicit authorization.
