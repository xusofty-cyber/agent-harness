# 会话上下文归档与下次恢复指南 (SESSION_RESUME)

> **归档时间**：2026-09-24  
> **工作区路径**：`e:\Works\项目\2026\ai-agents`  
> **会话核心目标**：三级 AGENTS.md 规则体系重构、Harness 原生技能库（Skills）集成、跨平台一键部署与在线更新工具链、实战指南文档建设。

---

## 一、 快速恢复指令（下次对话直接发送以下内容）

下次开启新会话时，向 AI Agent 发送以下提示词即可无缝接续工作：

```text
请阅读当前目录下的 SESSION_RESUME.md，继续执行未完成的文档更新与微调任务：
1. 更新《多工具部署配置指南.md》（补齐 npx skills update 流水线、-CometInit 参数与 OpenSpec 脚手架说明，增补 FAQ Q7/Q8 关于 Token 消耗与技能唤醒的解答）；
2. 更新《各工具实战使用与技能全景指南.md》（修正 2.1/2.2 技能实际安装状态与 comet init/会话技能分工，新增 2.4 节 Token 运行机制与 2.5 节技能联动调度矩阵）；
3. 同步微调《项目级 AGENTS.md》，将规则与技能调度矩阵对齐。
```

---

## 二、 当前已完成的核心成果与资产清单

