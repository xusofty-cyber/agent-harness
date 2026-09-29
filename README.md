# Agents Living

> **Language / 语言**: **English** | [中文](README_zh.md)

> **Cross-Tool (Claude Code / Antigravity IDE / Codex / Zed IDE) AI Engineering Specifications, Hardware Security Firewall & Native Skills Suite**

This repository provides an enterprise-ready engineering harness for multi-platform AI coding assistants. It combines a **Three-Tier AGENTS.md Progressive Disclosure Architecture**, **OS-level Hardware Security Interceptors (PreToolUse Hooks)**, **40+ Native Engineering Skills**, and **Cross-Platform One-Click Deployment & Delta Online Update Scripts**.

---

## Key Features

1. **Three-Tier AGENTS.md Progressive Disclosure Architecture**:
   - **Global Level ([`Global AGENTS.md`](Global%20AGENTS.md))**: Cross-project engineering constitution covering the no-nonsense communication gate, Ponytail minimal code ladder, Git protected branch iron laws, and the 3-step session ceremony.
   - **Project Level ([`Project AGENTS.md`](Project%20AGENTS.md))**: Deterministic engineering hub defining project CLI command slots, tech stack matrix, architecture red lines, and skill dispatching router (<1000 Tokens).
   - **Directory Level ([`Directory AGENTS.md`](Directory%20AGENTS.md))**: Micro-boundary patch for Monorepo packages or isolated submodules (In/Out Scope, dependency boundaries, targeted fast tests, and large-file safety).
   - **Modular Sub-Rules ([`.agents/rules/`](.agents/rules/))**: On-demand progressive rules including `token-discipline.md`, `engineering-spec.md`, `security-boundary.md`, and `git-workflow.md`.

2. **PreToolUse Hardware-Level Security Firewall ([`.claude/settings.json`](.claude/settings.json))**:
   - Intercepts dangerous operations at the OS process level before Bash or Write/Edit tools are executed;
   - Hard blocks (`exit 1`): direct commits on protected branches (`develop`/`master`/`main`/`release*`), `git push --force`, deleting protected remote branches, and rebasing protected branches;
   - High-risk warnings: `rm -rf`, `git reset --hard`, blind `git add .`, touching build configurations, and modifying secret credentials.

3. **40+ Integrated Official GitHub Native Skills ([`.agents/skills/`](.agents/skills/))**:
   - **Process & State Machine**: `comet` (8-phase anti-drift guard enforcing Open $\rightarrow$ Proposal $\rightarrow$ Specs $\rightarrow$ Design $\rightarrow$ Tasks $\rightarrow$ Build $\rightarrow$ Verify $\rightarrow$ Archive);
   - **Spec-Driven Development (SDD)**: Full 16-skill `openspec` suite (proposal, apply changes, verify, sync specs, archive, explore);
   - **Test-Driven Development (TDD)**: Full 15-skill `superpowers` suite (red-green cycle, systematic root-cause debugging, physical verification evidence gate, git worktrees);
   - **Code Entropy Reduction & AST Graph**: `ponytail` (7-step lazy ladder, standard library first) and `codegraph` (Tree-sitter AST syntax symbol discovery replacing blind grep);
   - **Execution Shield & Concise Output**: `rtk` (log truncation & local tee preservation) and `caveman` (ultra-compressed telegraphic output);
   - **Professional Document Processing**: `docx` (Word formatting & manipulation) and `pdf` (structured extraction & analysis).

4. **One-Click Deployment & Delta Online Updates (`deploy-agents`)**:
   - PowerShell automation ([`deploy-agents.ps1`](deploy-agents.ps1)) with automatic Directory Junctions for non-admin permission penetration and Bash automation ([`deploy-agents.sh`](deploy-agents.sh));
   - One-click bridging for Claude Code (`CLAUDE.md`), Antigravity IDE (`AGENTS.md`), GitHub Copilot (`.github/copilot-instructions.md`), and Zed IDE (`ZED.md`);
   - Delta online updates via `-Update`: Pulls upstream git changes, updates Comet CLI, runs `npx -y skills@latest update -y` against [`skills-lock.json`](skills-lock.json), and preserves custom project `AGENTS.md` while providing `AGENTS.template.md` for reference.

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
│   └── settings.json                # Claude Code PreToolUse security interceptor
├── Global AGENTS.md                 # Universal global constitution (system-wide resident)
├── Project AGENTS.md                # Project root template & central router
├── Directory AGENTS.md              # Monorepo / submodule micro-boundary patch
├── Multi-Tool Deployment and Configuration Guide.md # Comprehensive deployment & configuration guide (English)
├── 多工具部署配置指南.md              # 跨工具部署与配置指南（中文）
├── Tools Practical Usage and Skills Panorama Guide.md # Practical usage, token economics & skills panorama (English)
├── 各工具实战使用与技能全景指南.md     # 各工具实战使用与技能全景指南（中文）
├── deploy-agents.ps1                # Windows PowerShell one-click deploy & update script
├── deploy-agents.sh                 # Linux / macOS Bash one-click deploy & update script
├── skills-lock.json                 # Upstream Git version lock for skills
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
