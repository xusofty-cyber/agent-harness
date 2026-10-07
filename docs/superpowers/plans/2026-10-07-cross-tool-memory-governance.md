# Cross-Tool Memory Governance Implementation Plan

> **For agentic workers:** Use the approved execution method after the user reviews this plan. Complete each task in order and keep changes reviewable.

**Goal:** Make cross-tool project memory selective, private, source-aware, and consistent while preserving existing user configuration during deployment.

**Architecture:** Keep Markdown files as the default, human-readable memory layer. Clarify global, project, session, and directory responsibilities in the three templates; keep `-Global` non-destructive by default, while making explicit `-Global -Update` back up and replace active global instructions across supported tools; align hooks and bilingual docs with the safety-only, opt-in boundary.

**Tech Stack:** Markdown, PowerShell 5.1+/7+, Bash, Node.js Claude Code hook configuration (JSON/MJS); no new dependency or memory service.

**Spec:** [2026-10-07-cross-tool-memory-governance-design.md](../specs/2026-10-07-cross-tool-memory-governance-design.md)

## Global Constraints

- Keep the baseline file-based; do not install or require Hindsight, Memmy, `ai-memory`, a vector database, or a hosted service.
- Do not automatically capture prompts, tool inputs/outputs, source files, or terminal commands.
- Keep secrets, credentials, private keys, raw user data, full transcripts, and unnecessary personal data out of durable memory.
- The shared `Global AGENTS.md` remains generic and must not contain an individual's private preferences or project-specific facts.
- Memory summaries are subordinate to current user instructions and verified repository evidence.
- Preserve existing project and global instruction files; updates to existing global files produce review templates rather than replacing local content.
- Do not modify pre-existing user changes outside the task scope; inspect overlapping diffs before touching `.claude` files.
- Do not commit on protected `main`; implement on the approved feature branch. Keep the pre-existing dirty worktree intact; a separate worktree is unsuitable because it would omit the user's uncommitted inputs.
- No test files or test runs are in scope; use syntax/static checks and diff review only.
- Treat Claude Code Auto memory as an existing optional Claude-only feature; document its local scope and `/memory` audit controls without enabling, disabling, or synchronizing it.

## Review Focus

1. Existing global Claude and Antigravity instructions may contain private content; deployment must leave their bytes unchanged and write a separate review template.
2. Global template examples may encode facts from an unrelated sample project; remove them and keep the template project-neutral.
3. Memory may conflict with current code or session status; instructions must require verification and correction rather than blindly trusting it.
4. Deploy update behavior must distinguish project rules from explicit global updates: project rules retain their review-template flow, while `-Global -Update` backs up then replaces global instructions on both Windows and Unix.
5. Codex and Antigravity host loading support may vary by product/version; documentation must distinguish files the script writes from behavior that has been verified.

---

### Task 1: Make the Three Rule Templates Define Memory Scope

**Files:**
- Modify: `Global AGENTS.md`
- Modify: `Project AGENTS.md`
- Modify: `Directory AGENTS.md`

**Interfaces:**
- Consumes: the approved memory taxonomy and precedence from the design spec.
- Produces: consistent terms and update rules for global, project, session, directory, and task-lesson memory.

- [x] **Step 1: Replace the global template's project-specific examples**

Remove illustrative OpenClaw, AST obfuscation, Nuitka, USB seal, and branch-matrix facts from the generic global memory description. State that shared global rules contain reusable conventions only and that personal preferences belong only in a user-controlled machine-local location when explicitly requested.

- [x] **Step 2: Make memory capture selective in the project template**

Replace the unconditional “update both files after every session” requirement with these distinct duties: read context at task start when relevant; verify material facts against the repository; update `SESSION_STATE.md` at meaningful task/session boundaries; update `PROJECT_CONTEXT.md` only when durable project knowledge changes; remove stale checkpoint items; record evidence/source where practical; never save secrets, raw transcripts, or unnecessary personal data.

- [x] **Step 3: Keep directory instructions local and non-duplicative**

Specify that nested `AGENTS.md` files contain only local boundaries, commands, and constraints. Do not create a nested memory file by default; place durable repository-wide decisions in `PROJECT_CONTEXT.md` and transient task state in the root `SESSION_STATE.md`.

- [x] **Step 4: Review template alignment**

Compare scope names, precedence, privacy language, and update triggers across all three templates. Correct any contradiction inline; do not copy long global prose into the project or directory templates.

### Task 2: Support Explicit Global Rule Replacement and Codex

**Files:**
- Modify: `deploy-agents.ps1`
- Modify: `deploy-agents.sh`
- Modify: `多工具部署配置指南.md`
- Modify: `Multi-Tool Deployment and Configuration Guide.md`

**Interfaces:**
- Consumes: source global template and current deployment mode (`-Global`/`--global`, optional update flag).
- Produces: `-Global` initializes missing global targets and preserves existing ones; `-Global -Update` makes a timestamped backup and replaces each active global rule with the shared template. Codex uses `$CODEX_HOME` (default `~/.codex`) and its active non-empty `AGENTS.override.md` when present.

- [x] **Step 1: Define shared global targets and Codex override precedence**

Use shared-template destinations: `~/.claude/CLAUDE.md`, `~/.gemini/AGENTS.md` plus a lightweight `~/.gemini/GEMINI.md` compatibility pointer, and Codex `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`). Current Antigravity 2.0, CLI, and IDE/extensions support both global file names; the pointer also covers older IDE releases without loading a second full rule copy. For Codex, update the non-empty `$CODEX_HOME/AGENTS.override.md` instead when it is the active global file.

- [x] **Step 2: Apply identical behavior in PowerShell**

