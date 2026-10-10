# Skills Usage Guide

> **Language / 语言**: **English** | [简体中文](Skills%20Usage%20Guide.zh.md) | [繁體中文](Skills%20Usage%20Guide.zh-tw.md) | [Français](Skills%20Usage%20Guide.fr.md) | [Deutsch](Skills%20Usage%20Guide.de.md)

How the 43 bundled skills actually work in practice: which ones trigger automatically,
which ones you invoke explicitly, and when to use each.

## How Skill Triggering Works

Claude Code decides to load a skill in two ways:

| Mode | How | Example |
|---|---|---|
| **Auto** | Claude reads the skill's `description` and invokes it when your request matches | You say "fix this bug" → `systematic-debugging` loads automatically |
| **Explicit** | You type the slash command or name the skill | You type `/comet` or say "use comet for this task" |
| **Hybrid** | Both work — auto-triggers on matching context, also invocable directly | You say "review this PR" → `open-code-review` loads; or type `/open-code-review` |

**Key insight:** Auto-triggering depends on the `description` field in each skill's `SKILL.md`.
If Claude doesn't pick up a skill when you expect it, just name it explicitly.

## Skill Catalog by Category

> **Skill Domains** (namespaces for scoped loading): every skill belongs to one domain,
> recorded in `skills-lock.json` and enforced by CI. When building agents that only need
> a subset, load by domain instead of the full catalog.
>
> | Domain | Skills | Purpose |
> |---|---|---|
> | `openspec` | 17 | OpenSpec spec-driven workflow family |
> | `superpowers` | 16 | obra/superpowers methodology family |
> | `local` | 5 | In-repo authored (engineering-docs, living-documentation, open-code-review, option-review, cross-tool-memory) |
> | `document` | 2 | Document processing (docx, pdf) |
> | `integration` | 2 | External tool integrations (comet, codegraph) |
> | `utility` | 3 | Single-purpose utilities (caveman, ponytail, rtk) |
>
> **Note on counts**: `skills-lock.json` has 45 entries but this catalog lists 43 skills.
> The 2 extra entries (`openspec`, `superpowers`) are source-repo meta entries —
> provenance placeholders for the upstream families, not installable skills.

### 1. Workflow & Process Control

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `comet` | Explicit | `/comet` | Versioned workflow state machine (phases, guards, archives). Requires Comet CLI installed + `.comet/config.yaml` in project. | When the project uses Comet for phased task execution. Run `/comet init` once per project to set up, then `/comet` to enter workflow mode. Without the CLI, the skill explains the limitation and falls back to normal flow. |
| `openspec-new-change` | Auto | — | Starts a new OpenSpec change (spec-driven development). | When starting a feature/fix that needs spec artifacts first. Say "use openspec" or just describe the feature. |
| `openspec-propose` | Auto | — | Generates all OpenSpec artifacts in one step. | When you want a quick spec draft without the full explore cycle. |
| `openspec-explore` | Hybrid | — | Thinking-partner mode for exploring ideas before speccing. | When requirements are fuzzy. Say "let's explore this with openspec". |
| `openspec-apply-change` | Auto | — | Implements tasks from an existing OpenSpec change. | After spec is approved: "implement the openspec change". |
| `openspec-continue-change` | Auto | — | Creates the next artifact in an in-progress change. | When resuming OpenSpec work: "continue the openspec change". |
| `openspec-update-change` | Hybrid | — | Revises existing OpenSpec artifacts. | When spec needs revision mid-implementation. |
| `openspec-verify-change` | Auto | — | Validates implementation matches spec artifacts. | Before closing out: "verify against the openspec". |
| `openspec-sync-specs` | Auto | — | Syncs delta specs back to main specs. | After change is complete and merged. |
| `openspec-archive-change` | Auto | — | Archives a completed change. | Final cleanup after merge. |
| `openspec-bulk-archive-change` | Auto | — | Archives multiple completed changes. | Batch cleanup. |
| `openspec-ff-change` | Auto | — | Fast-forwards through artifact creation. | When you want to skip ceremony and get to implementation. |
| `openspec-onboard` | Hybrid | — | Guided walkthrough of the OpenSpec workflow. | First time using OpenSpec: "onboard me to openspec". |
| `draft-openspec-docs` | Hybrid | — | Collaborative page-drafting for OpenSpec docs. | When drafting OpenSpec documentation pages. |
| `write-openspec-docs` | Hybrid | — | OpenSpec docs-writing mode with house style. | When writing OpenSpec user docs. |
| `verify-openspec-docs` | Hybrid | — | Fact-checks OpenSpec docs with fresh-context subagent. | When validating OpenSpec documentation claims. |
| `release-openspec` | Hybrid | — | Audits merged work for OpenSpec releases. | When cutting an OpenSpec release. |
| `living-documentation` | Hybrid | — | Maintains specs/architecture/reference/guides with traceability. | Ongoing. Auto-activates for doc tasks; say "update living docs" to force. |

### 2. Code Quality & Review

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `requesting-code-review` | Auto | — | Decides WHEN a review is needed (timing gate). | Auto-triggers when you complete significant work. |
| `open-code-review` | Auto | — | Deterministic review HOW-TO (file selection, rule matching, line-anchored findings). | Auto-triggers on diffs/PRs. Explicit: "review this diff with open-code-review". |
| `receiving-code-review` | Auto | — | Processes incoming review feedback before implementing. | When you paste review comments: auto-activates to triage. |
| `systematic-debugging` | Auto | — | Structured debugging: reproduce → isolate → hypothesize → fix → verify. | Any bug, test failure, or unexpected behavior. Fires before you propose a fix. |
| `test-driven-development` | Auto | — | Enforces red-green-refactor cycle. | When implementing features/bugfixes. Write tests first. |
| `verification-before-completion` | Auto | — | Pre-completion checklist: run tests, verify claims. | Before you say "done" — forces evidence over assertion. |

