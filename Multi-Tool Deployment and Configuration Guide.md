# Multi-Tool (Codex / Claude Code / Antigravity IDE / Zed IDE) AI Engineering Deployment & Configuration Guide

> **Language / 语言**: **English** | [中文](多工具部署配置指南.md)

This guide provides an end-to-end specification on how to deploy, configure, and collaboratively utilize the **Three-Tier AGENTS.md Architecture** (Global, Project, and Directory levels) across **OpenAI Codex / GitHub Copilot**, **Claude Code**, **Google Antigravity IDE**, and **Zed IDE**, tailored for real-world scenarios emphasizing software engineering while supporting professional technical documentation.

---

## Table of Contents

1. [Architecture & Layered Positioning (Harness + Progressive Disclosure)](#1-architecture--layered-positioning-harness--progressive-disclosure)
2. [Four Mainstream Tools: Loading Mechanisms & Adaptation Strategies](#2-four-mainstream-tools-loading-mechanisms--adaptation-strategies)
3. [Physical Security Firewall: PreToolUse Hardware Interception Hooks (.claude/settings.json)](#3-physical-security-firewall-pretooluse-hardware-interception-hooks-claudesettingsjson)
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

To maintain high AI compliance across diverse tools without context dilution or $O(N^2)$ quadratic Token inflation, this specification implements a **"High-Frequency Resident Skeleton + Progressive On-Demand Reading"** design:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Global Level (Global AGENTS.md)                                     │
│    - Role: Cross-project engineering constitution & security baseline │
│    - Content: Concise communication, read/fetch/speak gates, Git rules │
│    - Scope: System-wide resident across all user projects (~1000 Tok) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Inherited (non-redundant)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Project Root Level (Project AGENTS.md)                              │
│    - Role: Deterministic engineering context & sub-rule/skill router   │
│    - Content: Concrete CLI command slots, tech stack, red lines       │
│    - Scope: Repository-wide resident (<1000 Tokens)                    │
│    - Bridges: CLAUDE.md / .github/copilot-instructions.md / ZED.md     │
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
   - Skills use a two-phase discovery mechanism: a ~750 Token static directory prefix is injected into system prompts (leveraging Prompt Cache at a 90% discount), and full skill instructions are only fetched when activated.
3. **Physical Security Firewall**: Operating-system-level pre-tool execution hooks prevent hallucinations from corrupting production branches or leaking credentials.

---

## 2. Four Mainstream Tools: Loading Mechanisms & Adaptation Strategies

| Dimension | Claude Code | Antigravity IDE | Codex / GitHub Copilot | Zed IDE |
| :--- | :--- | :--- | :--- | :--- |
| **Project Entry** | Looks for root `CLAUDE.md` | Loads root `AGENTS.md` or `GEMINI.md` | Reads root `AGENTS.md` or `.github/copilot-instructions.md` | Natively reads root `ZED.md` |
| **Global Entry** | `~/.claude/CLAUDE.md` | `~/.gemini/config/rules/` or `GEMINI.md` | User global prompt or Copilot instructions | `~/.config/zed/settings.json` |
| **Directory Rules** | Recursively supports nested `CLAUDE.md` | Supports `.agents/` cascade | Contextually linked or file-referenced | Inherits workspace folder context |
| **Execution Style** | Native Bash, high execution velocity | Planning Mode, Task scheduling, browser/terminal | Code completion & inline prompt-driven | Rust core, ultra-fast streaming |
| **Physical Defense**| Supports `.claude/settings.json` PreToolUse | Built-in approvals and workspace sandbox | Copilot policies and scanning | Shell permission controls |
| **Bridge Strategy** | Symlink `CLAUDE.md -> AGENTS.md` | Reads project `AGENTS.md` directly | Symlink `.github/copilot-instructions.md -> ../AGENTS.md` | Symlink `ZED.md -> AGENTS.md` |

---

## 3. Physical Security Firewall: PreToolUse Hardware Interception Hooks (.claude/settings.json)

### Why Software Rules Alone Are Not Enough
Even advanced models carry a 1%–5% probability of hallucination or misunderstanding (e.g., executing a direct `git commit` on `develop` or running `git push --force`).

The PreToolUse security hooks in `.claude/settings.json` intercept commands at the OS process level before execution. When a prohibited command pattern is detected, the hook prints an alert and returns `exit 1`, physically blocking execution.

### Interceptor Configuration (`.claude/settings.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"git commit\"*) BRANCH=$(git branch --show-current 2>/dev/null); case \"$BRANCH\" in develop|master|main|release*|staging) echo \"[SECURITY-HOOK] ❌ Direct commits on protected branch $BRANCH are forbidden! Work in a temporary branch.\" >&2; exit 1;; esac;; *\"git merge\"*|*\"git push\"*) BRANCH=$(git branch --show-current 2>/dev/null); case \"$BRANCH\" in develop|master|main|release*|staging) echo \"[SECURITY-HOOK] ⚠️ merge/push on protected branch $BRANCH requires explicit human authorization.\" >&2;; esac;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"git push\"*\"--force\"*|*\"git push\"*\"--force-with-lease\"*|*\"git push\"*\"-f\"*) echo \"[SECURITY-HOOK] ❌ force push / history rewrite is PERMANENTLY FORBIDDEN!\" >&2; exit 1;; *\"git push\"*\"--delete\"*|*\"git push\"*\" :\"*) case \"$CLAUDE_TOOL_INPUT\" in *\" :develop\"*|*\" :master\"*|*\" :main\"*|*\" :release\"*|*\" :staging\"*|*\"--delete develop\"*|*\"--delete master\"*|*\"--delete main\"*|*\"--delete release\"*|*\"--delete staging\"*) echo \"[SECURITY-HOOK] ❌ Deleting protected remote branch is PERMANENTLY FORBIDDEN!\" >&2; exit 1;; *) echo \"[SECURITY-HOOK] ⚠️ Deleting temporary remote branch requires explicit human authorization.\" >&2;; esac;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"git rebase\"*) BRANCH=$(git branch --show-current 2>/dev/null); case \"$BRANCH\" in develop|master|main|release*|staging) echo \"[SECURITY-HOOK] ❌ Rebase on protected branch $BRANCH is forbidden! Use merge.\" >&2; exit 1;; esac;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"rm -rf\"*|*\"rm -r \"*|*\"rm -fr\"*) echo \"[SECURITY-HOOK] ⚠️ rm -rf detected. Verify target path is not a critical source folder!\" >&2;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"git reset --hard\"*) echo \"[SECURITY-HOOK] ⚠️ git reset --hard discards workspace changes permanently!\" >&2;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\"git add -A\"*|*\"git add .\"*) echo \"[SECURITY-HOOK] ⚠️ Blind staging via git add . is forbidden! Use git add <explicit-path>.\" >&2;; esac"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\".pro\"*|*\"CMakeLists.txt\"*|*\"package.json\"*|*\"Cargo.toml\"*|*\"pom.xml\"*|*\"public_struct.h\"*|*\"protofile/\"*|*\"license\"*) echo \"[SECURITY-HOOK] 🔴 Modifying high-risk file (build config/core struct/protocol/license) requires consulting .agents/rules/security-boundary.md and confirming impact with human!\" >&2;; esac"
          },
          {
            "type": "command",
            "shell": "bash",
            "command": "case \"$CLAUDE_TOOL_INPUT\" in *\".pem\"*|*\".key\"*|*\".token\"*|*\"credentials\"*|*\"id_rsa\"*|*\"secret\"*) echo \"[SECURITY-HOOK] 🔐 Credential protection: Hardcoding secrets is strictly prohibited!\" >&2;; esac"
          }
        ]
      }
    ]
  }
}
```

---

## 4. Cross-Tool Automated Deployment & Online Update Pipeline (deploy-agents)

Automated scripts streamline deployment and non-destructive updating:
- **Windows PowerShell**: [`deploy-agents.ps1`](deploy-agents.ps1)
- **Linux / macOS Bash**: [`deploy-agents.sh`](deploy-agents.sh)

### 4.1 Script Core Architecture & Pipeline

```
[ Execute Deployment Script ]
       │
       ▼
 Phase 1: Online Update (-Update)
   ├─ Git upstream sync (git pull --rebase)
   ├─ Tool updates (comet update)
   └─ Skills refresh (npx -y skills@latest update -y) & skills-lock.json sync
       │
       ▼
 Phase 2: User Global Rules (-Global)
   ├─ Claude Code global: ~/.claude/CLAUDE.md
   └─ Antigravity IDE global: ~/.gemini/config/rules/global_agents.md
       │
       ▼
 Phase 3: Project Rules & Cross-Tool Bridges
   ├─ Root AGENTS.md (generates AGENTS.template.md if already exists)
   ├─ CLAUDE.md -> AGENTS.md (symlink/reference)
   ├─ .github/copilot-instructions.md -> ../AGENTS.md
   ├─ ZED.md -> AGENTS.md
   └─ PreToolUse security hooks: .claude/settings.json
       │
       ▼
 Phase 4: Sub-Rules (.agents/rules/*.md)
       │
       ▼
 Phase 5: Skills Library (.agents/skills/ & .claude/skills/)
   ├─ Copy skills to .agents/skills/
   ├─ Link to .claude/skills/ (Windows: Junction, Linux/macOS: Symlink)
   └─ Synchronize skills-lock.json
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
```

---

### 4.2 Windows Deployment (`deploy-agents.ps1`)

**Usage**:
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <target-path>] [-Global] [-Update] [-CometInit]
```

**Parameters**:
- `-ProjectPath` (Positional 0): Path to target project. If omitted with `-Global`, only updates user global rules.
- `-Global` (`-g`): Deploys `Global AGENTS.md` to `~/.claude/CLAUDE.md` and `~/.gemini/config/rules/global_agents.md`.
- `-Update` (`-u`): Online update mode. Refreshes upstream templates, checks `comet`, updates skills via `npx skills`, preserves existing `AGENTS.md`, and generates `AGENTS.template.md`.
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
  4. **3-Step Session Ceremony**: Read lessons and todo at start $\rightarrow$ check off items in progress $\rightarrow$ record lesson learned upon correction.

---

### 5.2 Project Router: `Project AGENTS.md`
- Repository-wide hub (<1000 Tokens).
- Enforces standard CLI command slots (install, dev, build, targeted test, lint, format, migration), architecture red lines, and the **Rule & Skill Dispatching Matrix**.

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
- Rules: Always work on temporary branches (`feature/*`, `fix/*`), TDD red-green cycle, verify with actual test runs, follow Git authorization model.

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
> **Answer**: Two-stage progressive disclosure. The agent only loads a static index (~750 Tokens) into the prefix, which benefits from Prompt Cache discounts (90% lower cost). Full skill markdown is only read when explicitly triggered.

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

---

## 8. Practical Usage & Skills Panorama Guide Reference

For detailed tutorials on Slash Commands (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD, and full end-to-end execution walkthroughs, see:
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](各工具实战使用与技能全景指南.md)
