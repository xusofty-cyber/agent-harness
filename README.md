# Agent Harness

> **Language / 语言**: **English** | [简体中文](README.zh.md) | [繁體中文](README.zh-tw.md)

> **Reusable AI coding-rule templates, a self-owned verification gate, Claude Code hooks, loop/graph orchestration, and multi-tool deployment scripts**

> **⚡ 30-second start**: `git clone https://github.com/xusofty-cyber/agent-harness.git && cd agent-harness && ./run-pipeline.sh --all -y`
> See [Quick Start](#quick-start) for details. New to the jargon? Check [Glossary](docs/glossary.md).

This repository provides global, project, and directory rule templates, Claude Code PreToolUse hooks, skill files, and Windows/Linux/macOS deployment scripts. Rule loading and hook behavior vary by tool. Hooks are client-side mechanisms, not operating-system or server-side security boundaries.

> **Positioning (v0.3.0)**: this repository is a gated harness, not just a config + skill distribution pack. The core is a self-owned, stdlib-only verification gate (`gate/pass-gate.py`): a machine-readable feature list, WIP=1, evidence-required `passing`, a three-layer termination check, and a five-dimension clean-state check. It contains no agent runtime: Comet is an optional adapter, not the harness itself. Loop/graph orchestration ships only on the `standard`/`full` profiles (D58); the `minimal` profile ships the gate itself only.

## Prerequisites

- **Linux/macOS**: `bash`, `git`, `python3` (pre-installed on most systems)
- **Windows**: PowerShell 5.1+, `git`
- **Optional**: `node` (for Claude Code hooks), `cargo` (for ai-memory)

---

## Architecture

```mermaid
graph TD
    G[Global AGENTS.md<br/>cross-project constitution] --> P[Project AGENTS.md<br/>project template]
    P --> D[Directory AGENTS.md<br/>monorepo micro-boundaries]
    P --> R[.agents/rules/<br/>on-demand sub-rules]
    R --> S[.agents/skills/<br/>40 on-demand skills]
    G --> H[.claude/hooks/<br/>PreToolUse guards]
    S --> T[tools/<br/>sync, tui, doc-impact]
```

## Key Features

1. **Three-Tier AGENTS.md Progressive Disclosure Architecture**:
   - **Global Level ([`Global AGENTS.md`](templates/agents/Global%20AGENTS.md))**: Cross-project engineering constitution covering the no-nonsense communication gate, minimal-implementation guidance, Git authorization rules, and contextual workflow guidance.
   - **Project Level ([`Project AGENTS.md`](templates/agents/Project%20AGENTS.md))**: Adaptable project template for CLI commands, tech stack, architecture boundaries, and on-demand rule references.
   - **Directory Level ([`Directory AGENTS.md`](templates/agents/Directory%20AGENTS.md))**: Micro-boundary patch for Monorepo packages or isolated submodules (In/Out Scope, dependency boundaries, targeted fast tests, and large-file safety).
   - **Modular Sub-Rules ([`.agents/rules/`](.agents/rules/))**: On-demand progressive rules including `token-discipline.md`, `engineering-spec.md`, `security-boundary.md`, and `git-workflow.md`.

2. **Claude Code client hooks ([`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/))**:
   - Run only for matching tool calls in Claude Code; they are not OS-level protections;
   - Some command patterns are hard-blocked while other cases emit non-blocking warnings;
   - Regex inspection cannot cover every command form and does not replace server-side branch protection.

3. **40 Reusable Skill Directories ([`.agents/skills/`](.agents/skills/))**:
   - **Comet integration guide**: checks the installed version and project configuration; this skill does not implement Comet's state machine or phase guards;
   - **Living Documentation & Engineering Docs**: `living-documentation` (4-tier doc model: specs/architecture/reference/guides, frontmatter-based code-doc bidirectional traceability, L0/L1/L2 impact maintenance) and `engineering-docs` (15 bilingual phase-gate templates covering 31 R&D document types for cross-agent consistency);
   - **Spec-Driven Development (SDD)**: Full 12-skill `openspec` suite (proposal, apply changes, verify, sync specs, archive, explore);
   - **Test-Driven Development (TDD)**: superpowers-derived workflow skills (red-green cycle, systematic root-cause debugging, physical verification evidence gate, git worktrees);
   - **Implementation and retrieval guidance**: `ponytail` (minimal-solution ladder) and `codegraph` (optional CodeGraph integration guide; CLI/MCP setup is separate);
   - **Output and communication guidance**: `rtk` (optional Rust Token Killer CLI guide; command-rewrite hooks require setup) and `caveman` (concise-response Skill);
   - **Pre-decision review and shared memory**: `option-review` (isolated 5-dimension candidate approach review matrix) and `cross-tool-memory` (project-scoped long-term memory navigation aid);
   - **Professional Document Processing**: `docx` (Word formatting & manipulation) and `pdf` (structured extraction & analysis). Note: `docx` ships its full OOXML validation toolchain (~1.3 MB, mostly XSD schemas), making it the largest skill in the repo — it is no longer deployed by default; pass `--include-heavy-skills` / `-IncludeHeavySkills` to include it (and `brainstorming`, which ships a local companion server `scripts/server.cjs`). Previously deployed copies are left in place; the flag only affects new copies.
   - **Skills Usage & Trigger Guide**: For trigger modes (auto/explicit/hybrid), categorization, and project memory setup of all 40 skills, see [`Skills Usage Guide.md`](docs/guides/Skills%20Usage%20Guide.md) ([简体中文](docs/guides/Skills%20Usage%20Guide.zh.md) | [繁體中文](docs/guides/Skills%20Usage%20Guide.zh-tw.md)). Deploy profiles (Phase 4, D58; membership is the single source of truth in `skills-profiles.json`): by default only the 15 skills are deployed (`--profile minimal`: 10 gate core + 5 openspec core) plus the gate itself (no `gate/graph.py`, no loop layer); `--profile standard` deploys 20 skills plus gate + orchestration (graph + loop); `--profile full` deploys 38 skills by default plus gate + orchestration, or all 40 with `--include-heavy-skills`. Re-deploying an older minimal project with `minimal` removes its graph/loop files (backed up first); use `--profile standard` to keep them.

4. **One-Click Deployment, Interactive Wizard & Unified Pipeline (`deploy-agents` & `run-pipeline`)**:
   - **Interactive Step-by-Step Terminal Wizard**: Running scripts without arguments (or with `--interactive` / `-Interactive`) launches a guided TUI wizard (arrow keys to move, spacebar to toggle, enter to confirm) to select template language (`en`, `zh`, `zh-tw`), deployment scope (`project`, `global`, `both`), target project path, and multi-select agent bridge files (Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy, WorkBuddy) plus optional workflows, preventing CLI mistakes;
   - **Unified OS Pipeline Runner** ([`run-pipeline.sh`](run-pipeline.sh) & [`run-pipeline.ps1`](run-pipeline.ps1)): Orchestrates the entire agent lifecycle in 4 sequential stages (Deploy rules & bridges → Setup AI memory → Sync external skills → Living documentation impact gate) with both interactive wizard and unattended (`--all -y` / `-All -Yes`) modes;
   - PowerShell automation ([`deploy-agents.ps1`](deploy-agents.ps1)) with automatic Directory Junctions for non-admin permission penetration and Bash automation ([`deploy-agents.sh`](deploy-agents.sh));
   - The project script creates `AGENTS.md` when absent, Claude Code and Copilot bridges, and Claude Code hooks; see the support matrix for the actual scope;
   - `--global` configures Claude Code, Antigravity, Codex, and DeepSeek Harness (dsh) global rule files; `--global --update` backs up replaced files;
   - `--update` fast-forwards this template repository and syncs files. It backs up managed target rules/skills before replacement. `skills-lock.json` is source/integrity metadata; the script does not download skills by locked hashes. Ponytail and Caveman are copied as Skill files. CodeGraph and RTK setup is optional; the deployment scripts offer interactive prompts for installation, agent wiring, and project initialization.
   - After project deployment, the scripts detect optional CodeGraph/RTK CLIs and ask separately before installation and agent/project configuration. The default is No. Non-interactive runs skip installation and print follow-up commands.

5. **Optional cross-tool project memory (`ai-memory`)**:
   - The selected backend is local-first and can run with no LLM, embedding provider, or API key; it is not installed or started by the normal deployment scripts;
   - Capture is project opt-in through an ignored local `.ai-memory.toml` and upstream hooks installed in allowlist mode;
   - Dedicated setup helpers configure Claude Code, Codex, and Antigravity CLI through the upstream merge-aware CLI; Antigravity 2.0 and IDE receive MCP-only setup through the same global config. ChatGPT web uses a human-mediated Markdown handoff in the free local setup.

### Support scope

| Tool | Configuration provided here | Enforcement | Status |
|---|---|---|---|
| Claude Code | `CLAUDE.md` bridge, `.claude/skills/` links, `.claude/settings.json` hooks | Enforced (hooks) | Configured by script; hooks run only in the Claude Code client |
| Antigravity 2.0 / CLI / IDE & extensions | Project rules/skills; `--global` writes `~/.gemini/AGENTS.md` plus a `GEMINI.md` compatibility pointer | Enforced (hooks) | Current surfaces load both global names; older IDE releases can follow the pointer. CLI-only rules remain separate. Project deploys an Antigravity rules adapter (`.agents/rules/agent-harness.md`, trigger: always_on) pointing at `AGENTS.md`, and a gate hook set (`.agents/hooks.json`: PreToolUse/Stop/SessionStart/PostToolUse) translating Antigravity payloads to the Claude gate hooks. Live Antigravity CLI/IDE run not verified in the build environment (no `agy` binary); protocol-level tests pass (`tests/antigravity-hooks.test.mjs`) |
| Codex | Global `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`), project `AGENTS.md`, and `.agents/skills/` | Config only | `-Global` initializes the Codex global file; `-Global -Update` backs up and replaces the active global instructions |
| WorkBuddy | `.workbuddy/rules/agent-harness.md` rule bridge | Config only | Bridge file only; no hooks installed for WorkBuddy in this layer; loading is not verified on every WorkBuddy version, confirm on the installed version |
| DeepSeek Harness (dsh) | Global `${DSH_HOME:-~/.dsh}/AGENTS.md` via `--global`; project `AGENTS.md` native; skills via `.agents/skills/` | Gate plugin (manual activation, unverified on live dsh) | No project bridge file (`AGENTS.md` is read natively); the deploy scripts also install a Cordis gate plugin (`.dsh/agent-harness-gate.mjs`, TypeScript source `.dsh/agent-harness-gate.ts`) plus a `.dsh/cordis.patch.yml` mount row — activation is manual and the dsh plugin API has not been verified against official documentation or a live dsh run in this round, so do not treat it as battle-tested enforcement |
| ai-memory | Optional MCP/hooks for Claude Code, Codex CLI, and Antigravity CLI; MCP-only setup for Antigravity 2.0 and IDE | Config only | Explicit per-project opt-in; Codex desktop must be checked against its installed version; ChatGPT web uses manual handoff |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Config only | Configured by script; behavior depends on Copilot version/mode |
| Zed | `AGENTS.md` | Files only | Reusable files only; no Zed-specific setup by script |
| Pi / OpenCode | No dedicated entry point or script validation | Files only | Not adapted; automatic loading is not implied |

Use `-Initialize` / `--initialize` during deployment to create guidance with locally verifiable project facts and a checklist for unknowns. Add `-DirectoryPath` / `--directory` with an existing module path to generate its directory-level guidance too. The scripts only infer facts supported by local Git metadata, manifests, lockfiles, and CI files. For `package.json`, detected scripts and common framework/storage dependencies are marked as suggestions for review, not verified facts. Users or the active coding agent must confirm purpose, ownership, module responsibility, and boundaries. Existing `AGENTS.md` files are preserved; a review copy is written as `AGENTS.generated.md`. Run `-Check` / `--check` to find unresolved items.

### Current status (v0.3.0) — read this before relying on the gate

- **Enforcement is host-dependent.** Claude Code hooks enforce the gate in the client (see the table above). Antigravity hooks and the dsh gate plugin are deployed, but their live-host enforcement is unverified (see the table). On every other host, the gate is a discipline plus a manual command: run `python3 gate/pass-gate.py verify` and `python3 gate/pass-gate.py check-clean` yourself. The host-independent backstop is CI, which re-runs every `passing` item's verification command (`tests/repo_checks.py` §3k). See [`gate/README.md`](gate/README.md) for the known bypasses, including direct edits through Bash and the plain-text cost ledger.
- **Benchmark claim, stated honestly.** The pre-registered B1 round (t1–t8 × bare/pack/gate × 3 rounds = 72 runs) passed 72/72 with 0 false completions on every arm, so per its pre-registered rules the result is NO DISCRIMINATION. This release makes no claim that the gate reduces false completions; the only interception evidence is the Phase 1 dogfood (a planted fake pass caught by the hook and by CI).
- **B2 harder bench, pre-registered but not yet run.** `eval/results/b2-preregistration-2026-10-29.md` registers t9–t12 (multi-file + docs sync, hidden boundary case, breakpoint resume, ambiguous requirement with a decision record first) × bare/pack/gate × 3 rounds = 36 runs, reusing B1's decision rules: DISCRIMINATION only if gate beats bare by at least 2 false completions pooled, and all-zero arms again mean NO DISCRIMINATION, not a success. No B2 runs exist yet; the tasks and their reference solutions are verified (setup + solution + acceptance) but no arm has been measured.
- **Host-independent second gate (pre-push + CI template).** `templates/pre-push-gate/` (hook template, checker, opt-in installer) and `templates/ci-gate-check.yml` give projects without runtime hooks a gate that depends on no host: the checker re-runs every `passing` item's verification and rejects stale evidence, mirroring §3k. Installation: either run the installer (explicit opt-in), or use the deploy scripts, which now install the three files by default (disable with `--no-prepush-gate` / `-NoPrepushGate`; `--prepush-gate` / `-PrepushGate` is retained for compatibility) with the usual skip-if-exists / backup-on-update rules. Limits, stated in the guides: the pre-push hook checks the working tree, not the pushed commits, and `git push --no-verify` bypasses it — pair it with the CI template and server-side branch protection.
- **Evaluator is advisory-only (D28).** `eval/rubric.md` scores six dimensions, but `evaluate.py --gate` always refuses and a human always decides. The rubric's five calibration rounds used recorded phase outcomes, not a live second judge.
- **Translations.** EN and ZH are the sources of truth. ZH-TW rows are stale/frozen per `docs/internal/i18n-status.md`; regenerate them from EN before the next release, do not hand-sync sentence by sentence.
- **Windows.** CI runs PSScriptAnalyzer on the PowerShell scripts; the deploy smoke test in CI runs the Bash script. PowerShell deployment paths are review-verified, not execution-verified on Windows in CI.

---

## Directory Structure

```text
agent-harness/
├── .agents/
│   ├── rules/                       # Modular sub-rules (loaded on-demand)
│   │   ├── engineering-spec.md      # SDD specification-first, TDD verification gate
│   │   ├── git-workflow.md          # Git authorization model, protected branch isolation
│   │   ├── security-boundary.md     # 8 High-risk operations protection matrix
│   │   └── token-discipline.md      # Read/fetch/speak gates, log truncation
│   └── skills/                      # 40 Native engineering skills (Comet, OpenSpec, Superpowers...)
├── .claude/
│   ├── settings.json                # Claude Code hook config (all five hook events)
│   └── hooks/                       # Hook scripts (Node.js, reads stdin JSON)
│       ├── guard.mjs                # Bash tool guard (exit 2 for hard blocks)
│       ├── guard-write.mjs          # Write/Edit tool guard (warnings)
│       ├── guard-feature-list.mjs   # Denies direct Write/Edit to feature_list.json
│       ├── stop-gate.mjs            # Blocks stopping with an in_progress item
│       ├── session-start.mjs        # Prints a session resume from gate state
│       └── post-tool-use.mjs        # Appends cost-ledger telemetry
├── gate/                            # Self-owned verification gate
│   ├── pass-gate.py                 # Feature-list state machine + verify + check-clean
│   ├── graph.py                     # Graph executor (standard/full only)
│   ├── feature_list.schema.json     # Statuses, transitions, WIP=1, evidence rules
│   └── init.template.sh             # Scaffold a project for the gate + one smoke run
├── tools/
│   ├── loop.py                      # Goal Loop / Maker-Checker runner (standard/full only)
│   ├── sync-skills.py               # External skill synchronization & upstream update checker
│   └── doc-impact.py                # Living documentation impact analysis & quality gate
├── eval/                            # Self-built benchmark (t1–t8) + rubric (advisory-only)
├── templates/
│   └── agents/                      # Canonical rule templates (Global/Project/Directory x en/zh/zh-tw)
├── run-pipeline.ps1                 # Windows PowerShell unified pipeline runner
├── run-pipeline.sh                  # Linux / macOS Bash unified pipeline runner
├── deploy-agents.ps1                # Windows PowerShell one-click deploy & update script
├── deploy-agents.sh                 # Linux / macOS Bash one-click deploy & update script
├── setup-ai-memory.ps1              # Explicit ai-memory setup for one opted-in project/client
├── setup-ai-memory.sh               # Linux / macOS / WSL setup helper
├── tools/tui.py                     # Terminal UI single/multi select library
├── .ai-memory.toml.example          # Safe-to-copy local opt-in marker example
├── skills-lock.json                 # Skill source and partial integrity metadata
├── README.md                        # Repository overview (English default)
└── README.zh.md                     # 项目中文概览
```

---

## Quick Start

### 1. Unified Pipeline One-Click Execution (Recommended)

Run all lifecycle stages in sequence via the unified OS pipeline runner (Deploy rules & bridges → Setup AI memory → Sync external skills → Living documentation impact check):

- **Linux / macOS (Bash)**:
  ```bash
  # Interactive wizard (step-by-step TUI selection):
  ./run-pipeline.sh
  # Unattended full pipeline:
  ./run-pipeline.sh --all -y
  ```

- **Windows (PowerShell)**:
  ```powershell
  # Interactive wizard (step-by-step TUI selection):
  .\run-pipeline.ps1
  # Unattended full pipeline:
  .\run-pipeline.ps1 -All -Yes
  ```

### 2. Standalone Deployment & Interactive Wizard

- **Interactive Wizard (Zero-argument execution)**:
  ```bash
  # Linux / macOS:
  ./deploy-agents.sh
  # Windows:
  .\deploy-agents.ps1
  ```
  *Launches the step-by-step TUI wizard: single-select language, single-select scope, enter path, multi-select agent bridges and optional workflows.*

- **Windows CLI (PowerShell)**:
  ```powershell
  # Deploy to target project (English default, or choose -Language zh / zh-tw)
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Global -Language en -Initialize -DirectoryPath "packages/core"
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Check -DirectoryPath "packages/core"
  ```

- **Linux / macOS CLI (Bash)**:
  ```bash
  chmod +x ./deploy-agents.sh
  # Deploy with language selection (English default, or --lang zh / zh-tw)
  ./deploy-agents.sh /path/to/my-project --global --lang en --initialize --directory packages/core
  ./deploy-agents.sh /path/to/my-project --check --directory packages/core
  ```

### 3. Optional: Enable Local Cross-Tool Memory (ai-memory)

This repository supports seamless sharing of architectural decisions and session context across multiple agents using [ai-memory](https://github.com/akitaonrails/ai-memory) (local-first, zero API keys, zero embedding cost). Detailed deployment workflow:

#### Step 1: Install prerequisite CLI and prepare environment
- **Via Rust Cargo**:
  ```bash
  cargo install ai-memory
  ```
- **Or via GitHub Releases (pre-built binary)**:
  - **Linux / macOS**:
    ```bash
    mkdir -p ~/.local/bin
    curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin/
    chmod +x ~/.local/bin/ai-memory
    export PATH="$HOME/.local/bin:$PATH"
    ```
  - **Windows**:
    Download the release archive from [Releases](https://github.com/akitaonrails/ai-memory/releases) (`ai-memory-windows-x86_64.zip`), extract it, and add its directory to your system `PATH`.
- 💡 **Troubleshooting: Windows Terminal PATH Refresh**
  If you modified `PATH` while Antigravity IDE / VS Code was running, active terminal sessions will not inherit the change. In PowerShell, refresh PATH directly from the registry without restarting the IDE:
  ```powershell
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  ```

#### Step 2: Initialize local project opt-in marker (.ai-memory.toml)
ai-memory enforces a safe, fail-closed policy requiring an explicit opt-in marker before capturing any repository (this file is ignored by `.gitignore` so it will never be accidentally committed):
- **Windows PowerShell**:
  ```powershell
  Copy-Item .ai-memory.toml.example .ai-memory.toml
  (Get-Content .ai-memory.toml) `
      -replace 'replace-with-workspace-name', 'default' `
      -replace 'replace-with-project-name', 'agent-harness' |
      Set-Content .ai-memory.toml
  ```
- **Linux / macOS (Bash)**:
  ```bash
  cp .ai-memory.toml.example .ai-memory.toml
  sed -i 's/replace-with-workspace-name/default/g; s/replace-with-project-name/agent-harness/g' .ai-memory.toml
  ```

#### Step 3: Run the client setup helper
Execute the setup script to register the MCP endpoint and managed skill instructions (supports `antigravity-ide`, `antigravity-cli`, `claude-code`, `codex`):
- **Windows**:
  ```powershell
  .\setup-ai-memory.ps1 -Agent antigravity-ide
  ```
- **Linux / macOS**:
  ```bash
  chmod +x ./setup-ai-memory.sh
  ./setup-ai-memory.sh antigravity-ide
  ```
- 🔍 **Output Guide**:
  - `✓ no-op ... (already up to date)`: Indicates **idempotency protection**; existing target files are already up-to-date and require no re-writing.
  - `Configured <agent>. No server, container, API key, or LLM provider was installed or started.`: Declarative confirmation that client configuration is complete, honoring the zero-daemon / zero-billing guarantee.

#### Step 4: Start the local memory engine
- **For Antigravity IDE (via HTTP MCP)**:
  > ⚠️ `ai-memory serve` defaults to `stdio` transport mode, which does not bind a network port. To serve Antigravity IDE, **you must start it with `--transport http`**:
  - **Terminal foreground**:
    ```bash
    ai-memory serve --transport http
    ```
    Once the terminal prints `bind=127.0.0.1:49374`, the server is ready and the IDE can query and store project memory over MCP.
  - **Linux background daemon (nohup / systemd)**:
    Use `nohup ai-memory serve --transport http > ~/.local/share/ai-memory/serve.log 2>&1 &` or create a user-level service with `systemd --user`.
  - **Docker Container**:
    ```bash
    # In-container data path is fixed to /data; binds to 127.0.0.1 for local security
    docker run -d --name ai-memory \
      --restart unless-stopped \
      -p 127.0.0.1:49374:49374 \
      -v "${HOME}/env/ai-memory-data:/data" \
      docker.io/akitaonrails/ai-memory:latest
    ```
- **For Claude Code / Codex CLI**:
  Native lifecycle hooks capture sessions automatically, or use `ai-memory run <harness>` for a managed workstream launch.

### 4. Perform Online Updates

When upstream rules or skills are updated, run directly in the repository:
```powershell
# Windows
.\deploy-agents.ps1 -ProjectPath "." -Update

# Linux / macOS
./deploy-agents.sh . --update
```

---

## Documentation Index

- 📖 **Deployment & Configuration**:
  - [English](docs/guides/Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [简体中文](docs/guides/Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [繁體中文](docs/guides/Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md)
- 📖 **Practical Usage & Skills Panorama**:
  - [English](docs/guides/Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [简体中文](docs/guides/Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | [繁體中文](docs/guides/Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md)
- 📜 **Three-Tier Rules Architecture**:
  - **Global Rules**: [`Global AGENTS.en.md`](templates/agents/Global%20AGENTS.en.md) (EN) | [`简体中文`](templates/agents/Global%20AGENTS.md) | [`繁體中文`](templates/agents/Global%20AGENTS.zh-tw.md)
  - **Project Rules**: [`Project AGENTS.en.md`](templates/agents/Project%20AGENTS.en.md) (EN) | [`简体中文`](templates/agents/Project%20AGENTS.md) | [`繁體中文`](templates/agents/Project%20AGENTS.zh-tw.md)
  - **Directory Rules**: [`Directory AGENTS.en.md`](templates/agents/Directory%20AGENTS.en.md) (EN) | [`简体中文`](templates/agents/Directory%20AGENTS.md) | [`繁體中文`](templates/agents/Directory%20AGENTS.zh-tw.md)

---

## License

This project is licensed under the MIT License. Embedded third-party skills belong to their respective original authors and licenses.