### 3. Planning & Design

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `brainstorming` | Auto | — | Explores intent, requirements, and design before implementation. **MUST use before creative work.** | Any new feature, component, or behavior change. If Claude jumps to code, say "brainstorm first". |
| `writing-plans` | Auto | — | Creates structured implementation plans from specs. | Multi-step tasks. Triggers when you have requirements but no plan yet. |
| `executing-plans` | Auto | — | Executes a plan as the implementer. | After plan approval: "execute the plan". |
| `option-review` | Auto | — | Compares 2+ viable approaches with decision matrix. | When you're torn: "should I do A or B?" |
| `dispatching-parallel-agents` | Auto | — | Splits independent tasks across parallel subagents. | 2+ independent tasks. Say "do these in parallel". |
| `subagent-driven-development` | Auto | — | Orchestrates implementation via subagents. | Large plans with independent components. |
| `using-git-worktrees` | Auto | — | Isolates feature work in git worktrees. | Before starting work that needs isolation from current branch. |
| `finishing-a-development-branch` | Auto | — | Decides integration strategy (merge/rebase/squash). | When implementation is complete and tests pass. |

### 4. Memory & Context

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `cross-tool-memory` | Auto | — | Loads/saves durable project memory across tools. Falls back to `PROJECT_CONTEXT.md` / `SESSION_STATE.md` when ai-memory MCP is unavailable. | When continuing prior work. Auto-loads relevant context; explicitly say "remember this" to save. See [Project Memory Setup](#project-memory-setup) below. |
| `using-superpowers` | Auto | — | Establishes skill-discovery protocol at conversation start. | Auto-fires at session start. Ensures Claude checks available skills before responding. |

### 5. Developer Tools

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `codegraph` | Auto | — | Semantic code exploration via CodeGraph MCP. Requires CodeGraph CLI installed. | "Find where X is used" / "show callers of Y". Falls back to grep if CLI missing. |
| `rtk` | Auto | — | Rust Token Killer: rewrites verbose CLI output to concise form. Requires RTK CLI. | Automatically compresses noisy command output. Say "disable rtk" to see raw output. |
| `docx` | Hybrid | — | Creates, reads, edits Word documents. | "Create a .docx report" or "read this Word file". |
| `pdf` | Hybrid | — | Reads/extracts text/tables from PDFs. | "Summarize this PDF" or "extract tables from...". |
| `caveman` | Hybrid | — | Ultra-compressed output mode (saves tokens). | "Be concise" / "caveman mode". Levels: lite, full, ultra. |
| `ponytail` | Hybrid | — | Forces the simplest working solution (anti-overengineering). | "Keep it simple" / when Claude over-engineers. |

### 6. Meta

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `writing-skills` | Auto | — | Guides skill creation/editing/verification. | When creating or modifying skills in `.agents/skills/`. |
| `diagnosing-superpowers` | Auto | — | Diagnoses when a superpowers workflow went wrong. | When Claude ignored plans, repeated work, or seemed "off". Say "diagnose what went wrong". |

### 7. Engineering Documentation

| Skill | Trigger | Slash | What It Does | When to Use |
|---|---|---|---|---|
| `engineering-docs` | Hybrid | — | 15 bilingual templates covering 31 R&D document types (proposal → requirements → design → test → delivery). Includes rendering spec (heading sizes, fonts, paragraph styles) for consistent output. | When writing any formal R&D document. Say "write a PRD" / "write an HLD" and it picks the right template. |

## Project Memory Setup

### `PROJECT_CONTEXT.md` and `SESSION_STATE.md`

These are the file-based fallback when the ai-memory MCP service is unavailable.
The `cross-tool-memory` skill reads them automatically. When running `deploy-agents.sh / .ps1` or `run-pipeline.sh / .ps1` (and `pipeline.sh / .ps1`), if either file is missing in the target project, the scripts **automatically initialize them from templates**. You can also create or customize them manually using the templates below.

**When to create:**
- `PROJECT_CONTEXT.md`: Once per project, when the architecture is stable. Update only when durable facts change (stack, constraints, key decisions).
- `SESSION_STATE.md`: At the end of each significant work session, or when handing off. Update with completed work, verification evidence, and next steps.

**How to create initial versions:**

Ask Claude directly:
```text
Create PROJECT_CONTEXT.md for this project following the cross-tool-memory skill format.
```

Or copy these templates:

#### `PROJECT_CONTEXT.md` template

```markdown
# PROJECT_CONTEXT.md

> Durable project facts. Update only when architecture, constraints, or confirmed decisions change.
> Do not put session-specific status here — that goes in SESSION_STATE.md.

## Stack
- Language/framework:
- Build:
- Test:

## Architecture
- (Key components and their responsibilities)

## Constraints
- (Non-negotiable technical or policy constraints)

## Key Decisions
- YYYY-MM-DD: (Decision and rationale)
```

#### `SESSION_STATE.md` template

```markdown
# SESSION_STATE.md

> Current checkpoint. Update at meaningful task boundaries.
> Remove stale items; keep it scannable.

## Last Updated
- YYYY-MM-DD: (brief session summary)

## Completed
- (What was done, with verification evidence)

## In Progress
- (What's currently being worked on)

## Next Steps
- (What remains, in priority order)

## Open Risks / Questions
- (Unresolved issues or decisions needed)
```

**Where to put them:** Project root. The `cross-tool-memory` skill looks for them there.

**Directory scope:** Do not create per-directory memory files. Keep project facts in the root files;
directory `AGENTS.md` files contain only local boundaries and constraints.
