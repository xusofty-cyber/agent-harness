# Agents Living

> **Language / 语言**: **English** | [中文](README_zh.md)

> **Reusable AI coding-rule templates, Claude Code hooks, and multi-tool deployment scripts**

This repository provides global, project, and directory rule templates, Claude Code PreToolUse hooks, skill files, and Windows/Linux/macOS deployment scripts. Rule loading and hook behavior vary by tool. Hooks are client-side mechanisms, not operating-system or server-side security boundaries.

The goal is to package mature, reusable engineering practices as a baseline for new projects, then let maintainers add the project's stack, commands, and module boundaries. The three rule levels are adaptable templates, not a requirement that every project use the same workflow. The original project was inspired by these articles: [article 1](https://mp.weixin.qq.com/s/ECw5lXpCw54iPdtn9PYaMw), [article 2](https://mp.weixin.qq.com/s/OfGmlh8R6PHdvyjoz34Gsg), [article 3](https://mp.weixin.qq.com/s/zpLbzq2VQuhfOlVWg6QBxg), and [article 4](https://mp.weixin.qq.com/s/IXWMmzH5llxFPlcr0FbqaQ).

---

## Key Features

1. **Three-Tier AGENTS.md Progressive Disclosure Architecture**:
   - **Global Level ([`Global AGENTS.md`](Global%20AGENTS.md))**: Cross-project engineering constitution covering the no-nonsense communication gate, minimal-implementation guidance, Git authorization rules, and contextual workflow guidance.
   - **Project Level ([`Project AGENTS.md`](Project%20AGENTS.md))**: Adaptable project template for CLI commands, tech stack, architecture boundaries, and on-demand rule references.
   - **Directory Level ([`Directory AGENTS.md`](Directory%20AGENTS.md))**: Micro-boundary patch for Monorepo packages or isolated submodules (In/Out Scope, dependency boundaries, targeted fast tests, and large-file safety).
   - **Modular Sub-Rules ([`.agents/rules/`](.agents/rules/))**: On-demand progressive rules including `token-discipline.md`, `engineering-spec.md`, `security-boundary.md`, and `git-workflow.md`.

