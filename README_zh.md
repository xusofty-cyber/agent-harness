# Agents Living

> **Language / 语言**: [English](README.md) | **中文**

> **可复用的 AI 编程规范模板、Claude Code 安全钩子与多工具部署脚本**

本项目提供全局、项目和目录级规范模板、Claude Code PreToolUse 钩子、技能文件，以及 Windows/Linux/macOS 部署脚本。各工具的规则加载方式和钩子能力不同；请以支持矩阵和部署脚本实际行为为准。钩子属于客户端机制，不是操作系统或服务端安全边界。

设计目标是把成熟、可复用的工程规则沉淀为新项目的起步基线，再由维护者补充项目技术栈、命令和模块边界。三层文件是可裁剪的模板，不要求每个项目使用相同流程。项目最初受以下文章启发：[文章一](https://mp.weixin.qq.com/s/ECw5lXpCw54iPdtn9PYaMw)、[文章二](https://mp.weixin.qq.com/s/OfGmlh8R6PHdvyjoz34Gsg)、[文章三](https://mp.weixin.qq.com/s/zpLbzq2VQuhfOlVWg6QBxg)、[文章四](https://mp.weixin.qq.com/s/IXWMmzH5llxFPlcr0FbqaQ)。

---

## 核心特性

1. **三级 AGENTS.md 渐进式披露架构**：
   - **全局级（[`Global AGENTS.md`](Global%20AGENTS.md)）**：跨项目通用工程宪法，涵盖沟通、实现、上下文与 Git 授权边界。
   - **项目级（[`Project AGENTS.md`](Project%20AGENTS.md)）**：可裁剪的项目工程模板，提供 CLI 命令、技术栈、架构边界和按需规则索引。
   - **目录级（[`Directory AGENTS.md`](Directory%20AGENTS.md)）**：Monorepo / 独立子模块的微型边界补丁（In/Out Scope、依赖隔离与极速测试）。
   - **细粒度子规则库（[`.agents/rules/`](.agents/rules/)）**：按需动态查阅，涵盖 `token-discipline.md`、`engineering-spec.md`、`security-boundary.md` 与 `git-workflow.md`。

2. **Claude Code 客户端钩子（[`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/)）**：
   - 仅针对 Claude Code 中匹配的工具调用运行，不是操作系统级防护；
   - 使用 Node.js 守卫脚本通过 stdin JSON 读取工具输入（Claude Code 官方协议），以 `exit 2` / `permissionDecision: deny` 实现可靠阻断；
   - 永久硬拦截（`exit 2`）：受保护分支（`develop`/`master`/`main`/`release*`）直改提交、`git push --force`、删除受保护远端分支、受保护分支 rebase；
   - 部分命令会硬拒绝，其他情况只是非阻断警告；正则检查不能覆盖所有命令形式，也不能替代 Git 服务端分支保护。

3. **40+ 可复用技能目录（[`.agents/skills/`](.agents/skills/)）**：
   - **Comet 集成说明**：引导检查已安装版本和项目配置；此技能本身不实现 Comet 状态机或阶段守卫。
   - **规范驱动开发（SDD）**：`openspec` 全套 16 个技能（提案、变更应用、验证、主文档同步、归档）。
   - **测试驱动开发（TDD）**：`superpowers` 全套 15 个技能（TDD 红绿循环、系统性排障、完工验证证据门、工作区隔离）。
   - **实现与检索指导**：`ponytail`（最小实现决策阶梯）与 `codegraph`（CodeGraph 可选集成指引；CLI/MCP 需单独安装配置）。
   - **输出与表达指导**：`rtk`（Rust Token Killer 可选 CLI 指引；需配置命令重写 Hook）与 `caveman`（简明表达 Skill）。
   - **专业文档处理**：`docx`（Word 专业排版）、`pdf`（结构化抽取与分析）。

4. **一键部署与模板同步（`deploy-agents`）**：
   - Windows PowerShell（[`deploy-agents.ps1`](deploy-agents.ps1)，内置 UTF-8 兼容与 Junction 权限免提权穿透）与 Linux/macOS Bash（[`deploy-agents.sh`](deploy-agents.sh)）；
   - 项目脚本创建 `AGENTS.md`（若不存在）、Claude Code 与 Copilot 桥接，并部署 Claude Code Hook；其他工具的具体加载行为以支持矩阵为准；
   - `--global` 配置 Claude Code、Antigravity 与 Codex 全局规则；`--global --update` 覆盖前备份；
   - `--update` 通过 fast-forward 更新本模板仓库并同步文件。覆盖工具管理的目标规则/技能前会创建备份；`skills-lock.json` 是来源/完整性元数据，不代表脚本按锁定哈希下载技能。Ponytail/Caveman 以 Skill 文件随项目复制；CodeGraph/RTK 的 CLI、Agent 接线与项目初始化是可选步骤；部署脚本会在交互模式下征询是否执行。
   - 项目部署后会检测可选的 CodeGraph/RTK CLI，并逐项询问是否安装、是否配置 Agent/项目；默认拒绝。非交互执行会跳过安装并输出后续命令。

5. **可选跨工具项目记忆（`ai-memory`）**：
   - 选择本地优先方案；不配置 LLM、embedding provider 或 API Key 也可使用；普通部署脚本不会安装或启动服务；
   - 自动采集需通过被 Git 忽略的 `.ai-memory.toml` 显式加入项目，并以 allowlist 模式安装上游 hooks；
   - 专用辅助脚本通过上游合并式 CLI 配置 Claude Code、Codex 和 Antigravity CLI；Antigravity 2.0 与 IDE 通过共用全局配置接入 MCP。免费本地方案下 ChatGPT 网页版采用人工 Markdown 交接。

### 支持范围

| 工具 | 本仓库提供的配置/接线 | 状态 |
|---|---|---|
| Claude Code | `CLAUDE.md` 桥接、`.claude/skills/` 链接、`.claude/settings.json` Hook | 脚本配置；Hook 仅在 Claude Code 客户端运行 |
| Antigravity 2.0 / CLI / IDE 与扩展 | 项目规则/技能目录；`--global` 写入 `~/.gemini/AGENTS.md` 和 `GEMINI.md` 兼容指针 | 当前表面支持两个全局文件名；较早 IDE 可跟随指针读取规范文件；CLI 专属规则另行配置 |
| Codex | 全局 `$CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`）、项目 `AGENTS.md` 与 `.agents/skills/` | `-Global` 初始化 Codex 全局文件；`-Global -Update` 备份后覆盖当前生效的全局规则 |
| ai-memory | Claude Code、Codex CLI、Antigravity CLI 的可选 MCP/hooks；Antigravity 2.0 与 IDE 提供 MCP-only 设置 | 项目显式选择加入；Codex 桌面版按安装版本核实；ChatGPT 网页版人工交接 |
| GitHub Copilot | `.github/copilot-instructions.md` 桥接 | 脚本配置；具体行为依 Copilot 版本/模式 |
| Zed | `AGENTS.md` 文件 | 提供可复用文件；脚本不创建 Zed 专属配置 |
| Pi / OpenCode | 未提供专用入口或脚本验证 | 未适配；不能据此推断自动加载 |

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
├── Global AGENTS.md                 # 全局规则模板（需部署到各工具的全局入口）
├── Project AGENTS.md                # 项目根目录标准模板与中枢路由器
├── Directory AGENTS.md              # Monorepo / 子模块边界隔离微型补丁
├── 多工具部署配置指南.md              # 跨工具适配原理、安全钩子与部署更新专著（中文）
├── Multi-Tool Deployment and Configuration Guide.md # 英文版部署配置指南
├── 各工具实战使用与技能全景指南.md     # 40+ 技能详解、Token 经济学与实战流转（中文）
├── Tools Practical Usage and Skills Panorama Guide.md # 英文版技能实战指南
├── deploy-agents.ps1                # Windows 一键部署与在线更新自动化脚本
├── deploy-agents.sh                 # Linux / macOS 一键部署与在线更新自动化脚本
├── setup-ai-memory.ps1              # 单项目/单客户端显式安装辅助脚本
├── setup-ai-memory.sh               # Linux / macOS / WSL 显式安装辅助脚本
├── .ai-memory.toml.example          # 本地显式加入标记示例
├── skills-lock.json                 # 技能来源及部分文件完整性元数据
├── README.md                        # 项目总览（English）
└── README_zh.md                     # 项目总览（中文）
```

`Directory AGENTS.md` 是模板，不会由部署脚本自动写入未知的子目录。需要模块规则时，复制该模板到目标模块并命名为 `AGENTS.md`，填写模块职责、边界和验证命令；只在确有边界差异的目录添加，避免重复根规则。

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

### 2. 可选：启用本地跨工具记忆

先按 [ai-memory 上游指南](https://github.com/akitaonrails/ai-memory) 单独安装并启动服务。无 Key 本地模式不要配置 LLM 或 embedding provider。检查 `.ai-memory.toml.example`，复制为 `.ai-memory.toml` 并替换 workspace/project 名称；然后按需为每种客户端运行辅助脚本：

```powershell
.\setup-ai-memory.ps1 -Agent codex
```

```bash
./setup-ai-memory.sh codex
```

脚本要求本机已安装 `ai-memory` 且项目标记存在；不会安装软件或启动服务。确认安装器选用了能执行 allowlist 门控的原生 hook。各工具边界、卸载和数据保留说明见部署指南。

### 3. 在线更新规范与技能库

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
