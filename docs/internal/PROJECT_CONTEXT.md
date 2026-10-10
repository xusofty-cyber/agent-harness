# PROJECT_CONTEXT.md — 项目全景与长期事实

> 本文件是便于代理快速定位的项目摘要，不替代源代码、官方文档或用户当前指令。事实冲突时先核验当前仓库。

## 项目定位

本仓库（`agent-harness`）维护面向多种主流 AI 编码工具的通用规则模板、42 项跨工具原生技能、安全防护钩子与自动化部署流水线脚本，目标是在保持跨项目规范高度一致的同时，保留各宿主工具的独特能力与加载差异。它不是特定业务产品仓库，不包含未经当前源码证实的旧版架构或硬件封签流水线。

## 主要内容与核心模块

- **三层规则模板体系**：`Global AGENTS.md`、`Project AGENTS.md`、`Directory AGENTS.md`，支持多语言（EN, ZH, ZH-TW, FR, DE）及动态事实提取（`-Initialize` / `--initialize` 生成项目和指定目录的规则草稿）。
- **脚手架与双轨记忆模板**：`templates/PROJECT_CONTEXT.template.*.md` 与 `templates/SESSION_STATE.template.*.md`，覆盖 5 种语言，供流水线自动初始化下游项目记忆。
- **自动化工程流水线**：`run-pipeline.sh` / `.ps1` 及入口包装器 `pipeline.sh` / `.ps1`，串联规则部署、AI-Memory 记忆服务、外部技能同步锁定与活体文档质检。
- **多平台部署脚本**：`deploy-agents.sh` / `deploy-agents.ps1`，具备双脚本 100% 特性对齐（Parity）、交互式 TUI 步骤向导、安全备份与多工具桥接部署能力。
- **19 款 Agent 工具支持**：覆盖 12 款桥接配置（Claude Code, Antigravity 2.0/CLI/IDE, Codex, Copilot, Cursor, Zed, Gemini CLI, Qwen Code, CodeBuddy, Windsurf, Cline, Roo Code, Kiro, Continue.dev, Trae）与 7 款原生支持工具（OpenCode, Aider, Qoder, Pi 等）。
- **42 项原生技能与安全钩子**：`.agents/skills/` 存放按需加载技能，`.claude/hooks/guard.mjs` 提供客户端安全操作防护（拦截危险强制推送、分支误删等）。
- **多语言文档矩阵**：4 份核心指南（README、多工具部署配置指南、实战使用与技能全景指南、技能使用指南）全部提供中/英/繁/法/德 5 语种对齐。

## 规则与记忆治理规范

- **双轨记忆落地区域**：在目标项目中，`PROJECT_CONTEXT.md`（项目长期事实）与 `SESSION_STATE.md`（会话当前断点）**必须创建在项目根目录下**；`docs/internal/` 仅为 `agent-harness` 仓库自身存放 dogfood 开发笔记的专用目录，不随模板分发。
- **共享全局模板通用性**：只保留跨项目通用的工程底线与协作规范，严禁硬编码特定项目的架构、分支、业务事实或敏感凭证。
- **可选后端集成**：选择 `ai-memory` 作为可选跨工具长期记忆后端，默认本地工作流无需依赖 LLM/Embedding API Key；不可用时以根目录的 Markdown 文件作为回退方案。
- **选择性维护原则**：仅在有意义的任务收尾时更新 `SESSION_STATE.md`；仅在确认的架构、技术栈或关键决策变更时更新 `PROJECT_CONTEXT.md`。

## 已确认的仓库开发约定

- **Git 分支与远端规范**：保护分支（`main`）强隔离，必须在临时分支进行修改后合并；触碰远端操作（`git push`）需明确授权；严禁盲目 `git add <明确路径>` 之外的提交。
- **PowerShell 编码规范**：所有 `.ps1` 脚本必须保留 UTF-8 BOM (`utf-8-sig`)，以彻底兼容 Windows PowerShell 5.1 在不同系统区域代码页（如 CP936/GBK）下的解析准确性。
- **双脚本特性同步**：`deploy-agents.ps1` 与 `deploy-agents.sh`、`run-pipeline.ps1` 与 `run-pipeline.sh` 必须保持严格特性对称，并通过 `tests/repo_checks.py` 的 Parity 测试。
