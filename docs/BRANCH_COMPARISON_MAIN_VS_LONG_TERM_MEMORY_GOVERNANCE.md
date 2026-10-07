# main 分支 vs long-term-memory-governance 分支功能对比与技术架构分析

> **对比基准**：
> - **基准分支**：`main` (commit `78e64a6`)
> - **特性分支**：`long-term-memory-governance` (commit `d210089`)
> - **分支关系**：`long-term-memory-governance` 基于 `main` 直接派生，超前 4 个 commit，无分叉冲突，变动文件 22 个 (+1036 / -319 行)。

---

## 一、 核心演进背景与核心结论

| 维度 | main 分支 | long-term-memory-governance 分支 | 核心影响与演进收益 |
|---|---|---|---|
| **核心定位** | 基于纯 Markdown 文件的通用 Agent 规则脚手架 | 增加了**跨工具长期记忆治理**、**解耦式状态维护**与**全平台部署安全网**的成熟工程框架 | 从“静态文件注入”升级为“可控长期上下文协作” |
| **记忆体系** | 静态双轨更新（强制双文件同步更新，存在遗留专有项目硬编码污染） | **解耦式双轨更新 + 可选接入本地零成本 ai-memory** | 消除虚假仪式与上下文污染，支持多 Agent 间决策与断点互通 |
| **部署与更新安全** | `-Global` 无条件覆盖已有全局规则；仅支持 Claude 与 Antigravity IDE | **安全保留优先**（`-Global` 仅初始化缺失，`-Update` 毫秒级备份后覆盖）；全矩阵覆盖 | 彻底消除误覆盖开发者既有全局配置的严重风险 |
| **工具生态支持** | Claude Code, Antigravity IDE（单一模式） | **Claude Code, Antigravity (2.0/CLI/IDE 统一双入口), Codex (CLI/App 全局支持)** | 覆盖业界主流三大 Agent 生态及其不同交互端（CLI / IDE / App） |
| **边界诚实度** | 存在绝对化断言，缺少网络/环境隔离防呆说明 | **明确各宿主真实限制（Honest Limits）**，防范假冒集成与安全漏洞 | 杜绝将无法连通的本地服务承诺给 ChatGPT 网页版，规避 Windows/WSL 路径混用 |

---

## 二、 详细功能与架构差异对比

### 2.1 长期记忆体系与会话治理（Memory Governance）

