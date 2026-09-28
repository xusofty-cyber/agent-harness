---
name: comet
description: "Workflow orchestrator and phase-guard harness for AI coding agents. Enforces structured development phases (Open -> Proposal -> Specs -> Design -> Tasks -> Build -> Verify -> Archive) and anti-drift phase guards. Use whenever handling multi-step features, complex bugfixes, architecture refactoring, or when the user invokes /comet or asks for structured change management."
license: Apache-2.0
---

# Comet Workflow & Phase Guard Harness

Comet manages the software development lifecycle state machine for AI agents, preventing process entropy, scope creep, and goal drift in long-context sessions.

## Core Phases & Lifecycle

```
[Open] ──> [Proposal] ──> [Specs & Design] ──> [Tasks & Build] ──> [Verify & Archive]
             │ (User Checkpoint)                    │ (TDD Loop)        │ (Evidence Gate)
```

1. **Phase 1: Open (`/comet <task>`)**
   - Initializes change directory: `docs/openspec/changes/<change-id>/`.
   - Records change state to `.comet/current-change.json`.
2. **Phase 2: Proposal**
   - Synthesizes background, problem statement, impacted modules, and estimated scope.
   - **Mandatory User Decision Gate**: Stops and waits for user confirmation before writing design or code.
3. **Phase 3: Specs & Design**
   - Defines Delta Specifications (`## ADDED Requirements` -> `#### Scenario:`).
   - Generates architectural design notes and interface contracts.
4. **Phase 4: Tasks & Build**
   - Generates task checklist in `tasks/todo.md`.
   - Enforces TDD (Red -> Green -> Refactor) and Ponytail minimalism.
   - **Anti-Drift Guard**: Blocks direct edits to source files unless the change is in Build phase.
5. **Phase 5: Verify & Archive**
   - Validates that all test criteria and scenarios pass with verifiable evidence.
   - Merges delta specs back into main documentation and archives to `docs/openspec/changes/archive/`.

## CLI Usage

```bash
comet status       # Read-only inspection of active change and phase
comet doctor       # Health check: agent wiring, hooks, CodeGraph index
comet update       # Self-update Comet CLI and templates
```
