# Multi-Tool (Codex / Claude Code / Antigravity IDE / Zed IDE) AI Engineering Deployment & Configuration Guide

> **Language / 语言**: **English** | [中文](多工具部署配置指南.md)

This guide provides an end-to-end specification on how to deploy, configure, and collaboratively utilize the **Three-Tier AGENTS.md Architecture** (Global, Project, and Directory levels) across **OpenAI Codex / GitHub Copilot**, **Claude Code**, **Google Antigravity IDE**, and **Zed IDE**, tailored for real-world scenarios emphasizing software engineering while supporting professional technical documentation.

---

## Table of Contents

1. [Architecture & Layered Positioning (Harness + Progressive Disclosure)](#1-architecture--layered-positioning-harness--progressive-disclosure)
2. [Four Mainstream Tools: Loading Mechanisms & Adaptation Strategies](#2-four-mainstream-tools-loading-mechanisms--adaptation-strategies)
3. [Claude Code Client Hooks: PreToolUse (.claude/settings.json)](#3-claude-code-client-hooks-pretooluse-claudesettingsjson)
4. [Cross-Tool Automated Deployment & Online Update Pipeline (deploy-agents)](#4-cross-tool-automated-deployment--online-update-pipeline-deploy-agents)
   - 4.1 Script Core Architecture & Pipeline
   - 4.2 Windows Deployment (`deploy-agents.ps1`)
   - 4.3 Linux / macOS Deployment (`deploy-agents.sh`)
   - 4.4 Symlink vs. Directory Junction Mechanics
5. [Deep Dive into the Four Rule Layers](#5-deep-dive-into-the-four-rule-layers)
   - 5.1 Global Constitution: `Global AGENTS.md`
   - 5.2 Project Router: `Project AGENTS.md`
   - 5.3 Modular Sub-Rules: `.agents/rules/`
   - 5.4 Micro-Boundary Patch: `Directory AGENTS.md`
6. [Dual-Track Practical Workflow: "Engineering First, Documentation Second"](#6-dual-track-practical-workflow-engineering-first-documentation-second)
7. [Frequently Asked Questions & Best Practices (FAQ)](#7-frequently-asked-questions--best-practices-faq)
8. [Practical Usage & Skills Panorama Guide Reference](#8-practical-usage--skills-panorama-guide-reference)

---

## 1. Architecture & Layered Positioning (Harness + Progressive Disclosure)

This repository organizes reusable rules as a **project entry point plus on-demand sub-rules** so teams can adapt the baseline and avoid loading unrelated guidance. Actual discovery and context cost depend on the host tool:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Global Level (Global AGENTS.md)                                     │
│    - Role: Cross-project engineering constitution & security baseline │
│    - Content: Reusable engineering baseline, Git safety, concise communication │
│    - Scope: System-wide resident across all user projects (~1000 Tok) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Inherited (non-redundant)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Project Root Level (Project AGENTS.md)                              │
│    - Role: Deterministic engineering context & sub-rule/skill router   │
│    - Content: Concrete CLI slots, tech stack, red lines, state memory  │
│    - Scope: Repository-wide; loading depends on the host tool          │
│    - Bridges: CLAUDE.md / .github/copilot-instructions.md              │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Progressive On-Demand Reading   │ Only as needed in submodules
┌──────────────────▼───────────────┐ ┌───────────────▼───────────────────┐
│ 3. Sub-Rules (.agents/rules/)    │ │ 4. Directory Level (Directory AGENTS.md)│
│  - token-discipline.md           │ │    - Role: Micro-boundary patch   │
│  - engineering-spec.md (SDD/TDD) │ │    - Content: In/Out scope, isolated│
│  - security-boundary.md          │ │            dependencies, fast tests│
│  - git-workflow.md (Auth model)  │ └───────────────────────────────────┘
└──────────────────────────────────┘
```

### Core Advantages
1. **Shared baseline**: Keep reusable rules in Markdown templates and use tool-specific bridges where supported; verify each host's discovery behavior instead of assuming every tool loads the same file.
2. **Progressive Disclosure**:
   - Rules are loaded dynamically when specific scenarios are triggered.
   - Skill discovery, loading, and prompt-cache behavior depend on the host tool and its configuration; deploying files does not guarantee automatic loading.
3. **Client-Side Risk Guardrails**: Claude Code hooks can reject selected matching tool calls or emit warnings. They are client-side checks, not operating-system or server-side security controls.

---

## 2. Configuration Scope by Tool

Rule discovery, inheritance, global settings, and memory mechanisms vary by product and version. This table separates paths written by the scripts from host discovery; file deployment is not a loading verification.

| Tool/surface | Provided or written by this repository | Loading notes |
| :--- | :--- | :--- |
| Codex (ChatGPT/desktop) | Project-root `AGENTS.md`; the script does not write product global settings | Verify current ChatGPT/Codex product behavior; do not infer desktop behavior from the CLI |
| Codex CLI | Project and directory `AGENTS.md`; user configures the global file | Official docs describe loading from Codex home and each directory from repository root to the current directory |
| Claude Code | `CLAUDE.md` bridge, `~/.claude/CLAUDE.md`, project hooks/skills | `CLAUDE.md` is an instruction entry point; Claude Auto memory is a separate optional machine-local project memory, not shared across tools |
| Antigravity CLI | Project `AGENTS.md` / `.agents/rules/`; global `~/.gemini/AGENTS.md` | Official rules docs list workspace, directory, and global discovery paths |
| Antigravity IDE | Project `AGENTS.md` / `.agents/rules/`; global `~/.gemini/AGENTS.md` | Official docs list IDE rule files and UI-based rule management |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Confirm loading in Copilot's current product settings/docs |
| Zed / Pi / OpenCode | Reusable Markdown only; no dedicated setup from this repository | Do not infer automatic discovery or global loading from file presence |

References: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---


## 3. Claude Code Client Hooks: PreToolUse (.claude/settings.json)

### Capability boundaries
The hooks in `.claude/settings.json` are Claude Code-specific and run only before matching tool calls. `guard.mjs` rejects selected command patterns; many other cases only emit a warning. Regex matching cannot identify every shell wrapper, alias, or command form, so this is not a complete security boundary. The hooks do not collect or transmit memory data. Claude Code Auto memory is a separate machine-local project feature that users can inspect/manage with `/memory`; this repository does not configure it. Use server-side branch protection and least-privilege credentials for shared repositories.

### Configuration and implementation

The installer copies [`.claude/settings.json`](.claude/settings.json) and deploys [`.claude/hooks/guard.mjs`](.claude/hooks/guard.mjs) plus [`guard-write.mjs`](.claude/hooks/guard-write.mjs). Inspect those source files directly; do not copy hook examples from older guide versions because the protocol and implementation can change.

---

## 4. Cross-Tool Deployment & Template Updates (deploy-agents)

The scripts deploy files to configured paths. Tool-specific loading behavior is not guaranteed by file deployment. Existing user-level global instruction files are preserved; `-Update` writes adjacent review templates:
- **Windows PowerShell**: [`deploy-agents.ps1`](deploy-agents.ps1)
- **Linux / macOS Bash**: [`deploy-agents.sh`](deploy-agents.sh)

### 4.1 Script Core Architecture & Pipeline

```
[ Execute Deployment Script ]
       │
       ▼
 Phase 1: Template Repository Update (-Update)
   └─ Fast-forward update of this template repository (`git pull --ff-only`); no global CLI upgrade or third-party updater in the caller directory
       │
       ▼
 Phase 2: User Global Rules (-Global)
   ├─ Initialize Claude Code (~/.claude/CLAUDE.md) only if the target is absent
   ├─ Initialize Antigravity (~/.gemini/AGENTS.md) only if the target is absent
   └─ Preserve existing files; with -Update write adjacent *.template.md files for manual merge
       │
       ▼
 Phase 3: Project Rules & Cross-Tool Bridges
   ├─ Root AGENTS.md (generates AGENTS.template.md if already exists)
   ├─ CLAUDE.md -> AGENTS.md (symlink/reference)
   ├─ .github/copilot-instructions.md -> ../AGENTS.md
   ├─ Zed uses the provided AGENTS.md; no Zed-specific configuration is created
   └─ Claude Code PreToolUse client hooks: .claude/settings.json
       │
       ▼
 Phase 4: Sub-Rules (.agents/rules/*.md)
       │
       ▼
 Phase 5: Skills Library (.agents/skills/ & .claude/skills/)
   ├─ Copy skills to .agents/skills/
   ├─ Link to .claude/skills/ (Windows: Junction, Linux/macOS: Symlink)
   └─ Copy skills-lock.json metadata
       │
       ▼
 Phase 6: Dynamic Task Tracking Scaffold
   ├─ tasks/lessons.md (mistake notebook)
   └─ tasks/todo.md (checklist)
       │
       ▼
 Phase 7: OpenSpec Scaffold (docs/openspec/changes/)
       │
       ▼
 Phase 8: Optional Comet CLI Init (-CometInit)
   └─ Runs `comet init` only when explicitly requested
```

---

### 4.2 Windows Deployment (`deploy-agents.ps1`)

**Usage**:
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <target-path>] [-Global] [-Update] [-CometInit]
```

**Parameters**:
- `-ProjectPath` (Positional 0): Path to target project. If omitted with `-Global`, only updates user global rules.
- `-Global` (`-g`): Initializes `~/.claude/CLAUDE.md` and `~/.gemini/AGENTS.md` only when absent. Existing files are preserved; with `-Update`, adjacent `CLAUDE.template.md` and `AGENTS.template.md` files are written for manual review/merge.
- `-Update` (`-u`): Fast-forwards the template repository and syncs files to the target. Existing project-managed rules, hooks, skills, and lock metadata follow their documented backup/update behavior. Existing global instruction files are never replaced; an adjacent review template is generated instead. It does not upgrade global CLIs.
- `-CometInit` (`-c`): Automatically executes `comet init` in the target project if Comet CLI is installed.

**Examples**:
```powershell
# Deploy to a new project
.\deploy-agents.ps1 "D:\Projects\my-project"

# Deploy project and update global rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global

# Online update skills and sub-rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global -Update

# Initialize with Comet terminal hooks
.\deploy-agents.ps1 "D:\Projects\my-project" -CometInit

# Update global rules only
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Linux / macOS Deployment (`deploy-agents.sh`)

```bash
chmod +x ./deploy-agents.sh

# Deploy to project
./deploy-agents.sh /path/to/my-project

# Deploy and update global rules
./deploy-agents.sh /path/to/my-project --global

# Online update
./deploy-agents.sh /path/to/my-project --global --update

# Deploy with Comet CLI init
./deploy-agents.sh /path/to/my-project --comet-init
```

---

### 4.4 Symlink vs. Directory Junction Mechanics

To enable Claude Code to discover skills located in `.agents/skills/`:
- **Linux / macOS**: Uses standard relative symbolic links:
  `ln -sf "../../.agents/skills/${name}" ".claude/skills/${name}"`
- **Windows**: Normal user accounts cannot create Directory Symbolic Links without Developer Mode or administrator privileges. `deploy-agents.ps1` resolves this by using **NTFS Directory Junctions**:
  `New-Item -ItemType Junction -Path ".claude\skills\$name" -Target ".agents\skills\$name"`
  - Works without elevation;
  - Real-time directory reflection without file duplication;
  - Automatically falls back to recursive copy if junctions are unsupported.

---

## 5. Deep Dive into the Four Rule Layers

### 5.1 Global Rules Template: `Global AGENTS.md`
- **Purpose:** A reusable cross-project engineering baseline. Whether a host loads it, and at what precedence, depends on that host and the user's configuration.
- **Sharing boundary:** Keep the shared template generic; do not put personal preferences, project facts, or sensitive information in it. Save personal preferences only in a user-controlled machine-local location when explicitly requested.
- **Memory layers:**
  1. At task start, read `PROJECT_CONTEXT.md` (verified durable project facts) and `SESSION_STATE.md` (current checkpoint) when relevant, then verify facts that affect the work.
  2. At a meaningful task/session boundary, update `SESSION_STATE.md` and remove stale status. Update `PROJECT_CONTEXT.md` only when durable project knowledge changes; no-op sessions do not need empty updates.
  3. `PROJECT_CONTEXT.md` is a project summary and navigation aid, not a single source of truth over code, configuration, or maintained documentation. Current user instructions and reproducible evidence take precedence over memory.
  4. Label uncertainty and date/source facts likely to change. Never store credentials, private keys, raw personal data, full conversation/tool logs, or unnecessary personal information.


**Selected optional backend: [ai-memory](https://github.com/akitaonrails/ai-memory).** Its local mode provides Markdown-backed project memory, full-text retrieval, and cross-agent handoff without an LLM or API key. It is not required for ordinary use. This repository supplies an explicit setup helper but never installs or starts the backend, creates a local opt-in marker, or changes tool configuration during normal deployment.

#### Explicit project opt-in and setup

1. Install and start ai-memory separately by following its [official installation guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md). Leave LLM and embedding providers unconfigured for the free, zero-key path.
2. Review `.ai-memory.toml.example`, copy it to `.ai-memory.toml`, and replace both names. `.ai-memory.toml` is ignored by Git; committing this opt-in is intentionally avoided.
3. From this repository, run `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>` on Linux/macOS/WSL2, or `./setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` in PowerShell. Before changing any tool configuration, the helper requires a marker, a native `ai-memory` executable, and a native hook mode; it rejects Docker/script wrappers and non-native platform overrides. After preflight it delegates MCP, allowlist hooks, and managed instruction setup to the upstream merge-aware CLI. It does not download/install software or start the server. Confirm installer output reports capture-policy enforcement.
4. Keep the server bound to loopback for same-machine use. Default data locations are `~/.local/share/ai-memory` on Linux, `~/Library/Application Support/ai-memory` on macOS, and typically `%LOCALAPPDATA%\ai-memory` on Windows; `AI_MEMORY_DATA_DIR` can override them. Back up with `ai-memory --data-dir <data-dir> backup --to <archive-path>` (for Docker deployments, use the upstream container command). `ai-memory uninstall --apply` removes managed client integrations but does not delete the data. To erase memory, stop the service and remove its configured data directory only after confirming the backup and target. See the [official installation/operations guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

#### Host boundaries

- **Claude Code:** upstream MCP/hooks; ai-memory owns only its entries and preserves unrelated hooks. The existing Claude `PreToolUse` security hook remains separate. Claude Code's default auto-memory is also separate and machine-local.
- **Codex CLI:** upstream `--client codex` / `--agent codex` integration. **Codex desktop:** uses the local Codex configuration surface where supported; verify the installed app's hook/MCP availability instead of assuming every CLI version behaves identically.
- **Antigravity CLI:** upstream `antigravity-cli` MCP/hooks. On Windows, run setup in the same environment that launches the agent.
- **Antigravity IDE:** MCP only; configure a local server in the IDE's MCP settings or its documented `~/.gemini/config/mcp_config.json` / project `.agents/mcp_config.json`. For same-machine use, the Antigravity schema uses `serverUrl` set to the ai-memory MCP endpoint `http://127.0.0.1:49374/mcp`. The IDE integration does not imply automatic lifecycle capture.
- **ChatGPT web:** the no-key, loopback setup has no direct connection to a remote web chat. Use a concise Markdown handoff manually. Remote MCP/write access is outside this free local setup.
- **Windows:** upstream documents both WSL2 and native Windows. Install and configure ai-memory in the same environment that launches each agent; do not mix WSL and Windows hook paths. Review the [Windows guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md) for client-specific support.

ai-memory allowlist mode only guarantees no capture for repositories without a marker when the installed native hook enforces capture policy. Its path exclusions do not redact arbitrary prompt text; never include secrets in prompts. See the [marker-file reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md).

### 5.2 Project Router: `Project AGENTS.md`
- Adaptable repository-level template.
- Provides standard CLI command slots (install, dev, build, targeted test, lint, format, migration), architecture red lines, the **Rule & Skill Dispatching Matrix**, selective Markdown memory rules, and optional ai-memory integration guidance.

---

### 5.3 Modular Sub-Rules: `.agents/rules/`
Loaded progressively on-demand:
- **`token-discipline.md`**: Restricts reading, fetching, and speaking; mandates AST index over blind grep;
- **`engineering-spec.md`**: SDD spec-first (In/Out scope), TDD verification gate (physical proof required);
- **`security-boundary.md`**: 8 high-risk operations confirmation matrix, zero credentials leak, large file safety;
- **`git-workflow.md`**: Protected branch isolation (zero direct commits), mandatory authorization for remote push, commit format `{type}: {description}`.

---

### 5.4 Micro-Boundary Patch: `Directory AGENTS.md`
- Created **only when necessary** in monorepo packages (`packages/*`) or isolated submodules.
- Defines In/Out scope, permitted/forbidden dependencies, and targeted local test commands (e.g., `pytest tests/submodule -q`).

---

## 6. Dual-Track Practical Workflow: "Engineering First, Documentation Second"

### 1. Software Engineering Track (Strict Gate)
- Scope: APIs, features, bug fixes, refactoring.
- Rules:
  - Read `PROJECT_CONTEXT.md` and `SESSION_STATE.md` at task start only when present and relevant, then verify material facts;
  - Always work on temporary branches (`feature/*`, `fix/*`);
  - TDD red-green cycle, verify with actual test runs;
  - Follow Git authorization model;
  - **Selective memory updates**: Update `SESSION_STATE.md` at meaningful closeout; update `PROJECT_CONTEXT.md` only when durable project facts change.

### 2. Technical Documentation Track (Lightweight Bypass)
- Scope: Markdown documentation, READMEs, API specifications, Word/PDF reports.
- Rules: **Exempt from running test suites**; leverage specialized skills (`docx`, `pdf`, `write-openspec-docs`); maintain GitHub Flavored Markdown standards.

---

## 7. Frequently Asked Questions & Best Practices (FAQ)

### Q1: Why not put all project commands into `Global AGENTS.md`?
> **Answer**: Global rules are resident across all sessions on the machine. Adding project-specific commands creates cross-project context pollution and wastes prompt tokens.

### Q2: How does online update (`-Update`) protect custom project configurations?
> **Answer**: If project `AGENTS.md` already exists, the script preserves it and generates [`AGENTS.template.md`](AGENTS.template.md) on update. Existing Claude Code and Antigravity global instruction files are also preserved; update mode writes adjacent `CLAUDE.template.md` and `AGENTS.template.md` for manual review. Other managed sub-rules, skills, and version metadata follow their documented update behavior.

### Q3: How do 40+ skills avoid blowing up the context window?
> **Answer**: It depends on how the host discovers and loads Skills. Do not assume fixed metadata costs or cache discounts; keep only useful Skills enabled and verify behavior in the target host.

### Q4: What is the 8 High-Risk Operations Protection Matrix?
> **Answer**: Defined in `security-boundary.md`, requiring human confirmation before:
> 1. Modifying build configs (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
> 2. Introducing new third-party dependencies;
> 3. Modifying global public data structures (`public_struct.h`, `types.ts`);
> 4. Changing core dispatch singletons or public service interfaces;
> 5. Modifying communication protocols or wire contracts (`protofile/`);
> 6. Altering license, cryptography, or auth code;
> 7. Modifying `.gitignore` or CI/CD pipelines;
> 8. High-impact cross-module changes affecting shared contracts or requiring broad coordination; file count alone is not a risk trigger.

### Q5: When should `PROJECT_CONTEXT.md` and `SESSION_STATE.md` be updated?
> At meaningful task/session boundaries, update `SESSION_STATE.md` with completed work, actual verification evidence, remaining steps, and still-relevant risks. Update `PROJECT_CONTEXT.md` only when durable architecture, constraints, or confirmed decisions change. Do not create no-op updates. Both files summarize project memory; they do not override current user instructions, code, configuration, or reproducible evidence. Never store credentials, raw personal data, or full conversation/tool logs.


---

## 8. Practical Usage & Skills Panorama Guide Reference

For detailed tutorials on Slash Commands (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD, and full end-to-end execution walkthroughs, see:
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](各工具实战使用与技能全景指南.md)
