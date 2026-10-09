# SESSION_STATE.md — 会话断点

> **最后更新**：2026-10-09
> **任务**：多语言 AGENTS 模板与部署语言选项、全景/部署核心文档多语言套件建设，以及文档启发描述清理

## 当前状态（待确认合并）

- **分支**：`feat/multilingual-agents-templates`（基于 `main` 检出，已完成 2 个本地提交 `3ef0a76` 与 `e78f2a7`）。
- **完成项**：
  - 三级 AGENTS 模板多语言版（EN / 繁中 / 法语 / 德语）就绪；部署脚本（`deploy-agents.sh` / `.ps1`）新增 `--lang` / `-Language` 支持及降级保护。
  - 三套核心文档多语言套件（`README`、`Multi-Tool Deployment and Configuration Guide`、`Tools Practical Usage and Skills Panorama Guide`）完整支持 EN、简中、繁中、法语、德语，全部通过 `##` 结构对称性自动化校验。
  - 彻底清理 `README_zh.md` 及全库中关于外部启发文章的描述与链接。
- **CI & 测试**：`python3 tests/repo_checks.py`、`node tests/hooks.test.mjs`、`python3 tests/sync_skills_test.py` 全数通过。
- **后续动作**：等待用户明确授权后，合入 `main` 并推送到远端仓库 `git@github.com:xusofty-cyber/agent-harness.git`。

## 历史记录（2026-10-08 前）

- **分支**：`long-term-memory-governance`，跟踪 `origin/long-term-memory-governance`。
- **本轮功能提交**：`c476978218f042155b6f89f5d129564c39e525fc`，已推送；`git ls-remote origin refs/heads/long-term-memory-governance` 返回相同 hash。
- **范围**：已完成 Antigravity 跨版本规则入口与 ai-memory 设置边界更新；保留工作区原有用户改动和未跟踪文件。
- **设计与计划**（已归档至 `docs/internal/superpowers/`）：`specs/2026-10-07-cross-tool-memory-governance-design.md`、`plans/2026-10-07-cross-tool-memory-governance.md`、`plans/2026-10-07-ai-memory-integration.md`。

## 本轮变更

- 将全局/项目/目录规则中的记忆策略改为按需读取、选择性更新、来源核验和隐私保护。
- 修复全局部署脚本会覆盖已有用户级 Claude/Antigravity 规则的问题；更新模式生成供人工审阅的旁置模板。
- 修订中英文部署与实战指南，区分各产品界面、规则加载与记忆能力；完成评估后仅选择 ai-memory 作为可选后端。
- 清理本文件与 `PROJECT_CONTEXT.md` 中无法由当前仓库证实的产品架构、硬件规则和分支/版本历史。
- 选定 ai-memory 作为唯一可选长期记忆后端；新增共享跨工具记忆 Skill、marker 示例和忽略规则、显式 PowerShell/Bash 安装辅助脚本，更新规范模板及中英文指南。
- 根据当前上游文档修正 Windows 支持边界：WSL2 与原生 Windows 均有文档化安装方式，必须在 Agent 实际运行的同一环境配置；Antigravity IDE 只写明 MCP，不宣称自动 hooks。
- 复核发现安装脚本此前会在提醒 fallback 风险前先安装 hooks；现已增加原生可执行文件格式与平台覆盖预检，不支持时在改动任何工具配置前退出，并同步中英文指南和实现计划。
- 按后续要求改为 `-g -u` 备份后覆盖已有全局规则，并增加 Codex home / `CODEX_HOME` 的 Codex 全局 AGENTS 部署；Codex 有非空 `AGENTS.override.md` 时更新当前生效文件。
- 核对 Antigravity 官方规则文档：Antigravity 2.0、CLI、IDE/Extensions 共用 `~/.gemini/AGENTS.md` 入口；CLI 专用 rules 目录另有说明。部署脚本与中英文文档统一为覆盖全部三类表面。
- 复核官方规则文档发现旧版 Antigravity IDE 仅列出 `~/.gemini/GEMINI.md`；部署脚本现在同时写入规范 `AGENTS.md` 与轻量兼容指针 `GEMINI.md`，避免重复复制整份规则。
- 扩展 `setup-ai-memory.ps1` / `.sh`：Antigravity 2.0 与 IDE 可选择 MCP-only 安装并同步项目指令；CLI 保持 MCP + allowlist hooks。上游没有 2.0/IDE 的第一方 ai-memory lifecycle-hook target，文档已明确此边界。
- 完善实战部署全流程：在 `README_zh.md`、`README.md`、《多工具部署配置指南.md》与《各工具实战使用与技能全景指南.md》中同步补充了从前置安装（含 Linux 一键 curl 原生下载）、Windows 终端环境变量强制刷新命令、`.ai-memory.toml` 标记初始化、脚本输出（`no-op` 幂等性与安全免责提示）解读，到 Linux/Windows 服务端启动命令（含 `ai-memory serve --transport http`、Linux nohup 与 systemd 用户级守护服务单元）以及验证指令的全量实操指南。

