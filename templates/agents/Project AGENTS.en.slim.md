# Project AGENTS.md

<!-- Slim variant: installed by the minimal/standard deploy tiers (D-009,
     ablation #2). The full template ships with the full tier. -->

- This file is the project's root instruction file. It supplements the
  baseline in Global AGENTS.md with this project's own engineering
  context. Fine-grained rules live in `.agents/rules/`, read on demand.

## Project Overview

- **Project name**: `<PROJECT_NAME>`
- **Purpose**: `<PROJECT_PURPOSE>`
- **Owners**: `<OWNERS>`
- **Repository and default branch**: `<REPOSITORY_URL>`; default branch `<DEFAULT_BRANCH>`

## Common Development Commands (CLI Context)

> Confirm the working directory before running commands. Always use
> filtering flags to prevent log flooding; never dump full logs into
> the context.

```bash
<INSTALL_COMMAND>       # dependency management / build configuration
<DEV_COMMAND>           # local development
<BUILD_COMMAND>         # build
<UNIT_TEST_COMMAND>     # targeted tests and verification (must run after changes, keep output terse)
<LINT_COMMAND>          # code quality / lint
<FORMAT_COMMAND>        # formatting
<TYPE_CHECK_COMMAND>    # type checking
<MIGRATION_COMMAND>     # data migration and release (high risk, requires confirmation)
```

## Technology Stack and Runtime Environment

| Category | Choice and version |
|---|---|
| **Language and runtime** | `<LANGUAGE_AND_VERSION>` |
| **Package manager / build tool** | `<PACKAGE_MANAGER>` |
| **Core frameworks / libraries** | `<FRAMEWORK>` |
| **Persistence and storage** | `<DATABASE_AND_CACHE>` |
| **CI/CD configuration** | `<CI_PATH>` |

## Core Architectural Red Lines

1. **One-way layered dependencies**: upper layers call lower layers;
   lower layers must never reference upper-layer business logic; no
   circular dependencies between modules.
2. **Unified error flow**: business errors must be raised as the
   unified business exception type; never swallow exceptions silently;
   async code must include error handling.
3. **Configuration isolation**: all configuration is read through the
   unified environment/config module; no deep hardcoding.
4. **Log redaction**: sensitive fields (PII, tokens, passwords) must
   be masked in any console or log output.
5. **Git safety**: see Global AGENTS.md; no `git add .`, no force push.

## How We Work

- Understand the existing implementation first, then choose the
  smallest correct approach. For feature work, consult
  `test-driven-development` on demand; for complex bugs use
  `systematic-debugging` (evidence first, hypothesis second, fix
  last — no blind patching).
- Branch flow and high-risk operations follow
  `.agents/rules/git-workflow.md` and
  `.agents/rules/security-boundary.md` respectively.
- Save long outputs to disk and summarize; never pour full logs into
  the context.

## Dynamic Memory and Task Tracking

- **Session start**: when present and relevant, read
  `PROJECT_CONTEXT.md` and `SESSION_STATE.md` and verify they are
  still current.
- **Session breakpoint**: at meaningful task boundaries, update
  `SESSION_STATE.md` (work completed, actual verification evidence,
  remaining steps, still-valid risks). Touch `PROJECT_CONTEXT.md`
  only when long-term facts change.
- **Sources and safety**: mark inferences as inferences; never store
  credentials, private keys, or raw personal data.

## Definition of Done Checklist

When `gate/feature_list.json` is present, drive task state exclusively via `python3 gate/pass-gate.py` (`pass-gate.py status` -> `pass-gate.py start` [WIP=1] -> `pass-gate.py verify` -> `pass-gate.py check-clean`; never hand-edit `gate/feature_list.json`):

1. [ ] **Tests & gate verify**: run relevant tests and `python3 gate/pass-gate.py verify --id <id>`, confirming exit 0 with recorded run evidence
2. [ ] **Update SESSION_STATE.md & check-clean**: record completed work and verification evidence, then run `python3 gate/pass-gate.py check-clean`
3. [ ] **Code review**: perform a code review before merging;
   Critical / High findings must be zero