#### 1. 规约层解耦与防污染
- **main 分支**：
  - 在 `Global AGENTS.md` 中规定了“双轨状态更新铁律”，要求任何会话、新需求或 Bug 修复完成后，**必须同时**更新 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md`。
  - 在全局模板中错误地硬编码了 OpenClaw 专有项目的架构拓扑（Go 引导层、Node.js 调度核、Nuitka 编译、硬件 U 盘防伪封签等），导致向其它项目部署全局规则时发生严重的内容幻觉与上下文污染。
- **long-term-memory-governance 分支**：
  - **彻底清洗全局模板**：移除了所有特定项目的硬编码，恢复纯粹通用的研发规范。
  - **解耦式会话收尾**：
    - `SESSION_STATE.md`（短期工作台）：在有实质成果的任务边界维护，记录真实验证依据与下一步断点，定期清理过期现场信息；无实质改动禁止制造空更新。
    - `PROJECT_CONTEXT.md`（长期记忆）：**仅在长期架构、核心约束或技术决策发生变化时**才进行增量记录，日常小修复无需碰此文件。
  - **权威性与边界**：明确“记忆仅为导航辅助”，永远不得凌驾于当前用户明确指令、源码、配置文件及真实测试证据之上。

#### 2. 可选跨工具长期记忆引擎（ai-memory）
- **main 分支**：没有任何跨工具记忆机制，Claude Code、Codex 与 Antigravity 之间的上下文完全割裂。
- **long-term-memory-governance 分支**：
  - **选型与集成**：选定 [ai-memory](https://github.com/akitaonrails/ai-memory) 作为唯一可选后端（排除依赖云端或复杂本地模型的方案）。
  - **零成本与本地优先**：纯本地 Markdown 与 FTS（全文检索），**无需任何 LLM API Key 或 Embedding 模型**，开箱即用。
  - **显式加入机制（Opt-in）**：根目录提供 `.ai-memory.toml.example`，默认被 `.gitignore` 忽略。必须由开发者手动配置指定 workspace/project 后方可激活采集。
  - **隐私与脱敏防护**：在模板中预设 `ignore_paths` 排除敏感文件（`.env*`, `*.key`, `*.pem`, `**/secrets/**` 等），并在规约中严正声明“路径排除无法对 Prompt 正文脱敏，禁止在输入或记忆中存放凭据”。
  - **新增配套技能**：`.agents/skills/cross-tool-memory/SKILL.md`，定义了精准 Recall（召回特定决策而非无脑拉取全量历史）与 Retain（记录经检验的架构结论而非代码片段）的标准范式。

---

### 2.2 全局与项目部署流水线（Deployment Pipelines）

#### 1. 安全部署与配置保护机制
- **main 分支**：
  - 运行 `deploy-agents.ps1 -Global` 时，脚本会粗暴地直接覆盖 `~/.claude/CLAUDE.md` 与 `~/.gemini/AGENTS.md`（虽然生成了单次 `.bak`，但缺乏主动防护意识）。
- **long-term-memory-governance 分支**：
  - 引入了 `Sync-GlobalRule` (PowerShell) / `deploy_global_rule` (Bash) 核心逻辑：
    - **非更新模式（默认）**：若目标全局规则已存在，**自动保留现有规则，跳过写入**，绝不破坏用户既有配置。
    - **更新模式（`-Update` / `-u`）**：采用带毫秒级时间戳（`yyyyMMddHHmmssfff`）的多版本安全备份机制（`.bak.<timestamp>.<suffix>`），完成备份后方执行覆盖。

#### 2. 工具矩阵与生态扩展
- **main 分支**：仅处理 Claude Code 与 Antigravity IDE。
- **long-term-memory-governance 分支**：
  - **Codex 生态全覆盖**：
    - 支持 `$CODEX_HOME` 环境变量及默认路径 `~/.codex/`；
    - 具备智能检测机制：当发现用户配置了非空的 `AGENTS.override.md` 时，自动对准该当前生效的覆盖文件执行部署/更新。
  - **Antigravity 双入口兼容**：
    - 针对新版 Antigravity 2.0 / CLI / IDE 部署标准 `~/.gemini/AGENTS.md`；
    - 新增 `templates/antigravity-GEMINI.md`，在 `~/.gemini/GEMINI.md` 部署轻量级指向指针，完美兼顾只读取 GEMINI.md 的旧版 IDE 表面，杜绝重复冗余。

#### 3. 记忆专项配置脚本（`setup-ai-memory.ps1` / `.sh`）
- **main 分支**：无此脚本。
- **long-term-memory-governance 分支**：新增独立的配置脚手架，具备严格的执行前防御性检查：
  - **环境与二进制预检**：检查 `.ai-memory.toml` 是否已配置；检查本地是否已安装 `ai-memory` CLI（脚本绝不擅自下载或运行后台守护进程）。
  - **Windows PE 格式校验**：在 Windows 上严格校验 `ai-memory.exe` 的 MZ PE 二进制头，拦截假冒包装脚本或兼容模式，确保 allowlist 采集门控真实有效。
  - **宿主能力差异化配置**：
    - `claude-code`, `codex`, `antigravity-cli`：配置 MCP + 原生 allowlist 钩子 + 托管指令；
    - `antigravity`, `antigravity-ide`：清晰提示“MCP-only setup”，仅配置 MCP 与指令，不虚假声称 hook 自动采集。

---

### 2.3 规约文档与指南矩阵（Documentation & Guides）

#### 1. 宿主表面与诚实边界说明（Honest Limits）
- **main 分支**：
  - 工具归类较粗，将 Antigravity IDE、CLI 与 2.0 混为一谈；
  - 规则中存在僵化指标，例如“单次涉及 3 个以上文件即必须向人类申请授权”。
- **long-term-memory-governance 分支**：
  - **修正高危操作规则**：改为“影响共享契约或需要广泛协调的高影响跨模块改动；文件数量本身不触发授权”。
  - **界定四大宿主边界**：
    - **Claude Code**：阐明 PreToolUse 是安全拦截工具，与 ai-memory hooks 和原生 `/memory` 彼此独立。
    - **Antigravity**：拆解 CLI (`agy`)、桌面 IDE 与 2.0 的差异，提供官方共用 `mcp_config.json` 的接入方案。
    - **Codex**：区分 CLI 与 Desktop，不将 CLI 特性盲目套用到桌面版。
    - **ChatGPT 网页版**：明确告知免费本地 loopback 服务无法连接云端网页会话，只支持人工 Markdown 交接。
    - **Windows / WSL2**：强调 Agent 运行环境与 memory 安装环境必须一致，不可混用路径。

#### 2. 工程化规范资产沉淀
- **main 分支**：无相关的技术设计说明。
- **long-term-memory-governance 分支**：沉淀了完整的 OpenSpec / Superpowers 规划文档：
  - [`docs/superpowers/specs/2026-10-07-cross-tool-memory-governance-design.md`](docs/superpowers/specs/2026-10-07-cross-tool-memory-governance-design.md)
  - [`docs/superpowers/plans/2026-10-07-cross-tool-memory-governance.md`](docs/superpowers/plans/2026-10-07-cross-tool-memory-governance.md)
  - [`docs/superpowers/plans/2026-10-07-ai-memory-integration.md`](docs/superpowers/plans/2026-10-07-ai-memory-integration.md)

---

## 三、 代码与文件变动清单一览

```
 .agents/skills/cross-tool-memory/SKILL.md          |  25 ++++       # [新增] 跨工具记忆标准实践技能
 .ai-memory.toml.example                            |  16 ++         # [新增] 本地记忆项目声明模板
 .gitignore                                         |   3 +          # [修改] 忽略 .ai-memory.toml 等本地状态
 Directory AGENTS.md                                |   8 +          # [修改] 增加局部记忆边界与约束
 Global AGENTS.md                                   |  35 ++---      # [修改] 清洗专有业务污染，解耦双轨记忆
 Multi-Tool Deployment and Configuration Guide.md   | 100 ++++++++--  # [修改] 英文部署指南全量同步
 PROJECT_CONTEXT.md                                 |  63 +++-----   # [修改] 长期记忆剔除虚假架构陈述
 Project AGENTS.md                                  |  18 +--        # [修改] 项目级规约同步记忆与安全规则
 README.md                                          |  31 +++-       # [修改] 英文 README 增加能力矩阵
 README_zh.md                                       |  31 +++-       # [修改] 中文 README 增加能力矩阵
 SESSION_STATE.md                                   |  59 ++++----   # [修改] 会话状态准确切入当前治理任务
 Tools Practical Usage and Skills Panorama Guide.md |  85 ++++++-----# [修改] 英文实战指南全量同步
 deploy-agents.ps1                                  |  82 ++++++---- # [修改] 增加安全同步、Codex与Antigravity双入口
 deploy-agents.sh                                   |  85 ++++++++---# [修改] Bash 部署脚本对齐安全同步与生态矩阵
 docs/superpowers/plans/...                         | 281 +++++++++++ # [新增] 治理与集成规划文档
 docs/superpowers/specs/...                         |  95 ++++++++++++# [新增] 记忆治理架构设计规范
 setup-ai-memory.ps1                                |  69 +++++++++  # [新增] Windows 本地记忆初始化与预检脚本
 setup-ai-memory.sh                                 |  77 ++++++++++ # [新增] Linux/macOS 记忆初始化辅助脚本
 templates/antigravity-GEMINI.md                    |   5 +          # [新增] Antigravity 旧版 IDE 兼容指针模板
 各工具实战使用与技能全景指南.md                    |  94 ++++++-----# [修改] 中文实战指南全量同步
 多工具部署配置指南.md                              |  93 +++++++-----# [修改] 中文部署指南全量同步
```

---

## 四、 总结与合入建议

1. **兼容性**：`long-term-memory-governance` 分支完全向后兼容 `main` 分支既有工作流，且修正了原有脚本对全局规则盲目覆盖的隐患；
2. **纯粹性**：清洗了 `main` 分支遗留的 OpenClaw 硬编码污染，使模板真正成为标准通用的开发框架；
3. **扩展性**：补全了 Codex 全局支持和 Antigravity 2.0/IDE/CLI 双入口兼容，并为项目未来接入跨工具记忆奠定了本地安全、免 API Key 的坚实底座；
4. **建议**：建议将 `long-term-memory-governance` 分支合入 `main`（推荐使用 Fast-Forward 或标准 PR 合入）。