## 验证与后续

- 4 份核心文档修改已通过 `git diff --stat` 校验，内容结构中英对齐无遗漏。
- 本地 `ai-memory` 实测通过（Linux x86_64 环境）：
  - 二进制已软链接至 `~/.local/bin/ai-memory`（版本 2.6.0）。
  - 已生成本仓库 `.ai-memory.toml`（`default/agents-living`）。
  - 执行 `./setup-ai-memory.sh antigravity-ide` 完成 Antigravity IDE 的 MCP 配置（写入 `~/.gemini/config/mcp_config.json`）、项目 `AGENTS.md` 托管指令和 `.agents/skills/` 技能文件。
  - Systemd 用户服务 `~/.config/systemd/user/ai-memory.service` 已部署并激活（自启动监听 `127.0.0.1:49374`），通过 `curl` 验证 HTTP MCP 握手及工具调用，并通过 CLI 验证读写闭环。

## 已知现场约束

- `.claude/settings.json` 等既存本地工作区改动与未跟踪文件不属于本轮修改目标，必须保留；用户级工具配置当前仍为本地未提交状态。
- 当前工作区有用户本地工具配置；不要将其误作为本轮新建或已验证的仓库规范。
- 仓库内 `.ai-memory.toml` 为本地单机生效项（已在 `.gitignore` 中），不随提交共享。

## 2026-10-08 Ponytail 规范适配

- **改动**：只吸收适合本项目的实现简化原则；修订 Ponytail Skill 的适用范围、调用路径调查方式、用户范围边界和回答详略规则；同步 `.agents/rules/engineering-spec.md`、`Global AGENTS.md` 与本文件。
- **明确不引入**：不添加独立 Ponytail 插件/依赖，不复制上游适配器；保留当前跨工具共享 Skill 路径。
- **验证**：`git diff --check` 通过；旧的全响应强制、逐字 grep 和固定回答长度冲突措辞已清除；两个 `.agents` Markdown 文件保留 UTF-8 无 BOM 与 CRLF。未运行测试，变更仅涉及规范文档；Skill 的压力场景测试未执行，后续可在多 Agent 环境补测。

## 2026-10-08 AGENTS 初始化向导

- **改动**：PowerShell/Bash 部署脚本新增项目与目录规则初始化、事实候选提取、待确认清单、占位检查；已有规则不覆盖，输出生成文件供审阅。同步 Project 模板、中英文 README 与部署指南。
- **识别范围**：本地目录名、Git origin 和明确的 `origin/HEAD`、常见清单/锁文件、CI 路径；`package.json` 可选解析脚本及常见框架/存储依赖，并以“建议确认”标记。用途、维护者、职责与边界不作猜测。
- **验证**：PowerShell AST 与 Git Bash `-n` 语法检查通过；PowerShell/Bash 临时项目均完成初始化 smoke check，验证项目和目录字段、候选命令以及 `--Check` 对未确认字段返回失败；另确认 Bash 按 `package.json` 的 `packageManager` 生成 pnpm 安装/脚本建议。`git diff --check` 通过，临时验证目录已清理。未修改测试套件。
