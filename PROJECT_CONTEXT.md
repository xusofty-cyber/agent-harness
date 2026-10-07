# PROJECT_CONTEXT.md — 项目全景与长期事实

> 本文件是便于代理快速定位的项目摘要，不替代源代码、官方文档或用户当前指令。事实冲突时先核验当前仓库。

## 项目定位

本仓库维护面向多种 AI 编码工具的规则模板、技能与辅助部署脚本，目标是让通用规范可复用，同时保留各宿主工具的差异。它不是 OpenClaw 产品仓库；当前内容不支持关于 Go/Node/Electron 架构、硬件封签、Nuitka 或 AST 混淆流水线的旧描述。

## 主要内容

- `Global AGENTS.md`、`Project AGENTS.md`、`Directory AGENTS.md`：全局、项目与目录层级的规则模板。
- `.agents/rules/`、`.agents/skills/`：按需加载的规则与技能资料。
- `deploy-agents.ps1`、`deploy-agents.sh`：将模板部署到项目或受支持的用户级入口；部署文件不等于宿主已加载文件。
- `.claude/settings.json` 等工具配置及中英文指南：说明当前适配方式、边界和部署流程。Claude Code PreToolUse 钩子属于客户端工具调用控制，不是操作系统级拦截器或长期记忆系统。
- `PROJECT_CONTEXT.md`、`SESSION_STATE.md`、可选 `tasks/lessons.md`：按需读取的项目摘要、短期断点与经验记录。

## 规则与记忆治理

- 共享全局模板只放跨项目稳定规则，不放个人偏好、项目专属事实或秘密。
- 项目记忆应精简、可核验并及时清理过期状态；当前用户指令、代码与可复现证据优先于摘要。
- 有意义的任务收尾更新 `SESSION_STATE.md`；只有确认的长期架构、约束或决策变化时才更新本文件。无实质变化时无需写空记录。
- 本仓库只选择 ai-memory 作为可选跨工具长期记忆后端；它不属于普通部署依赖，默认本地工作流不需要 LLM、embedding provider 或 API Key。显式加入通过被 Git 忽略的项目 `.ai-memory.toml` 和上游合并式 CLI 完成。能力边界与启用方式见双语部署/实战指南及 `.agents/skills/cross-tool-memory/SKILL.md`。

## 工具适配边界

Codex CLI、Codex 桌面产品、Claude Code、Antigravity CLI 与 IDE 对规则文件和记忆的加载方式各不相同。ai-memory 上游支持 Claude Code、Codex、Antigravity CLI 的 MCP/hooks；Antigravity IDE 采用 MCP 手动配置；Codex 桌面端需核实当前版本能力；ChatGPT 网页在免费本地方案下使用人工 Markdown 交接。Windows 上游支持 WSL2 与原生两种模式，但必须在与 Agent 相同的运行环境安装/配置。指南应注明适用的具体表面，并链接官方文档；不得仅凭脚本写入文件就声称宿主会自动加载。Claude Code Auto memory 是独立的 Claude 专属机器本地功能，不等同于仓库共享记忆。

## 已确认的仓库约定

- 受保护分支规则、远端操作授权和精确暂存要求见 `Global AGENTS.md` 与项目规则；执行前检查实际仓库状态。
- Windows PowerShell 脚本需保留 UTF-8 BOM 以兼容 Windows PowerShell 5.1；修改后做语法/编码核验。
- 当前仓库没有经此摘要确认的产品版本编年史或 `main`、`lite-edition`、`standalone-app` 分支产品矩阵；需以 Git 与实际源码核验，不得沿用未经证实的历史陈述。
