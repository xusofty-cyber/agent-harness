# SESSION_STATE.md — 会话断点

> **最后更新**：2026-10-10
> **状态**：阶段性功能已全部合入 `main` 并推送到远端 `origin/main`（最新提交 `bf47199`）

## 当前工程基线与已完成项

1. **项目重命名与工程底座统一 (`agent-harness`)**：
   - 全仓库核心文档、配置及 CI 完成名称统合；仓库定位确立为通用 AI 编码规则模板、桥接与技能流水线工具。

2. **19 款主流 Agent 工具矩阵覆盖（12 桥接 + 7 原生）**：
   - 桥接工具（TUI 向导可勾选）：Claude Code、Antigravity 2.0/CLI/IDE、Codex、GitHub Copilot、Cursor、Zed、Gemini CLI、Qwen Code、CodeBuddy、Windsurf、Cline、Roo Code、Kiro、Continue.dev、Trae。
   - 原生读取支持：OpenCode、Aider、Qoder、Pi 等自动识别 `AGENTS.md` 无需额外桥接。

3. **全流程交互式向导与工程流水线 (`run-pipeline` / `pipeline`)**：
   - 实现 `run-pipeline.sh` / `.ps1` 及便捷入口 `pipeline.sh` / `.ps1`，串联规则部署、AI-Memory 服务、外部技能同步校验与活体文档分析 4 大阶段。
   - 所有脚本均支持 TUI 交互式选择向导（上下键移动、空格勾选、回车确认）及非交互命令行参数静默执行。

4. **项目长期事实与会话断点自动初始化 (`PROJECT_CONTEXT.md` / `SESSION_STATE.md`)**：
   - 建立了包含 5 种语言（EN, ZH, ZH-TW, FR, DE）的工业级模板矩阵 `templates/PROJECT_CONTEXT.template.*.md` 与 `templates/SESSION_STATE.template.*.md`。
   - 在流水线与部署脚本运行阶段，自动检测目标工程根目录，缺失时即刻从对应语言模板初始化，动态注入目标项目名称。

5. **多语言文档体系升级 (5 语种全量对齐)**：
   - 《README》、《多工具部署与配置指南》、《实战使用与技能全景指南》、《技能使用指南》全部提供 EN、ZH、ZH-TW、FR、DE 5 种语言版本，保持严格的二级标题数量一致性。

6. **Windows PowerShell 与编码兼容性修复**：
   - 所有 `.ps1` 脚本统一以带 BOM 的 UTF-8 (`utf-8-sig`) 保存，彻底消除 Windows PowerShell 5.1 在 GBK/CP936 代码页环境下的语法分析器解析错位问题。
   - `deploy-agents.ps1` 增加 `$npmCmd` 探测，优先调用 `npm.cmd`，避免 PowerShell 下 `& npm` 调用触发 Node.js 官方 `npm.ps1` 的入参切片截断 Bug（`Unknown command: "pm"`）。
   - `tools/doc-impact.py` 与技能端副本在 `subprocess.run` 中显式指定 `encoding="utf-8", errors="replace"`，彻底消除中文 Windows (CP936/GBK) 运行环境下的 `UnicodeDecodeError`。

7. **外部技能库同步与哈希锁定**：
   - 随流水线阶段 3 完成 11 项外部技能最新版本拉取，同步刷新 `skills-lock.json` 与 `.claude/settings.json` 工具权限。

8. **`engineering-docs` 原生技能与 `/comet` 工作流全链路打通**：
   - 引入并完善本地自研技能 `engineering-docs`（v0.1.0，31 种文档类型、15 个中英双语门禁模板），统一跨 AI Agent 工具在各阶段的输出格式。
   - 深度贯通 `/comet` 研发流转：Open (04/05/06) → Design (07/08/09/10) → Build (10/11/12) → Verify (13/14) → Archive (15)。
   - 强化 Frontmatter 铁律以保证 `doc-impact.py` 活体文档模块依赖追溯与门禁正常流转。
   - 同步更新 5 种语言的全部 README、Skills Usage Guide、Panorama Guide 及 `skills-lock.json`（原生技能数校准为 43 个）。
   - 完善 `.gitignore`，增加 `.comet/` 运行时目录与 `*.bak-*` 备份文件隔离，防止运行时软链接污染版本库。

## 验证证据与质量闸门

- `python3 tests/repo_checks.py`：**68 项检查全数 PASS**（包含跨脚本 Parity、文档结构对称性、doc-impact 副本逐字节同步校验等）。
- `node tests/hooks.test.mjs`：**16 项测试全数 PASS**（Claude Code PreToolUse Bash 安全卫士拦截测试）。
- `python3 tests/sync_skills_test.py`：**7 项测试全数 PASS**（技能自更新与哈希校验）。
- `python tools/doc-impact.py`：**正常识别并输出变更文件，无任何 UnicodeDecodeError 异常**。
- 本地实测通过：`npm.cmd` 与 `deploy-agents.ps1` 可顺利调起包安装。

## 现场约束与下一步事项

- **现场约束**：下游目标项目创建的双轨记忆文件必须严格放置于下游项目的根目录下；`docs/internal/` 仅为 `agent-harness` 仓库自身的 dogfood 实践，切勿混淆。
- **后续规划**：
  - 持续跟进各宿主 Agent 工具的最新规则加载机制并扩展桥接；
  - 关注 upstream CodeGraph 1.6.2+ 后续对 Windows platform `statInode` 导出修复。
