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
│    - Content: No-nonsense gates, Git rules, Dual-Track State Memory    │
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
1. **Single Source of Truth**: The root `AGENTS.md` serves as the core. All tools point to it via lightweight symlinks or bridge files, eliminating configuration drift.
2. **Progressive Disclosure**:
   - Rules are loaded dynamically when specific scenarios are triggered.
   - Skill discovery, loading, and prompt-cache behavior depend on the host tool and its configuration; deploying files does not guarantee automatic loading.
3. **Client-Side Risk Guardrails**: Claude Code hooks can reject selected matching tool calls or emit warnings. They are client-side checks, not operating-system or server-side security controls.

---

## 2. Configuration Scope by Tool

Rule discovery, inheritance, global settings, and skill loading are tool- and version-specific. This table lists files and deployment actions provided by this repository; file presence does not guarantee automatic discovery.

| Tool | Provided here | Not provided by the deployment script |
| :--- | :--- | :--- |
| Claude Code | `CLAUDE.md` bridge, `.claude/skills/`, project PreToolUse hooks, `~/.claude/CLAUDE.md` | Server-side Git protection; cross-client hooks |
| Antigravity | Project `.agents/` files; `--global` writes `~/.gemini/AGENTS.md` | Loading verification for every version/settings combination |
| Codex | Project `AGENTS.md` and `.agents/skills/` | Codex global rules or hook configuration |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Copilot policy configuration |
| Zed | Reusable `AGENTS.md` file | Zed-specific configuration/bridge |
| Pi / OpenCode | No dedicated entry point | Auto-discovery, global install, or hook wiring |

Verify current loading paths against each target tool's official documentation before deployment.
---

## 3. Claude Code Client Hooks: PreToolUse (.claude/settings.json)

### Capability boundaries
The hooks in `.claude/settings.json` run only before matching tool calls in the Claude Code client. `guard.mjs` rejects selected command patterns; many other cases only emit a warning and allow the command. Regex matching cannot reliably identify every shell wrapper, alias, or command form. Use server-side branch protection and least-privilege credentials for shared repositories.

### Configuration and implementation

The installer copies [`.claude/settings.json`](.claude/settings.json) and deploys [`.claude/hooks/guard.mjs`](.claude/hooks/guard.mjs) plus [`guard-write.mjs`](.claude/hooks/guard-write.mjs). Inspect those source files directly; do not copy hook examples from older guide versions because the protocol and implementation can change.

---

## 4. Cross-Tool Deployment & Template Updates (deploy-agents)

The scripts deploy files to configured paths. Tool-specific loading behavior is not guaranteed by file deployment; `-Update` backs up replaced managed paths but still replaces them:
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
   ├─ Claude Code global: ~/.claude/CLAUDE.md
   └─ Antigravity IDE global: ~/.gemini/AGENTS.md
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
- `-Global` (`-g`): Deploys `Global AGENTS.md` to `~/.claude/CLAUDE.md` and `~/.gemini/AGENTS.md`.
- `-Update` (`-u`): Fast-forwards the template repository and syncs files to the target. Existing managed rules, hooks, skills, and lock metadata are backed up as `.bak.<timestamp>` before replacement. It does not upgrade global CLIs.
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

