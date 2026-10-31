# Project AGENTS.md

## Inheritance and Purpose

- This file serves as the root instruction file for the current project, supplementing the general baseline of [Global AGENTS.md] with project-specific engineering context.
- Adopting a **Progressive Disclosure** architecture, high-frequency red lines and project commands are maintained here, while granular rules reside in `.agents/rules/`, accessed on-demand by the Agent.

## Project Overview

- **Project Name**: `<PROJECT_NAME>`
- **Business Purpose**: `<PROJECT_PURPOSE>` (one sentence explaining core business scenario and target audience)
- **Primary Maintainers**: `<OWNERS>`
- **Repository URL & Default Branch**: `<REPOSITORY_URL>`; default branch `<DEFAULT_BRANCH>` (matching remote `origin/HEAD`)

## Common Development Commands (CLI Context)

> Confirm working directory before running commands. Command execution must use filtering flags to avoid log floods; never dump full verbose logs directly into context.

```bash
# 1. Dependency management / build configuration
<INSTALL_COMMAND>                  # e.g.: npm ci / poetry install / cmake -B build / go mod download / cargo check

# 2. Local development and compilation
<DEV_COMMAND>                      # e.g.: npm run dev / python main.py / cargo run
<BUILD_COMMAND>                    # e.g.: npm run build / cmake --build build / go build ./... / cargo build --release

# 3. Targeted unit tests and verification (must run after changes; concise output required)
<UNIT_TEST_COMMAND>                # e.g.: npm test -- --reporter=dot / pytest -q / ctest --output-on-failure
<TARGETED_TEST_COMMAND>            # Single-file tests: npm test -- <path> / pytest <path> -q / ctest -R <test_name>
<INTEGRATION_TEST_COMMAND>         # Integration tests: npm run test:e2e

# 4. Code quality, linting, and static analysis
<LINT_COMMAND>                     # e.g.: npm run lint / ruff check . / clang-tidy / golangci-lint run / cargo clippy
<FORMAT_COMMAND>                   # e.g.: npm run format / black . / clang-format -i / gofmt -w . / cargo fmt
<TYPE_CHECK_COMMAND>               # e.g.: npm run typecheck / mypy .

# 5. Data migration and deployment (high-risk operations require confirmation)
<MIGRATION_COMMAND>                # e.g.: npm run db:migrate / alembic upgrade head
```

## Technology Stack and Runtime Environment

| Category | Technology Choice & Version | Additional Notes |
|---|---|---|
| **Language & Standard/Runtime** | `<LANGUAGE_AND_VERSION>` | e.g.: C++20 / Python 3.11 / TypeScript 5.4 (Node 20) / Go 1.22 / Rust 1.78 |
| **Package Manager / Build Tool** | `<PACKAGE_MANAGER>` | e.g.: CMake+Ninja / Conan / Poetry / pnpm / Cargo / Go Modules |
| **Core Frameworks / Libraries** | `<FRAMEWORK>` | e.g.: Qt 6 / Boost / FastAPI / Next.js / Gin / Tokio |
| **Persistence Layer & Storage** | `<DATABASE_AND_CACHE>` | e.g.: PostgreSQL 16 / SQLite 3 / Redis 7 |
| **CI/CD Configuration** | `<CI_PATH>` | e.g.: `.github/workflows/ci.yml` / `.gitlab-ci.yml` |

## Core Architectural Red Lines

1. **Unidirectional Layered Dependencies**: Upper layers call lower layers; lower layers must never reference upper-layer business logic. Cyclic dependencies between modules are strictly forbidden.
2. **Unified Exception Flow**: Business errors must throw unified encapsulated business exceptions; never silently swallow exceptions. Asynchronous calls must include error handling.
3. **Configuration Isolation**: All configuration is read via unified environment variables or configuration modules; never hardcode or read raw env vars deep within modules.
4. **Log Desensitization**: Any sensitive field printed to the console or logs (PII, tokens, passwords) must be masked and desensitized.
5. **Risk Classification**: Differentiate alerts, notices, and mandatory authorization per `.agents/rules/security-boundary.md`; file count alone is not an authorization threshold.
6. **Git Protected Branch Isolation**: Never edit code directly on protected branches (develop/master/main/release*/staging). Changes must use temporary branches. Blind `git add .` is prohibited.