Change the global deployment block so existing targets are preserved without `-Update`; with `-Update`, back them up with a unique timestamp and copy the shared template over the active path. Print the backup path. Preserve UTF-8 BOM in `deploy-agents.ps1` for Windows PowerShell 5.1.

- [x] **Step 3: Apply identical behavior in Bash**

Change the global deployment block with the same initialize/preserve/update behavior. Back up existing files before replacement and account for symlinks. Preserve existing shell quoting and backup conventions.

- [x] **Step 4: Align both deployment guides**

Document the explicit overwrite contract and backup behavior. List Codex's default/CODEX_HOME path and override precedence. State that Antigravity gets a canonical AGENTS.md and legacy GEMINI.md pointer, with CLI-only rules identified separately. Keep host discovery claims separate from script output paths.

- [x] **Step 5: Inspect script syntax and focused diffs**

Run the PowerShell parser without executing the deployer, run `bash -n deploy-agents.sh` when a Bash runtime is available, confirm the PowerShell source still begins with UTF-8 BOM, and inspect the focused diff. Do not run the deployer against the user's live global files during validation.

### Task 3: Align Hooks and Tool Support Documentation

**Files:**
- Inspect: `.claude/settings.json`
- Inspect: `.claude/hooks/guard.mjs`
- Inspect: `.claude/hooks/guard-write.mjs`
- Modify: `各工具实战使用与技能全景指南.md`
- Modify: `Tools Practical Usage and Skills Panorama Guide.md`
- Modify if required by a confirmed inconsistency: `.claude/settings.json`, `.claude/hooks/guard.mjs`, `.claude/hooks/guard-write.mjs`

**Interfaces:**
- Consumes: current Claude security-only hook behavior and the named host support matrix.
- Produces: accurate guidance that memory capture is not performed by `PreToolUse`; host-specific loading claims are labeled by verification status.

- [x] **Step 1: Audit current uncommitted hook/config diffs**

Inspect the existing worktree diff for the three Claude files before editing. Preserve any user changes. Do not edit them unless current behavior conflicts with the approved design.

- [x] **Step 2: Document hook boundaries in the Chinese guide**

State that the hook is Claude Code-specific and safety-focused; it does not collect or transmit memory data. If a future adapter is considered, require a separate opt-in design for consent, data minimization, local storage, failure behavior, and uninstall.

- [x] **Step 3: Mirror the same boundary in the English guide**

Use equivalent wording and avoid claiming that a Claude hook applies to Codex ChatGPT/CLI or Antigravity.

Document Claude Code Auto memory separately as a host-managed, machine-local per-repository feature that can be inspected/edited with `/memory`; it is not shared across tools, and this repository does not configure it.

- [x] **Step 4: Reconcile tool discovery matrix**

For Codex (ChatGPT and CLI), Claude Code, Antigravity CLI, and Antigravity IDE, list the configured path and distinguish confirmed discovery from script deployment. Verify version-sensitive claims against official docs before asserting them; otherwise mark them as unverified/version-dependent.

- [x] **Step 5: Review Claude configuration syntax if changed**

If `.claude/settings.json` changes, parse it as JSON; if hook scripts change, inspect the exact hook path and confirm no code path writes to memory files or sends payloads externally. Do not add automatic capture behavior.

### Task 4: Update This Repository's Memory and Close the Documentation Loop

**Files:**
- Modify: `PROJECT_CONTEXT.md`
- Modify: `SESSION_STATE.md`
- Modify: `README_zh.md` only if it contains conflicting memory or deployment claims.
- Modify: `README.md` only if it contains conflicting memory or deployment claims.
- Review: the four deployment/practical-use guides and three templates.

**Interfaces:**
- Consumes: final delivered policy and current branch/worktree facts.
- Produces: current project context, accurate session checkpoint, and consistent public-facing documentation.

- [x] **Step 1: Update `PROJECT_CONTEXT.md` with the policy decision**

Record the verified policy decision: the project uses selective file-based memory by default, current repository evidence outranks memory summaries, and external memory backends remain optional. Do not invent a version number or release history. Remove or correct template-specific project facts if they are presented as this repository's actual architecture.

- [x] **Step 2: Update `SESSION_STATE.md` from verified repository state**

Record the feature branch/worktree used, design/implementation files changed, static checks actually performed, any remaining limitations, and next steps. Do not copy stale remote-sync claims from the previous checkpoint without checking them.

- [x] **Step 3: Run a scoped documentation consistency review**

Search only the named templates, guides, README files, and state documents for unconditional dual-file updates, global overwrite claims, project-specific facts in global rules, and any implication of automatic memory capture. Fix only statements relevant to this change.

- [x] **Step 4: Final static review**

Review `git diff --check`, inspect the intended file list and full diff, verify the deploy scripts' syntax checks and Claude JSON parse if applicable, and confirm pre-existing untracked/user-modified files remain untouched. Do not run or add tests under this plan.

## Self-Review

- **Spec coverage:** Task 1 covers memory model, precedence, privacy, capture, retrieval, and maintenance. Task 2 covers the global overwrite defect, cross-platform deployment compatibility, and guide updates. Task 3 covers Claude hook boundaries and tool-specific discovery claims. Task 4 covers project state and final consistency review. Optional memory backends remain explicitly out of scope.
- **Placeholder scan:** The tasks name exact files, outputs, behaviors, and checks; no TODO/TBD or unspecified implementation work remains.
- **Type/interface consistency:** The same two global destinations and their `.template.md` sibling names are used in both script tasks and docs.
- **Review focus coverage:** Existing target preservation (Task 2), generic global examples (Task 1), stale memory precedence (Task 1), update-mode symmetry (Task 2), and tool verification labeling (Task 3) each have an owning task and an explicit review step.
- **Protected branch handling:** Implementation is on `long-term-memory-governance`, preserving the existing dirty working tree. No commit is made on `main`.