2. **Claude Code client hooks ([`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/))**:
   - Run only for matching tool calls in Claude Code; they are not OS-level protections;
   - Some command patterns are hard-blocked while other cases emit non-blocking warnings;
   - Regex inspection cannot cover every command form and does not replace server-side branch protection.

3. **40+ Reusable Skill Directories ([`.agents/skills/`](.agents/skills/))**:
   - **Comet integration guide**: checks the installed version and project configuration; this skill does not implement Comet's state machine or phase guards;
   - **Spec-Driven Development (SDD)**: Full 16-skill `openspec` suite (proposal, apply changes, verify, sync specs, archive, explore);
   - **Test-Driven Development (TDD)**: Full 15-skill `superpowers` suite (red-green cycle, systematic root-cause debugging, physical verification evidence gate, git worktrees);
   - **Implementation and retrieval guidance**: `ponytail` (minimal-solution ladder) and `codegraph` (optional CodeGraph integration guide; CLI/MCP setup is separate);
   - **Output and communication guidance**: `rtk` (optional Rust Token Killer CLI guide; command-rewrite hooks require setup) and `caveman` (concise-response Skill);
   - **Professional Document Processing**: `docx` (Word formatting & manipulation) and `pdf` (structured extraction & analysis).

4. **One-Click Deployment & Template Sync (`deploy-agents`)**:
   - PowerShell automation ([`deploy-agents.ps1`](deploy-agents.ps1)) with automatic Directory Junctions for non-admin permission penetration and Bash automation ([`deploy-agents.sh`](deploy-agents.sh));
   - The project script creates `AGENTS.md` when absent, Claude Code and Copilot bridges, and Claude Code hooks; see the support matrix for the actual scope;
   - `--global` configures Claude Code and Antigravity global rule files and backs up replaced files;
   - `--update` fast-forwards this template repository and syncs files. It backs up managed target rules/skills before replacement. `skills-lock.json` is source/integrity metadata; the script does not download skills by locked hashes. Ponytail and Caveman are copied as Skill files. CodeGraph and RTK setup is optional; the deployment scripts offer interactive prompts for installation, agent wiring, and project initialization.
   - After project deployment, the scripts detect optional CodeGraph/RTK CLIs and ask separately before installation and agent/project configuration. The default is No. Non-interactive runs skip installation and print follow-up commands.

### Support scope

| Tool | Configuration provided here | Status |
|---|---|---|
| Claude Code | `CLAUDE.md` bridge, `.claude/skills/` links, `.claude/settings.json` hooks | Configured by script; hooks run only in the Claude Code client |
| Antigravity | Project rules/skills; `--global` writes `~/.gemini/AGENTS.md` | File deployment; loading depends on version and settings |
| Codex | Project `AGENTS.md` and `.agents/skills/` | Files provided; script does not configure Codex global rules or hooks |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Configured by script; behavior depends on Copilot version/mode |
| Zed | `AGENTS.md` | Reusable files only; no Zed-specific setup by script |
| Pi / OpenCode | No dedicated entry point or script validation | Not adapted; automatic loading is not implied |

`Directory AGENTS.md` is a template and is not copied into an unknown module path by the installer. For a module that needs distinct rules, copy it into that module as `AGENTS.md`, then fill in its ownership, boundaries, and validation commands. Add nested files only where they add constraints beyond the root rules.

---

## Directory Structure

```
agents-living/
├── .agents/
│   ├── rules/                       # Modular sub-rules (loaded on-demand)
│   │   ├── engineering-spec.md      # SDD specification-first, TDD verification gate
│   │   ├── git-workflow.md          # Git authorization model, protected branch isolation
│   │   ├── security-boundary.md     # 8 High-risk operations protection matrix
│   │   └── token-discipline.md      # Read/fetch/speak gates, log truncation
│   └── skills/                      # 40+ Native engineering skills (Comet, OpenSpec, Superpowers...)
├── .claude/
│   ├── settings.json                # Claude Code PreToolUse security interceptor config
│   └── hooks/                       # Security hook scripts (Node.js, reads stdin JSON)
│       ├── guard.mjs                # Bash tool guard (exit 2 for hard blocks)
│       └── guard-write.mjs          # Write/Edit tool guard (warnings)
├── Global AGENTS.md                 # Global rule template (deploy to each tool's global entry point)
├── Project AGENTS.md                # Project root template & central router
├── Directory AGENTS.md              # Monorepo / submodule micro-boundary patch
├── Multi-Tool Deployment and Configuration Guide.md # Comprehensive deployment & configuration guide (English)
├── 多工具部署配置指南.md              # 跨工具部署与配置指南（中文）
├── Tools Practical Usage and Skills Panorama Guide.md # Practical usage, token economics & skills panorama (English)
├── 各工具实战使用与技能全景指南.md     # 各工具实战使用与技能全景指南（中文）
├── deploy-agents.ps1                # Windows PowerShell one-click deploy & update script
├── deploy-agents.sh                 # Linux / macOS Bash one-click deploy & update script
├── skills-lock.json                 # Skill source and partial integrity metadata
├── README.md                        # Repository overview (English default)
└── README_zh.md                     # 项目中文概览
```

---

## Quick Start

### 1. Deploy Harness & Skills to a Project

- **Windows (PowerShell)**:
  ```powershell
  # Deploy to target project and update current user's global rules
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Global
  ```

- **Linux / macOS (Bash)**:
  ```bash
  chmod +x ./deploy-agents.sh
  ./deploy-agents.sh /path/to/my-project --global
  ```

### 2. Perform Online Updates

When upstream rules or skills are updated, run directly in the repository:
```powershell
# Windows
.\deploy-agents.ps1 -ProjectPath "." -Update

# Linux / macOS
./deploy-agents.sh . --update
```

---

## Documentation Index

* 📖 **Deployment & Configuration**:
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](多工具部署配置指南.md)
* 📖 **Practical Usage & Skills Panorama**:
  - [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md)
  - [各工具实战使用与技能全景指南 (中文)](各工具实战使用与技能全景指南.md)
* 📜 **Three-Tier Rules Architecture**:
  - [`Global AGENTS.md`](Global%20AGENTS.md)
  - [`Project AGENTS.md`](Project%20AGENTS.md)
  - [`Directory AGENTS.md`](Directory%20AGENTS.md)

---

## License

This project is licensed under the MIT License. Embedded third-party skills belong to their respective original authors and licenses.