## Engineering Lifecycle Roles and Phase Gates

This project enforces a tightly-knit engineering closed loop across all phases. Feature work, change requests, and bug fixes must advance sequentially without skipping gates:

| Lifecycle Phase | Core Role | Responsibilities & Artifacts | Linked Rules & Skills | Exit Gate |
|---|---|---|---|---|
| **1. Requirements** | 🎯 **Product Manager (PM)** | Requirement elicitation, user stories, PRD, and acceptance criteria | `brainstorming`, `engineering-docs` (PRD), `openspec` | Clear acceptance criteria; unambiguous scope and value |
| **2. Architecture** | 🏗️ **Architect** | Technical design, architecture diagrams, stack selection, risk analysis (HLD/LLD) | `option-review`, `codegraph`, `engineering-docs` (HLD/LLD) | Multi-angle review complete; zero irreversible one-way doors |
| **3. Implementation**| 💻 **Developer** | Production code, unit tests, clean refactoring | `test-driven-development`, `ponytail`, `writing-plans` | Test-first (red-green loop); minimal clean implementation |
| **4. Code Review** | 🔍 **Reviewer** | Deterministic review reports, security audit, remediation list | `open-code-review`, `requesting-code-review` | Line-anchored findings; zero Critical/Important defects |
| **5. Verification** | 🧪 **QA (Test Engineer)** | Test case design, boundary testing, bug retests, test report | `verification-before-completion`, `systematic-debugging` | Full test suite passing with authentic terminal evidence |
| **6. Delivery** | 📦 **Release Team** | Living doc & code traceability sync, release tagging, archiving | `living-documentation`, `finishing-a-development-branch` | Bidirectional living doc and code traceability verified |

> See Global AGENTS.md "Multi-Angle Deterministic Review Protocol" section for the review protocol.

## Sub-rule and Engineering Skill Dispatch Matrix (On-Demand Activation)

To avoid context explosion, fine-grained rules and skills reside in `.agents/rules/` and `.agents/skills/`. Skills requiring external CLI / MCP operate only when installed and configured:

| Scenario | Bound Rule / Skill | Trigger Syntax & Action | Expected Behavioral Standard |
|---|---|---|---|
| **Branching / Commits / Pushes** | `git-workflow.md` | Any `git commit` / `git push` / branch switch | Commit only on feature branches; no `git add .`; require authorization before touching remote; no force push |
| **High-Risk Operations / Structural Changes** | `security-boundary.md` | Triggering threshold defined by rules | Explain impacts per risk level; pause only when authorization is explicitly mandatory |
| **Complex Features / Architecture Overhauls** | `engineering-spec.md` + optional `comet` / `openspec` workflow | Workflow specified by user or configured in project | Comply with state files and流程 of chosen tool; plan as needed when unconfigured |
| **Code Dependencies / Finding Usages** | `token-discipline.md` + optional `codegraph` | Semantic exploration when CodeGraph MCP is available; else bounded `rg` | Do not assume CLI/MCP availability if unconfigured; bound search scope to problem |
| **Implementation / Coding Phase** | `engineering-spec.md` + `ponytail` + `test-driven-development` | Consult deployed skills on-demand; test per risk and project requirements | Understand existing code before choosing minimal valid solution; verify along Ponytail ladder |
| **Complex Bugs / Intermittent Triage** | `engineering-spec.md` + `systematic-debugging` | Paste full error trace | No blind band-aids; collect evidence, formulate hypotheses, find root causes before fixing |
| **Verbose Output / Batch Test Runs** | `token-discipline.md` + optional `rtk` | RTK hook rewrites supported commands when configured; else use native concise flags | Do not assume automatic rewrites; save long logs locally and report only relevant summaries |
| **Token Exhaustion / Concise Output** | `Global AGENTS.md` + optional `caveman` | Enable on-demand when host tool loads skill | Concise expression while retaining safety warnings, necessary context, and technical precision |
| **Documentation / Architecture Sync** | `engineering-spec.md` + optional `living-documentation` | `/living-documentation` / Arch and reference docs sync | Sync four-tier docs per L0/L1/L2 thresholds; maintain bi-directional Frontmatter traceability |
| **Formal R&D Docs / Templated Output** | `engineering-docs` | When writing PRD/SRS/HLD/LLD/test plans etc. | Pick template via 31→15 decision tree; follow rendering-spec.md (heading sizes/fonts/paragraphs) |
| **Code Review / Pre-Merge Quality Gate** | `open-code-review` + `requesting-code-review` | Feature complete or prior to merging | Rule-first, line-anchored, full-coverage; use Tier A via `ocr` CLI if present, else Tier B |

