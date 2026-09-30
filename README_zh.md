# Agents Living

> **Language / 语言**: [English](README.md) | **中文**

> **跨工具（Claude Code / Antigravity IDE / Codex / Zed IDE）AI 研发工程规范、物理安全防火墙与原生技能套件**

本项目为多平台 AI 辅助研发提供统一的**分层规范架构（三级 AGENTS.md）**、**操作系统级硬件安全拦截（PreToolUse Hooks）**、**40+ 原生工程技能（Skills）**以及**跨平台一键自动化部署与差量在线更新脚本**。

---

## 核心特性

1. **三级 AGENTS.md 渐进式披露架构**：
   - **全局级（[`Global AGENTS.md`](Global%20AGENTS.md)）**：跨项目通用工程宪法，涵盖去废话输出闸门、Ponytail 懒人阶梯、Git 保护分支铁律与会话三步仪式。
   - **项目级（[`Project AGENTS.md`](Project%20AGENTS.md)）**：确定性工程中枢，规范项目 CLI 命令槽位、技术栈矩阵、架构核心红线与技能调度矩阵（<1000 Token）。
   - **目录级（[`Directory AGENTS.md`](Directory%20AGENTS.md)）**：Monorepo / 独立子模块的微型边界补丁（In/Out Scope、依赖隔离与极速测试）。
   - **细粒度子规则库（[`.agents/rules/`](.agents/rules/)）**：按需动态查阅，涵盖 `token-discipline.md`、`engineering-spec.md`、`security-boundary.md` 与 `git-workflow.md`。

2. **PreToolUse 安全防火墙（[`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/)）**：
   - 在客户端发起 Bash 命令或写文件前由操作系统底层进行强拦截；
   - 使用 Node.js 守卫脚本通过 stdin JSON 读取工具输入（Claude Code 官方协议），以 `exit 2` / `permissionDecision: deny` 实现可靠阻断；
   - 永久硬拦截（`exit 2`）：受保护分支（`develop`/`master`/`main`/`release*`）直改提交、`git push --force`、删除受保护远端分支、受保护分支 rebase；
   - 高危预警防呆：`rm -rf`、`git reset --hard`、`git add .`、触碰核心构建配置与敏感凭证。

3. **40+ 官方 GitHub 原生技能全量集成（[`.agents/skills/`](.agents/skills/)）**：
   - **流程状态机**：`comet`（八阶段流程守卫，防目标漂移）。
   - **规范驱动开发（SDD）**：`openspec` 全套 16 个技能（提案、变更应用、验证、主文档同步、归档）。
   - **测试驱动开发（TDD）**：`superpowers` 全套 15 个技能（TDD 红绿循环、系统性排障、完工验证证据门、工作区隔离）。
   - **代码极简与图谱**：`ponytail`（7 步极简阶梯）、`codegraph`（AST 语法树调用链检索）。
   - **终端截断与电报沟通**：`rtk`（输出过滤与日志本地留底）、`caveman`（电报体去废话）。
   - **专业文档处理**：`docx`（Word 专业排版）、`pdf`（结构化抽取与分析）。

4. **一键自动化部署与差量在线更新（`deploy-agents`）**：
   - Windows PowerShell（[`deploy-agents.ps1`](deploy-agents.ps1)，内置 UTF-8 兼容与 Junction 权限免提权穿透）与 Linux/macOS Bash（[`deploy-agents.sh`](deploy-agents.sh)）；
   - 一键桥接 Claude Code（`CLAUDE.md`）、Antigravity IDE（`AGENTS.md`）与 GitHub Copilot（`.github/copilot-instructions.md`）。Zed IDE 原生读取 `AGENTS.md`，无需额外桥接；
   - 全局配置覆盖前自动备份既有文件；
   - 支持 `-Update` 在线模式：基于 [`skills-lock.json`](skills-lock.json) 版本锁，通过 `npx -y skills@latest update -y` 从官方 GitHub 差量更新，保护用户已有 `AGENTS.md` 不被覆盖。

---

## 目录结构

```
agents-living/
├── .agents/
│   ├── rules/                       # 细粒度工程子规则库（按需渐进式加载）
│   │   ├── engineering-spec.md      # SDD 规范先行、TDD 验证证据门
│   │   ├── git-workflow.md          # Git 授权模型、受保护分支强隔离、提交规范
│   │   ├── security-boundary.md     # 八大高风险操作防呆矩阵、凭证零泄露
│   │   └── token-discipline.md      # 读拿说三道闸门、上下文防漏与日志截断
│   └── skills/                      # 40+ 原生工程技能库（Comet, OpenSpec, Superpowers...）
├── .claude/
│   ├── settings.json                # Claude Code PreToolUse 安全拦截配置
│   └── hooks/                       # 安全钩子脚本（Node.js，读取 stdin JSON）
│       ├── guard.mjs                # Bash 工具守卫（exit 2 硬阻断）
│       └── guard-write.mjs          # Write/Edit 工具守卫（高危预警）
├── Global AGENTS.md                 # 全局通用底线与安全宪法（常驻系统级）
├── Project AGENTS.md                # 项目根目录标准模板与中枢路由器
├── Directory AGENTS.md              # Monorepo / 子模块边界隔离微型补丁
├── 多工具部署配置指南.md              # 跨工具适配原理、安全钩子与部署更新专著（中文）
├── Multi-Tool Deployment and Configuration Guide.md # 英文版部署配置指南
├── 各工具实战使用与技能全景指南.md     # 40+ 技能详解、Token 经济学与实战流转（中文）
├── Tools Practical Usage and Skills Panorama Guide.md # 英文版技能实战指南
├── deploy-agents.ps1                # Windows 一键部署与在线更新自动化脚本
├── deploy-agents.sh                 # Linux / macOS 一键部署与在线更新自动化脚本
├── skills-lock.json                 # 全套技能上游 Git 版本锁定清单
├── README.md                        # 项目总览（English）
└── README_zh.md                     # 项目总览（中文）
```

---

## 快速开始

### 1. 为新项目部署完整规范与技能库

- **Windows 环境 (PowerShell)**:
  ```powershell
  # 部署到指定项目，并同时配置当前用户全局规则
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Global
  ```

- **Linux / macOS 环境 (Bash)**:
  ```bash
  chmod +x ./deploy-agents.sh
  ./deploy-agents.sh /path/to/my-project --global
  ```

### 2. 在线更新规范与技能库

当上游规则或 GitHub Skills 发生更新时，直接在项目根目录运行：
```powershell
# Windows
.\deploy-agents.ps1 -ProjectPath "." -Update

# Linux / macOS
./deploy-agents.sh . --update
```

---

## 文档索引

* 📖 **部署与配置指南**：[`多工具部署配置指南.md`](多工具部署配置指南.md) | [English Version](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
* 📖 **实战与技能全景**：[`各工具实战使用与技能全景指南.md`](各工具实战使用与技能全景指南.md) | [English Version](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md)
* 📜 **规则宪法**：[`Global AGENTS.md`](Global%20AGENTS.md) | [`Project AGENTS.md`](Project%20AGENTS.md) | [`Directory AGENTS.md`](Directory%20AGENTS.md)

---

## 许可证

本项目遵循 MIT 开源许可协议。各内置第三方技能遵循其各自的原生开源协议。
