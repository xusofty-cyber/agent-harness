# PROJECT_CONTEXT.md —— 项目全景与演进编年史

> **项目定位**：AI Agents 通用工程规约体系、多工具适配中枢与官方 GitHub 原生技能套件（单一真理源 / Single Source of Truth）。

---

## 一、 系统架构与拓扑

本项目为多平台 AI 研发代理（Claude Code、OpenAI Codex、Google Antigravity IDE、Zed IDE）提供统一的工程规范、硬件级安全拦截与按需调度的技能扩展库。

### 1. 三级规则架构（Harness + 渐进式披露）
- **全局宪法（Global AGENTS.md）**：跨项目跨工具统一行为底线、去废话沟通标准、Ponytail 极简阶梯、Git 授权铁律与双轨状态记忆。
- **项目枢纽（Project AGENTS.md）**：代码仓库确定性工程上下文、标准 CLI 脚本槽位、核心红线与技能调度路由器（Router）。
- **目录隔离补丁（Directory AGENTS.md）**：Monorepo 子包与独立隔离模块的边界约束，定义 In/Out Scope 与极速单测命令。
- **细粒度子规则（.agents/rules/）**：`token-discipline.md`、`engineering-spec.md`、`security-boundary.md`、`git-workflow.md`。

### 2. 工具适配与桥接拓扑
- **Claude Code**：通过根目录 `CLAUDE.md`（符号链接或 `@AGENTS.md` 引用）与 `.claude/settings.json`（PreToolUse 客户端安全钩子）接入。
- **Google Antigravity IDE**：原生识别根目录 `AGENTS.md` 与 `.agents/` 目录结构。
- **OpenAI Codex / Copilot**：通过 `.github/copilot-instructions.md` 桥接。
- **Zed IDE**：通过项目根目录 `AGENTS.md` 统一识别。

---

## 二、 核心工程硬性规则

1. **Git 受保护分支强隔离**：`develop` / `master` / `main` / `release*` 分支严禁直接 commit；所有改动必须在临时分支（`feature/*`, `fix/*`）进行。
2. **触碰远端强授权**：执行 `git push`、合入受保护分支前必须获得人类明确授权。
3. **永久禁止破坏性操作**：严禁 `git push --force`；严禁在受保护分支执行 `git rebase`；回滚代码优先使用 `git revert -m 1`。
4. **防误提交闸门**：严禁盲目 `git add .` 或 `git add -A`，必须只 `git add <明确路径>`。
5. **Windows 脚本编码硬性约束**：`deploy-agents.ps1` 必须强制包含 UTF-8 BOM（`\xEF\xBB\xBF`），防止 Windows PowerShell 5.1 在 CP936 默认代码页下产生语法解析与乱码错误。
6. **双轨状态记忆铁律**：每次会话完成、新需求开发或 Bug 修复时，必须在项目根目录同步更新 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md`。

---

## 三、 分支矩阵与分工

- **`main`**：生产就绪发布主干。保持绝对线性安全与端到端验证通过，严禁直接提交。
- **`feature/*`**：新功能开发分支（如 `feature/dual-track-state-memory`）。
- **`fix/*`**：紧急 Bug 修复分支（如修复编码、路径、拦截 Hook 等）。
- **`refactor/*`**：规约重构与架构微调分支。

---

## 四、 版本演进编年史

- **v1.0**：初始化 AI Agents 研发规约底线、PreToolUse 硬件拦截钩子与 40+ 原生技能套件（Comet、OpenSpec、Superpowers、CodeGraph 等）。
- **v1.1**：规范模板统一重命名为标准英文（Global/Project/Directory AGENTS.md），完善跨平台部署流水线（`deploy-agents.ps1` / `deploy-agents.sh`），建立中英双语文档体系。
- **v1.2**：集成 CodeGraph AST 代码图谱 MCP 权限体系；优化 RTK 输出截断与 Ponytail 防过度设计机制。
- **v1.3（当前）**：
  - 确立 `PROJECT_CONTEXT.md`（长期真理源）与 `SESSION_STATE.md`（短期工作台）双轨状态更新铁律；
  - 修复 Windows PowerShell 5.1 UTF-8 BOM 编码解析缺陷；
  - 全量同步更新中英部署指南与实战全景指南。
