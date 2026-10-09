# Practical Guide to AI Tooling and Skills Panorama (Claude Code / Codex / Antigravity IDE / Zed IDE)

> **Language / 語言**: [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [簡體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | **繁體中文** | [Français](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.fr.md) | [Deutsch](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.de.md)

This guide provides a comprehensive handbook for software engineering and technical documentation with AI agents: **which skills and Harness tools to install, underlying token economics, tool configuration and wiring, when and how to invoke core slash commands (e.g., `/comet`, `/plan`, `/opsx`, `codegraph`), and an end-to-end practical walkthrough.**

---

## Table of Contents

1. [Core Architecture & Tool Matrix (Who Manages What)](#1-core-architecture--tool-matrix-who-manages-what)
2. [Skills & Ecosystem Tools Inventory](#2-skills--ecosystem-tools-inventory)
   - 2.1 42 Integrated Native Skills Categorized
   - 2.2 Version Locking, Online Updates & Skill Sync (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)
   - 2.3 Optional Harness CLI Tools
   - 2.4 Token Economics of Skills (Why 40+ Skills Do NOT Blow Up Context)
   - 2.5 Engineering Skills & Rules Dispatching Matrix
3. [Deep Dive into Core Harness Tools & Slash Commands](#3-deep-dive-into-core-harness-tools--slash-commands)
   - 3.1 Comet: Versioned Workflow Entry Point
   - 3.2 OpenSpec: Spec-Driven Development (`/opsx:propose`, `/opsx:apply`, etc.)
   - 3.3 Superpowers: TDD, Systematic Debugging & Verification Gate
   - 3.4 CodeGraph: Optional MCP Code-Graph Integration
   - 3.5 Ponytail: Minimal Implementation Ladder (Generation Gate)
   - 3.6 Caveman: Ultra-Compressed Output (Communication Gate)
   - 3.7 RTK: Output Truncation & Log Shielding (Execution Gate)
   - 3.8 Git Authorization Model & Protected Branch Workflow
   - 3.9 3-Step Session Ceremony & Dynamic Memory Loop
   - 3.10 8 High-Risk Operations Protection Matrix
4. [Platform-Specific Native Commands & Best Practices](#4-platform-specific-native-commands--best-practices)
   - 4.1 Google Antigravity IDE
   - 4.2 Claude Code & PreToolUse Hooks
   - 4.3 OpenAI Codex / GitHub Copilot
   - 4.4 Zed IDE
5. [End-to-End Practical Walkthrough (Real-World Feature Development)](#5-end-to-end-practical-walkthrough-real-world-feature-development)
6. [Daily Health Checks & Troubleshooting](#6-daily-health-checks--troubleshooting)

---

## 1. Core Architecture & Tool Matrix (Who Manages What)

Without physical boundaries, AI-assisted development frequently drifts, over-engineers, or breaks backward compatibility. Our Harness architecture enforces five consecutive gates:

```text
       [ User Request ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. Process & State Gate: Comet (/comet) + OpenSpec SDD │
       └──────┬─────────────────────────────────────────────────┘
              │ Scope locked; begin exploration & discovery
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. Optional semantic retrieval: CodeGraph MCP, if configured │
       └──────┬─────────────────────────────────────────────────┘
              │ Symbol dependencies clear; design & code
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. Code Gate: Superpowers (TDD red-green) + Ponytail   │
       └──────┬─────────────────────────────────────────────────┘
              │ Run tests & build commands
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. Optional command filtering: RTK CLI + agent hook          │
       └──────┬─────────────────────────────────────────────────┘
              │ Deliver & commit
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. Communication & Git: Caveman guidance (if loaded) + Git  │
       └────────────────────────────────────────────────────────┘
```

### Responsibility Matrix

| Component | Core Responsibility | Pain Point Solved | Interface |
|---|---|---|---|
| **Comet** | Versioned Native/Classic workflows | Resumable, verifiable task workflows | Follow installed version and `.comet/config.yaml` |
| **OpenSpec** | Spec-Driven Development (SDD) | Requirement amnesia, untracked delta changes | `/opsx:propose`, `docs/openspec/` live docs |
| **Superpowers** | TDD & Verification evidence gate | Hallucinated task completion, missing physical proof | Red test $\rightarrow$ Green test $\rightarrow$ Verification report |
| **CodeGraph** | Optional semantic code-search integration | Requires CLI, agent MCP wiring, and a project index | Query through configured CodeGraph MCP tools |
| **Ponytail** | Minimal-implementation guidance Skill | Unneeded dependencies and abstractions | Guidance only when the host loads the Skill |
| **Caveman** | Concise-communication guidance Skill | Overlong responses | Style guidance when loaded; preserve clarity and safety details |
| **RTK** | Optional Rust Token Killer CLI | Verbose terminal output | Requires CLI installation and a supported agent hook |
| **Git Auth** | Protected branch guidance plus limited client hook checks | Preventing accidental shared-branch operations | Rules, Claude Code client hook, and server-side branch protection |

### Rule and Memory Scope by Coding Tool

| Tool/surface | Instruction entry point | Memory scope |
|---|---|---|
| Codex desktop app | Project `AGENTS.md`; ai-memory can use the local Codex integration where the installed app exposes configured MCP/hooks | Verify the exact desktop version; ChatGPT web conversation memory is separate |
| Codex CLI | Codex home and `AGENTS.md` files from repository root through the current directory; ai-memory upstream installer supports MCP/hooks | Project context/checkpoint files remain repository-managed |
| Claude Code | User/project/directory `CLAUDE.md` or supported `AGENTS.md` | Optional Auto memory is machine-local and Claude-specific; `/memory` opens its controls |
| Antigravity CLI | Global, workspace, and directory `AGENTS.md` / `.agents/rules/*.md`; ai-memory upstream supports MCP/hooks | Run setup in the same environment as the CLI |
| Antigravity IDE | Project Markdown rules/skills plus a manually configured ai-memory MCP server | MCP provides explicit retrieval/write tools; no automatic lifecycle capture is claimed |

The deployment scripts write paths; check each host's current documentation and loaded context before assuming a file was consumed.

---

## 2. Skills & Ecosystem Tools Inventory

### 2.1 42 Integrated Native Skills Categorized

The installer copies the repository's skill directories into `.agents/skills/`; actual discovery depends on the host tool and its configuration.

#### 1. Versioned Workflow Entry Point
- **`comet`**: The Comet CLI provides versioned Native and Classic workflows. This repository ships an entry-point guide only; it does not implement Comet phase guards.

#### 2. OpenSpec Specification-Driven Suite (16 skills)
- **`openspec`**: Core architecture.
- **`openspec-propose`**: Proposes changes with design, specs, and tasks in one step.
- **`openspec-new-change`**: Step-by-step artifact creation.
- **`openspec-continue-change`**: Advances change to next artifact.
- **`openspec-ff-change`**: Fast-forwards through artifact generation.
- **`openspec-apply-change`**: Implements tasks from an active change.
- **`openspec-verify-change`**: Verifies code against delta specifications.
- **`openspec-sync-specs`**: Syncs delta specs into main specs.
- **`openspec-archive-change`**: Archives completed change.
- **`openspec-bulk-archive-change`**: Archives multiple changes in parallel.
- **`openspec-explore`**: Interactive thinking partner before creating changes.
- **`openspec-onboard`**: Guided interactive walkthrough.
- **`write-openspec-docs`**: Writes docs in house style.
- **`draft-openspec-docs`**: Collaborative section-by-section drafting.
- **`verify-openspec-docs`**: Fact-checks documentation claims.
- **`release-openspec`**: Release audit and changeset management.

#### 3. Superpowers Engineering Quality Suite (15 skills)
- **`superpowers`**: Quality constitution.
- **`using-superpowers`**: Skills discovery and invocation guard.
- **`brainstorming`**: Design exploration before implementation.
- **`writing-plans`**: Step-by-step execution planning.
- **`executing-plans`**: Strict plan execution.
- **`test-driven-development`**: TDD red-green cycle.
- **`systematic-debugging`**: Root-cause analysis before code modification.
- **`verification-before-completion`**: Mandatory proof before claiming completion.
- **`dispatching-parallel-agents`**: Spawns isolated concurrent subagents.
- **`subagent-driven-development`**: Subagent plan execution harness.
- **`using-git-worktrees`**: Isolated physical workspaces.
- **`finishing-a-development-branch`**: Merge and integration decisions.
- **`requesting-code-review`**: Pre-merge review verification.
- **`open-code-review`**: Deterministic code review — rule-first, line-anchored, coverage-mandated. Tier A via `ocr` CLI delegation, Tier B methodology without it.
- **`receiving-code-review`**: Technical evaluation of human review comments.
- **`writing-skills`**: Skill creator and validator.
- **`diagnosing-superpowers`**: Audits session drift or cost.

#### 4. Minimal Code & Syntax Graph
- **`ponytail`**: Minimal implementation ladder (stdlib first, YAGNI).
- **`codegraph`**: optional CodeGraph CLI/MCP setup guidance; installation and agent wiring are separate.

#### 5. Output Filtering & Concise Delivery
- **`rtk`**: optional Rust Token Killer CLI guidance; command rewriting requires a configured agent hook.
- **`caveman`**: Ultra-compressed telegraphic output.

#### 6. Professional Document Processing
- **`docx`**: Word document generation, editing, and styling.
- **`pdf`**: PDF text/table extraction and processing.

#### 7. Pre-Decision Review, Cross-Tool Memory & Living Documentation (In-Repo Skills)
- **`cross-tool-memory`**: Cross-tool project-scoped memory navigation and recall aid (pairs with local ai-memory backend).
- **`option-review`**: Pre-decision multi-option review generating an isolated 5-dimension decision matrix.
- **`living-documentation`**: 4-tier living documentation suite (specs/architecture/reference/guides) with frontmatter-based code-doc bidirectional traceability, supporting L0/L1/L2 change impact thresholds.

---

### 2.2 Version Locking, Online Updates & Skill Sync (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)

1. **`skills-lock.json`**:
   - Records upstream sources and LF-normalized SHA256 integrity hashes for vendored external skills;
   - Distinguishes locally-authored core skills (`sourceType: local`) from external upstream skills (`sourceType: github`).
2. **External Skill Upstream Sync (`tools/sync-skills.py`)**:
   - Built-in updater for vendored external skills;
   - **Check mode**: `python3 tools/sync-skills.py --check` (read-only, compares local and upstream `SKILL.md` hashes, reports 🟢 in-sync / 🟡 outdated);
   - **Apply mode**: `python3 tools/sync-skills.py --apply` (updates outdated `SKILL.md` files in-place and refreshes lock hashes; locally-authored skills are strictly protected);
   - Interactive terminal UI powered by `tools/tui.py` when invoked without arguments;
   - Supports `--skill <name>` for targeted updates and `--json` for automation.
3. **Living Documentation Impact Analysis (`tools/doc-impact.py`)**:
   - Analyzes code changes against living documentation traceability metadata (`docs/{specs,architecture,reference,guides,adr}/`);
   - Supports working tree inspection, commit baselines (`--since`), explicit file lists, and interactive wizard mode (`--interactive`).
4. **Unified Pipeline Runner (`pipeline.sh` / `pipeline.ps1`)**:
   - Chains the full workflow into a single execution per OS (Deploy → AI Memory → Skills Sync → Living Doc Impact);
   - Interactive wizard: `./pipeline.sh` (Linux/macOS) or `.\pipeline.ps1` (Windows);
   - Unattended automation: `./pipeline.sh --all -y` or `.\pipeline.ps1 -All -Yes`.
5. **終端互動式 TUI 核心組件 (`tools/tui.py`)**:
   - 提供基於終端原生鍵盤導航的單選選單（上下方向鍵移動游標，Enter 確認）與多選選單（上下方向鍵移動游標，空白鍵切選複選框，Enter 確認提交）；
   - 內建 TTY 與 ANSI 相容性自檢，當處於非互動管道或無 ANSI 終端時自動優雅降級為帶編號文字輸入，作為底層互動基座驅動所有部署指令碼與維護工具。
6. **Integrated Online Update Flow**:
   ```powershell
   # Windows
   .\deploy-agents.ps1 -ProjectPath "." -Update

   # Linux / macOS
   ./deploy-agents.sh . --update
   ```
   - The deployment scripts fast-forward the template repository, prompt to check/apply external skill updates, and sync managed files to target projects with `.bak.<timestamp>` backups.

---

### 2.3 Optional Harness CLI Tools

Skill availability depends on the host tool and its configuration. Terminal-level CLI tools are optional:
- **Comet CLI**: install via `npm install -g @rpamis/comet`; provides native/classic workflow execution and `--comet-init` initialization.
- **CodeGraph CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh`; Windows PowerShell: `irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex`. Run `codegraph install` to wire agents and `codegraph init` in the project.
- **RTK (Rust Token Killer) CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh`; Windows: `winget install rtk-ai.rtk`. Verify with `rtk gain`. Run `rtk init` in the project to configure agent hooks.
- **Open Code Review (OCR) CLI**: install via `npm install -g @alibaba-group/open-code-review`; enables Tier A zero-LLM-cost delegation review via the `open-code-review` skill.

The deployment scripts automatically detect these optional CLIs during initial setup and guide installation where appropriate.

---

### 2.4 Skill Loading and Optional CLI Setup

Skill discovery and context costs depend on the host agent and its configuration. File presence alone does not guarantee that a Skill is loaded. Ponytail and Caveman are guidance Skills copied with the project; CodeGraph and RTK also need their separate CLI and agent integration steps. Their effectiveness depends on the project, host, and setup, so this guide makes no fixed token-savings claims.

---

### 2.5 Engineering Skills & Rules Dispatching Matrix

| Scenario | Rule / Skill | Trigger / Keyword | Expected Behavior |
|---|---|---|---|
| **Branching / Commit / Push** | [`git-workflow.md`](.agents/rules/git-workflow.md) | `git commit` / `git push` | Commit only on temp branches; no `git add .`; human authorization required for remote push |
| **High-Risk Operations** | [`security-boundary.md`](.agents/rules/security-boundary.md) | Modifying build configs, protocols, public structs | Pause and confirm impact with human |
| **Complex Requirements** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` or "use openspec" | Propose change under `docs/openspec/changes/`; wait for confirmation |
| **Symbol Discovery** | [`token-discipline.md`](.agents/rules/token-discipline.md) + optional `codegraph` | CodeGraph MCP when configured; otherwise scoped `rg` | Do not assume CodeGraph is installed or available |
| **Feature Implementation** | `ponytail` + `test-driven-development` | Consult loaded Skills as appropriate | Understand current code, then choose the smallest correct implementation and suitable validation |
| **Bug Investigation** | `systematic-debugging` | Error trace pasted | Gather evidence $\rightarrow$ form hypothesis $\rightarrow$ minimal repro $\rightarrow$ fix |
| **Long Terminal Output** | optional `rtk` | Only when installed and its agent hook is configured | Otherwise use native concise flags; keep required validation and preserve relevant logs |
| **Token Conservation** | `caveman` | Only when the host loads the Skill or plugin | Be concise while preserving necessary context, technical accuracy, and safety details |
| **Document Processing** | `docx` / `pdf` | Mentions `.docx` or `.pdf` | Professional formatting without running code test suites |
| **Living Docs & Traceability** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `living-documentation` | `/living-documentation` / sync trace docs | Maintain 4-tier docs (specs/architecture/reference/guides) via L0/L1/L2 impact thresholds and frontmatter traceability |
| **Code Review & Quality Gate** | `open-code-review` + `requesting-code-review` | Before merge or after task completion | Rule-first, line-anchored, coverage-mandated; Tier A delegation if `ocr` CLI exists, otherwise Tier B methodology |
| **Task Completion** | `verification-before-completion` | End of task | Present physical command execution evidence |

---

## 3. Deep Dive into Core Harness Tools & Slash Commands

### 3.1 Comet: Versioned workflow entry point

Comet is an independently versioned workflow tool. Check the project's `.comet/config.yaml` and installed CLI version, then follow the Native or Classic workflow supported by that version. This repository's Comet skill is an entry-point guide; it does not create Comet state files or enforce phase guards. If Comet is not installed or configured, use the project's existing process or make a task-appropriate plan.

```text
/comet Add date-range filtered CSV export for the order service
```

Use Comet's current upstream documentation for version-specific entry points, configuration, artifact paths, and archive behavior.

---

### 3.2 OpenSpec: Spec-Driven Development

- `/opsx:propose <name>`: Proposes new change under `docs/openspec/changes/`;
- `/opsx:apply`: Implements approved change;
- `/opsx:verify`: Compares actual implementation with delta specification;
- `/opsx:sync`: Syncs delta specifications into main docs;
- `/opsx:archive`: Moves finished change to `docs/openspec/changes/archive/`.

---

### 3.3 Superpowers: TDD, Systematic Debugging & Verification Gate

1. **TDD Red-Green Cycle**:
   - Write failing test based on specification scenario;
   - Run test and observe the expected failure;
   - Write minimal code to pass;
   - Refactor and run verification.
2. **Systematic Debugging**:
   - Step 1: Trace collection;
   - Step 2: Form hypothesis;
   - Step 3: Minimal reproduction test;
   - Step 4: Fix root cause and verify.
3. **Verification Evidence Gate**:
   - No task is complete without physical terminal output evidence.

---

### 3.4 CodeGraph: Optional MCP Code-Graph Integration

```bash
# Explore call chains and architecture
Query the CodeGraph MCP tool configured for the current agent: “User authentication and JWT token flow”.

# Find definitions and all call references
Query the configured CodeGraph MCP tool for `OrderService::calculateDiscount`.
```

---

### 3.5 Ponytail: Minimal Implementation Ladder

1. Does this feature need to exist? (YAGNI);
2. Is there an existing utility to reuse?
3. Can the language standard library do this?
4. Change 1 line before rewriting 10 lines;
5. Never opportunistic refactor during bug fixes.

---

### 3.6 Caveman: Ultra-Compressed Output

- Eliminates fluff: "Sure, I'll do that for you", "Note that this requires caution";
- Delivers: Conclusion & Impact $\rightarrow$ Diff $\rightarrow$ Verification evidence.

---

### 3.7 RTK: Optional Rust Token Killer CLI

- RTK rewrites supported commands only when installed and integrated with the active agent. The repository Skill alone does not filter terminal output.
- Verify the correct product with `rtk gain`; initialize supported project hooks with `rtk init`.
- If RTK is not configured, use native concise flags and bounded log handling.

- Never run bare verbose commands;
- Always use `git status -s`, `pytest -q`, `ctest --output-on-failure`;
- Redirect multi-hundred line logs to local scratch files and slice only the failure traces.

---

### 3.8 Git Authorization Model & Protected Branch Workflow

1. **Temporary Branch Isolation**:
   - All work happens in `feature/*`, `fix/*`, `refactor/*`;
   - Never commit directly to `develop`, `master`, `main`, `release*`.
2. **Remote Push Authorization**:
   - AI can create branches and commit locally;
   - Pushing to remote or merging into protected branches requires explicit human confirmation.
3. **Iron Laws**:
   - `git push --force` is permanently forbidden;
   - Rebasing protected branches is permanently forbidden;
   - Blind staging via `git add .` is forbidden (use `git add <explicit-path>`);
   - Commit message standard: `{type}: {description}`.

---

### 3.9 Project Memory and Session Checkpoint (`PROJECT_CONTEXT.md` / `SESSION_STATE.md`)

Treat memory as a verifiable summary and navigation aid, not as a replacement for code or maintained documentation:
1. **Task start:** Read `PROJECT_CONTEXT.md` (verified durable project facts) and `SESSION_STATE.md` (current checkpoint) only when present and relevant; verify branch, configuration, and implementation facts that affect the task.
2. **During work:** Keep plans when useful for multi-step work. Do not add automatic capture of prompts, tool inputs/outputs, source files, or terminal commands.
3. **Meaningful closeout:** Update `SESSION_STATE.md` with completed work, actual verification evidence, remaining steps, and still-relevant risks; remove stale items. Update `PROJECT_CONTEXT.md` only when durable architecture, constraints, or confirmed decisions change. No-op sessions need no empty update.
4. **Sources and conflicts:** Label uncertainty and date/source facts likely to change. Current user instructions and current code/configuration/reproducible evidence take precedence over memory summaries.
5. **Privacy:** Do not record credentials, private keys, raw personal data, full conversation/tool logs, or unnecessary personal information. Shared global templates must not contain private user preferences.
6. **Directory scope:** A directory `AGENTS.md` contains only local boundaries and constraints. Do not create directory memory files by default; keep project facts and checkpoints in their root files.

**Claude Code native Auto memory** is a separate machine-local project memory that can be inspected, edited, or deleted with `/memory`. It is not shared across tools or machines and does not replace the project files above. Claude Code manages this feature; this repository's deployer does not enable, disable, or capture it. See the [Claude Code memory docs](https://code.claude.com/docs/en/memory).

#### Optional cross-agent memory: ai-memory

This repository selects only [ai-memory](https://github.com/akitaonrails/ai-memory) as an optional cross-agent backend. Its local Markdown and full-text search path uses no LLM, embedding provider, or API key. The repository does not install or start it automatically.

To opt in one repository, copy `.ai-memory.toml.example` to the ignored `.ai-memory.toml`, replace the workspace/project names, then run `setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` or `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>`. The helper requires an existing ai-memory install and delegates configuration to its upstream merge-aware commands. Review the hook capability output; allowlist mode is effective only for hooks that enforce native capture policy.

The setup includes Claude Code and Codex CLI MCP/hooks, plus Antigravity CLI MCP/hooks. Codex desktop support depends on the installed desktop version exposing the local Codex integration; verify it in the app. Antigravity IDE is MCP-only: add `http://127.0.0.1:49374/mcp` as `serverUrl` through its MCP settings or the documented config file. ChatGPT web uses manual Markdown handoff in the free local setup.

Windows supports both WSL2 and native modes upstream. Install and configure ai-memory in the same environment that launches the agent; see the [Windows guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md). Path exclusions do not redact arbitrary prompt text. Back up with `ai-memory --data-dir <data-dir> backup --to <archive-path>`; uninstall removes integrations but not data. Stop the service and verify the configured data directory before intentionally deleting it. See the [marker reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md) and [installation guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) for platform paths and Docker commands.

### 3.10 8 High-Risk Operations Protection Matrix

Human confirmation is mandatory before:
- [ ] 1. Modifying build configs (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
- [ ] 2. Adding new third-party dependencies;
- [ ] 3. Modifying global public data structures (`public_struct.h`, `types.ts`);
- [ ] 4. Modifying core dispatch singletons or public service APIs;
- [ ] 5. Changing wire protocols or serialization contracts (`protofile/`);
- [ ] 6. Altering license, cryptography, or auth code;
- [ ] 7. Modifying `.gitignore` or CI/CD pipelines;
- [ ] 8. High-impact cross-module changes that affect shared contracts or require broad coordination (file count alone is not a risk trigger).

---

## 4. Platform-Specific Native Commands & Best Practices

### 4.1 Google Antigravity CLI and IDE
- The CLI runs as `agy`; the desktop IDE is a separate surface. Both document file-based workspace/global rules, but CLI slash commands and IDE controls are surface-specific.
- `/plan`: Structured task planning for $\ge 3$ steps;
- `/goal`: Unattended autonomous loop until verified completion;
- `/grill-me`: Interactive discovery interview when requirements are ambiguous;
- `/learn`: Captures lessons learned into `tasks/lessons.md`;
- `/schedule`: Background timers and recurring cron monitoring.

### 4.2 Claude Code and PreToolUse Client Hook
- `/compact`: Compresses conversation history when token count is high;
- `/cost`: Real-time session token usage;
- `/review`: Reviews working copy diffs;
- `@<path>`: Dynamically loads specific rules on demand.
- **Security hook**: `.claude/settings.json` runs Claude Code client-side checks for matching tool calls. It can reject selected patterns or warn; it is not an operating-system control or memory collector.

### 4.3 Codex in ChatGPT, Codex CLI, and GitHub Copilot
- Codex CLI documents `AGENTS.md` discovery from Codex home and the repository path to the current directory. Do not infer that exact behavior for ChatGPT/desktop; check its current product behavior and configuration.
- `/hooks`: Inspects and trusts lifecycle hooks;
- `$comet`: Triggers Comet state machine in Codex CLI;
- `@workspace`: Scans workspace context in VS Code.

### 4.4 Zed IDE
- Reuse the project `AGENTS.md`; this installer does not create a Zed-specific file;
- `Ctrl+Enter` (Inline Assist) with `follow ponytail principles`;
- Assistant Panel (`Ctrl+?`) for multi-turn architectural planning.

---

## 5. End-to-End Practical Walkthrough (Real-World Feature Development)

**Requirement**: "Add a CSV export endpoint with date range filtering to the order service."

```text
Step 1: Session Ceremony & Breakpoint Awareness (Session Start)
  ├─ Prioritize reading PROJECT_CONTEXT.md & SESSION_STATE.md to restore architecture & resume from breakpoint
  ├─ Check tasks/lessons.md and tasks/todo.md (if present)
  └─ git checkout -b feature/order-csv-export

Step 2: Scoping & Change Creation (Comet + OpenSpec SDD)
  ├─ /comet Add date range CSV export endpoint
  ├─ Generated: docs/openspec/changes/add-csv-export/
  └─ Confirm Proposal with human

Step 3: Optional semantic retrieval (CodeGraph, if configured)
  ├─ Prohibited: grep -rn "export" .
  └─ Query configured CodeGraph MCP; otherwise use scoped code search
      └─ Located: router.py, order_repo.py, types.ts

Step 4: Red Test (Superpowers TDD)
  ├─ tests/test_export.py: Write failing test with invalid date range check
  └─ pytest tests/test_export.py -q -> FAILED (Red)

Step 5: Minimal Implementation (Ponytail)
  ├─ Python stdlib: import csv, datetime (no heavy export package)
  └─ Add filter condition in order_repo.py and route in router.py

Step 6: Green Verification (RTK)
  ├─ pytest tests/test_export.py -q -> PASSED (Green, 2 passed in 0.3s)
  └─ npm test -- packages/order --reporter=dot

Step 7: Delivery, Safe Commit & Selective Memory Closeout (Session Finish)
  ├─ Output: Concise diff and passing test evidence
  ├─ git add tests/test_export.py api/router.py repo/order_repo.py
  ├─ git commit -m "feat: add date-range CSV export endpoint"
  ├─ Ask human before git push
  ├─ Selective memory closeout:
  │   ├─ Update SESSION_STATE.md at meaningful task boundaries with actual evidence and remaining work
  │   └─ Update PROJECT_CONTEXT.md only when durable project facts change; skip empty updates
  ├─ Update tasks/todo.md
  └─ Archive OpenSpec change
```

---

## 6. Daily Health Checks & Troubleshooting

### Daily Health Check:
```bash
Check the installed Comet version and project configuration before using Comet-specific commands.
Read `tasks/lessons.md` when it is relevant to the task.
```

### Reference Documentation:
- Unified Pipeline Runners:
  - Windows: [`run-pipeline.ps1`](run-pipeline.ps1) / [`pipeline.ps1`](pipeline.ps1)
  - Linux / macOS: [`run-pipeline.sh`](run-pipeline.sh) / [`pipeline.sh`](pipeline.sh)
- One-Click Deployment Scripts:
  - Windows: [`deploy-agents.ps1`](deploy-agents.ps1)
  - Linux / macOS: [`deploy-agents.sh`](deploy-agents.sh)
- Maintenance Tools:
  - Terminal UI Library: [`tools/tui.py`](tools/tui.py)
  - Skill Sync Tool: [`tools/sync-skills.py`](tools/sync-skills.py)
  - Living Doc Impact Gate: [`tools/doc-impact.py`](tools/doc-impact.py)
- Deployment & Configuration Guide:
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md)
- Rules Architecture:
  - [`Global AGENTS.md`](Global%20AGENTS.md)
  - [`Project AGENTS.md`](Project%20AGENTS.md)
  - [`Directory AGENTS.md`](Directory%20AGENTS.md)
