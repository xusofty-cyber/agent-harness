# Skills 使用指南

> **Language / 语言**: [English](Skills%20Usage%20Guide.md) | **简体中文** | [繁體中文](Skills%20Usage%20Guide.zh-tw.md) | [Français](Skills%20Usage%20Guide.fr.md) | [Deutsch](Skills%20Usage%20Guide.de.md)

42 个内置 skill 在实际中如何工作：哪些自动触发、哪些需要显式调用，以及每个的使用时机。

## Skill 触发机制

Claude Code 通过两种方式决定加载 skill：

| 模式 | 方式 | 示例 |
|---|---|---|
| **自动 (Auto)** | Claude 读取 skill 的 `description`，当你的请求匹配时自动调用 | 你说"修这个 bug" → `systematic-debugging` 自动加载 |
| **显式 (Explicit)** | 你输入斜杠命令或直接点名 | 你输入 `/comet` 或说"用 comet 处理这个任务" |
| **混合 (Hybrid)** | 两种都行——上下文匹配时自动触发，也可以直接调用 | 你说"review 这个 PR" → `open-code-review` 加载；或直接输入 `/open-code-review` |

**关键：** 自动触发依赖每个 skill 的 `SKILL.md` 中的 `description` 字段。
如果 Claude 没按预期加载某个 skill，直接点名即可。

## Skill 分类速查

### 1. 工作流与流程控制

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `comet` | 显式 | `/comet` | 版本化工作流状态机（阶段、门禁、归档）。需要安装 Comet CLI 且项目中有 `.comet/config.yaml`。 | 项目使用 Comet 做分阶段任务时。每个项目先跑一次 `/comet init` 初始化，之后用 `/comet` 进入工作流模式。没装 CLI 时 skill 会说明限制并回退到普通流程。 |
| `openspec-new-change` | 自动 | — | 启动新的 OpenSpec 变更（规格驱动开发）。 | 开始需要先写规格的功能/修复时。说"use openspec"或直接描述功能。 |
| `openspec-propose` | 自动 | — | 一步生成全部 OpenSpec 制品。 | 想要快速出规格草稿，跳过完整探索周期。 |
| `openspec-explore` | 混合 | — | 探索想法的思考伙伴模式。 | 需求模糊时。说"用 openspec 探索一下"。 |
| `openspec-apply-change` | 自动 | — | 按已有 OpenSpec 变更实施任务。 | 规格通过后："implement the openspec change"。 |
| `openspec-continue-change` | 自动 | — | 为进行中的变更创建下一个制品。 | 恢复 OpenSpec 工作时："continue the openspec change"。 |
| `openspec-update-change` | 混合 | — | 修订已有 OpenSpec 制品。 | 实施中途需要改规格。 |
| `openspec-verify-change` | 自动 | — | 验证实现与规格制品一致。 | 收尾前："verify against the openspec"。 |
| `openspec-sync-specs` | 自动 | — | 把增量规格同步回主规格。 | 变更完成合并后。 |
| `openspec-archive-change` | 自动 | — | 归档已完成的变更。 | 合并后的最终清理。 |
| `openspec-bulk-archive-change` | 自动 | — | 批量归档多个已完成变更。 | 批量清理。 |
| `openspec-ff-change` | 自动 | — | 快进跳过制品创建。 | 想跳过仪式感、直接开干。 |
| `openspec-onboard` | 混合 | — | OpenSpec 工作流引导。 | 第一次用："onboard me to openspec"。 |
| `living-documentation` | 混合 | — | 维护规格/架构/参考/指南，带追溯关系。 | 持续。文档任务自动激活；说"update living docs"强制触发。 |

### 2. 代码质量与评审

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `requesting-code-review` | 自动 | — | 决定**何时**需要评审（时机门禁）。 | 完成重要工作时自动触发。 |
| `open-code-review` | 自动 | — | 确定性评审**方法**（文件选择、规则匹配、行级发现）。 | Diff/PR 时自动触发。显式："用 open-code-review 评审这个 diff"。 |
| `receiving-code-review` | 自动 | — | 处理收到的评审意见。 | 粘贴评审意见时自动分诊。 |
| `systematic-debugging` | 自动 | — | 结构化调试：复现→隔离→假设→修复→验证。 | 任何 bug、测试失败、异常行为。在你提修复方案之前触发。 |
| `test-driven-development` | 自动 | — | 强制红-绿-重构循环。 | 实现功能/修 bug 时。先写测试。 |
| `verification-before-completion` | 自动 | — | 完成前检查清单：跑测试、验证断言。 | 说"做完了"之前——强制用证据说话。 |

