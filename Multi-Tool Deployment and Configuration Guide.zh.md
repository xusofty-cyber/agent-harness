# 多工具（Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed）AI 研发指令部署与配置指南

> **Language / 语言**: **中文** | [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)

本指南系统阐述如何在 **OpenAI Codex / GitHub Copilot**、**Claude Code**、**Google Antigravity IDE** 以及 **Zed IDE** 中部署并高效协同使用 **三级 AGENTS.md 体系**（全局级、项目级、目录级），并针对“以软件研发为主、兼顾专业文档处理”的实际工程场景提供开箱即用的落地指南与自动化部署方案。

---

## 目录

1. [整体架构与分层定位（Harness + 渐进式披露）](#一-整体架构与分层定位harness--渐进式披露)
2. [工具配置覆盖范围](#二工具配置覆盖范围)
3. [Claude Code 客户端 PreToolUse 钩子（.claude/settings.json）](#三claude-code-客户端-pretooluse-钩子claudesettingsjson)
4. [跨工具一键自动化部署与更新实战（deploy-agents）](#四-跨工具一键自动化部署与更新实战deploy-agents)
   - 4.1 脚本核心架构与更新流水线
   - 4.2 Windows 环境部署 (`deploy-agents.ps1`)
   - 4.3 Linux / macOS 环境部署 (`deploy-agents.sh`)
   - 4.4 符号链接（Symlink）与目录连接点（Junction）底层适配原理
5. [规则模板与项目规范](#五规则模板与项目规范)
   - 5.1 全局宪法：`Global AGENTS.md`
   - 5.2 项目中枢路由器：`Project AGENTS.md`
   - 5.3 细粒度子规则库：`.agents/rules/`
   - 5.4 模块边界隔离补丁：`Directory AGENTS.md`
6. [“研发为主、文档为辅”双轨实战技巧](#六-研发为主文档为辅双轨实战技巧)
7. [常见避坑指南与最佳实践 (FAQ)](#七-常见避坑指南与最佳实践-faq)
8. [实战演练与高级技能指南索引](#八-实战演练与高级技能指南索引)

---

## 一、 整体架构与分层定位（Harness + 渐进式披露）

为了让规则易于跨项目复用、按项目裁剪，并减少与当前任务无关的上下文，本套规范采用**“项目入口 + 按需子规则（Progressive Disclosure）”**的组织方式。实际加载与上下文成本由宿主工具决定：

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. 全局级 (Global AGENTS.md)                                            │
│    - 角色：跨工具跨项目通用工程宪法与安全底线                            │
│    - 内容：可复用工程底线、Git 安全、简洁沟通                              │
│    - 作用域：当前机器/用户的所有项目（用户级模板，实际加载取决于工具）          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 继承（不重复全局准则）
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. 项目根级 (Project AGENTS.md)                                         │
│    - 角色：确定性工程上下文 & 子规则/技能路由器 (Router)                  │
│    - 内容：确切 CLI 槽位、技术栈、架构红线、调度矩阵、全景与断点记忆        │
│    - 作用域：当前代码仓库（实际加载取决于宿主工具）                        │
│    - 桥接：CLAUDE.md / .github/copilot-instructions.md                │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ 渐进式按需读取 (仅在涉及场景时查阅) │ 仅在必要子模块按需建立
┌──────────────────▼───────────────┐ ┌───────────────▼───────────────────┐
│ 3. 子规则库 (.agents/rules/)      │ │ 4. 目录级 (Directory AGENTS.md)    │
│  - token-discipline.md (读拿说)  │ │    - 角色：微型模块边界补丁          │
│  - engineering-spec.md (SDD/TDD) │ │    - 内容：In/Out 范围、禁止依赖项、  │
│  - security-boundary.md (高危阻断)│ │            超大文件维护、极速单测命令│
│  - git-workflow.md (Git 授权模型)│ └───────────────────────────────────┘
└──────────────────────────────────┘
```

### 设计目标与核心分工

本项目的目标是把成熟、可复用的工程规则整理成新项目可部署的基线，再由项目维护者填入技术栈、命令和模块边界。全局、项目、目录文件是模板与规则层，不意味着所有工具都会自动发现它们，也不要求所有项目采用同一工作流。受以下实践文章启发： [文章一](https://mp.weixin.qq.com/s/ECw5lXpCw54iPdtn9PYaMw)、[文章二](https://mp.weixin.qq.com/s/OfGmlh8R6PHdvyjoz34Gsg)、[文章三](https://mp.weixin.qq.com/s/zpLbzq2VQuhfOlVWg6QBxg)、[文章四](https://mp.weixin.qq.com/s/IXWMmzH5llxFPlcr0FbqaQ)。

### 核心分工与优势
1. **共享基线**：将可复用规则维护为 Markdown 模板，并在支持的工具中使用专属桥接；核对各宿主的发现规则，不假设所有工具都会加载同一文件。
2. **渐进式披露（Progressive Disclosure）**：
   - 规则按需动态载入，不把所有大而全的规范一脑子塞进每次对话；
   - Skill 的发现、加载与上下文成本取决于宿主工具和配置；部署 Skill 文件不保证宿主自动加载。
3. **客户端风险提示与拒绝**：Claude Code PreToolUse Hook 对部分命令模式硬拒绝、对其他操作发出非阻断警告；它不是操作系统级防护，也不能替代服务端分支保护。

---

## 二、工具配置覆盖范围

工具的规则发现、继承、全局设置和记忆机制由各自产品及版本决定。下表区分脚本写入的路径与宿主规则发现，不把文件部署误称为加载验证。

| 工具/表面 | 本仓库提供或脚本写入 | 加载说明 |
| :--- | :--- | :--- |
| Codex（本地 App / IDE 扩展 / CLI） | 全局 `$CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`）；项目及目录 `AGENTS.md` | `-g` 初始化，`-g -u` 备份后覆盖当前生效规则；非空 `AGENTS.override.md` 优先生效 |
| Claude Code | `CLAUDE.md` 桥接、`~/.claude/CLAUDE.md`、项目 Hook/Skills | `CLAUDE.md` 是规则入口；Claude Auto memory 是另一个机器本地、项目级可选记忆机制，不跨工具共享 |
| Antigravity 2.0 | 项目 `AGENTS.md` / `GEMINI.md` / `.agents/rules/`；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针 | 当前版本加载两种全局文件名；较早版本可通过指针读取规范文件 |
| Antigravity CLI | 项目/目录规则；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针；另支持 `~/.gemini/antigravity-cli/rules/*.md` | 通用规则使用规范入口；CLI 专用 rules 可按需另行配置 |
| Antigravity IDE / Extensions | 项目/目录规则；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针 | 当前版本支持两种全局文件名；较早 IDE 可跟随指针 |
| GitHub Copilot | `.github/copilot-instructions.md` 桥接 | 按 Copilot 当前产品配置单独确认加载方式 |
| Zed / Pi / OpenCode | 可复用 Markdown；无专属部署接线 | 不据文件存在推断自动发现或全局加载 |

参考：[Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[Claude Code memory](https://code.claude.com/docs/en/memory)、[Antigravity rules](https://www.antigravity.google/docs/rules/)。

---

## 三、Claude Code 客户端 PreToolUse 钩子（.claude/settings.json）

### 能力边界

`.claude/settings.json` 配置了 Claude Code 专属的 **PreToolUse Hook**，仅在匹配工具调用前运行。`guard.mjs` 对若干命令模式拒绝，其他场景可能仅警告；命令文本正则不能识别所有包装、别名或写法，因此 Hook 不是完整安全边界。它不采集或发送记忆数据。Claude Code 的 Auto memory 是独立的机器本地项目记忆，可通过 `/memory` 查看和管理；本仓库不配置它。生产仓库仍应使用 Git 服务端分支保护和最小权限凭证。

### 配置与实现

部署脚本复制 [`.claude/settings.json`](.claude/settings.json) 并部署 [`.claude/hooks/guard.mjs`](.claude/hooks/guard.mjs) 与 [`guard-write.mjs`](.claude/hooks/guard-write.mjs)。请直接检查这些源文件；不要从旧版指南复制示例配置，因为钩子协议和实现会随版本变化。

### 其他工具的等效机制（扩展点）

PreToolUse 钩子是 Claude Code 专属机制，部署脚本不会为其他工具安装拦截器。如需同等保护，请按各工具自身的钩子/审批机制接线：`guard.mjs` 的判定逻辑（受保护分支、危险命令模式）是纯 Node.js，可直接复用其正则与分支表，改写为目标工具的钩子入口即可。无论接在哪一层，都不能替代 Git 服务端的分支保护——客户端拦截永远只是纵深防御的一环。

### 当前检查行为：
1. **命令硬拒绝**：受保护分支直接 commit、force push、部分受保护远端分支删除模式、受保护分支 rebase 会返回拒绝。
2. **非阻断警告**：`rm -rf`、`git reset --hard`、`git add .`、受保护分支上的 merge/push 等匹配项只发出提醒。
3. **文件编辑提醒**：`guard-write.mjs` 对若干构建、协议和凭证路径发出警告后放行。

正则检查不覆盖所有命令形式；在共享仓库仍应启用服务端分支保护。

---

## 四、 跨工具一键自动化部署与更新实战（deploy-agents）

代码库提供 Windows 与 Linux/macOS 部署脚本。目标文件的加载行为由各工具决定；`--update` 会覆盖工具管理的同名规则和技能，并先创建备份，不承诺零影响：
- **Windows PowerShell 自动化脚本**：[`deploy-agents.ps1`](deploy-agents.ps1)
- **Linux / macOS Bash 自动化脚本**：[`deploy-agents.sh`](deploy-agents.sh)

### 4.1 脚本核心架构与更新流水线

部署脚本包含以下主要步骤（具体行为以脚本为准）：

```text
[ 用户执行部署脚本 ]
       │
       ▼
 阶段 1：更新模板仓库并同步文件 (-Update)
   └─ 使用 `git pull --ff-only` 更新模板仓库；不升级全局 CLI，也不在调用者当前目录运行第三方技能更新器
       │
       ▼
 阶段 2：部署/更新用户全局规则 (-Global)
   ├─ 目标文件不存在时初始化 Claude Code (~/.claude/CLAUDE.md)
   ├─ 初始化 Antigravity ~/.gemini/AGENTS.md 与兼容入口 GEMINI.md
   └─ 已有全局文件保持原样；-Global -Update 会备份并覆盖规范文件与兼容入口
       │
       ▼
 阶段 3：部署项目级规则与跨工具桥接
   ├─ 生成根目录 AGENTS.md (若已存在则保护用户已有配置，更新时生成 AGENTS.template.md)
   ├─ 建立 Claude Code 桥接 (CLAUDE.md -> AGENTS.md)
   ├─ 建立 GitHub Copilot 桥接 (.github/copilot-instructions.md -> AGENTS.md)
   ├─ Zed 使用项目提供的 AGENTS.md；脚本不创建 Zed 专属配置
   └─ 部署 Claude Code PreToolUse 客户端钩子 (.claude/settings.json)
       │
       ▼
 阶段 4：同步细粒度子规则库
   └─ 将 .agents/rules/*.md 同步到目标项目的 .agents/rules/
       │
       ▼
 阶段 5：部署技能库与双平台接线
   ├─ 复制 .agents/skills/ 到目标项目
   ├─ 建立 Claude Code 技能接线 (Windows 创建 Junction；Linux/macOS 创建 Symlink)
   └─ 复制 skills-lock.json 来源/完整性元数据
       │
       ▼
 阶段 6：初始化动态任务追踪骨架
   ├─ 初始化项目错题本：tasks/lessons.md
   └─ 初始化任务打勾清单：tasks/todo.md
       │
       ▼
 阶段 7：初始化 OpenSpec 架构脚手架
   └─ 自动创建 docs/openspec/changes/ 变更目录
       │
       ▼
 阶段 8：可选的 Comet CLI 初始化 (-CometInit)
   └─ 仅在用户指定该参数时，在目标项目运行 comet init
       │
       ▼
 阶段 9：可选的 ai-memory 初始化 (-AiMemoryInit)
   └─ 仅在用户指定该参数时，生成 .ai-memory.toml 接入跨工具记忆
       │
       ▼
 阶段 10：检测可选 CLI 并逐项征询
   ├─ 缺少 CodeGraph / RTK / Open Code Review (ocr) / Comet 时询问是否安装
   ├─ 单独询问是否运行 CodeGraph Agent 接线 / 项目索引初始化
   ├─ 单独询问是否在项目运行 rtk init；默认跳过，非交互时仅显示命令
   ├─ 检测/安装 ocr 可启用 open-code-review 的 Tier A 委托评审；不安装仍支持 Tier B
   └─ 检测/安装 comet CLI；支持后续通过 --comet-init 初始化工作流
```

---

### 4.2 Windows 环境部署 (`deploy-agents.ps1`)

> **运行环境**：支持 Windows PowerShell 5.1（系统自带）与 PowerShell 7+。脚本内置 UTF-8 编码兼容保护。

#### 语法格式（Windows）：
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <目标项目路径>] [-Global] [-Update] [-CometInit] [-AiMemoryInit] [-UpdateSource <URL>]
```

#### 参数说明：
| 参数名 | 简写别名 | 是否必填 | 说明 |
|---|---|---|---|
| `-ProjectPath` | (位置参数 0) | 选填 | 目标项目的相对路径或绝对路径。如果不传且指定了 `-Global`，则只执行全局配置更新。 |
| `-Global` | `-g` | 选填 | 初始化不存在的全局规则文件；已有文件保持不变。与 `-Update` 同用时，在原文件旁生成 `CLAUDE.template.md` / `AGENTS.template.md` 供人工审阅合并。 |
| `-Update` | `-u` | 选填 | 使用 `git pull --ff-only` 更新模板仓库，自动调用 `tools/sync-skills.py --check` 扫描外部技能上游变动并提供交互式同步选项，将文件同步到目标项目；更新受管理的项目规则、Hook、技能和元数据前按脚本策略备份。已有全局指令文件不覆盖，而是在显式 `-Global -Update` 时生成旁置审阅模板；不会升级全局 CLI。 |
| `-CometInit` | `-c` | 选填 | 若系统中已安装 `comet` CLI，自动在目标项目根目录下执行 `comet init` 注册客户端生命周期 Hooks。 |
| `-AiMemoryInit` | `-m` | 选填 | 自动为目标项目生成 `.ai-memory.toml` 配置文件（智能推导 `workspace` 与 `project`），接入跨工具项目记忆 (ai-memory)。 |
| `-UpdateSource` | 无 | 选填 | 指定自定义的技能或规则更新上游源。 |

#### 实战命令示例（Windows）：
```powershell
# 场景 1：为新项目初始化完整的 Harness 规范、子规则与全套技能库
.\deploy-agents.ps1 "D:\Projects\my-order-service"

# 场景 2：部署新项目，同时更新当前用户的全局规则
.\deploy-agents.ps1 "D:\Projects\my-order-service" -Global

# 场景 3：在线升级并同步（拉取官方最新规则与 Skills，并安全应用到项目）
.\deploy-agents.ps1 "D:\Projects\my-order-service" -Global -Update

# 场景 4：部署项目并一并触发 Comet CLI 的终端 Hooks 初始化向导
.\deploy-agents.ps1 "D:\Projects\my-order-service" -CometInit

# 场景 5：部署项目并初始化 .ai-memory.toml 接入跨工具记忆
.\deploy-agents.ps1 "D:\Projects\my-order-service" -AiMemoryInit

# 场景 6：仅更新当前用户的全局规则（不影响任何特定项目）
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Linux / macOS 环境部署 (`deploy-agents.sh`)

> **运行环境**：原生 Bash 环境（Linux / macOS / WSL）。脚本默认开启 `set -euo pipefail` 严格容错。

#### 首次赋予执行权限：
```bash
chmod +x ./deploy-agents.sh
```

#### 语法格式（Linux/macOS）：
```bash
./deploy-agents.sh [<目标项目路径>] [--global|-g] [--update|-u] [--comet-init] [--ai-memory-init|-m]
```

#### 实战命令示例（Linux/macOS）：
```bash
# 场景 1：一键部署指定项目
./deploy-agents.sh /path/to/my-web-app

# 场景 2：部署项目并同时更新用户全局规则 (~/.claude/ 与 ~/.gemini/)
./deploy-agents.sh /path/to/my-web-app --global

# 场景 3：更新模板并同步规则与技能
./deploy-agents.sh /path/to/my-web-app --global --update

# 场景 4：部署项目并自动执行 Comet CLI 初始化
./deploy-agents.sh /path/to/my-web-app --comet-init

# 场景 5：部署项目并自动初始化 .ai-memory.toml 接入跨工具记忆
./deploy-agents.sh /path/to/my-web-app --ai-memory-init

# 场景 6：仅更新当前用户的所有全局规则
./deploy-agents.sh --global --update
```

---

### 4.4 符号链接（Symlink）与目录连接点（Junction）底层适配原理

在跨工具适配中，如何让 Claude Code 读取存放在 `.agents/skills/` 中的 30 多个技能目录？
- **在 Linux / macOS 下**：脚本使用标准相对路径软链接：
  ```bash
  ln -sf "../../.agents/skills/${skill_name}" ".claude/skills/${skill_name}"
  ```
- **在 Windows 下**：普通用户权限默认禁止创建文件夹符号链接（SymbolicLink）。为了解决此权限痛点，`deploy-agents.ps1` 采用 Windows NTFS 原生支持的 **目录连接点（Directory Junction）**：
  ```powershell
  New-Item -ItemType Junction -Path ".claude\skills\$skillName" -Target ".agents\skills\$skillName"
  ```
  - **优势 1**：普通非管理员权限即可成功创建，无需开启 Windows 开发者模式；
  - **优势 2**：在文件系统底层无损映射，Claude Code 可通过本地文件系统路径访问技能文件，修改单边两端同步。
  - **优雅降级**：若运行环境不支持 Junction，脚本会自动优雅降级为深拷贝模式（Copy-Item），保证 100% 部署成功率。

---

## 五、规则模板与项目规范

### 5.1 全局规则模板：`Global AGENTS.md`
- **定位**：跨项目通用工程约定模板；工具是否加载、采用何种优先级，取决于工具自身及用户配置。
- **共享边界**：模板只放可复用规范，不包含个人偏好、项目事实或敏感信息。个人偏好仅在用户明确要求时保存到用户控制的机器本地配置。
- **记忆分层**：
  1. 任务开始时，按需读取项目 `PROJECT_CONTEXT.md`（已验证的长期事实）与 `SESSION_STATE.md`（当前断点），并核实影响当前任务的信息。
  2. 有意义的任务/会话收尾时更新 `SESSION_STATE.md`，清理过期状态；仅当项目长期事实变化时更新 `PROJECT_CONTEXT.md`。无实质变化不要求空更新。
  3. `PROJECT_CONTEXT.md` 是项目摘要和导航入口，不是代码、配置或正式文档的单一真理源；记忆与当前用户指令或可复现证据冲突时，以当前指令和证据为准。
  4. 标注不确定性，易变信息尽量附日期或来源；不保存凭证、私钥、原始个人数据、完整对话/工具日志或不必要的个人信息。

**本仓库选择的可选后端：[ai-memory](https://github.com/akitaonrails/ai-memory)。** 本地模式以 Markdown 保存项目记忆，支持全文检索和跨 Agent 交接；不需要 LLM 或 API Key，也不影响未启用时的常规使用。本仓库只提供显式安装辅助脚本，不安装/启动后端、不创建本地加入标记，也不在普通部署时改写工具配置。

> **供应链信任说明**：ai-memory 是读取 prompt 的第三方原生二进制，务必从官方 Releases 页面下载并核对发布的 SHA256 校验和；`cargo install` 时确认 crate 名为 `ai-memory`。`setup-ai-memory.*` 出于安全考虑**永远不会**替你下载它，配置前还会校验它是原生可执行文件（拒绝包装脚本），并 pin 定验证过的版本（当前为 **v2.6.0**，版本不符会拒绝配置）。升级前先看 upstream 的 release notes，重新验证安装参数后再 bump pin。

#### 显式启用项目记忆（详细端到端实战流程）

##### 步骤 1：安装前置 CLI 与环境变量就绪
1. **安装二进制**：
   - **通过 Rust Cargo 安装（跨平台）**：`cargo install ai-memory`
   - **Linux / macOS（快速下载原生二进制）**：
     ```bash
     mkdir -p ~/.local/bin
     curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin/
     chmod +x ~/.local/bin/ai-memory
     # 确保 ~/.local/bin 在 PATH 中（写入 ~/.bashrc 或 ~/.zshrc）
     export PATH="$HOME/.local/bin:$PATH"
     ```
   - **Windows（下载 Release 解压）**：
     访问 [Releases](https://github.com/akitaonrails/ai-memory/releases) 下载 `ai-memory-windows-x86_64.zip`，解压后将其所在目录加入系统环境变量 `PATH`。
2. 💡 **Windows 环境变量避坑（IDE 终端继承机制）**：
   若在已启动的 Antigravity IDE / VS Code 中修改了系统 PATH，IDE 派生的内置终端仍保持启动时的旧环境快照，会报错 `ai-memory is not installed`。此时无需重启 IDE，在当前 PowerShell 窗口执行以下命令即可从注册表强制刷新 PATH：
   ```powershell
   $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   ```

##### 步骤 2：初始化项目本地声明标记（`.ai-memory.toml`）
ai-memory 采用安全优先的 Fail-closed 门禁，必须显式声明才激活项目采集（该文件已被 `.gitignore` 忽略，安全不会被误提交）：
- **Windows PowerShell**:
  ```powershell
  Copy-Item .ai-memory.toml.example .ai-memory.toml
  (Get-Content .ai-memory.toml) `
      -replace 'replace-with-workspace-name', 'default' `
      -replace 'replace-with-project-name', 'agents-living' |
      Set-Content .ai-memory.toml
  ```
- **Linux / macOS (Bash)**:
  ```bash
  cp .ai-memory.toml.example .ai-memory.toml
  sed -i 's/replace-with-workspace-name/default/g; s/replace-with-project-name/agents-living/g' .ai-memory.toml
  ```

##### 步骤 3：运行客户端配置脚本
运行辅助脚本自动向客户端挂载 MCP 节点与专属技能指令（支持 `antigravity-ide`, `antigravity-cli`, `claude-code`, `codex`）：
- **Windows**:
  ```powershell
  .\setup-ai-memory.ps1 -Agent antigravity-ide
  ```
- **Linux / macOS**:
  ```bash
  chmod +x ./setup-ai-memory.sh
  ./setup-ai-memory.sh antigravity-ide
  ```
- 🔍 **控制台输出解读**：
  - `✓ no-op ... (already up to date)`：代表**幂等性保护**生效，目标配置已经是最新版本，自动跳过重复写入；
  - `Configured <agent>. No server, container, API key, or LLM provider was installed or started.`：声明性成功结语，表明配置已完成，且坚守零常驻、零容器、零 API 扣费的安全底线。
  - Antigravity 2.0 用 `antigravity`，IDE 用 `antigravity-ide`，两者配置 MCP 与托管指令；CLI 另外配置 allowlist hooks。安装脚本对会安装 hooks 的目标先校验原生可执行文件和 hook 模式，MCP-only 目标无需此项校验。

##### 步骤 4：启动本地记忆引擎服务
- **面向 Antigravity IDE（通过 HTTP MCP 接入）**：
  > ⚠️ `ai-memory serve` 默认采用 `stdio` 管道模式，不会开启网络端口。要为 IDE 提供服务，**必须使用 `--transport http` 启动**：
  - **终端直接运行**：
    ```bash
    ai-memory serve --transport http
    ```
    终端输出 `bind=127.0.0.1:49374` 即代表服务就绪，IDE 的 MCP 即可正常检索与存储记忆。
  - **Linux 后台常驻（nohup）**：
    ```bash
    nohup ai-memory serve --transport http > ~/.local/share/ai-memory/serve.log 2>&1 &
    ```
  - **Linux 生产级守护进程（Systemd 用户服务，推荐开机自启）**：
    创建服务文件 `~/.config/systemd/user/ai-memory.service`：
    ```ini
    [Unit]
    Description=ai-memory Local MCP Server
    After=network.target

    [Service]
    Type=simple
    ExecStart=%h/.local/bin/ai-memory serve --transport http
    Restart=always
    RestartSec=3

    [Install]
    WantedBy=default.target
    ```
    启用并启动：
    ```bash
    systemctl --user daemon-reload
    systemctl --user enable --now ai-memory
    ```
- **面向 Claude Code / Codex CLI**：
  可通过原生 hooks 自动捕获，或使用 `ai-memory run <harness>` 进行受管托管启动。

##### 步骤 5：服务验证与运维备份
1. **联通性验证**：
   - 检查端口监听：`curl -I http://127.0.0.1:49374/mcp`
   - 查验项目记忆页面：`ai-memory read-page --path "notes/init.md"`
2. **数据运维**：
   同机服务保持 loopback 绑定。默认数据目录为 Linux `~/.local/share/ai-memory`、macOS `~/Library/Application Support/ai-memory`、Windows 通常 `%LOCALAPPDATA%\ai-memory`；可用 `AI_MEMORY_DATA_DIR` 覆盖。通过 `ai-memory --data-dir <data-dir> backup --to <archive-path>` 备份（Docker 部署按上游容器命令操作）。`ai-memory uninstall --apply` 只移除受管理的客户端集成，不删除数据。确需清空记忆时，先停服务、核对备份与实际数据目录，再删除该目录。详见[上游安装与运维指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md)。

#### 各工具边界

- **Claude Code**：上游 MCP/hooks；ai-memory 只管理自身配置项并保留其他 hook。仓库现有 Claude `PreToolUse` 安全钩子与记忆 hook 相互独立；Claude 原生 Auto memory 也仍是单机功能。
- **Codex CLI**：上游支持 `--client codex` / `--agent codex`。**Codex 桌面版**：在该版本支持的本地 Codex 配置界面下使用；须核实当前桌面版 MCP/hook 能力，不能直接假定所有 CLI 版本行为都相同。
- **Antigravity CLI**：上游支持 `antigravity-cli` MCP/hooks。Windows 下应在实际启动 Agent 的同一环境运行安装。
- **Antigravity 2.0 与 IDE**：设置脚本通过 `antigravity-cli` MCP 安装器写入官方共用的 `~/.gemini/config/mcp_config.json`，并更新项目托管指令；运行 `./setup-ai-memory.sh antigravity` / `-Agent antigravity` 或 `... antigravity-ide`。当前 ai-memory 上游没有 2.0/IDE 独立 lifecycle-hook target，因此此路径不自动采集会话事件；如只配置 MCP，也可在 Antigravity MCP 设置中手动添加 `serverUrl=http://127.0.0.1:49374/mcp`。参见[官方 MCP 文档](https://www.antigravity.google/docs/mcp)。
- **ChatGPT 网页版**：免费本地 loopback 服务无法直接连接远程网页会话；使用 Markdown 手动交接。远程 MCP/写入不属于本方案范围。
- **Windows**：上游文档分别支持 WSL2 与原生 Windows。必须在启动 Agent 的同一环境安装和配置，不要混用 Windows 与 WSL 路径；按[Windows 指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md)核对各客户端能力。

allowlist 只有在已安装的原生 hook 执行 capture-policy 时，才能保证没有标记的仓库不采集。路径排除不能脱敏任意提示词文本；提示词中不要包含秘密。详见 [marker-file 参考](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md)。

### 5.2 项目规则模板：`Project AGENTS.md`
- **定位**：项目维护者填写的工程上下文模板；按实际需要填写命令、技术栈和边界。
- **初始化向导**：部署时添加 `-Initialize` / `--initialize` 可根据项目目录名、Git origin 与远端 HEAD、根目录清单/锁文件和 CI 文件生成初始化版本及待确认清单；`package.json` 中存在的 scripts、常见框架/存储依赖会作为建议项，必须复核。`-DirectoryPath <相对路径>` / `--directory <相对路径>` 可同时初始化一个已存在的模块目录。脚本不猜业务定位、维护者或职责边界。已有 `AGENTS.md` 保留，输出到 `AGENTS.generated.md`。
- **检查未填项**：运行 `-Check` / `--check`，可搭配目录参数扫描规则文件中的占位符与待确认标记；若有遗漏会返回非零状态，便于合入 CI 或部署前核对。
- **核心模块**：
  1. **标准 CLI 命令槽位**：依赖安装、本地编译构建、针对单文件的精准测试、Lint 代码格式化、数据库迁移。
  2. **技术栈与运行环境矩阵**：明确语言标准（如 C++20 / Python 3.11）、包管理器、持久层版本及 CI 流水线路径。
  3. **架构核心红线**：单向依赖禁循环、统一异常处理、配置隔离防硬编码、八大高风险操作防呆。
  4. **子规则与技能调度矩阵（Router）**：
     明确定义分支流转唤醒 `git-workflow.md`、高危操作唤醒 `security-boundary.md`、复杂架构唤醒 `comet`/`openspec`、符号排查唤醒 `codegraph`、编码实现唤醒 `ponytail`+`test-driven-development`、排障唤醒 `systematic-debugging`、输出截断唤醒 `rtk`、沟通去废话唤醒 `caveman`。
  5. **项目记忆**：明确 `PROJECT_CONTEXT.md` 记录变化时的长期事实，`SESSION_STATE.md` 记录有意义收尾时的断点；无实质变化不要求双文件空更新。跨工具 ai-memory 为显式选择加入的可选项。

---

### 5.3 细粒度子规则库：`.agents/rules/`
存放于 `.agents/rules/`，Agent 仅在特定场景被唤醒时按需查阅，彻底斩断上下文滚动雪球：

| 规则文件 | 规范主题 | 核心准则与红线 |
|---|---|---|
| **`token-discipline.md`** | 上下文防漏与节流 | 管读（禁全局递归 grep，图谱优先）；管拿（精简测试参数，长日志重定向）；管说（去废话直出 Diff 与证据）。 |
| **`engineering-spec.md`** | 工程方法论与质量门禁 | SDD 规范先行（先明确 In/Out Scope 与验收场景）；TDD 验证证据门（未出示真实测试通过证据严禁宣称完成）；Ponytail 7步极简阶梯。 |
| **`security-boundary.md`** | 安全边界与高危防呆 | 落地**八大高风险操作确认矩阵**；生产环境禁止 DROP/TRUNCATE；凭证与 API Key 零泄露；超大文件（>100KB）做外科手术式微调，保持风格一致。 |
| **`git-workflow.md`** | Git 授权模型与分支流转 | **受保护分支（develop/master/main）零直接提交**；一切改动切临时分支；触碰远端必须人类强授权；严禁 `git push --force` 与 rebase 主干；**严禁盲目 `git add .`**；统一 Commit 规范。 |

#### Git 提交信息（Commit Message）格式规范：
遵循 Conventional Commits：`<type>[optional scope]: <description>`，例如 `feat(api): add export endpoint`、`fix: handle empty input`、`docs: clarify setup`。

---

### 5.4 模块边界隔离补丁：`Directory AGENTS.md`
- **使用原则**：按需创建。仅在 Monorepo 子包（`packages/*`）、独立前后端目录、或具有严格隔离边界的子模块中使用。**普通子目录默认继承根目录，严禁泛滥无脑创建！**
- **初始化**：部署脚本可通过 `-Initialize -DirectoryPath <相对路径>`（PowerShell）或 `--initialize --directory <相对路径>`（Bash）生成；目录必须已存在且位于项目根目录内。模块名称和路径可自动确定，其余待确认项会列出供当前编码 Agent 根据代码证据补全。
- **包含要素**：
  1. **模块职责定义**：清晰列出 In-Scope（负责项）与 Out-of-Scope（不负责项）；
  2. **依赖与隔离约束**：明确允许依赖的公共库与禁止反向击穿的依赖项；所有对外公开能力统一在模块入口（如 `index.ts` / `mod.rs` / `include/`）导出；
  3. **本地极速验证命令**：仅运行当前子模块的轻量单测（如 `pytest tests/core -q`），严禁全量跑测导致 Token 膨胀；
  4. **超大/遗留文件安全维护**：行号精确定位、风格一致性与封装保护。

---

## 六、 “研发为主、文档为辅”双轨实战技巧

在实际工程项目中，AI Agent 既要充当核心软件架构师，又要协助编写技术方案、用户手册或导出交付文档。必须明确区分“研发”与“文档”两套截然不同的质量控制通道：

### 1. 软件研发任务（走严谨工程通道）
- **触发场景**：功能实现、代码重构、Bug 修复、接口开发。
- **执行法则**：
  - 必须严格遵循 `engineering-spec.md` 与 `git-workflow.md`；
  - **会话启动按需感知**：仅在文件存在且与任务相关时查阅 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md`，并核实影响当前工作的事实；
  - 严格切临时分支（`feature/*`, `fix/*`）；
  - 实行 TDD 红绿单测循环：未出示测试通过的真实终端输出前，绝对不可宣称任务完成；
  - 遇到高风险操作必须停下向人类确认；
  - 严格遵守 `token-discipline.md`，执行命令追加精简过滤参数；
  - **选择性更新**：有意义的任务收尾维护 `SESSION_STATE.md`；只有长期事实变化时才更新 `PROJECT_CONTEXT.md`。

### 2. 文档与技术写作任务（走免测轻量通道）
- **触发场景**：编写或修改 `.md` 规范说明、API 文档、项目 README、架构图绘制、或处理 Word/PDF 文档。
- **执行法则**：
  - **单测免跑豁免**：修改纯文档时，AI Agent **坚决禁止盲目运行全量单元测试或重新编译整个工程**，避免徒增数千 Token 与无谓等待；
  - **专业文档技能联动**：
    - 涉及 Word 报告排版时，自动联动 `docx` 技能；
    - 涉及从设计规范、论文等 PDF 提取数据时，自动联动 `pdf` 技能；
    - 涉及 OpenSpec 规范文档撰写与校验时，联动 `write-openspec-docs`；
  - **文档结构化规范**：统一采用 GitHub Flavored Markdown 语法，使用 Alert 块（`> [!NOTE]`, `> [!IMPORTANT]`）强化关键结论，流程关系优先使用 Mermaid 状态机与序列图呈现。

---

## 七、 常见避坑指南与最佳实践 (FAQ)

### Q1：为什么不要把项目的所有命令全写进全局 `AGENTS.md`？
> **答**：全局规则是否自动进入上下文取决于工具和用户配置。如果把项目专有的构建命令写进全局，不仅会导致跨项目上下文污染（例如将 C++ 编译命令带入 Python 项目中），还会白白消耗每个项目的首轮 Token。全局规则应仅保留行为底线、去废话标准与 Git 授权宪法。

### Q2：Windows 下创建符号链接提示权限不足怎么办？
> **答**：
> 1. 打开 Windows 设置 -> **开发者选项（Developer Settings）** -> 启用 **开发人员模式（Developer Mode）**，即可在普通权限下创建符号链接；
> 2. 我们提供的 `deploy-agents.ps1` 针对目录默认使用 Windows 原生支持的 **Directory Junction（连接点）**，普通非管理员权限即可秒级创建，无需额外配置；
> 3. 针对 `CLAUDE.md` 单文件桥接，脚本会自动检测权限，并在受限时自动优雅降级写入单行 `@AGENTS.md`，Claude Code 同样能够无缝识别并引用规则上下文。

### Q3：多个工具是否会以相同方式加载规则？
> **答**：不能假设一致。Markdown 内容可以复用，但规则入口、继承优先级、Skills 和 Hook 能力应按各工具及版本分别核实。

### Q4：项目升级或重构后，如何维护这些规则文件？
> **答**：
> - 规则文件应随项目变化定期维护；用户明确要求修改时可直接调整并说明差异；
> - 本地命令、技术栈、架构边界或工具支持范围变化时，更新对应模板/文档，并核对部署脚本行为。

### Q5：这套规范适用于哪些编程语言？
> **答**：**完全语言无关（Language-Agnostic），天然支持所有主流编程语言**。
> - **全局规范**定义的是普适的工程师行为底线（最小修改、凭证安全、防编造、文档免测通道）；
> - **项目级与目录级规范**定义的是标准的“工程生命周期槽位”（依赖管理、编译构建、单元测试、静态代码分析 Lint、架构边界隔离）；
> - 无论在 **C/C++**（CMake + CTest + Clang-Tidy）、**Python**（Poetry + Pytest + Ruff）、**Rust**（Cargo + Clippy）、**Go**（Go Modules + Go Test）、还是 **JS/TS**（pnpm + Vitest + ESLint）项目中，只需将 `Project AGENTS.md` 中的槽位填入当前技术栈的原生 CLI 命令，AI 便能立刻掌握该语言的开发与测试闭环。

### Q6：为什么要建立子级文档（.agents/rules/）？如何从根本上节省 Token？
> **答**：基于 **Harness 工程与 Token 经济学** 的两项核心推论：
> 按需读取子规则可以减少与当前任务无关的指令，但实际上下文成本取决于工具、缓存和会话配置。规则分层的主要价值是保持入口聚焦、便于项目裁剪；不要把未经测量的固定 Token 节省比例当作保证。

### Q7：部署 30+ 个 Skill 会增加上下文成本吗？
> **答**：可能，具体取决于宿主工具如何发现和加载 Skills、启用了哪些目录及其描述长度。不要假设所有宿主都只加载元数据，也不要把缓存命中或固定 Token 节省比例当作保证。按需保留项目真正使用的 Skills，并在目标工具中验证加载行为。

### Q8：在项目中部署后，AI Agent 能否在会话中正确调用这些技能？
> **答**：取决于宿主是否发现并加载 Skill，以及当前会话可用的工具能力。项目规则只能引导，不会强制宿主提供未安装的 CLI/MCP。Ponytail/Caveman 作为指导 Skill 随项目复制；CodeGraph/RTK 还需安装 CLI 并配置 Agent。部署脚本会检测并逐项询问是否安装及配置，默认跳过。

### Q9：Git 受保护分支与临时分支隔离机制是什么？为什么严禁直接在主分支提交？
> **答**：源自大型工程实战教训（如 `comm_ipc`）：
> 1. **受保护分支强隔离**：`develop` / `master` / `main` / `release*` 是团队协同共享主干。如果 AI 在主干上直接改代码并 commit，一旦改出问题或引入脏代码，会立刻阻塞全体团队成员；
> 2. **一切改动走临时分支**：所有需求与修复必须在 `feature/*`、`fix/*` 等临时分支上编写并完成单测验证；
> 3. **触碰远端强授权**：AI 允许在本地切分支、改动和提交，但**合入主干（merge）与推向远端（push）必须人类明确授权**；
> 4. **禁止 `git add .`**：防止将构建产物、本地测试 json、以及 `*.autosave` 临时文件带入版本库。

### Q10：什么是“八大高风险操作防呆矩阵”？
> **答**：为杜绝 AI 自作主张引发级联编译灾难，在 `.agents/rules/security-boundary.md` 中定义了 8 种必须停下向人类确认的操作：
> 1. 修改构建配置（`.pro` / `CMakeLists.txt` / `package.json` / `Cargo.toml`）；
> 2. 引入新的第三方依赖；
> 3. 修改核心全局公共数据结构/公共头文件（如 `public_struct.h`）；
> 4. 修改核心调度单例与全局公共接口；
> 5. 修改通信协议与报文契约（如 `protofile/*.json`）；
> 6. 修改软件授权（license）、加解密与认证安全代码；
> 7. 修改 `.gitignore` 或 CI/CD 构建发布流水线；
> 8. 影响共享契约或需要广泛协调的高影响跨模块改动；文件数量本身不触发授权。

### Q11：为什么要在 Claude Code 中配置 PreToolUse 拦截钩子（.claude/settings.json）？
> **答**：模型可能误解命令或目标分支，因此对共享远端使用服务端保护，并将客户端 Hook 视为辅助检查。
> Hook 只在 Claude Code 客户端匹配的工具调用前运行。它会拒绝部分命令模式，并对其他风险操作发出非阻断警告；不能替代 Git 服务端分支保护。

### Q12：模板更新（`-Update` / `-u`）会覆盖哪些配置？
> **答**：单独使用 `-g` 时，只初始化缺失的 Claude、Antigravity 和 Codex 全局规则；已有文件保留。`-g -u` 会先创建带时间戳的 `.bak.*` 备份，再用最新模板覆盖。Antigravity 部署规范正文 `~/.gemini/AGENTS.md`，并生成轻量 `GEMINI.md` 兼容指针以覆盖旧版 IDE；避免完整规则重复注入。Codex 默认写入 `~/.codex/AGENTS.md`，设置 `CODEX_HOME` 时使用其目录；存在非空 `AGENTS.override.md` 时更新该当前生效文件。已有项目根 `AGENTS.md` 仍保留，并生成 `AGENTS.template.md` 供审阅。其他规则、Hook、技能和元数据仍按各自备份/更新策略处理。

### Q13：如何复用项目经验？
> 项目可将 `tasks/lessons.md` 作为可选经验记录。只在出现值得复用的经验时更新，并在相关任务中查阅；不要求每次会话执行固定仪式。

### Q14：什么时候更新 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md`？
> 在有意义的任务/会话边界维护断点：`SESSION_STATE.md` 记录实际完成项、验证证据、未完成步骤与仍有效风险；长期架构、约束或已确认决策发生变化时才更新 `PROJECT_CONTEXT.md`。无变化时不制造空更新。两者都是项目记忆摘要，不覆盖当前用户指令、代码、配置或可复现证据；不得写入凭证、原始个人数据或完整对话/工具日志。

---

## 八、 实战演练与高级技能指南索引

更详细的各生态工具（Comet、OpenSpec、Superpowers、CodeGraph、Ponytail、Caveman、RTK）深度使用说明、四大平台原生斜杠命令（`/plan`、`/goal`、`/opsx` 等）、以及端到端典型研发实战流转演练，请参阅兄弟指南：
👉 [各工具实战使用与技能全景指南.zh.md](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
