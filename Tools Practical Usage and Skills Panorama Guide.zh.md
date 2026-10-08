# 多工具（Claude Code / Codex / Antigravity 2.0 / CLI / IDE / Zed）AI 研发实战与技能全景指南

> **Language / 语言**: **中文** | [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md)

> 本指南针对日常“以软件研发为主、兼顾专业文档处理”的实际工程场景，系统解答：**需要安装哪些技能（Skills）与 Harness 工具、底层加载与 Token 经济学原理、各工具如何配置与接线、核心命令（如 `/comet`、`/plan`、`/opsx`、`codegraph` 等）在何时以及如何使用**，并提供端到端的实战流转演示与避坑自检指南。

---

## 目录

1. [核心架构与工具矩阵全景（谁管什么）](#一-核心架构与工具矩阵全景谁管什么)
2. [技能（Skills）与生态工具安装清单](#二-技能skills与生态工具安装清单)
   - 2.1 开箱即用 / 40+ 原生技能分类全景清单
   - 2.2 版本锁与在线更新机制 (`skills-lock.json` + `deploy-agents`)
   - 2.3 Harness 核心工程扩展工具（按需选用）
   - 2.4 平台安装与配置文件位置速查表
   - 2.5 技能底层运行机制与 Token 经济学（为什么装 40+ 技能不耗 Token？）
   - 2.6 工程技能与规则联动调度矩阵（实战唤醒表）
3. [核心 Harness 工具与 Slash Commands 深度使用说明](#三-核心-harness-工具与-slash-commands-深度使用说明)
   - 3.1 Comet：版本化工作流入口
   - 3.2 OpenSpec：需求规格驱动 SDD（`/opsx:propose` / `/opsx:apply` 等子技能群）
   - 3.3 Superpowers：测试驱动 TDD、排障与验证证据门
   - 3.4 CodeGraph：可选 MCP 代码图谱集成
   - 3.5 Ponytail：代码防熵增懒人阶梯（生成端）
   - 3.6 Caveman：简明表达指导（输出端）
   - 3.7 RTK：可选命令过滤 CLI（执行端）
   - 3.8 Git 授权模型与受保护分支协作流转（版本控制端）
   - 3.9 可选任务记录与项目经验
   - 3.10 八大高风险操作防呆矩阵（安全边界）
4. [四大工具平台原生实践与技巧对照表](#四-四大工具平台原生实践与技巧对照表)
   - 4.1 Google Antigravity IDE 专属命令与实践
   - 4.2 Claude Code 专属命令与 PreToolUse 客户端钩子
   - 4.3 OpenAI Codex / Copilot 专属命令与钩子管理
   - 4.4 Zed IDE 专属实战与技巧
5. [端到端研发全流程实战演示（以一个典型需求为例）](#五-端到端研发全流程实战演示以一个典型需求为例)
6. [日常健康诊断与常见避坑指南](#六-日常健康诊断与常见避坑指南)

---

## 一、 核心架构与工具矩阵全景（谁管什么）

在复杂的 AI 辅助研发过程中，任务失控、越界或代码劣化（熵增）的根本原因在于**缺乏物理边界与受控跑道**。我们所采用的 Harness 体系将软件研发全流程划分为五个核心控制闸门：

```text
       [ 用户输入需求 ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. 流程与状态门：Comet (/comet) + OpenSpec (SDD 需求契约) │
       └──────┬─────────────────────────────────────────────────┘
              │ 需求契约已锁定，开始阅读与检索
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. 可选语义检索：CodeGraph（已配置 MCP 时使用）               │
       └──────┬─────────────────────────────────────────────────┘
              │ 影响范围与符号关系已明确，开始设计与实现
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. 代码形态门：Superpowers (TDD 红绿循环) + Ponytail (懒人阶梯)│
       └──────┬─────────────────────────────────────────────────┘
              │ 验证代码，执行本地命令与单测
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. 可选命令过滤：RTK（CLI 与 Agent Hook 配置后生效）        │
       └──────┬─────────────────────────────────────────────────┘
              │ 交付与版本控制
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. 沟通与提交：Caveman 风格指导（已加载时）+ Git 规则       │
       └────────────────────────────────────────────────────────┘
```

### 职责分工速查表

| 组件 / 工具 | 核心职责 | 解决的核心痛点 | 交互形态 |
|---|---|---|---|
| **Comet** | 版本化 Native/Classic 工作流 | 需要可恢复、可验收的任务流程 | 按已安装版本及 `.comet/config.yaml` 使用 |
| **OpenSpec** | 规范驱动开发（SDD） | 需求在对话中失真、改动不可回溯、无验收标尺 | `/opsx:propose`、`docs/openspec/` 活文档 |
| **Superpowers** | 测试驱动开发（TDD）与质量门禁 | Agent 谎报“已做完”、缺少客观物理验证证据 | 编写失败用例 $\rightarrow$ 刚好通过 $\rightarrow$ 出具验证报告 |
| **CodeGraph** | 可选的代码语义检索集成 | 需要 CLI、Agent MCP 接线及项目索引 | 配置后通过 CodeGraph MCP 查询 |
| **Ponytail** | 最小实现指导 Skill | 过度封装、无必要依赖与抽象 | 宿主工具加载 Skill 后提供建议，不强制执行 |
| **Caveman** | 简明表达指导 Skill | 冗长表达 | 宿主加载 Skill 后提供风格指导；仍须保留清晰度与必要安全说明 |
| **RTK** | 可选 Rust Token Killer CLI | 终端输出冗长 | 需安装并配置支持的 Agent Hook；仓库 Skill 不会自动改写命令 |
| **Git 授权模型** | 受保护分支规范与有限客户端检查 | 避免误操作共享分支 | 规则、Claude Code Hook 检查、服务端分支保护 |

---

## 二、 技能（Skills）与生态工具安装清单

### 2.1 开箱即用 / 40+ 原生技能分类全景清单

通过执行自动化部署脚本 [`deploy-agents.ps1`](deploy-agents.ps1)（Windows）或 [`deploy-agents.sh`](deploy-agents.sh)（Linux/macOS）后，全套技能库会自动部署至目标项目的 `.agents/skills/`，并无缝接线至 `.claude/skills/`。

整套技能库包含 **40 个专业工程技能**，按功能领域归类如下：

#### 1. Comet 工作流
- **`comet`**：Comet CLI 按版本提供 Native/Classic 工作流。本仓库只提供入口指引，不实现 Comet 的状态机或阶段守卫；使用前检查项目配置和 CLI 版本。

#### 2. OpenSpec 规范驱动开发套件（16 个模块化技能）
- **`openspec`**：OpenSpec 基础核心架构。
- **`openspec-propose`**：一键生成完整需求提案（包含 Design、Specs、Tasks）。
- **`openspec-new-change`**：步进式创建新变更。
- **`openspec-continue-change`**：推进当前变更至下一产物。
- **`openspec-ff-change`**：快速前进（Fast-Forward）跳过中间确认直接就绪实施。
- **`openspec-apply-change`**：读取变更任务清单并逐步执行代码实施。
- **`openspec-verify-change`**：严格对比实际代码实现与变更规格，核验一致性。
- **`openspec-sync-specs`**：将增量 Delta Spec 同步合入主规格文档。
- **`openspec-archive-change`**：归档已完结的单项变更。
- **`openspec-bulk-archive-change`**：批量归档多项已合并变更。
- **`openspec-explore`**：在立项前与人类思维对齐，探索需求细节与可行性。
- **`openspec-onboard`**：交互式实操新手引导。
- **`write-openspec-docs`**：以 OpenSpec 官方规范语调撰写或重构文档。
- **`draft-openspec-docs`**：协同逐节起草长篇规范。
- **`verify-openspec-docs`**：事实核查文档命令与配置正确性。
- **`release-openspec`**：版本发布、Changeset 审计与发布日志管理。

#### 3. Superpowers 工程质量与严谨开发套件（15 个模块化技能）
- **`superpowers`**：核心质量总规约。
- **`using-superpowers`**：对话入口技能分发与原则判定。
- **`brainstorming`**：创意思维推演与需求边界挖掘。
- **`writing-plans`**：复杂任务执行前制定严密的实施计划。
- **`executing-plans`**：按计划逐步严谨执行改动。
- **`test-driven-development`**：严格 TDD 红绿循环（先写红单测 $\rightarrow$ 最小绿代码 $\rightarrow$ 重构）。
- **`systematic-debugging`**：系统化排障（先抓根因 Trace $\rightarrow$ 建立假设 $\rightarrow$ 验证证伪，严禁创可贴盲修）。
- **`verification-before-completion`**：完工证据门（未出示真实命令输出严禁宣称完工）。
- **`dispatching-parallel-agents`**：无状态无依赖的独立并行任务调度。
- **`subagent-driven-development`**：子代理驱动的任务分流执行。
- **`using-git-worktrees`**：利用 Git Worktree 实现物理工作区强隔离。
- **`finishing-a-development-branch`**：开发分支收尾、审查与合并决策。
- **`requesting-code-review`**：提交前自我代码审查与要求人工评审。
- **`receiving-code-review`**：技术性接收人类评审意见并求证，拒绝盲目顺从。
- **`writing-skills`**：技能编写与校验框架。
- **`diagnosing-superpowers`**：会话偏航排查与质量审计。

#### 4. 代码防熵增与语法图谱检索
- **`ponytail`**：代码防熵增懒人阶梯（能改 1 行绝不写 10 行，标准库优先，严禁机会主义过度封装）。
- **`codegraph`**：可选 CodeGraph MCP 代码语义检索指引；CLI、Agent 接线和项目索引需单独配置。

#### 5. 终端防爆与电报体去废话
- **`rtk`**：可选 Rust Token Killer CLI；安装并配置支持的 Agent Hook 后，才能改写其支持的命令。
- **`caveman`**：简明表达指导 Skill；宿主加载后按其风格要求回复，同时保留必要说明。

#### 6. 专业格式文档处理
- **`docx`**：Word（.docx / .dotx）专业文档生成、排版、样式与内容抽取。
- **`pdf`**：PDF 结构化文本抽取、表格分析、页面拆分合并与 OCR。

---

### 2.2 技能来源元数据与模板同步 (`skills-lock.json` + `deploy-agents`)

仓库提供技能来源/完整性元数据和模板同步脚本；当前脚本不按锁定哈希下载上游技能，也不保证各项目已安装副本一致：

1. **`skills-lock.json`**：
   - 记录技能来源及部分文件的完整性哈希；具体字段取决于上游条目，不能等同于完整的 commit 锁定清单；
   - 位于代码库根目录，随项目版本控制一起追踪。
2. **一键在线更新**：
   - 当官方技能库发布新版本或修补 Bug 时，只需在项目根目录运行：
     ```powershell
     # Windows 环境一键拉取最新规则与技能库
     .\deploy-agents.ps1 -ProjectPath "." -Update

     # Linux / macOS 环境一键更新
     ./deploy-agents.sh "." --update
     ```
   - 脚本通过 `git pull --ff-only` 更新模板仓库，再将管理文件复制到目标项目；它不会运行第三方技能更新器或升级全局 CLI；
   - 更新会备份被替换的规则、Hook、技能目录和版本元数据。已有根目录 `AGENTS.md` 保持原样，并在更新时生成 `AGENTS.template.md`。

---

### 2.3 可选的 CLI 工具

技能的发现与运行能力取决于宿主工具及其配置。需要 CLI 时再单独安装相应工具；CLI 本身不代表所有宿主都能自动调用技能。

#### 1. Comet CLI（按需安装）
- **定位**：提供 Comet 自身版本支持的项目初始化与 Native/Classic 工作流。具体命令和状态管理依版本而异，请查阅当前官方文档。
- **说明**：本仓库的 Markdown 技能不能替代 Comet CLI，也不会凭空提供终端状态机或客户端 Hook。
- **安装与初始化**：
  ```bash
  # 全局安装 CLI（单台机器仅需安装一次，需 Node.js >= 22）
  npm install -g @rpamis/comet

  # 如需配置 Comet 项目，再按当前版本文档初始化
  cd /path/to/your-project
  comet init
  ```

#### 2. CodeGraph CLI（可选）
- **本仓库已提供**：Skill 使用说明，不包含 CodeGraph CLI 或 MCP 服务。
- **安装**：macOS/Linux 可用 `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh`；Windows PowerShell 可用 `irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex`；也可按官方文档使用 `npm i -g @colbymchenry/codegraph`。
- **接线与索引**：运行 `codegraph install` 配置 Agent MCP，然后在项目根目录运行 `codegraph init` 创建本地索引。CLI 安装本身不会完成这两步。项目部署脚本会先检测 CLI；缺失时询问是否安装，配置和索引步骤另行询问。Agent 通过已配置的 MCP 工具查询，不要假设存在 `codegraph explore` 命令。

#### 3. RTK CLI（可选）
- **本仓库已提供**：Skill 使用说明，不包含 RTK CLI，也不会自动拦截或重写命令。
- **安装**：macOS/Linux 可使用官方安装命令 `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh`；Windows 可用 `winget install rtk-ai.rtk`。
- **验证与接线**：运行 `rtk gain` 确认安装的是 Rust Token Killer（存在同名的其他工具）；再在项目根目录运行 `rtk init` 配置支持的 Agent Hook。项目部署脚本会先检测 CLI；缺失时询问是否安装，Hook 初始化单独询问。`rtk init --global` 会改全局配置，需按需单独选择。

---

### 2.4 平台安装与规则记忆入口速查表

| 平台/表面 | 规则入口 | 记忆特性与边界 |
|---|---|---|
| Codex（本地 App / IDE 扩展 / CLI） | Codex home 全局 `AGENTS.md`；项目与目录 `AGENTS.md` | `-g` 初始化，`-g -u` 备份并替换生效规则；支持 `$CODEX_HOME` 和优先级更高的非空 `AGENTS.override.md` |
| Claude Code | `CLAUDE.md` / `AGENTS.md`；用户、项目和目录规则 | 可选 Auto memory 为 Claude 管理的机器本地项目记忆，使用 `/memory` 查看/编辑；不与其他工具自动共享 |
| Antigravity 2.0 | 项目/目录 `AGENTS.md`、`GEMINI.md`、`.agents/rules/*.md`；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针 | 当前版本加载两种全局文件名；较早版本可跟随指针 |
| Antigravity CLI | 项目/目录规则；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针；CLI 规则目录可另行配置 | 通用全局规则来自规范入口；CLI 专属 rules 按需配置 |
| Antigravity IDE / Extensions | 项目/目录规则；全局 `~/.gemini/AGENTS.md` 与 `GEMINI.md` 兼容指针 | 当前版本支持两种全局文件名；IDE 也提供 Customizations UI |
| Copilot / Zed | 各自产品设置或桥接文件 | 当前部署脚本不保证自动发现或全局持久记忆 |

本仓库以 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md` 提供可审阅、可跨工具复用的文件基线。工具原生记忆是可选且各自独立的能力，不能取代项目事实源。

### 2.5 技能底层运行机制与 Token 经济学（为什么装 40+ 技能不耗 Token？）

很多开发者担心：“安装了 40 个 Skills，每次对话会不会把上下文撑爆、消耗超多 Token？”
是否增加上下文取决于宿主工具如何发现 Skills、配置了多少技能，以及会话是否加载它们。本仓库不对 Token 成本或节省比例作固定承诺。

| 组件 | 仓库提供什么 | 运行前提 |
|---|---|---|
| `ponytail` | 最小实现决策指导 Skill | 宿主工具发现并加载对应 Skill |
| `caveman` | 简明表达指导 Skill | 宿主工具发现并加载对应 Skill；保留必要技术与安全信息 |
| `codegraph` | 可选集成说明 Skill | 需安装 CLI、运行 `codegraph install` 配置 Agent，再在项目运行 `codegraph init`；查询通过已配置的 MCP 工具进行 |
| `rtk` | 可选 Rust Token Killer 使用说明 Skill | 需安装正确的 RTK 并配置支持的 Agent Hook；用 `rtk gain` 验证，避免同名工具混淆 |

Skill 文件的存在不代表宿主自动加载。实际上下文成本和 CLI 效果受工具、版本与配置影响；可选工具未安装时，使用项目可用的常规检索和命令输出控制。

---

### 2.6 工程技能与规则联动调度矩阵（实战唤醒表）

为了让 AI Agent 和开发者在日常研发中能精准对号入座，形成“条件反射级”的高遵从度，以下为核心研发场景与技能的唤醒映射表：

| 研发场景 | 绑定规则 / 技能 | 触发方式 / 唤醒关键词 | 预期交付与行为规范 |
|---|---|---|---|
| **分支流转 / 提交 / 推送** | [`git-workflow.md`](.agents/rules/git-workflow.md) | 涉及 `git commit` / `git push` / 分支切换 | 严格在临时分支提交；严禁 `git add .`；触碰远端必须明确授权；禁 force push 与 rebase |
| **高危操作 / 核心结构变更** | [`security-boundary.md`](.agents/rules/security-boundary.md) | 触碰 8 大高风险操作（改构建/协议/公共头/依赖） | 暂停执行，列出变动清单与影响面，待人类明确确认后再操作 |
| **复杂需求 / 架构改造** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` 或 `用 openspec 规范出方案` | 仅在用户指定或项目已配置相应工作流时，遵循该工具当前版本流程 |
| **代码依赖 / 找符号引用** | [`token-discipline.md`](.agents/rules/token-discipline.md) + `codegraph` | CodeGraph MCP 可用时进行语义查询；否则限定范围搜索 | 不假设 CodeGraph 已安装；MCP 不可用时使用相关目录的 `rg` |
| **功能实现 / 编码阶段** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `ponytail` + `test-driven-development` | `用 ponytail 策略实现` / 指令后追加 `极简原则` | 理解现有实现后遵循适用的最小实现原则；测试按任务与项目约定执行验证 |
| **复杂 Bug / 偶现排障** | [`engineering-spec.md`](.agents/rules/engineering-spec.md) + `systematic-debugging` | `系统性排查该 bug` 或粘贴完整报错 Trace | 严禁创可贴盲修；必须先收集证据、建立假设、定位根因再写修复 |
| **超长输出 / 测试跑批** | [`token-discipline.md`](.agents/rules/token-discipline.md) + `rtk` | RTK Hook 配置后才会改写支持的命令；否则使用原生命令参数 | 保留必要验证，长日志可重定向到本地文件 |
| **Token 告急 / 精简输出** | [`Global AGENTS.md`](Global%20AGENTS.md) + `caveman` | `/caveman` 或 `进入 caveman 模式` / `说人话` | 在宿主加载 Skill 时可简化表达，同时保留必要背景、技术精度和安全说明 |
| **Word / PDF 专业文档** | `docx` / `pdf` | 直接提及 `.docx`、`.pdf` 或 `导出规范文档` | 遵循专业排版规范，自动处理表格对齐、样式维护与内容抽取，不乱跑单测 |
| **任务收尾 / 完工声明** | `verification-before-completion` | 任务收尾阶段自动触发 | 未出示真实可复现的验证依据（测试输出片段或运行结果）前，绝不可声称任务完成 |

---

## 三、 核心 Harness 工具与 Slash Commands 深度使用说明

### 3.1 Comet：版本化工作流入口

Comet 是独立版本的工作流工具。使用前检查项目 `.comet/config.yaml` 与 CLI 版本，并按该版本支持的 Native 或 Classic 工作流执行。此仓库中的 Comet Skill 仅引导检查和使用，不创建虚构的状态文件，也不提供自动阶段拦截。未安装或未配置 Comet 时，按项目已有流程或任务需要制定计划。

```text
/comet 为订单模块新增按日期范围批量导出接口
```

Comet 具体入口、配置、产物路径和归档行为以当前版本官方文档为准。

---

### 3.2 OpenSpec：需求规格驱动 SDD（`/opsx:propose` / `/opsx:apply` 等子技能群）

#### 核心思想
**“规范是唯一真相，代码只是规范的实现产物。”**

#### 常用命令与时机：
- `/opsx:propose <name>`：在进行架构改造或复杂新特性前，先生成需求草案，产出 `docs/openspec/` 结构文档；
- `/opsx:apply`：需求讨论完毕并经人工确认后，将 Delta 变更应用并驱动代码生成；
- `/opsx:verify`：自动比对实际实现代码与变更规格，输出一致性核验报告；
- `/opsx:sync`：将增量 Delta Spec 合并入主规格资产库；
- `/opsx:archive`：所有单测与验证均通过后，将零散变更正式归档；
- `/opsx:explore`：立项前探索需求细节，与人类思想对齐。

---

### 3.3 Superpowers：测试驱动 TDD、排障与验证证据门

#### 核心要求
**“没有真实可复现的物理验证依据（Verification Report），绝不可声称任务完成。”**

#### 使用流程：
1. **红（Red）**：根据 OpenSpec 规范中的 `#### Scenario:` 先行编写单测。运行测试，**必须看到预期的失败报错**（确认测试确实在测这个逻辑，而非恒真盲测）；
2. **绿（Green）**：编写刚好能够让单测通过的业务代码（Ponytail 极简原则）；
3. **重构与证据沉淀（Refactor & Report）**：运行项目快速单测命令（带精简输出参数），如 `pytest -q` 或 `ctest --output-on-failure`。向用户出具最终验证报告，附带测试通过的真实输出片段。

#### 系统化排障（`systematic-debugging`）四步法：
遇到复杂 Bug 时，严禁凭直觉修改代码，必须执行：
1. **收集完整证据**：读取完整堆栈 Trace，分析崩溃点局部变量；
2. **建立假设**：基于调用链路提出 1~2 个明确的可能根因；
3. **编写最小复现用例**：通过一个极简测试稳定复现该 Bug；
4. **针对性修复与验证**：修复根因并验证复现测试变绿，出具复现与修复证据。

---

### 3.4 CodeGraph：可选 MCP 代码图谱集成

#### 为什么优先用它，而不是全局 `grep`？
- 全文 `grep` 往往会命中数千行构建产物、测试 Mock 数据或无关同名变量，直接撑爆会话窗口；
- CodeGraph 需要 CLI 安装、Agent MCP 接线和项目索引；不可用时使用针对性代码搜索。

#### 使用方式：
1. 通过 Agent 已连接的 CodeGraph MCP 工具查询“用户登录与 Token 签发流程”。
2. 查询 `OrderService::calculateDiscount` 的定义和调用关系。

---

### 3.5 Ponytail：代码防熵增懒人阶梯（生成端）

Ponytail Skill 提供一套实现前决策阶梯。先读懂问题和现有代码，再按需评估：
1. **这行代码/功能必须存在吗？**（YAGNI：不需要就别写）；
2. **代码库内是否已经有类似函数或工具类？**（优先复用已有逻辑）；
3. **语言自带的标准库能否直接解决？**（例：能用 Python 标准库 `urllib`/`sqlite3` 就不引入额外大库；C++ 能用 `<filesystem>` 就不引额外包）；
4. **能改动 1 行解决，绝不重写 10 行**；
5. **严禁在修复局部 Bug 时顺手做“机会主义重构”**。

---

### 3.6 Caveman：简明表达指导（输出端）

#### 核心规约（Caveman）
- 严禁输出：“好的，我明白了”、“接下来我将为您分步执行”、“请注意，使用本方案需要谨慎”等寒暄与免责铺垫；
- **交付格式**：先给结论与核心影响 $\rightarrow$ 再给代码 Diff $\rightarrow$ 最后给出测试通过的证据与待确认点；
- **边界说明**：精简仅适用于**聊天交互过程**；正式的需求提案（Proposal）、设计文档（Design Spec）、Commit 信息与 PR 描述仍须保持语义严谨完整。

---

### 3.7 RTK：可选 Rust Token Killer CLI（执行端）

#### 核心规约（RTK）
- 控制无关输出，但不得为了精简而省略必要验证：
- 仅当 RTK CLI 已安装且当前 Agent Hook 已配置时，RTK 才会改写其支持的命令。否则使用项目 CLI 的精简参数：
  - 查看状态：使用 `git status -s`（而不是整段 `git status`）；
  - 执行测试：使用 `pytest -q`、`npm test -- --reporter=dot`、`ctest --output-on-failure`；
  - 遇到长日志报错：将其重定向到本地临时文件（如 `scratch/build_error.log`），仅向上下文回传带有 `FAIL` 或 `Error` 的关键 20 行切片。

---

### 3.8 Git 授权模型与受保护分支协作流转（版本控制端）

#### 为什么必须采用受保护分支隔离？
在团队协作与正规工程中，`develop`、`master`、`main`、`release*` 是共享生命线。AI 代理一旦在受保护分支上直接 commit，极易将未测代码、半成品或本地脏配置写入主干。

#### 核心授权与流转准则：
1. **新改动一律切临时分支**：所有需求与 Bug 修复必须通过 `git checkout -b {type}/short-description` 切换临时分支；常见类型前缀：`feature/`、`fix/`、`refactor/`、`cleanup/`、`docs/`；
2. **触碰共享远端必须人类强授权**：AI 可以自发在本地切分支、修改代码、执行单测验证；**禁止擅自 push 到共享远端**；**禁止擅自将临时分支 merge 到受保护分支**；
3. **三大永久硬性禁令**：
   - 严禁 `git push --force`（或 `-f` / `--force-with-lease`）改写远端历史；
   - 严禁在受保护分支上执行 `git rebase`；
   - 线上已合入代码的回滚一律使用 `git revert -m 1`，保持版本历史线性安全；
4. **防误提交闸门（严禁 `git add .`）**：
   - 严禁盲目执行 `git add .` 或 `git add -A`，必须只 `git add <明确文件路径>`，防止将二进制构建产物（`image/`、`build/`）、自动保存文件（如 `*.autosave`）以及本地测试 json 意外提交入库；
5. **提交信息（Commit Message）格式规范**：遵循 Conventional Commits：`<type>[optional scope]: <description>`，如 `feat(api): add export endpoint`。

---

### 3.9 项目记忆与会话断点（`PROJECT_CONTEXT.md` / `SESSION_STATE.md`）

把记忆作为可核实的摘要和导航，而非代码或正式文档的替代品：
1. **开始任务**：仅在存在且相关时读取 `PROJECT_CONTEXT.md`（已验证的长期项目事实）和 `SESSION_STATE.md`（当前断点），并核实影响任务的分支、配置与实现。
2. **工作中**：多步骤任务按需维护计划；不把原始提示、工具输入/输出、源文件或终端命令自动采集为记忆。
3. **有意义的收尾**：更新 `SESSION_STATE.md` 中的完成项、实际验证证据、未完成步骤与仍有效风险，清理过期信息。仅当长期架构、约束或确认决策变化时更新 `PROJECT_CONTEXT.md`；无实质变化不做空更新。
4. **来源与冲突**：标注不确定性，易变事实尽量附日期/来源。当前用户指令和当前代码/配置/可复现证据优先于记忆摘要。
5. **隐私**：不记录凭证、私钥、原始个人数据、完整对话/工具日志或不必要的个人信息；共享全局模板不得记录用户私人偏好。
6. **目录范围**：目录级 `AGENTS.md` 只记本目录独有边界和约束；默认不另建目录级记忆文件，项目事实与断点分别留在根目录文件。

**Claude Code 原生 Auto memory** 是独立的机器本地项目记忆，支持通过 `/memory` 查看、编辑或删除；它不跨工具或机器共享，也不替代上述项目文件。其行为由 Claude Code 管理，本仓库部署脚本不会启用、关闭或采集它。详见 [Claude Code memory docs](https://code.claude.com/docs/en/memory)。

#### 可选跨 Agent 长期记忆：ai-memory（实操部署与使用全景）

本仓库只选择 [ai-memory](https://github.com/akitaonrails/ai-memory) 作为可选跨工具后端。它的本地 Markdown 与全文检索路径不需要 LLM、embedding provider 或 API Key；本仓库不会自动安装或启动服务。

##### 1. 前置安装与 Windows 终端环境变量刷新
- **通过 Rust Cargo 安装（跨平台）**：`cargo install ai-memory`；
- **Linux / macOS（快速下载原生二进制）**：
  ```bash
  mkdir -p ~/.local/bin
  curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin/
  chmod +x ~/.local/bin/ai-memory
  export PATH="$HOME/.local/bin:$PATH"
  ```
- **Windows（下载 Release 解压并加 PATH）**：
  从 [GitHub Releases](https://github.com/akitaonrails/ai-memory/releases) 下载 `ai-memory-windows-x86_64.zip`；
- 💡 **避坑要点（Windows IDE 内置终端）**：若在运行中的 Antigravity IDE / VS Code 中修改了系统 PATH，由于 Windows 进程环境变量继承机制，已开终端无法感知新 PATH。在 PowerShell 中无需重启 IDE，运行以下命令即可强制刷新当前会话 PATH：
  ```powershell
  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  ```

##### 2. 单仓库加入与显式声明
检查 `.ai-memory.toml.example`，复制为被 Git 忽略的 `.ai-memory.toml` 并替换 workspace/project 名称（未替换占位符将触发脚本防呆）：
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

##### 3. 运行客户端配置脚本
运行辅助脚本自动向客户端挂载 MCP 节点与专属技能指令：
- **PowerShell**: `.\setup-ai-memory.ps1 -Agent antigravity-ide` （支持 `antigravity-ide`, `antigravity-cli`, `claude-code`, `codex`）
- **Bash**: `chmod +x ./setup-ai-memory.sh && ./setup-ai-memory.sh antigravity-ide`
- **输出解读**：
  - `✓ no-op ... (already up to date)`：代表**幂等性保护**生效，目标配置已经是最新版本，自动跳过重复写入；
  - `Configured <agent>. No server, container, API key, or LLM provider was installed or started.`：声明性成功结语，表明配置已完成，且坚守零常驻、零容器、零 API 扣费的安全底线。

##### 4. 启动本地记忆引擎服务
- **面向 Antigravity IDE（通过 HTTP MCP 接入）**：
  > ⚠️ `ai-memory serve` 默认采用 `stdio` 管道模式，不会开启网络端口。要为 IDE 提供服务，**必须使用 `--transport http` 启动**：
  - **前台调试**：`ai-memory serve --transport http` （终端输出 `bind=127.0.0.1:49374` 即就绪）；
  - **Linux 后台常驻**：`nohup ai-memory serve --transport http > ~/.local/share/ai-memory/serve.log 2>&1 &`；
  - **Linux 生产级开机自启（Systemd 用户服务）**：
    创建 `~/.config/systemd/user/ai-memory.service`（写入 `ExecStart=%h/.local/bin/ai-memory serve --transport http` 与 `Restart=always`），执行 `systemctl --user enable --now ai-memory`。
- **面向 Claude Code / Codex CLI**：
  可通过原生 hooks 自动捕获，或使用 `ai-memory run <harness>` 进行受管托管启动。

##### 5. 服务验证与运维备份
- **联通性验证**：Linux 下可通过 `curl -I http://127.0.0.1:49374/mcp` 验证端口，并运行 `ai-memory read-page --path "notes/init.md"` 校验数据读取；
- **数据运维**：默认数据目录 Linux 为 `~/.local/share/ai-memory`，Windows 为 `%LOCALAPPDATA%\ai-memory`；数据备份使用 `ai-memory --data-dir <data-dir> backup --to <archive-path>`。

Claude Code、Codex CLI 与 Antigravity CLI 可安装 MCP/hooks。Antigravity 2.0 和 IDE 通过共享 MCP 配置连接 ai-memory；上游当前没有其专属 ai-memory 生命周期 hook target，因此只提供 MCP，不自动采集事件。Codex 桌面版需核实当前版本是否暴露本机 Codex MCP/hooks 配置。免费本地方案下，ChatGPT 网页版通过 Markdown 人工交接，不直接访问本机服务。

Windows 上游文档支持 WSL2 和原生 Windows；必须在启动 Agent 的同一环境安装和配置。路径排除不会过滤提示词中的任意文本。备份使用 `ai-memory --data-dir <data-dir> backup --to <archive-path>`；卸载客户端集成不会删除数据。确需删除时先停服务、核实备份和配置的数据目录。各平台默认数据路径及 Docker 备份命令见 [Windows 指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md)、[marker-file 参考](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md) 与[安装指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md)。

### 3.10 高风险操作分级处理

以下情况按风险分级说明影响；只有标为需授权或用户要求时才暂停等待，不以文件数量单独触发确认：
- [ ] 1. **构建配置变更**（`.pro` / `CMakeLists.txt` / `package.json` / `Cargo.toml` / `pom.xml`）
- [ ] 2. **引入新第三方依赖**
- [ ] 3. **修改核心全局公共数据结构/头文件**（如 `public_struct.h`、`types.ts`）
- [ ] 4. **修改核心调度单例与全局公共接口**
- [ ] 5. **修改通信协议与报文契约**（如 `protofile/*.json`、Protobuf 定义）
- [ ] 6. **修改软件授权（license）、加解密与认证安全代码**
- [ ] 7. **修改 `.gitignore` 或 CI/CD 构建发布流水线**
- [ ] 8. **高影响跨模块改动**（影响共享契约或需要广泛协调时评估影响并拆解验证；文件数量本身不触发授权）

---

## 四、 四大工具平台原生实践与技巧对照表

### 4.1 Google Antigravity CLI 与 IDE 命令和实践

CLI 通过 `agy` 启动，桌面 IDE 是另一个界面。官方文档说明两者支持文件规则；具体 Slash Command 和界面管理方式按各自表面区分。

| 斜杠命令 | 适用场景 | 最佳实践说明 |
|---|---|---|
| `/plan` | 复杂任务规划（$\ge 3$ 步） | 需求较复杂时，主动键入 `/plan`。Agent 会严格输出执行规划，并在假设推翻时自动中断重新评估。 |
| `/goal` | 长时间无人值守/端到端闭环 | 任务目标明确（如修复一套顽固单测、完成整套模块迁移）。Agent 会持续排障、验证直至彻底完结，中途不因琐碎问题反复打扰。 |
| `/grill-me` | 需求模糊时的质询对齐 | 发现用户给出的需求存在多处歧义或隐式边界时使用。Agent 会反向对用户进行结构化提问，彻底锁死需求细节。 |
| `/learn` | 经验固化与自我进化 | 当用户纠偏了某个方案或提示了踩坑点后执行。Agent 会提取教训并持久化沉淀到 `tasks/lessons.md`。 |
| `/schedule` | 定时执行与长效监控 | 设定一次性提醒或后台定时巡检（如定期监控构建日志、异步长任务轮询）。 |

---

### 4.2 Claude Code 专属命令与 PreToolUse 客户端钩子

Claude Code 的 `/memory` 可查看/管理其 Auto memory；这是 Claude 专属的机器本地记忆。本仓库的 PreToolUse 钩子只做匹配工具调用的安全检查，不采集记忆，也不是操作系统级拦截。

| 命令 / 语法 | 适用场景 | 最佳实践说明 |
|---|---|---|
| `/compact` | 长会话上下文急救 | 当会话轮次超过 15 轮、响应开始变慢或上下文接近上限时执行，自动进行上下文压缩与摘要清理。 |
| `/cost` | 实时 Token 与资费查看 | 随时查看当前会话消耗的 Input/Output Token 与累计成本，评估 Token 节流效果。 |
| `/review` | 代码评审门禁 | 针对当前工作区已修改的未提交变更（git diff）执行快速安全与质量审查。 |
| `/bug` | 错误报告反馈 | 遇到客户端环境异常时抓取错误堆栈并向上游报告。 |
| `@<path>` | 动态按需载入规则文件 | **关键特性**：在需要特定规则时，直接输入 `@.agents/rules/git-workflow.md`，实现渐进式披露。 |

#### Claude Code PreToolUse 客户端钩子 (`.claude/settings.json`)：
脚本可部署 Bash 与 Write|Edit 钩子。它们只在 Claude Code 客户端匹配工具调用前运行：
- 受保护分支 commit、force push 等部分模式会被拒绝；删除、重置、盲目暂存、敏感路径等检查包含非阻断警告；正则检查不完整，不能替代远端分支保护。
- 部分命令模式以非零退出码拒绝；删除、重置、盲目暂存、敏感路径等检查可能只是警告并放行；
- Hook 是客户端机制，正则匹配不完整，需结合 Git 服务端分支保护。

---

### 4.3 Codex ChatGPT、Codex CLI 与 GitHub Copilot

Codex CLI 文档说明其从 Codex home 和仓库到当前目录逐级发现 `AGENTS.md`。不要把 CLI 行为直接推断为 ChatGPT/桌面 Codex 行为；应按当前产品版本核对加载与全局设置。

| 命令 / 功能 | 适用场景 | 最佳实践说明 |
|---|---|---|
| `/hooks` | 生命周期钩子审查与信任 | **必做步骤**：按 Codex 当前版本的界面与信任提示检查 Hook 状态。Ponytail 是指导 Skill，不是 Hook；本部署脚本不会为 Codex 配置 Hook。 |
| `$comet` 或 `$comet-native` | 唤起工作流入口 | 在 Codex CLI 中通过 `$` 符号或自定义命令补全直接触发 Comet 编排流程。 |
| `/explain` | 代码解释 | 选中代码块后进行语法与架构解析。 |
| `/tests` | 针对当前选中代码生成单元测试 | 辅助生成 TDD 初始测试用例。 |
| `@workspace` | 工作区级代码检索 | 配合 VS Code / Copilot 检索跨文件上下文。 |

---

### 4.4 Zed IDE 专属实战与技巧

| 命令 / 交互 | 适用场景 | 最佳实践说明 |
|---|---|---|
| 复用 `AGENTS.md` | 规则内容可复用 | 本脚本不创建 Zed 专属桥接；请核对所用 Zed 版本的规则发现方式。 |
| `Ctrl+Enter` (或 `Cmd+Enter`) | 内联 AI 代码生成与重构 (Inline Assist) | 选中代码或空行唤起内联辅助，提示词中可直接追加 `遵循 ponytail 极简原则`，Zed 会直接生成高可读性 Diff 供快捷确认 (`Tab` 接受)。 |
| Assistant Panel (`Ctrl+?` / `Cmd+?`) | 右侧全功能长对话与架构推演 | 相当于多轮交互控制台，支持 `/clear`、引用文件、以及多步任务规划。 |
| Git 终端集成 | 临时分支流转与安全提交 | 配合 Zed 内置终端，严格遵循 `git checkout -b` 临时分支模式，绝不直改 master。 |

---

## 五、 端到端研发全流程实战演示（以一个典型需求为例）

假设当前项目为 Python/TypeScript 混合系统，用户提出需求：
> **“给后台管理系统的导出功能加一个按时间范围过滤的 CSV 导出接口。”**

### 完整执行轨迹：

```text
Step 1: 会话启动与断点感知 (Session Start)
  ├─ 文件存在且与任务相关时，查阅 PROJECT_CONTEXT.md 与 SESSION_STATE.md，并核验影响当前工作的事实。
  ├─ 检阅 tasks/lessons.md 与 tasks/todo.md（若存在）。
  └─ 确认当前位于干净分支，通过 git checkout -b feature/order-csv-export 切入临时分支。

Step 2: 评估路径与需求立项 (Comet + OpenSpec SDD)
  ├─ 唤醒 /comet 为订单模块新增按日期范围批量导出 CSV 接口。
  ├─ 自动生成变更目录：docs/openspec/changes/add-csv-export/
  ├─ 生成 proposal.md 与 specs/ 契约（说明增加 GET /api/v1/orders/export-csv 接口及时间参数校验）。
  └─ 停顿确认点：向人类出具简要契约，人类输入确认：“OK，继续”。

Step 3: 可选语义检索（CodeGraph MCP 已配置时）
  ├─ 严禁：盲目运行 grep -rn "export" .
  └─ 若 CodeGraph MCP 已配置，通过 MCP 查询；否则使用限定范围的代码搜索
      └─ 精确获得：路由挂载点 router.py、数据查询层 order_repo.py 及类型定义 types.ts。

Step 4: 测试先导 (Superpowers + TDD)
  ├─ 在 tests/test_export.py 中编写失败用例：
  │   - 正常时间区间导出用例
  │   - 结束时间小于开始时间的 400 校验用例
  └─ 执行快速单测：pytest tests/test_export.py -q
      └─ 预期结果：FAILED（红灯，成功捕获到了未实现的契约）。

Step 5: 极简实现 (Ponytail 懒人阶梯)
  ├─ 评估：使用 Python 标准库 `csv` 与 `datetime`，拒绝引入庞大的第三方导出插件库。
  ├─ 改动代码：仅在 order_repo.py 增加区间过滤条件，在 router.py 实现精简路由。
  └─ 架构守卫：确认未触碰 8 大高危操作，无底层循环依赖。

Step 6: 执行验证与输出控制 (RTK 已配置时可改写支持的命令)
  ├─ 运行针对性单测：pytest tests/test_export.py -q
  │   └─ 结果：PASSED（绿灯，2 passed in 0.3s）。
  └─ 运行全局回归（仅限关联模块）：npm test -- packages/order --reporter=dot

Step 7: 交付、安全提交与选择性记忆收尾 (Session Finish)
  ├─ 输出交付内容：去废话直出 Diff 概览与测试通过的真实输出片段。
  ├─ 安全暂存与提交：git add tests/test_export.py api/router.py repo/order_repo.py
  │   └─ 执行提交：git commit -m "feat(export): add date-range CSV export"
  ├─ 远端推送停顿：向人类出具合入命令，未经授权绝不擅自 push。
  ├─ 选择性记忆收尾：
  │   ├─ 有意义的任务断点更新 SESSION_STATE.md，并记录真实验证结果与未完成事项。
  │   └─ 仅在长期项目事实改变时更新 PROJECT_CONTEXT.md；无实质变化时不写空记录。
  ├─ 会话收尾：更新 tasks/todo.md 打勾状态。
  └─ Comet 自动将本次 Delta Spec 合并至主文档并归档。
```

---

## 六、 日常健康诊断与常见避坑指南

### 1. 踩坑点：安装了插件或钩子，但并没有生效？
- **Codex 平台**：Codex 拥有严格的信任门禁。安装任何带 Hook 的插件后，必须在终端执行一次 `/hooks`，确认状态为 `trusted`；
- **Claude Code 平台**：检查 `.claude/settings.json` 是否已由部署脚本正确生成，确保 PreToolUse 钩子已加载；
- **Antigravity IDE**：确认工作区根目录下存在 `.agents/rules/` 与 `.agents/skills/`。

### 2. 踩坑点：Windows 下 PowerShell 提示乱码或解析报错？
- 我们提供的 `deploy-agents.ps1` 内置 UTF-8 兼容保护，确保在 Windows PowerShell 5.1/7.x 下均能稳定解析中文字符。如果自己编写扩展脚本，务必保存为 UTF-8 编码。

### 3. 踩坑点：多 Agent 协作导致 Token 迅速耗尽？
- 谨记 Token 二次方成本模型：常规单步编码任务**坚决采用单 Agent 模式**；
- 仅在遇到**超长第三方 PDF/Docx 研读**、或者**跨模块并行扫描**时，才允许临时启用子代理（Subagent）做独立数据抽取，抽取完毕后将精简摘要交回主会话。

### 4. 每日自检三板斧：
```bash
# 按当前 Comet 版本文档检查项目工作流配置
# 仅在与当前任务相关时查阅项目经验
cat tasks/lessons.md
```

### 5. 跨工具部署与参考文档索引：
- 一键自动化部署脚本：
  - Windows：[`deploy-agents.ps1`](deploy-agents.ps1)
  - Linux/macOS：[`deploy-agents.sh`](deploy-agents.sh)
- 跨工具部署与配置专著：
  - 👉 [`多工具部署配置指南.md`](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md)
- 规则中枢文件：
  - 全局宪法：[`Global AGENTS.md`](Global%20AGENTS.md)
  - 项目枢纽：[`Project AGENTS.md`](Project%20AGENTS.md)
  - 目录补丁：[`Directory AGENTS.md`](Directory%20AGENTS.md)