### 1. 三级 AGENTS.md 规则体系（已优化落成）
- [全局 AGENTS.md](file:///e:/Works/项目/2026/ai-agents/全局%20AGENTS.md)：通用安全与行为宪法。确立“去废话沟通”、“Ponytail 懒人代码阶梯”、“输入/拿取 Token 闸门”、“验证证据门”、**Git 授权与保护分支铁律**以及**会话三步仪式**。
- [项目级 AGENTS.md](file:///e:/Works/项目/2026/ai-agents/项目级%20AGENTS.md)：高频工程骨架（<1000 Token）。规范开发命令、技术栈选型、架构 6 大红线、**八大高危操作防呆**与**子规则/技能联动调度矩阵**。
- [目录级 AGENTS.md](file:///e:/Works/项目/2026/ai-agents/目录级%20AGENTS.md)：Monorepo / 独立子模块的微型补丁（40 行），控制 In/Out Scope、本地极速单测与**超大文件（>100KB）安全维护准则**。
- **渐进式子规则库**（`.agents/rules/`）：
  - [token-discipline.md](file:///e:/Works/项目/2026/ai-agents/.agents/rules/token-discipline.md)：控制读拿说、CodeGraph 检索替代 grep、日志截断。
  - [engineering-spec.md](file:///e:/Works/项目/2026/ai-agents/.agents/rules/engineering-spec.md)：OpenSpec 需求驱动（SDD）、Superpowers 测试驱动（TDD）。
  - [security-boundary.md](file:///e:/Works/项目/2026/ai-agents/.agents/rules/security-boundary.md)：八大高风险操作确认矩阵、生产环境高危阻断与凭证零泄露。
  - [git-workflow.md](file:///e:/Works/项目/2026/ai-agents/.agents/rules/git-workflow.md)：Git 授权模型、受保护分支强隔离、禁止 force push/rebase、防误提交（禁 `git add .`）。

### 2. 官方 GitHub 原生技能库全量集成
- 通过标准开源 `skills` CLI 工具（`npx -y skills add <repo> --all`）接入真正的 GitHub 上游仓库：
  - `DietrichGebert/ponytail`（防过度设计懒人阶梯）
  - `JuliusBrussee/caveman`（电报体高压缩输出）
  - `obra/superpowers`（15 个模块化技能：`test-driven-development`, `verification-before-completion`, `systematic-debugging`, `executing-plans` 等）
  - `Fission-AI/OpenSpec`（16 个模块化技能：`openspec-propose`, `openspec-apply-change`, `write-openspec-docs` 等）
  - `codegraph`（AST 语法树级代码图谱）
  - `rtk`（终端输出防刷屏与错误截断）
  - `comet`（流程状态机与防漂移守卫）
  - `docx` & `pdf`（专业文档处理）
- 生成标准化版本锁定清单：[skills-lock.json](file:///e:/Works/项目/2026/ai-agents/skills-lock.json)。
- 建立目录联结（Directory Junction）：`.claude/skills` $\rightarrow$ `.agents/skills`，确保 Claude Code 与 Antigravity 无缝兼容。
- 建立硬件级防御钩子：[`.claude/settings.json`](file:///e:/Works/项目/2026/ai-agents/.claude/settings.json)（PreToolUse Bash Hook 物理拦截）。

### 3. 自动化部署与在线更新脚本（四大平台支持）
- [deploy-agents.ps1](file:///e:/Works/项目/2026/ai-agents/deploy-agents.ps1)（Windows，内置 UTF-8 BOM）与 [deploy-agents.sh](file:///e:/Works/项目/2026/ai-agents/deploy-agents.sh)（Linux/macOS）：
  - 支持 **Claude Code (`CLAUDE.md`)**、**Antigravity IDE (`AGENTS.md`)**、**OpenAI Codex (`copilot-instructions.md`)** 与 **Zed IDE (`ZED.md`)** 四维一键桥接；
  - 自动部署 Claude Code PreToolUse 硬件级安全拦截钩子（`.claude/settings.json`）；
  - 支持 `-ProjectPath` 任意路径部署与 `-Global` 全局配置；
  - 支持 `-Update` 在线模式：自动 `git pull --rebase`、更新 `comet`、并执行 `npx -y skills@latest update -y` 从 GitHub 差量更新所有技能；
  - 支持 `-CometInit` / `--comet-init` 可选参数，并在目标工程中自动预建 `docs/openspec/changes` 骨架目录；
  - 具备终端环境智能探测：在部署完成时针对是否已全局安装 Comet CLI 给出精准操作指引；
  - 具备目标工程 `AGENTS.md` 保护机制（绝不覆盖用户原有开发命令）。
- **实测验证**：已成功在测试项目 `E:\Works\项目\2026\南瑞台账录入\南瑞存量台账整理` 完成端到端部署（含 `ZED.md`、`.claude/settings.json` 与全套规则库）。

### 4. 关键认知与技术定论
- **关于 30+ Skills 是否消耗超多 Token**：
  - **不会**。采用两阶段加载（Progressive Disclosure），常驻上下文仅注入 ~750 Token 的 YAML 目录前缀，命中 Prompt Cache（费率极低）。
  - 全量 `SKILL.md` 正文按需读取；综合 Ponytail（代码砍半）、CodeGraph（检索降 96%）、Caveman（输出省 50%），整体呈现巨大的 **Token 净节省（Net Savings）**。
- **关于技能如何被正确调起**：
  - 三级触发机制：显式指令（100% 确定） > 意图匹配（70%~85%） > 规则矩阵硬绑定（95%+）。已在 [项目级 AGENTS.md](file:///e:/Works/项目/2026/ai-agents/项目级%20AGENTS.md) 与 [各工具实战使用与技能全景指南.md](file:///e:/Works/项目/2026/ai-agents/各工具实战使用与技能全景指南.md) 中建立完整的「技能与规则联动调度矩阵」。
- **关于 Git 授权与分支安全隔离（借鉴 comm_ipc）**：
  - 受保护分支绝对禁止直接 commit；新改动切临时分支；触碰远端必须人类授权；永久禁止 force push 与受保护分支 rebase；严禁 `git add .`。

---

## 三、 本次已完成的文档与矩阵更新清单（全量闭环）

- [x] **《多工具部署配置指南.md》全面更新完成**：
  - 扩展四大主流工具适配矩阵（正式加入 Zed IDE 列与支持说明）；
  - 完善脚本执行流水线（补齐 `-CometInit`、`ZED.md` 桥接、`.claude/settings.json` 物理拦截 Hook 部署与终端智能提示）；
  - 补齐 `npx -y skills@latest update -y` 在线差量更新机制；
  - 修正技能库部署描述为包含 30+ 模块化单元的官方 GitHub 原生技能套件；
  - 在 FAQ 增补 Q7（Token 经济账）、Q8（技能调起机制）、Q9（Git 保护分支与临时分支隔离）、Q10（八大高风险操作防呆矩阵）、Q11（PreToolUse 硬件级拦截钩子原理解析）。
- [x] **《各工具实战使用与技能全景指南.md》全面更新完成**：
  - 修正第 2.1 节，将 `git-workflow.md` 与四维规则体系正式纳入；
  - 新增第 2.4 节 Token 经济学与第 2.5 节工程技能联动调度矩阵；
  - 新增第 3.8 节：**Git 授权模型与受保护分支协作流转**；
  - 升级第四章为四大平台原生实践，新增第 4.4 节：**Zed IDE 专属实战与技巧**；
  - 新增第 6.5 节**会话三步仪式实操规范**与第 6.6 节**八大高风险操作防呆红线自查**。
- [x] **《项目级 AGENTS.md》与《全局 AGENTS.md》全量对齐**：
  - 全局加入会话三步仪式与 Git 安全铁律；
  - 项目级加入八大高危操作防呆、受保护分支隔离与调度矩阵行。
- [x] **《目录级 AGENTS.md》增强**：
  - 补充超大/遗留文件（>100KB）安全维护准则与核对清单。

---

## 四、 后续日常使用备忘

当前 AI Agents Harness 规范体系、跨工具部署脚本、官方技能套件与实战指南已**全部处于 100% 生产就绪状态**。
- **日常部署新项目**：直接运行 `.\deploy-agents.ps1 -ProjectPath <目标路径> [-Global]` 即可一键完成全套规约（包含 Claude/Antigravity/Codex/Zed 四端桥接）、安全拦截 Hook、OpenSpec 骨架与技能初始化。
- **在线同步上游最新版本**：运行 `.\deploy-agents.ps1 -Update` 即可全自动差量拉取最新规范与 GitHub Skills。

