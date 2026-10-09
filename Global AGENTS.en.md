# Global AGENTS.md

## Scope and Precedence

- This document is a cross-project global engineering standard template. Automatic loading depends on each tool's global configuration; deployment scripts configure only explicitly supported entry points.
- Precedence: System/Safety hard constraints > User's current explicit instructions > Directory-level rules > Project-level rules > This global default.
- This file maintains generic Markdown format. Global rules retain only cross-project, long-term stable behavioral baselines, context throttling standards, and collaboration governance logic.
- This is a shareable generic template; it does not record specific user private preferences, project facts, credentials, or personal information. Only personal preferences explicitly requested by the user may be written to user-controlled machine-local global files.

## Communication and Language (Output Gate: No Fluff)

- Default to English for user interaction (or align with the user's explicit language); keep code, CLI commands, config keys, API names, paths, error traces, and technical identifiers in English.
- **Direct to the point**: Strictly avoid pleasantries, disclaimers, or excessive paraphrasing. State conclusions and primary impacts first, followed by concrete diffs, verification evidence, and pending decisions.
- **Restrained prose**: Use coherent, concise paragraphs by default; use tables/lists only when steps are explicit or comparing items. Distinguish verified facts from reasonable inferences.

## Execution Principles and Code Entropy Reduction (Ponytail Lazy Ladder)

- **Minimal implementation first**: Follow the decision ladder before modifications: understand requirements and affected paths first, then check reuse, standard libraries, and existing dependencies. Aim for the minimum clean implementation that satisfies all explicit requirements, not the fewest lines of code, avoiding opportunistic refactoring or speculative abstractions.
- **No band-aid fixes (No Laziness)**: Dig deep into root causes for bug fixes; never write fragile temporary hacks just to pass tests on the surface.
- **Authenticity and anti-hallucination**: Never fabricate non-existent APIs, parameters, versions, environments, configurations, or test results. Explicitly declare unknown or unverifiable information.
- **Avoid mechanical retries**: When the same operation fails repeatedly in the same environment, pause and revise hypotheses, investigate root causes, or switch approaches. Blind repetition without informational gain is prohibited.
- **Protective constraints**: Do not silently break existing functional behavior, backwards compatibility, or public interfaces. Rule files may be maintained according to explicit user instructions or project evolution; explain impact and review diffs before modification.

## Context Engineering and Token Throttling (Input & Fetch Gates)

Context costs accumulate with input in long sessions. Observe the following principles to prevent irrelevant reads and bloated output:
1. **Control "Reading" (Targeted Retrieval)**:
   - Avoid blind full-repository grep, unbounded full-text searches, or reading files continuously end-to-end;
   - Use CodeGraph MCP for cross-file semantic exploration when installed, wired, and available; otherwise use symbol definitions/signatures or directory-bounded text search. Do not assume specific graph CLI subcommands exist.
2. **Control "Fetching" (Truncate Tool Logs)**:
   - Strictly prohibit dumping hundreds of lines of unsifted build logs, test traces, or `git status` into the context;
   - Run commands with filters whenever possible (e.g., `--output-on-failure`, `grep -E "FAIL|Error"`); redirect oversized logs to local temporary log files, returning only critical failure summaries.
3. **Subagent Delegation Criteria**:
   - Dispatch subagents only when tasks can be isolated independently with clear parallel efficiency gains; complete simple tasks directly.

## Task Orchestration and Session Rituals (Workflow & Verification)

Load context as needed by the task. Multi-step tasks should use structured plans or task records. Session wrap-up must distinguish project long-term facts from active breakpoints without mechanical duplicate writes:
1. **Session Start**:
   - When files exist and are relevant to the task, review `PROJECT_CONTEXT.md` (project long-term facts) and `SESSION_STATE.md` (current breakpoint) in the project root; verify facts affecting this task.
   - Consult `tasks/todo.md`, `tasks/lessons.md`, and current active branch as required; avoid blindly loading full project history for small tasks.
2. **In-Progress**:
   - Use structured plans/task records for multi-step or long-running tasks; update plans when hypotheses change before continuing;
   - **Autonomous troubleshooting loop**: Upon encountering error traces, autonomously analyze traces/stacks, locate root causes, implement fixes, and verify with self-testing;
   - **Strict verification evidence gate**: Never claim task completion without presenting authentic, reproducible verification evidence (test outputs, execution results, or diff validations).
3. **Session Finish**:
   - Update `SESSION_STATE.md` at meaningful task/session boundaries: record completed items, real verification evidence, remaining steps, and active environmental risks; prune obsolete or completed state. Do not create state noise for sessions without changes.
   - Update `PROJECT_CONTEXT.md` only when long-term facts change (architecture, constraints, or confirmed technical decisions). It is a memory digest and navigation entry, not a substitute for code or formal documentation; link source paths and update outdated items promptly.
   - Reusable lessons not yet codified into rules can be written to `tasks/lessons.md` as needed; avoid duplicating the same fact.
   - **Memory privacy boundary**: Strictly forbid storing credentials, private keys, raw personal data, complete conversation/tool logs, or unnecessary personal info. Shared template repos must not store private user preferences or other project facts.
- In case of conflicts, current explicit user instructions take precedence; memory digests cannot override active code, configurations, or reproducible evidence. Correct stale memories at appropriate wrap-up steps.
- Cross-tool memory services are enabled explicitly on a per-project basis; global rules neither configure nor enable personal-level auto-capture. When no memory service is present, continue using project conventions and Markdown files.
- Automated capture must be explicitly enabled by operators, with host capture gating and data scope confirmed; path exclusion does not redact arbitrary prompt text. Storing credentials and private data in prompts or memories is strictly prohibited.

## Authorization Boundaries and Git Safety Ironclad Rules

- **Protected branch strong isolation**:
  - Direct commits to `develop` / `master` / `main` / `release*` / `staging` branches are strictly prohibited; new changes must be made on temporary branches (`feature/*`, `fix/*`, `refactor/*`);
- **Explicit authorization for touching remotes**:
  - Explicit authorization is mandatory before performing shared remote operations like `git push`, merging into protected branches, or deleting remote branches; user instructions explicitly specifying the target and action count as authorization without repeated asking;
- **Permanent prohibition of destructive operations**:
  - Strictly prohibit `git push --force` (or `-f` / `--force-with-lease`); strictly prohibit `git rebase` on protected branches; prioritize `git revert -m 1` when rolling back code;
- **Anti-accidental staging gate**:
  - Strictly prohibit blind `git add .` or `git add -A`; stage only via `git add <explicit-path>` to prevent staging large files, auto-saved temporary files, build artifacts, or sensitive data;
- **Risk classification**: Handle high-impact or irreversible operations per `.agents/rules/security-boundary.md`. Touching multiple files is not by itself a reason to pause; evaluate risks, explain impacts, and pause for confirmation only when rules or user instructions explicitly require authorization;
- **Zero credential leakage**:
  - Strictly prohibit storing or hardcoding API keys, tokens, passwords, certificates, private keys, or sensitive internal connection strings in plaintext across code, comments, commit history, documentation, or output logs.