### 5.1 Global Constitution: `Global AGENTS.md`
- System-wide baseline resident in user configuration.
- Enforces:
  1. **No-Nonsense Communication**: Direct answers, conclusions first, Diff and evidence before explanations;
  2. **Ponytail Minimal Code**: Standard library first, 1 line over 10 lines, no speculative abstractions;
  3. **Token Discipline**: Controlled reading, filtered test commands, log redirection, single-agent default;
  4. **Session Ritual & Dual-Track State Memory (Iron Law)**:
     - **Session Start**: Prioritize reading root `PROJECT_CONTEXT.md` (long-term architectural memory) and `SESSION_STATE.md` (short-term workbench breakpoint) to achieve instant contextual awareness without re-explaining history;
     - **In-Progress**: Multi-step plan tracking, autonomous stack-trace diagnosis, and strict verification evidence gate;
     - **Session Finish (State Solidification)**: Whenever completing a coding session, new feature development, or bug fix, **MUST update/sync two files in the project root**:
       - **`PROJECT_CONTEXT.md` (Project Panorama & Evolution Chronicle / Long-Term Memory)**: Serves as the **Single Source of Truth** and global architecture manual. Records: ① System architecture & topology (e.g. OpenClaw 3-tier architecture: Go bootloader, Node.js scheduler core, Web/Electron shell); ② Core engineering hard rules (AST deep obfuscation pipeline, Nuitka C++ native compilation, physical USB hardware seals); ③ Branch matrix & role division (main, lite-edition, standalone-app); ④ Version evolution chronicle (v1.0 to latest technical decisions). Value: Anyone or any AI can grasp the full system in seconds on any machine at any time without breaking conventions.
       - **`SESSION_STATE.md` (Session State & Real-Time Breakpoint / Short-Term Workbench)**: Serves as the task status board and breakpoint resumption engine. Records: ① Current dev context (branch, latest commit hash, remote sync status); ② Latest fix/feature list (problems solved, key files touched); ③ Next Steps (unverified items, edge cases, pending build commands); ④ Known risks memo (file locks, old binaries). Value: Enables subsequent AI sessions to resume precisely from the breakpoint without re-explaining history.

---

### 5.2 Project Router: `Project AGENTS.md`
- Adaptable repository-level template.
- Enforces standard CLI command slots (install, dev, build, targeted test, lint, format, migration), architecture red lines, the **Rule & Skill Dispatching Matrix**, and **Mandatory Panorama & Breakpoint Memory** (`PROJECT_CONTEXT.md` & `SESSION_STATE.md`).

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
  - Prioritize reading `PROJECT_CONTEXT.md` and `SESSION_STATE.md` at session start;
  - Always work on temporary branches (`feature/*`, `fix/*`);
  - TDD red-green cycle, verify with actual test runs;
  - Follow Git authorization model;
  - **Dual-Track State Synchronization**: Enforce updating `PROJECT_CONTEXT.md` and `SESSION_STATE.md` in the project root upon completing any session, feature, or fix.

### 2. Technical Documentation Track (Lightweight Bypass)
- Scope: Markdown documentation, READMEs, API specifications, Word/PDF reports.
- Rules: **Exempt from running test suites**; leverage specialized skills (`docx`, `pdf`, `write-openspec-docs`); maintain GitHub Flavored Markdown standards.

---

## 7. Frequently Asked Questions & Best Practices (FAQ)

### Q1: Why not put all project commands into `Global AGENTS.md`?
> **Answer**: Global rules are resident across all sessions on the machine. Adding project-specific commands creates cross-project context pollution and wastes prompt tokens.

### Q2: How does online update (`-Update`) protect custom project configurations?
> **Answer**: If `AGENTS.md` already exists, the script **never overwrites it**. Instead, it generates [`AGENTS.template.md`](AGENTS.template.md) for diff reference, while safely updating sub-rules, skills, and version locks.

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
> 8. Making large cross-module changes spanning 3+ files.

### Q5: Why mandate updating `PROJECT_CONTEXT.md` and `SESSION_STATE.md` on session completion?
> **Answer**: Long agent conversations suffer from context compression, truncation, or unexpected disconnects.
> - `PROJECT_CONTEXT.md` (Long-Term Memory) stores unchanging architectural truths, branch topologies, hard constraints, and technical evolution milestones, guaranteeing zero architectural drift across developers or machines.
> - `SESSION_STATE.md` (Short-Term Workbench) pins exact commit hashes, touched files, uncompleted Next Steps, and environment quirks, eliminating the overhead of re-explaining context and ensuring seamless breakpoint continuation.

---

## 8. Practical Usage & Skills Panorama Guide Reference

For detailed tutorials on Slash Commands (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD, and full end-to-end execution walkthroughs, see:
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](各工具实战使用与技能全景指南.md)