---

## Dynamic Memory and Task Tracking

- **Session Start**: When files exist and are relevant to the task, review `PROJECT_CONTEXT.md` and `SESSION_STATE.md`; verify branches, states, configurations, and implementation facts affecting work.
- **Project Long-Term Memory**: `PROJECT_CONTEXT.md` records verified, cross-task useful architectural facts, constraints, technical decisions, and rationales. It is an index and navigation aid, not a substitute for code or formal designs; include source paths or decision records.
- **Session Breakpoints**: Update `SESSION_STATE.md` at meaningful boundaries, recording completed work, real verification evidence, remaining steps, and active environmental risks. Verify on session start and prune expired breakpoints; avoid empty updates.
- **Update Scope**: Modify `PROJECT_CONTEXT.md` only when long-term facts change; update only `SESSION_STATE.md` for current breakpoints. Do not force rewriting both for small tasks.
- **Reusable Experience**: When the project uses `tasks/lessons.md`, record reusable lessons not yet codified into rules; use `tasks/todo.md` or tool plans for in-progress items.
- **Source and Timeliness**: Mark inferences as inferences; date volatile facts. In case of conflicts with current user instructions, code, or reproducible evidence, current evidence takes precedence.
- **Privacy and Security**: Do not store credentials, private keys, raw personal data, complete logs, or unnecessary personal info; shared repositories must not store private preferences.
- **Optional Long-Term Memory**: Cross-tool memory uses local ai-memory only; not deployed or started by default, zero API keys required. Explicitly configure hooks/MCP and local `.ai-memory.toml` when needed; never block tasks when unavailable.
- **Shared Memory Skill**: Use `.agents/skills/cross-tool-memory/SKILL.md` when continuing across sessions or making durable decisions; never persist full conversations or unverified conclusions.
- **Living Documentation & Code Traceability**: Long-term documentation lives under `docs/` (`docs/specs/`, `docs/architecture/`, `docs/reference/`, `docs/guides/`). Declare `modules` and `depends_on` in Frontmatter. Keep code and docs synchronized; see `.agents/skills/living-documentation/SKILL.md`.

## Definition of Done Checklist

When the verification gate is active (`gate/feature_list.json` exists), drive all task transitions through `python3 gate/pass-gate.py` (`WIP=1`; never hand-edit or script-edit `gate/feature_list.json`): check `pass-gate.py status` and claim work with `start --id <id>` before coding (register new items first via `add --level <unit|integration|e2e>` with the verification command written upfront). After completing feature development or requirement implementation, execute these steps in order — none may be skipped:

1. [ ] **Test & gate verification**: Run relevant tests (unit/integration) and `python3 gate/pass-gate.py verify --id <id>` (or three-layer `pass-gate.py terminate`), confirming exit 0 with recorded execution evidence
2. [ ] **Update SESSION_STATE.md & check-clean**: Record completed items, verification evidence, remaining steps, and active risks, then run `python3 gate/pass-gate.py check-clean` to confirm a clean handover
3. [ ] **Update PROJECT_CONTEXT.md / DECISIONS.md**: If architecture, technical decisions, or long-term constraints changed, sync updates; skip if only breakpoints changed
4. [ ] **Execute code review**: You MUST invoke the `open-code-review` skill (or `ocr` CLI) yourself — line-anchored, full coverage. NEVER ask the user whether to review; just do it
5. [ ] **Zero defects**: Fix per review feedback; Critical / Important defects must be zero before merge

> Never skip step 4 to merge directly. Do not claim task completion without gate verification and review evidence.

## Directory-Level Rule Index

In monorepos or projects with highly isolated submodules, create directory-level `AGENTS.md` only where necessary:
- Add `AGENTS.md` inside submodules with distinct boundaries to define custom scope and verification commands; standard directories inherit this file directly.
