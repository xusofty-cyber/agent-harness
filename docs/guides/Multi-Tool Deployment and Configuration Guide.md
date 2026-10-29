# Multi-Tool (Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed) AI Engineering Deployment & Configuration Guide

> **Language / 语言**: **English** | [简体中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [繁體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md)

This guide provides an end-to-end specification on how to deploy, configure, and collaboratively utilize the **Three-Tier AGENTS.md Architecture** (Global, Project, and Directory levels) across **OpenAI Codex / GitHub Copilot**, **Claude Code**, **Google Antigravity IDE**, and **Zed IDE**, tailored for real-world scenarios emphasizing software engineering while supporting professional technical documentation.

---

## Table of Contents

1. [Architecture & Layered Positioning (Harness + Progressive Disclosure)](#1-architecture--layered-positioning-harness--progressive-disclosure)
2. [Configuration Scope by Tool](#2-configuration-scope-by-tool)
3. [Claude Code Client Hooks: PreToolUse (.claude/settings.json)](#3-claude-code-client-hooks-pretooluse-claudesettingsjson)
4. [Cross-Tool Deployment & Template Updates (deploy-agents)](#4-cross-tool-deployment--template-updates-deploy-agents)
   - 4.1 Script Core Architecture & Pipeline
   - 4.2 Windows Deployment (`deploy-agents.ps1`)
   - 4.3 Linux / macOS Deployment (`deploy-agents.sh`)
   - 4.4 Symlink vs. Directory Junction Mechanics
5. Deep Dive into the Four Rule Layers
   - 5.1 Global Constitution: `Global AGENTS.md`
   - 5.2 Project Router: `Project AGENTS.md`
   - 5.3 Modular Sub-Rules: `.agents/rules/`
   - 5.4 Micro-Boundary Patch: `Directory AGENTS.md`
6. Dual-Track Practical Workflow: "Engineering First, Documentation Second"
7. Frequently Asked Questions & Best Practices (FAQ)
8. Practical Usage & Skills Panorama Guide Reference

---

## 1. Architecture & Layered Positioning (Harness + Progressive Disclosure)

This repository organizes reusable rules as a **project entry point plus on-demand sub-rules** so teams can adapt the baseline and avoid loading unrelated guidance. Actual discovery and context cost depend on the host tool:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Global Level (Global AGENTS.md)                                     │
│    - Role: Cross-project engineering constitution & security baseline │
│    - Content: Reusable engineering baseline, Git safety, concise communication │
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
1. **Shared baseline**: Keep reusable rules in Markdown templates and use tool-specific bridges where supported; verify each host's discovery behavior instead of assuming every tool loads the same file.
2. **Progressive Disclosure**:
   - Rules are loaded dynamically when specific scenarios are triggered.
   - Skill discovery, loading, and prompt-cache behavior depend on the host tool and its configuration; deploying files does not guarantee automatic loading.
3. **Client-Side Risk Guardrails**: Claude Code hooks can reject selected matching tool calls or emit warnings. They are client-side checks, not operating-system or server-side security controls.

---

## 2. Configuration Scope by Tool

Rule discovery, inheritance, global settings, and memory mechanisms vary by product and version. This table separates paths written by the scripts from host discovery; file deployment is not a loading verification.

| Tool/surface | Provided or written by this repository | Loading notes |
| :--- | :--- | :--- |
| Codex (local app / IDE / CLI) | Global `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`); project and directory `AGENTS.md` | `-Global` creates the global file; `-Global -Update` backs up and replaces the active global instruction file. Codex uses a non-empty `AGENTS.override.md` in Codex home in preference to `AGENTS.md` |
| Claude Code | `CLAUDE.md` bridge, `~/.claude/CLAUDE.md`, project hooks/skills | `CLAUDE.md` is an instruction entry point; Claude Auto memory is a separate optional machine-local project memory, not shared across tools |
| Antigravity 2.0 | Project `AGENTS.md` / `GEMINI.md` / `.agents/rules/`; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer; deployed `.agents/rules/agent-harness.md` (trigger: always_on); deployed `.agents/hooks.json` gate hooks | Current docs list both global names; older releases can follow the pointer to the canonical file. Antigravity requires YAML frontmatter with a trigger in `.agents/rules/*.md`, so the deployed adapter is a small always_on pointer to `AGENTS.md`, not a duplicate rule set. The gate hooks (PreToolUse/Stop/SessionStart/PostToolUse) translate Antigravity payloads to the Claude gate hooks; live Antigravity CLI/IDE run not verified in the build environment, protocol-level tests pass |
| Antigravity CLI | Project/directory rules; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer; optional `~/.gemini/antigravity-cli/rules/*.md` | Common rules use the canonical entry; configure CLI-only rules separately |
| Antigravity IDE / extensions | Project/directory rules; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer | Current IDE supports both global names; older IDE generations can follow the pointer |
| WorkBuddy | `.workbuddy/rules/agent-harness.md` rule bridge (symlink to `AGENTS.md`, pointer fallback); deployed `.workbuddy/settings.json` gate hooks plus adapters in `.workbuddy/hooks/` and copies of the six Claude gate scripts | Tencent CodeBuddy successor. Bridge-file deployment is not a loading verification; confirm on the installed WorkBuddy version. The gate hooks (PreToolUse/Stop/SessionStart/PostToolUse) forward the Claude-shaped payload to the Claude gate hooks; live WorkBuddy run not verified in the build environment, protocol-level tests pass. Settings-file location caveat: the hook format and the settings-file location are UNVERIFIED against official docs or a live build in this run (see the WorkBuddy paragraph below); this repository deploys to `.workbuddy/settings.json` |
| DeepSeek Harness (dsh) | Global `${DSH_HOME:-~/.dsh}/AGENTS.md` via `-Global`; project `AGENTS.md` native; skills via `.agents/skills/` | dsh reads `AGENTS.md` natively, so no project bridge file is created. MCP via `cordis.patch.yml` and gate enforcement are NOT part of this bridge layer |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Confirm loading in Copilot's current product settings/docs |
| Zed / Pi / OpenCode | Reusable Markdown only; no dedicated setup from this repository | Do not infer automatic discovery or global loading from file presence |

References: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---

## 3. Claude Code Client Hooks: PreToolUse (.claude/settings.json)

### Capability boundaries
The hooks in `.claude/settings.json` are Claude Code-specific and run only before matching tool calls. `guard.mjs` rejects selected command patterns; many other cases only emit a warning. Regex matching cannot identify every shell wrapper, alias, or command form, so this is not a complete security boundary. The hooks do not collect or transmit memory data. Claude Code Auto memory is a separate machine-local project feature that users can inspect/manage with `/memory`; this repository does not configure it. Use server-side branch protection and least-privilege credentials for shared repositories.

### Configuration and implementation

The installer copies [`.claude/settings.json`](../../.claude/settings.json), which wires all five Claude Code hook events, and deploys the full hook set in [`.claude/hooks/`](../../.claude/hooks/): [`guard.mjs`](../../.claude/hooks/guard.mjs) (PreToolUse Bash guard), [`guard-write.mjs`](../../.claude/hooks/guard-write.mjs) (Write/Edit warnings), [`guard-feature-list.mjs`](../../.claude/hooks/guard-feature-list.mjs) (denies direct edits to `feature_list.json`), [`stop-gate.mjs`](../../.claude/hooks/stop-gate.mjs) (Stop gate), [`session-start.mjs`](../../.claude/hooks/session-start.mjs) (SessionStart resume), and [`post-tool-use.mjs`](../../.claude/hooks/post-tool-use.mjs) (cost-ledger telemetry). Inspect those source files directly; do not copy hook examples from older guide versions because the protocol and implementation can change. On hosts other than Claude Code, Antigravity and WorkBuddy none of these hooks run; dsh still has no hooks in this layer, so on it use `gate/pass-gate.py verify` / `check-clean` manually and rely on the CI re-run described in [`gate/README.md`](../../gate/README.md).

Host-independent second gate (pre-push + CI template): for hosts with no runtime hooks, the repository ships a gate that depends on no host at all — only on git, Python 3, and the project's own `gate/` directory. `templates/pre-push-gate/` contains a `pre-push` hook template, its checker `gate-prepush-check.py`, and an installer `install-pre-push-gate.sh`; `templates/ci-gate-check.yml` is a GitHub Actions workflow template to copy into a project's `.github/workflows/gate-check.yml`. The checker re-runs every `passing` item's verification command and rejects stale evidence (evidence.command must equal verification.command), mirroring the repository's own CI re-verification (`tests/repo_checks.py` §3k); human-override evidence is skipped, as in §3k. Installation is explicit opt-in for the standalone installer, and on by default for the deploy scripts, in two forms: run the installer yourself (it refuses to overwrite an existing hook unless you pass `--force`, in which case it backs the old hook up first), or simply run the deploy scripts, which install the three files (`.git/hooks/pre-push`, `scripts/gate-prepush-check.py`, `.github/workflows/gate-check.yml`) with the usual skip-if-exists / backup-on-update rules; pass `--no-prepush-gate` (`-NoPrepushGate` in PowerShell) to skip them (`--prepush-gate` / `-PrepushGate` is retained for compatibility). Two honest limits must stay attached to this gate wherever it is described: it checks the working tree's gate state, not the pushed commits' gate state; and `git push --no-verify` bypasses it entirely, so it is a local tripwire, not a server-side control — pair it with the CI template and with server-side branch protection. The pre-push hook runs `check-clean` as a warning by default (a working tree mid-task is legitimately not handoff-clean) and only blocks on it when `GATE_PREPUSH_STRICT=1` is set; the CI template blocks on both steps, because CI checks committed state.

Antigravity gate hooks (project `.agents/hooks.json`, hook set `agent-harness-gate`, following the official [Antigravity hooks reference](https://antigravity.google/docs/hooks/)): the deploy scripts copy [`.agents/hooks.json`](../../.agents/hooks.json) and the adapters in [`.agents/hooks/`](../../.agents/hooks/) (`antigravity-pre-tool-use.mjs`, `antigravity-stop.mjs`, `antigravity-session-start.mjs`, `antigravity-post-tool-use.mjs`, plus a shared `antigravity-common.mjs`), together with copies of the six Claude gate scripts they delegate to, so Antigravity-only projects gate without `.claude/hooks/`. The mapping is: `run_command` (argument `CommandLine`) → Bash guard; `write_to_file` / `replace_file_content` / `multi_replace_file_content` (argument `TargetFile`) → write warnings plus the feature-list write block; `Stop` → stop gate; `SessionStart` → gate resume injected as a system message; `PostToolUse` → cost-ledger line. The gate rules are not duplicated: each adapter translates the Antigravity payload into the Claude payload, runs the existing Claude hook, and translates its decision back. Two protocol facts shape the implementation and must not be "simplified" away: PreToolUse decisions are required and explicit — an adapter never prints `{}` for PreToolUse (its treatment is disputed across Antigravity versions), it prints `{"decision":"allow"}` or `{"decision":"deny","reason":...}`; and hooks fail open in Antigravity itself (missing binary, timeout, or invalid JSON is logged and the session continues), so every adapter error path also fails open and says so on stderr. The Stop adapter keeps its own second-attempt state in `gate/antigravity-stop-state.json` (Antigravity's Stop payload carries no equivalent of Claude Code's `stop_hook_active` flag), so a session cannot be trapped in a `continue` loop; the human override channel (`GATE_ALLOW_STOP=1` + `GATE_STOP_REASON`) is unchanged. Verification status, stated honestly: protocol-level tests pass ([`tests/antigravity-hooks.test.mjs`](../../tests/antigravity-hooks.test.mjs), 15 tests: deny/allow, stop continue-then-allow, session resume, ledger, fail-open), plus 2 cwd-regression tests added with the 2026-10-29 path fix (17 total), and a deploy smoke test confirms the deployed files gate a temp project — but no live Antigravity CLI/IDE run was possible in the environment where this layer was built (no `agy` binary), so a live run on an installed Antigravity version is still owed before calling this enforcement battle-tested. The official hooks reference lists the workspace `.agents/hooks.json` surface for the App, CLI, and IDE alike; that is the basis for shipping one workspace file, not a live IDE verification. Hook-command cwd fix (2026-10-29, agy CLI 1.4.10 `--print`): agy runs these commands with cwd = `<project>/.agents`, so all four commands are `node hooks/<adapter>.mjs`; the previous `node .agents/hooks/...` form doubled the path to `.agents/.agents/hooks/...`, and agy then rejected the covered tool call with a hook-load error instead of failing open — so this bug blocked tools rather than merely failing to block them. The adapters' project-root fallback was corrected for the same reason (a `.agents` cwd now resolves to its parent when `workspacePaths` is absent). Trade-off, stated plainly: this form is correct for the observed CLI 1.4.10 cwd; Antigravity IDE cwd is still NOT live-verified, and if a future IDE run shows a workspace-root cwd, one shared hooks.json cannot serve both cwds with a single relative path — that case must be revisited (for example a per-host file or a probe wrapper), not fixed by re-prefixing for one host at the other's expense. No hooks.json-relative variable is documented in the local repository files, so no cwd-proof single command is claimed here. Already-deployed projects are NOT fixed by this template change alone: the deploy scripts skip an existing `.agents/hooks.json` unless run in update mode, so existing deployments need an update-mode redeploy (code path: backup then overwrite) or a manual edit of the four commands.

WorkBuddy gate hooks (project `.workbuddy/settings.json`, using an ASSUMED Claude Code-compatible hook protocol — UNVERIFIED in this run: the official WorkBuddy/CodeBuddy hook documentation was NOT fetched here (no external fetches during the night window) and no installed WorkBuddy build was available, so the hook format, the settings-file location, and the output forms below are provisional until a live run on an installed WorkBuddy version confirms them; a prior draft cited the [Hooks Reference](https://staging-codebuddy.tencent.com/docs/cli/hooks) and the [Plugin Reference](https://www.workbuddy.ai/docs/cli/plugins-reference) for this shape, but those links were not re-fetched or verified in this run): when WorkBuddy is selected, the deploy scripts copy [`.workbuddy/settings.json`](../../.workbuddy/settings.json) and the adapters in [`.workbuddy/hooks/`](../../.workbuddy/hooks/) (`workbuddy-pre-tool-use.mjs`, `workbuddy-stop.mjs`, `workbuddy-session-start.mjs`, `workbuddy-post-tool-use.mjs`, plus a shared `workbuddy-common.mjs`), together with copies of the six Claude gate scripts they delegate to, so WorkBuddy-only projects gate without `.claude/hooks/`. Unlike Antigravity, no payload translation is assumed to be needed: WorkBuddy/CodeBuddy hooks are assumed to receive the same Claude-shaped stdin (`tool_name`, `tool_input`, `cwd`, `session_id`), so the mapping is identity — `Bash` → Bash guard, `Write|Edit|NotebookEdit` → write warnings plus the feature-list write block, `Stop` → stop gate, `SessionStart` → gate resume, `PostToolUse` → cost-ledger line. Only the outputs whose assumed form differs from Claude's are translated: SessionStart plain text is wrapped as `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`, and Stop exit 2 becomes `{"continue": false, "reason": "..."}` (the assumed current form; `"decision": "block"` is assumed deprecated). Two protocol facts shape the implementation and must not be "simplified" away: PreToolUse allow is exit 0 with no stdout — the normal permission flow continues, and the adapter never prints an explicit `"allow"`, because an explicit allow would skip the host's permission prompt on the gate's sole authority; and every adapter error path fails open with a stderr note, matching the graded policy in `guard.mjs`. The Stop adapter keeps its own second-attempt state in `gate/workbuddy-stop-state.json` (the assumed Stop payload used here carries no equivalent of Claude Code's `stop_hook_active` flag; if the host does pass it, `stop-gate.mjs` handles the second attempt itself), and the `GATE_ALLOW_STOP` override channel is unchanged. Verification status, stated honestly: protocol-level tests pass ([`tests/workbuddy-hooks.test.mjs`](../../tests/workbuddy-hooks.test.mjs), 16 tests: deny/allow, stop block-then-allow, session resume, ledger, fail-open) and a deploy smoke test confirms the deployed files gate a temp project — but no live WorkBuddy run was possible in the environment where this layer was built (no WorkBuddy binary installed), so a live run on an installed WorkBuddy version is still owed before calling this enforcement battle-tested. Settings-file location caveat, also unresolved until that live run: the legacy CodeBuddy path cited by the prior draft is `.codebuddy/settings.json` (user `~/.codebuddy/settings.json`, likewise unverified here), while this repository deploys the WorkBuddy build's settings to `.workbuddy/settings.json`, matching the `.workbuddy/rules/` bridge this repository already ships. If an installed WorkBuddy build still reads the legacy path, copy the deployed `.workbuddy/settings.json` to `.codebuddy/settings.json` — the hook commands are project-root-relative (`node .workbuddy/hooks/...`) and need no change. WorkBuddy has no global hook file in this layer; its project bridge remains `.workbuddy/rules/agent-harness.md`, and a machine-wide WorkBuddy rules file, if wanted, is created manually under `~/.workbuddy/rules/`.

### Equivalents on other tools (extension point)

PreToolUse-style interception is no longer Claude Code-only: the installer now also deploys the Antigravity and WorkBuddy hooks described above. It still does not install interceptors for dsh. For equivalent protection on dsh, wire up its own hook/approval mechanism: the decision logic in `guard.mjs` (protected branches, dangerous command patterns) is plain Node.js — reuse its regexes and branch table and adapt them to the target tool's hook entry point. Whichever layer you hook, it never replaces server-side branch protection; client-side interception is only one layer of defense in depth.

---

## 4. Cross-Tool Deployment & Template Updates (deploy-agents)

The scripts deploy files to configured paths. Tool-specific loading behavior is not guaranteed by file deployment. `-Global` initializes missing global rule files and preserves existing ones. Combining `-Global -Update` first creates a timestamped backup, then replaces the active global rule with the current template. Antigravity receives the canonical `~/.gemini/AGENTS.md` plus a small `GEMINI.md` compatibility pointer instead of a duplicate full rule set. DeepSeek Harness (dsh) receives a global `AGENTS.md` from `$DSH_HOME` (default `~/.dsh`) under the same preserve/backup rules. WorkBuddy has no global hook file in this layer; its project bridge is `.workbuddy/rules/agent-harness.md` plus the project hooks in `.workbuddy/settings.json` + `.workbuddy/hooks/` when WorkBuddy is selected (see §3), and a machine-wide WorkBuddy rules file, if wanted, is created manually under `~/.workbuddy/rules/`. Codex uses `$CODEX_HOME` when set (otherwise `~/.codex`); if a non-empty `AGENTS.override.md` exists there, that active file is backed up and updated instead of `AGENTS.md`:
- **Windows PowerShell**: [`deploy-agents.ps1`](../../deploy-agents.ps1)
- **Linux / macOS Bash**: [`deploy-agents.sh`](../../deploy-agents.sh)

### 4.1 Script Core Architecture & Pipeline

```text
[ Execute Deployment Script ]
       │
       ├─ [Zero arguments in terminal OR with -Interactive / --interactive]
       │       ▼
       │  Phase 0: Interactive Step-by-Step Terminal Wizard (TUI Arrow-Key & Checkboxes)
       │    ├─ [1/5] Select Template Language (English / 简体中文 / 繁體中文)
       │    ├─ [2/5] Select Deployment Scope (Target Project only / Global Rules only / Both)
       │    ├─ [3/5] Enter Target Project Path (defaults to current directory [.])
       │    │        (Note: Codex, Antigravity, Zed natively read AGENTS.md without bridges)
       │    ├─ [4/5] Multi-Select Agent Bridge Files (Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy)
       │    └─ [5/5] Multi-Select Optional Workflows (Update mode / Project fact scan / ai-memory / Comet)
       │
       ▼
 Phase 1: Template Repository Update (-Update)
   └─ Fast-forward update of this template repository (`git pull --ff-only`); no global CLI upgrade or third-party updater in the caller directory
       │
       ▼
 Phase 2: User Global Rules (-Global)
   ├─ Initialize Claude Code (~/.claude/CLAUDE.md) only if the target is absent
   ├─ Initialize Antigravity (~/.gemini/AGENTS.md) only if the target is absent
   └─ Preserve existing files; with -Update write adjacent *.template.md files for manual merge
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
       │
       ▼
 Phase 9: Optional ai-memory Init (-AiMemoryInit)
   └─ Initializes .ai-memory.toml for cross-tool memory when explicitly requested
       │
       ▼
 Phase 10: Probe Optional CLIs & Interactive Prompts
   ├─ Offer CodeGraph / RTK / Open Code Review (ocr) / Comet install if missing
   ├─ Ask whether to wire CodeGraph agents / index project
   ├─ Ask whether to run rtk init; skipped in non-interactive mode
   ├─ Installing ocr enables Tier A delegation review; Tier B works offline without it
   └─ Installing Comet CLI enables subsequent workflow initialization via --comet-init
```

---

### 4.2 Windows Deployment (`deploy-agents.ps1`)

**Usage**:
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <target-path>] [-Global] [-Update] [-Interactive] [-CometInit] [-AiMemoryInit] [-Pipeline]
```

**Parameters**:
- `-ProjectPath` (Positional 0): Path to target project. If omitted with `-Global`, only updates user global rules.
- `-Global` (`-g`): Initializes missing `~/.claude/CLAUDE.md`, `~/.gemini/AGENTS.md`, and Codex `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`). Existing files are preserved without `-Update`.
- `-Language` (`-l`): Selects template language (`en`, `zh`, `zh-tw`; defaults to `en`).
- `-Interactive` (`-i`): Launches the step-by-step interactive selection wizard (single-select language & scope, multi-select agent bridges and options). Triggered automatically when run with zero arguments in an interactive terminal.
- `-Update` (`-u`): Fast-forwards the template repository, automatically invokes `tools/sync-skills.py --check` to scan external skills for upstream updates with interactive confirmation, and syncs files to the target. Combined with `-Global`, it backs up and replaces existing global rule files. Codex's non-empty `$CODEX_HOME/AGENTS.override.md` takes precedence and is updated as the active file. Existing project-managed rules, hooks, skills, and lock metadata follow their documented backup/update behavior. It does not upgrade global CLIs.
- `-CometInit` (`-c`): Automatically executes `comet init` in the target project if Comet CLI is installed.
- `-AiMemoryInit` (`-m`): Automatically initializes `.ai-memory.toml` in the target project (inferring `workspace` and `project`) for cross-tool ai-memory integration.
- `-Pipeline`: Delegates execution directly to the unified pipeline runner ([`run-pipeline.ps1`](../../run-pipeline.ps1)).

**Unified Pipeline Runner (Windows)**:
```powershell
# Interactive step-by-step wizard (select language, project, stages, detail mode):
.\run-pipeline.ps1

# Unattended full pipeline execution in one shot:
.\run-pipeline.ps1 -All -Yes

# Run specific stages:
.\run-pipeline.ps1 -Stages "deploy,skills,docs"
```

**Examples**:
```powershell
# Scenario 0: Interactive wizard (zero-argument execution)
.\deploy-agents.ps1

# Deploy to a new project
.\deploy-agents.ps1 "D:\Projects\my-project"

# Deploy project and update global rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global

# Online update skills and sub-rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global -Update

# Initialize with Comet terminal hooks
.\deploy-agents.ps1 "D:\Projects\my-project" -CometInit

# Initialize with cross-tool ai-memory configuration
.\deploy-agents.ps1 "D:\Projects\my-project" -AiMemoryInit

# Launch unified pipeline directly
.\deploy-agents.ps1 -Pipeline

# Update global rules only
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Linux / macOS Deployment (`deploy-agents.sh`)

```bash
chmod +x ./deploy-agents.sh ./run-pipeline.sh

# Scenario 0: Interactive wizard (zero-argument execution)
./deploy-agents.sh

# Deploy to project
./deploy-agents.sh /path/to/my-project

# Deploy and update global rules
./deploy-agents.sh /path/to/my-project --global

# Online update
./deploy-agents.sh /path/to/my-project --global --update

# Deploy with Comet CLI init
./deploy-agents.sh /path/to/my-project --comet-init

# Launch unified pipeline directly
./deploy-agents.sh --pipeline
```

**Unified Pipeline Runner (Linux / macOS)**:
```bash
# Interactive step-by-step wizard (language, project, stages, mode):
./run-pipeline.sh

# Unattended full pipeline execution in one shot:
./run-pipeline.sh --all -y

# Run specific stages:
./run-pipeline.sh --stages deploy,skills,docs
```

### Deploy with ai-memory init
```bash
./deploy-agents.sh /path/to/my-project --ai-memory-init
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

### 5.1 Global Rules Template: `Global AGENTS.md`
- **Purpose:** A reusable cross-project engineering baseline. Whether a host loads it, and at what precedence, depends on that host and the user's configuration.
- **Sharing boundary:** Keep the shared template generic; do not put personal preferences, project facts, or sensitive information in it. Save personal preferences only in a user-controlled machine-local location when explicitly requested.
- **Memory layers:**
  1. At task start, read `PROJECT_CONTEXT.md` (verified durable project facts) and `SESSION_STATE.md` (current checkpoint) when relevant, then verify facts that affect the work.
  2. At a meaningful task/session boundary, update `SESSION_STATE.md` and remove stale status. Update `PROJECT_CONTEXT.md` only when durable project knowledge changes; no-op sessions do not need empty updates.
  3. `PROJECT_CONTEXT.md` is a project summary and navigation aid, not a single source of truth over code, configuration, or maintained documentation. Current user instructions and reproducible evidence take precedence over memory.
  4. Label uncertainty and date/source facts likely to change. Never store credentials, private keys, raw personal data, full conversation/tool logs, or unnecessary personal information.

**Selected optional backend: [ai-memory](https://github.com/akitaonrails/ai-memory).** Its local mode provides Markdown-backed project memory, full-text retrieval, and cross-agent handoff without an LLM or API key. It is not required for ordinary use. This repository supplies an explicit setup helper but never installs or starts the backend, creates a local opt-in marker, or changes tool configuration during normal deployment.

> **Supply-chain note**: ai-memory is a third-party native binary with prompt-reading hooks. Download it only from the official Releases page and verify the published SHA256 checksums (for `cargo install`, confirm the crate name is `ai-memory`). `setup-ai-memory.*` deliberately never downloads it for you, verifies it is a native executable (rejecting wrapper scripts) before configuring anything, and pins the validated version (currently **v2.6.0** — a mismatch refuses to configure). Check upstream release notes before upgrading, and re-verify the install flags before bumping the pin.

#### Explicit project opt-in and setup

1. Install and start ai-memory separately by following its [official installation guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md). Leave LLM and embedding providers unconfigured for the free, zero-key path.
2. Review `.ai-memory.toml.example`, copy it to `.ai-memory.toml`, and replace both names. `.ai-memory.toml` is ignored by Git; committing this opt-in is intentionally avoided.
3. Run `./setup-ai-memory.sh <claude-code|codex|antigravity|antigravity-ide|antigravity-cli>` on Linux/macOS/WSL2, or the equivalent `-Agent` value in PowerShell. Use `antigravity` for Antigravity 2.0 and `antigravity-ide` for the IDE; both configure MCP and managed instructions. The CLI target additionally installs allowlist hooks. Native executable and hook-mode preflight applies to hook targets; MCP-only targets do not need it. The helper does not download software or start the server.
4. Keep the server bound to loopback for same-machine use. Default data locations are `~/.local/share/ai-memory` on Linux, `~/Library/Application Support/ai-memory` on macOS, and typically `%LOCALAPPDATA%\ai-memory` on Windows; `AI_MEMORY_DATA_DIR` can override them.
   - **Docker deployment (for Antigravity IDE HTTP MCP)**:
     ```bash
     # In-container storage path must be /data; binds to loopback 127.0.0.1
     mkdir -p "${HOME}/env/ai-memory-data"
     docker run -d --name ai-memory \
       --restart unless-stopped \
       -p 127.0.0.1:49374:49374 \
       -v "${HOME}/env/ai-memory-data:/data" \
       docker.io/akitaonrails/ai-memory:latest
     ```
     *Note: The Docker container does not need to mount repository trees or `.ai-memory.toml`. Antigravity IDE passes project context (`workspace`/`project`) through MCP tool calls.*
   - Back up with `ai-memory --data-dir <data-dir> backup --to <archive-path>` (for Docker deployments, use the upstream container command). `ai-memory uninstall --apply` removes managed client integrations but does not delete the data. To erase memory, stop the service and remove its configured data directory only after confirming the backup and target. See the [official installation/operations guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

#### Host boundaries

- **Claude Code:** upstream MCP/hooks; ai-memory owns only its entries and preserves unrelated hooks. The existing Claude `PreToolUse` security hook remains separate. Claude Code's default auto-memory is also separate and machine-local.
- **Codex CLI:** upstream `--client codex` / `--agent codex` integration. **Codex desktop:** uses the local Codex configuration surface where supported; verify the installed app's hook/MCP availability instead of assuming every CLI version behaves identically.
- **Antigravity CLI:** upstream `antigravity-cli` MCP/hooks. On Windows, run setup in the same environment that launches the agent.
- **Antigravity 2.0 and IDE:** the helper uses the upstream Antigravity MCP installer to write the shared `~/.gemini/config/mcp_config.json` and managed project instructions. The current ai-memory upstream has no dedicated 2.0/IDE lifecycle-hook target, so this is MCP-only and does not automatically capture session events. Manual MCP setup uses `serverUrl=http://127.0.0.1:49374/mcp`; see [Antigravity MCP docs](https://www.antigravity.google/docs/mcp).
- **ChatGPT web:** the no-key, loopback setup has no direct connection to a remote web chat. Use a concise Markdown handoff manually. Remote MCP/write access is outside this free local setup.
- **Windows:** upstream documents both WSL2 and native Windows. Install and configure ai-memory in the same environment that launches each agent; do not mix WSL and Windows hook paths. Review the [Windows guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md) for client-specific support.

ai-memory allowlist mode only guarantees no capture for repositories without a marker when the installed native hook enforces capture policy. Its path exclusions do not redact arbitrary prompt text; never include secrets in prompts. See the [marker-file reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md).

### 5.2 Project Router: `Project AGENTS.md`
- Adaptable repository-level template.
- Add `-Initialize` / `--initialize` to deployment to generate a draft from verifiable local facts and a pending-items checklist. `-DirectoryPath <relative-path>` / `--directory <relative-path>` also initializes an existing module directory. The scripts do not guess project purpose, owners, or module boundaries. Existing `AGENTS.md` files are preserved; generated review copies use `AGENTS.generated.md`.
- Detected `package.json` scripts and common framework/storage dependencies appear as review suggestions, not verified facts; confirm them before relying on those commands or boundaries.
- Run `-Check` / `--check` (optionally with the directory parameter) to scan for unresolved template fields before adopting the generated rules; the command returns a nonzero exit status when it finds any.
- Provides standard CLI command slots (install, dev, build, targeted test, lint, format, migration), architecture red lines, the **Rule & Skill Dispatching Matrix**, selective Markdown memory rules, and optional ai-memory integration guidance.

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
- Generate one with `-Initialize -DirectoryPath <relative-path>` (PowerShell) or `--initialize --directory <relative-path>` (Bash); the target must already exist inside the project root. Module path/name are detected, while responsibility and boundaries remain explicit review items.
- Defines In/Out scope, permitted/forbidden dependencies, and targeted local test commands (e.g., `pytest tests/submodule -q`).

---

## 6. Dual-Track Practical Workflow: "Engineering First, Documentation Second"

### 1. Software Engineering Track (Strict Gate)
- Scope: APIs, features, bug fixes, refactoring.
- Rules:
  - Read `PROJECT_CONTEXT.md` and `SESSION_STATE.md` at task start only when present and relevant, then verify material facts;
  - Always work on temporary branches (`feature/*`, `fix/*`);
  - TDD red-green cycle, verify with actual test runs;
  - Follow Git authorization model;
  - **Selective memory updates**: Update `SESSION_STATE.md` at meaningful closeout; update `PROJECT_CONTEXT.md` only when durable project facts change.

### 2. Technical Documentation Track (Lightweight Bypass)
- Scope: Markdown documentation, READMEs, API specifications, Word/PDF reports.
- Rules: **Exempt from running test suites**; leverage specialized skills (`docx`, `pdf`, `write-openspec-docs`); maintain GitHub Flavored Markdown standards.

---

## 7. Frequently Asked Questions & Best Practices (FAQ)

### Q1: Why not put all project commands into `Global AGENTS.md`?
> **Answer**: Global rules are resident across all sessions on the machine. Adding project-specific commands creates cross-project context pollution and wastes prompt tokens.

### Q2: How does online update (`-Update`) protect custom project configurations?
> **Answer**: Existing project `AGENTS.md` is preserved and an `AGENTS.template.md` is generated for review. `-Global` initializes missing Claude Code, Antigravity, and Codex global instructions while preserving existing files. Combining `-Global -Update` makes timestamped backups and replaces those global files with the current template; Codex's active non-empty `AGENTS.override.md` is updated in place of `AGENTS.md`.

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
> 8. High-impact cross-module changes affecting shared contracts or requiring broad coordination; file count alone is not a risk trigger.

### Q5: When should `PROJECT_CONTEXT.md` and `SESSION_STATE.md` be updated?
> At meaningful task/session boundaries, update `SESSION_STATE.md` with completed work, actual verification evidence, remaining steps, and still-relevant risks. Update `PROJECT_CONTEXT.md` only when durable architecture, constraints, or confirmed decisions change. Do not create no-op updates. Both files summarize project memory; they do not override current user instructions, code, configuration, or reproducible evidence. Never store credentials, raw personal data, or full conversation/tool logs.

---

## 8. Practical Usage & Skills Panorama Guide Reference

For detailed tutorials on Slash Commands (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD, and full end-to-end execution walkthroughs, see:
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
