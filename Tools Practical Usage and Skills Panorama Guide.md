# Practical Guide to AI Tooling and Skills Panorama (Claude Code / Codex / Antigravity IDE / Zed IDE)

> **Language / 语言**: **English** | [中文](各工具实战使用与技能全景指南.md)

This guide provides a comprehensive handbook for software engineering and technical documentation with AI agents: **which skills and Harness tools to install, underlying token economics, tool configuration and wiring, when and how to invoke core slash commands (e.g., `/comet`, `/plan`, `/opsx`, `codegraph`), and an end-to-end practical walkthrough.**

---

## Table of Contents

1. [Core Architecture & Tool Matrix (Who Manages What)](#1-core-architecture--tool-matrix-who-manages-what)
2. [Skills & Ecosystem Tools Inventory](#2-skills--ecosystem-tools-inventory)
   - 2.1 40+ Integrated Native Skills Categorized
   - 2.2 Version Locking & Online Updates (`skills-lock.json` + `deploy-agents`)
   - 2.3 Optional Harness CLI Tools
   - 2.4 Token Economics of Skills (Why 40+ Skills Do NOT Blow Up Context)
   - 2.5 Engineering Skills & Rules Dispatching Matrix
3. [Deep Dive into Core Harness Tools & Slash Commands](#3-deep-dive-into-core-harness-tools--slash-commands)
   - 3.1 Comet: Process Orchestration & Phase Guards (`/comet`)
   - 3.2 OpenSpec: Spec-Driven Development (`/opsx:propose`, `/opsx:apply`, etc.)
   - 3.3 Superpowers: TDD, Systematic Debugging & Verification Gate
   - 3.4 CodeGraph: AST-Level Symbol Discovery (`codegraph explore`)
   - 3.5 Ponytail: Minimal Implementation Ladder (Generation Gate)
   - 3.6 Caveman: Ultra-Compressed Output (Communication Gate)
   - 3.7 RTK: Output Truncation & Log Shielding (Execution Gate)
   - 3.8 Git Authorization Model & Protected Branch Workflow
   - 3.9 3-Step Session Ceremony & Dynamic Memory Loop
   - 3.10 8 High-Risk Operations Protection Matrix
4. [Platform-Specific Native Commands & Best Practices](#4-platform-specific-native-commands--best-practices)
   - 4.1 Google Antigravity IDE
   - 4.2 Claude Code & PreToolUse Hardware Interception
   - 4.3 OpenAI Codex / GitHub Copilot
   - 4.4 Zed IDE
5. [End-to-End Practical Walkthrough (Real-World Feature Development)](#5-end-to-end-practical-walkthrough-real-world-feature-development)
6. [Daily Health Checks & Troubleshooting](#6-daily-health-checks--troubleshooting)

---

## 1. Core Architecture & Tool Matrix (Who Manages What)

Without physical boundaries, AI-assisted development frequently drifts, over-engineers, or breaks backward compatibility. Our Harness architecture enforces five consecutive gates:

```
       [ User Request ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. Process & State Gate: Comet (/comet) + OpenSpec SDD │
       └──────┬─────────────────────────────────────────────────┘
              │ Scope locked; begin exploration & discovery
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. Retrieval Gate: CodeGraph (AST graph; no blind grep)│
       └──────┬─────────────────────────────────────────────────┘
              │ Symbol dependencies clear; design & code
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. Code Gate: Superpowers (TDD red-green) + Ponytail   │
       └──────┬─────────────────────────────────────────────────┘
              │ Run tests & build commands
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. Execution Gate: RTK (truncate long output, tee log) │
       └──────┬─────────────────────────────────────────────────┘
              │ Deliver & commit
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. Communication & Git Gate: Caveman + Protected Branch│
       └────────────────────────────────────────────────────────┘
```

### Responsibility Matrix

| Component | Core Responsibility | Pain Point Solved | Interface |
|---|---|---|---|
| **Comet** | State machine & phase guard | Goal drift, jumping ahead to code before design is agreed | `/comet <task>`, CLI `comet doctor` |
| **OpenSpec** | Spec-Driven Development (SDD) | Requirement amnesia, untracked delta changes | `/opsx:propose`, `docs/openspec/` live docs |
| **Superpowers** | TDD & Verification evidence gate | Hallucinated task completion, missing physical proof | Red test $\rightarrow$ Green test $\rightarrow$ Verification report |
| **CodeGraph** | AST syntax code knowledge graph | Grep pollution with thousands of irrelevant tokens | `codegraph explore "query"` / MCP |
| **Ponytail** | Lazy ladder (entropy reduction) | Unnecessary third-party packages, premature abstractions | Standard library first, 1 line over 10 |
| **Caveman** | Ultra-compressed output | Chatty greetings, disclaimers, and token waste | Direct Diff and evidence |
| **RTK** | Command output truncation | Thousands of compiler/test lines flooding context | CLI / PreToolUse hook |
| **Git Auth** | Protected branch isolation | AI corrupting master/develop branches directly | `.claude/settings.json` hardware exit 1 |

---

## 2. Skills & Ecosystem Tools Inventory

### 2.1 40+ Integrated Native Skills Categorized

The automated installer ([`deploy-agents.ps1`](deploy-agents.ps1) / [`deploy-agents.sh`](deploy-agents.sh)) deploys 40 modular engineering skills into `.agents/skills/`:

#### 1. Workflow & State Machine
- **`comet`**: Enforces strict phases: Open $\rightarrow$ Proposal $\rightarrow$ Specs $\rightarrow$ Design $\rightarrow$ Tasks $\rightarrow$ Build $\rightarrow$ Verify $\rightarrow$ Archive.

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
- **`receiving-code-review`**: Technical evaluation of human review comments.
- **`writing-skills`**: Skill creator and validator.
- **`diagnosing-superpowers`**: Audits session drift or cost.

#### 4. Minimal Code & Syntax Graph
- **`ponytail`**: Minimal implementation ladder (stdlib first, YAGNI).
- **`codegraph`**: AST Tree-sitter code graph exploration.

#### 5. Output Filtering & Concise Delivery
- **`rtk`**: Command log truncation and local tee preservation.
- **`caveman`**: Ultra-compressed telegraphic output.

#### 6. Professional Document Processing
- **`docx`**: Word document generation, editing, and styling.
- **`pdf`**: PDF text/table extraction and processing.

---

### 2.2 Version Locking & Online Updates (`skills-lock.json` + `deploy-agents`)

1. **`skills-lock.json`**:
   - Locks the exact Git commit SHA and upstream URL for every installed skill.
2. **One-Click Online Update**:
   ```powershell
   # Windows
   .\deploy-agents.ps1 -ProjectPath "." -Update

   # Linux / macOS
   ./deploy-agents.sh . --update
   ```
   - Automatically executes `npx -y skills@latest update -y`;
   - Preserves custom project configurations in `AGENTS.md` and generates [`AGENTS.template.md`](AGENTS.template.md) for comparison.

---

### 2.3 Optional Harness CLI Tools

All skills are **100% active in conversation**. Terminal-level CLI tools are optional:
- **Comet CLI**: `npm install -g @rpamis/comet` (provides `comet doctor` and `comet status`);
- **CodeGraph CLI**: `npm install -g @codegraph/cli` (provides terminal `codegraph explore`);
- **RTK Binary**: `brew install rtk` or download release binary.

---

### 2.4 Token Economics of Skills (Why 40+ Skills Do NOT Blow Up Context)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Static Prefix (~750 Tokens)                                         │
│    - Only YAML Frontmatter (name + description, ~20 Tokens each)       │
│    - Hits Prompt Cache (KV Cache): 90%–99% cache rate, 10% base cost    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Only read when triggered
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Progressive On-Demand Disclosure                                    │
│    - Agent reads full SKILL.md instructions only when relevant         │
│    - Context is archived when task finishes                             │
└────────────────────────────────────────────────────────────────────────┘
```

#### Token Return on Investment (ROI):
| Component | Cost Mechanism | Savings | Net Benefit |
|---|---|---|---|
| **Skill Prefix** | ~750 Tokens (cached) | Provides accurate routing anchors | Negligible cost |
| **`Caveman`** | Triggered on demand | Cuts response Tokens by **40%–75%** | Highest savings |
| **`Ponytail`** | Active during coding | Reduces code length by **30%–50%** | Large code reduction |
| **`CodeGraph`** | Runs AST queries | Replaces full-repo grep (tens of thousands of tokens) | Saves **90%+** retrieval tokens |
| **`RTK`** | Output truncation | Truncates multi-thousand line logs to key 20 lines | Saves **80%+** environment noise |

---

### 2.5 Engineering Skills & Rules Dispatching Matrix

| Scenario | Rule / Skill | Trigger / Keyword | Expected Behavior |
|---|---|---|---|
| **Branching / Commit / Push** | [`git-workflow.md`](.agents/rules/git-workflow.md) | `git commit` / `git push` | Commit only on temp branches; no `git add .`; human authorization required for remote push |
| **High-Risk Operations** | [`security-boundary.md`](.agents/rules/security-boundary.md) | Modifying build configs, protocols, public structs | Pause and confirm impact with human |
| **Complex Requirements** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` or "use openspec" | Propose change under `docs/openspec/changes/`; wait for confirmation |
| **Symbol Discovery** | [`token-discipline.md`](.agents/rules/token-discipline.md) + `codegraph` | `codegraph explore "query"` | Use AST symbol graph; no blind recursive grep |
| **Feature Implementation** | `ponytail` + `test-driven-development` | "use ponytail" / "TDD" | 7-step minimal code ladder; write failing test first |
| **Bug Investigation** | `systematic-debugging` | Error trace pasted | Gather evidence $\rightarrow$ form hypothesis $\rightarrow$ minimal repro $\rightarrow$ fix |
| **Long Terminal Output** | `rtk` | Test / build commands | Append filtering flags (`-q`, `--output-on-failure`); redirect long logs |
| **Token Conservation** | `caveman` | `/caveman` | Telegraphic format; conclusions, Diff, and proof only |
| **Document Processing** | `docx` / `pdf` | Mentions `.docx` or `.pdf` | Professional formatting without running code test suites |
| **Task Completion** | `verification-before-completion` | End of task | Present physical command execution evidence |

---

## 3. Deep Dive into Core Harness Tools & Slash Commands

### 3.1 Comet: Process Orchestration & Phase Guards (`/comet`)

- **When to use**: New features, multi-file bug fixes, structural refactoring, audited enterprise changes.
- **When to bypass**: Quick questions, single-file doc fixes, syntax typos.
- **Invocation**:
  ```text
  /comet Add date-range filtered CSV export for order service
  ```
- **8-Phase Guard**:
  1. Open $\rightarrow$ 2. Proposal $\rightarrow$ 3. Specs $\rightarrow$ 4. Design $\rightarrow$ 5. Tasks $\rightarrow$ 6. Build $\rightarrow$ 7. Verify $\rightarrow$ 8. Archive.
  If the Design phase has not been approved, the guard blocks code implementation!

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

### 3.4 CodeGraph: AST-Level Symbol Discovery (`codegraph explore`)

```bash
# Explore call chains and architecture
codegraph explore "User authentication and JWT token flow"

# Find definitions and all call references
codegraph explore "OrderService::calculateDiscount"
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

### 3.7 RTK: Output Truncation & Log Shielding

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

### 3.9 3-Step Session Ceremony & Dynamic Memory Loop

1. **Session Start**: Read [`tasks/lessons.md`](tasks/lessons.md) and [`tasks/todo.md`](tasks/todo.md);
2. **In-Progress**: Maintain checklist for $\ge 3$-step tasks; stop and re-plan if assumptions fail;
3. **Session Finish**: Update todo status; record mistakes and corrections into `tasks/lessons.md`. **Never repeat the same mistake twice.**

---

### 3.10 8 High-Risk Operations Protection Matrix

Human confirmation is mandatory before:
- [ ] 1. Modifying build configs (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
- [ ] 2. Adding new third-party dependencies;
- [ ] 3. Modifying global public data structures (`public_struct.h`, `types.ts`);
- [ ] 4. Modifying core dispatch singletons or public service APIs;
- [ ] 5. Changing wire protocols or serialization contracts (`protofile/`);
- [ ] 6. Altering license, cryptography, or auth code;
- [ ] 7. Modifying `.gitignore` or CI/CD pipelines;
- [ ] 8. Making large cross-module changes spanning 3+ files.

---

## 4. Platform-Specific Native Commands & Best Practices

### 4.1 Google Antigravity IDE
- `/plan`: Structured task planning for $\ge 3$ steps;
- `/goal`: Unattended autonomous loop until verified completion;
- `/grill-me`: Interactive discovery interview when requirements are ambiguous;
- `/learn`: Captures lessons learned into `tasks/lessons.md`;
- `/schedule`: Background timers and recurring cron monitoring.

### 4.2 Claude Code & PreToolUse Hardware Interception
- `/compact`: Compresses conversation history when token count is high;
- `/cost`: Real-time session token usage;
- `/review`: Reviews working copy diffs;
- `@<path>`: Dynamically loads specific rules on demand.
- **Hardware Hook**: `.claude/settings.json` enforces OS-level `exit 1` on forbidden git actions.

### 4.3 OpenAI Codex / GitHub Copilot
- `/hooks`: Inspects and trusts lifecycle hooks;
- `$comet`: Triggers Comet state machine in Codex CLI;
- `@workspace`: Scans workspace context in VS Code.

### 4.4 Zed IDE
- `ZED.md` auto-discovery (symlinked to `AGENTS.md`);
- `Ctrl+Enter` (Inline Assist) with `follow ponytail principles`;
- Assistant Panel (`Ctrl+?`) for multi-turn architectural planning.

---

## 5. End-to-End Practical Walkthrough (Real-World Feature Development)

**Requirement**: "Add a CSV export endpoint with date range filtering to the order service."

```
Step 1: Session Ceremony
  ├─ Check tasks/lessons.md and tasks/todo.md
  └─ git checkout -b feature/order-csv-export

Step 2: Scoping & Change Creation (Comet + OpenSpec SDD)
  ├─ /comet Add date range CSV export endpoint
  ├─ Generated: docs/openspec/changes/add-csv-export/
  └─ Confirm Proposal with human

Step 3: AST Retrieval (CodeGraph)
  ├─ Prohibited: grep -rn "export" .
  └─ codegraph explore "OrderExportHandler"
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

Step 7: Delivery & Safe Commit (Caveman + Git Workflow)
  ├─ Output: Concise diff and passing test evidence
  ├─ git add tests/test_export.py api/router.py repo/order_repo.py
  ├─ git commit -m "feat: add date-range CSV export endpoint"
  ├─ Ask human before git push
  ├─ Update tasks/todo.md
  └─ Archive OpenSpec change
```

---

## 6. Daily Health Checks & Troubleshooting

### Daily Health Check:
```bash
comet doctor        # Check wiring of tools, hooks, and index
comet status        # Check status of in-progress changes
cat tasks/lessons.md # Review latest learned lessons
```

### Reference Documentation:
- One-Click Deployment Scripts:
  - Windows: [`deploy-agents.ps1`](deploy-agents.ps1)
  - Linux / macOS: [`deploy-agents.sh`](deploy-agents.sh)
- Deployment & Configuration Guide:
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](多工具部署配置指南.md)
- Rules Architecture:
  - [`Global AGENTS.md`](Global%20AGENTS.md)
  - [`Project AGENTS.md`](Project%20AGENTS.md)
  - [`Directory AGENTS.md`](Directory%20AGENTS.md)