### 3. 规划与设计

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `brainstorming` | 自动 | — | 在实现前探索意图、需求和设计。**创造性工作前必须用。** | 新功能、组件、行为变更。如果 Claude 直接写代码，说"先 brainstorm"。 |
| `writing-plans` | 自动 | — | 从规格生成结构化实施计划。 | 多步骤任务。有需求但没计划时触发。 |
| `executing-plans` | 自动 | — | 按计划执行。 | 计划通过后："execute the plan"。 |
| `option-review` | 自动 | — | 对比 2+ 可行方案，输出决策矩阵。 | 纠结时："A 还是 B 好？" |
| `dispatching-parallel-agents` | 自动 | — | 把独立任务拆给并行 subagent。 | 2+ 独立任务。说"并行做"。 |
| `subagent-driven-development` | 自动 | — | 通过 subagent 编排实施。 | 大型计划的独立组件。 |
| `using-git-worktrees` | 自动 | — | 用 git worktree 隔离功能开发。 | 需要与当前分支隔离的工作。 |
| `finishing-a-development-branch` | 自动 | — | 决定集成策略（merge/rebase/squash）。 | 实现完成、测试通过后。 |

### 4. 记忆与上下文

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `cross-tool-memory` | 自动 | — | 跨工具加载/保存持久项目记忆。ai-memory MCP 不可用时回退到 `PROJECT_CONTEXT.md` / `SESSION_STATE.md`。 | 继续之前的工作时。自动加载相关上下文；说"记住这个"显式保存。详见下方[项目记忆设置](#项目记忆设置)。 |
| `using-superpowers` | 自动 | — | 会话开始时建立 skill 发现协议。 | 会话开始自动触发。确保 Claude 回复前先检查可用 skill。 |

### 5. 开发工具

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `codegraph` | 自动 | — | 通过 CodeGraph MCP 做语义代码探索。需要安装 CodeGraph CLI。 | "X 在哪被用了" / "Y 的调用者有哪些"。没装 CLI 时回退到 grep。 |
| `rtk` | 自动 | — | Rust Token Killer：把冗长终端输出改写成简洁版。需要 RTK CLI。 | 自动压缩 noisy 输出。说"disable rtk"看原始输出。 |
| `docx` | 混合 | — | 创建/读取/编辑 Word 文档。 | "生成 .docx 报告" 或 "读这个 Word 文件"。 |
| `pdf` | 混合 | — | 读取/提取 PDF 文本/表格。 | "总结这个 PDF" 或 "提取表格"。 |
| `caveman` | 混合 | — | 超压缩输出模式（省 token）。 | "简洁点" / "caveman mode"。分级：lite、full、ultra。 |
| `ponytail` | 混合 | — | 强制最简可用方案（反过度设计）。 | "保持简单" / Claude 过度设计时。 |

### 6. 元技能

| Skill | 触发 | 命令 | 作用 | 使用时机 |
|---|---|---|---|---|
| `writing-skills` | 自动 | — | 指导 skill 的创建/编辑/验证。 | 在 `.agents/skills/` 下创建或修改 skill 时。 |
| `diagnosing-superpowers` | 自动 | — | 诊断 superpowers 工作流出错的原因。 | Claude 忽略计划、重复劳动、表现异常时。说"诊断哪里出问题了"。 |

## 项目记忆设置

### `PROJECT_CONTEXT.md` 和 `SESSION_STATE.md`

这是 ai-memory MCP 服务不可用时的文件回退方案。
`cross-tool-memory` skill 会自动读取它们。在执行 `deploy-agents.sh / .ps1` 或 `run-pipeline.sh / .ps1`（及快捷入口 `pipeline.sh / .ps1`）时，若目标项目缺少这两个文件，脚本会**自动从模板初始化创建**。亦可在任何时候通过问答或下方模板手动初始化。

**何时创建：**
- `PROJECT_CONTEXT.md`：每个项目一次，架构稳定后创建。只在持久事实变化时更新（技术栈、约束、关键决策）。
- `SESSION_STATE.md`：每次重要工作会话结束时，或交接时更新。记录完成的工作、验证证据、下一步。

**如何创建初始版本：**

直接问 Claude：
```text
按 cross-tool-memory skill 的格式，为这个项目创建 PROJECT_CONTEXT.md。
```

或复制以下模板：

#### `PROJECT_CONTEXT.md` 模板

```markdown
# PROJECT_CONTEXT.md

> 持久项目事实。只在架构、约束或确认决策变化时更新。
> 会话级状态放 SESSION_STATE.md，不要放这里。

## 技术栈
- 语言/框架：
- 构建：
- 测试：

## 架构
- （关键组件及职责）

## 约束
- （不可协商的技术或政策约束）

## 关键决策
- YYYY-MM-DD：（决策及理由）
```

#### `SESSION_STATE.md` 模板

```markdown
# SESSION_STATE.md

> 当前检查点。在有意义的任务边界更新。
> 删除过时项，保持可扫读。

## 最后更新
- YYYY-MM-DD：（本次会话简述）

## 已完成
- （做了什么，附验证证据）

## 进行中
- （正在做什么）

## 下一步
- （还剩什么，按优先级）

## 开放风险 / 问题
- （未解决的问题或待决策事项）
```

**放哪里：** 项目根目录。`cross-tool-memory` skill 会在根目录找它们。

**目录作用域：** 不要创建按目录的记忆文件。项目事实放根目录文件；
目录级 `AGENTS.md` 只放本地边界和约束。
