# Agent 正确触发与常见问题排查指南 (FAQ & Troubleshooting)

> 本文档面向在目标项目中部署了 `agent-harness` 规范体系的开发者。旨在帮助您理解 Agent 技能调度心智模型，掌握精准唤醒各类专业技能（Skill）的方法，并避免因提示词模糊或语义偏差导致 Agent 陷入“纯文本角色扮演、盲目脑补或跳过关键工具”。

---

## 核心心智模型：Agent 是工具编排器，而非聊天拟态机

在传统对话中，若要求大模型“扮演多个专家团队”，模型会倾向于使用**角色扮演（Persona-based reasoning）**，在单次输出中自说自话地列出“架构专家说...、安全专家说...”；
但在部署了 `agent-harness` 的工程中，**Agent 的核心价值在于调用确定性工具与规范化技能**（如 `open-code-review` 确定性审查、`codegraph` 图谱索引、`systematic-debugging` 根因排查）。

要让 Agent 真正干活，关键在于：**将模糊的角色要求，转化为清晰的“操作目标 + 阶段意图 + 技能引用”**。

---

## 目录

- [第一部分：代码审查与审计相关 QA](#第一部分代码审查与审计相关-qa)
  - [Q1: 为什么让 Agent“全方位审查代码”，它却在文本脑补，没有调用 `open-code-review`？](#q1-为什么让-agent全方位审查代码它却在文本脑补没有调用-open-code-review)
  - [Q2: `requesting-code-review` 与 `open-code-review` 是什么关系？](#q2-requesting-code-review-与-open-code-review-是什么关系)
- [第二部分：工程流水线与 AI 记忆相关 QA](#第二部分工程流水线与-ai-记忆相关-qa)
  - [Q3: 为什么本地或 Docker 运行了 `ai-memory`，流水线还提示 `[↷ SKIP] 配置包含未替换占位符`？](#q3-为什么本地或-docker-运行了-ai-memory流水线还提示--skip-配置包含未替换占位符)
  - [Q4: 什么时候用 `run-pipeline.sh`，什么时候用 `deploy-agents.sh`？](#q4-什么时候用-run-pipelinesh什么时候用-deploy-agentssh)
- [第三部分：工作流编排与状态机相关 QA](#第三部分工作流编排与状态机相关-qa)
  - [Q5: 为什么输入了 `/comet`，Agent 没有像状态机一样推进任务？](#q5-为什么输入了-cometagent-没有像状态机一样推进任务)
  - [Q6: 如何防止 Agent 跳过需求设计直接乱改代码？](#q6-如何防止-agent-跳过需求设计直接乱改代码)
- [第四部分：开发防偷懒与证据门 QA](#第四部分开发防偷懒与证据门-qa)
  - [Q7: 怎么阻止 Agent 盲目瞎猜改代码，强制其执行科学调试？](#q7-怎么阻止-agent-盲目瞎猜改代码强制其执行科学调试)
  - [Q8: 如何强制让 Agent 走测试驱动开发（TDD）？](#q8-如何强制让-agent-走测试驱动开发tdd)
  - [Q9: 怎么防止 Agent 伪造测试结果声称“已全部修复”？](#q9-怎么防止-agent-伪造测试结果声称已全部修复)
- [第五部分：Git 安全操作与拦截 QA](#第五部分git-安全操作与拦截-qa)
  - [Q10: 为什么 Agent 尝试提交时会被 Hook 强行拦截并退出（exit 2）？](#q10-为什么-agent-尝试提交时会被-hook-强行拦截并退出exit-2)
- [附录：高频场景精准 Prompt 模板速查](#附录高频场景精准-prompt-模板速查)

---

## 第一部分：代码审查与审计相关 QA

### Q1: 为什么让 Agent“全方位审查代码”，它却在文本脑补，没有调用 `open-code-review`？

#### 现象
开发者对 Agent 说：
> ❌ *“请再次用多个专家团队对整个 service_tw_fault_location 项目的代码进行全方位无死角的分析评审！”*

Agent 开始在回复中输出长篇大论（“【架构专家】认为... 【安全专家】指出...”），但没有任何工具调用、也没有执行任何审查脚本。

#### 根因剖析
1. **技能设计边界错配**：
   - `open-code-review` 的本质是 **Git Diff / 增量变更集（Commit / PR / 分支差异）的确定性审查工具**；
   - 它的核心算法依赖 `ocr delegate preview`、`scripts/group-diff.py` 或 `git diff` 进行文件分组与**行号精准锚定**。它天生不是用来“无差别把上百个存量文件一次性丢给 LLM 通读”的，否则会严重破坏 Token 节流纪律；
   - 当用户要求审查“整个项目”，Agent 的意图路由器会判定全量存量审查与 Diff 审查不匹配。
2. **提示词触发角色扮演**：
   - “多个专家团队”属于典型的角色扮演提示词（Persona Prompting），大模型会直接拟态专家口吻输出文本，从而抑制了工具调度逻辑。

#### 正确做法

- **场景 A：审查当前分支的代码改动（使用 `open-code-review`）**
  > ✔ *“请调用 `open-code-review` 技能，对我当前分支相较于 `main` 分支的代码变更（Diff）进行严格的规则审查与行级问题报告。”*

- **场景 B：对大型项目全仓代码进行宏观架构与质量体检**
  全库分析不能走单次 Diff 审查，应当采用 **图谱索引 + 子代理分工**：
  > ✔ *“请首先使用 `codegraph` 技能索引并梳理本项目模块调用链与依赖边界；接着使用 `dispatching-parallel-agents` 技能派发两个独立子代理：一个专注排查认证与敏感数据安全，另一个专注核心计算模块的代码质量与异味。”*

---

### Q2: `requesting-code-review` 与 `open-code-review` 是什么关系？

#### 核心区别
- **`requesting-code-review`（决定“何时”审）**：
  在子任务实施完成、重大功能落地或准备合入分支前触发。它的职责是派发一个具有**独立隔离上下文**的 Reviewer Subagent，防止被主会话的历史思考过程带偏；
- **`open-code-review`（决定“怎么”审）**：
  Reviewer Subagent 启动后，具体使用哪种工程化手段审代码——通过规则优先（Rule-first）、行级锚定（Line-anchored）和文件分组进行确定性判定。

---

## 第二部分：工程流水线与 AI 记忆相关 QA

### Q3: 为什么本地或 Docker 运行了 `ai-memory`，流水线还提示 `[↷ SKIP] 配置包含未替换占位符`？

#### 现象
运行 `./run-pipeline.sh` 或 `.un-pipeline.ps1` 时，流水线汇总显示：
```text
[↷ SKIP]  AI-Memory 记忆服务 (setup-ai-memory) : 配置包含未替换占位符
```
即使后台确实启动了 Docker 容器或本地 `ai-memory` 服务。

#### 根因剖析
流水线在准备接入 MCP（阶段 2）前，会强制检查目标项目根目录下的 `.ai-memory.toml`：
```bash
if [ -f "$toml_path" ] && ! grep -Eq 'replace-with-' "$toml_path"; then
    # 通过前置门禁，挂载 MCP 配置
fi
```
若文件中仍然保留默认模板字符串：
```toml
workspace = "replace-with-workspace-name"
project = "replace-with-project-name"
```
由于没有定义项目命名空间，若强行接入，AI 工具在多会话读写记忆时会导致作用域串线。因此流水线主动跳过该阶段。

#### 修复方式
将目标项目根目录的 `.ai-memory.toml` 中的占位符修改为真实工作区与项目名：
```toml
workspace = "tpim_system"
project = "backend"
```
或执行单行替换：
```bash
sed -i 's/replace-with-workspace-name/my_workspace/; s/replace-with-project-name/my_project/' .ai-memory.toml
```

> **补充提示**：使用 Docker 启动时，必须确保暴露了端口映射 `-p 127.0.0.1:49374:49374`；若宿主机已通过本地二进制启动了 `ai-memory serve`，两者会冲突，保留其中一种即可。

---

### Q4: 什么时候用 `run-pipeline.sh`，什么时候用 `deploy-agents.sh`？

- **`deploy-agents.sh`（一键脚手架与规则部署器）**：
  - **时机**：新项目刚立项，或者需要更新全局 Agent 桥接配置与规则集；
  - **功能**：向目标项目部署 `.agents/`、配置 12 款 Agent 桥接、生成初始记忆文件。
- **`run-pipeline.sh`（全生命周期工程流水线）**：
  - **时机**：日常工程自动化、CI 质检门禁或阶段性综合校验；
  - **功能**：全自动贯穿 4 大阶段：① 规则部署 → ② 跨工具 AI 记忆配置 → ③ 外部技能完整性锁定校验 → ④ 活体文档影响分析。

---

## 第三部分：工作流编排与状态机相关 QA

### Q5: 为什么输入了 `/comet`，Agent 没有像状态机一样推进任务？

#### 现象
在会话中输入了 `/comet`，但 Agent 依然像普通 LLM 一样自由漫游或询问“我能帮你做什么？”。

#### 根因剖析
- Comet 是基于 **显式工件流转与阶段约束** 的状态机（`Open -> Design -> Build -> Verify -> Archive`），它要求当前工作区已初始化 `.comet/config.yaml` 并有明确的变更提案（Change）；
- 如果只是空泛地输入 `/comet`，Agent 无法猜测当前是要“开启新需求”、“进行技术方案设计”还是“验收归档”。

#### 正确操作链路
1. **启动并定义需求（Open 阶段）**：
   > ✔ *“/comet-open 帮我创建一个新需求：在告警服务中支持线路专属免打扰时间段配置。”*
2. **方案设计与技术评审（Design 阶段）**：
   > ✔ *“/comet-design 针对当前变更出具技术方案，对比三种实现选项并等待我确认。”*
3. **分步编码实施（Build 阶段）**：
   > ✔ *“/comet-build 按照已批准的技术设计，使用 TDD 模式开始编码。”*
4. **自动化验收与验证（Verify 阶段）**：
   > ✔ *“/comet-verify 运行全量测试并出具真实通过证据。”*
5. **交付与归档（Archive 阶段）**：
   > ✔ *“/comet-archive 整理本次变更，同步活体文档并归档当前 change。”*

---

### Q6: 如何防止 Agent 跳过需求设计直接乱改代码？

#### 解决方案
利用内置的 `brainstorming` 或 `openspec` 技能，明确建立“设计门禁”：
> ✔ *“在修改任何代码之前，必须先使用 `brainstorming` 技能澄清设计意图并出具设计概要，在我确认同意后才能编写实现代码。”*

---

## 第四部分：开发防偷懒与证据门 QA

### Q7: 怎么阻止 Agent 盲目瞎猜改代码，强制其执行科学调试？

#### 现象
测试报错时，Agent 在没有搞清楚原因的情况下，反复修改同一个文件的不同位置，连续几次都改不对。

#### 解决方案
显式唤醒 `systematic-debugging` 技能，封锁“创可贴修复”：
> ✔ *“测试失败了。严禁直接猜测修改代码！请严格使用 `systematic-debugging` 技能：① 先定位根因并在日志/堆栈中出示证据；② 提出并验证假设；③ 给出最小修复方案并重新验证。”*

---

### Q8: 如何强制让 Agent 走测试驱动开发（TDD）？

#### 解决方案
直接唤醒 `test-driven-development` 技能：
> ✔ *“请使用 `test-driven-development` 技能实现本功能。遵循红-绿-重构循环：先编写一个一定会失败的单测，运行它并出示失败输出；然后编写最小实现代码直至测试变绿。”*

---

### Q9: 怎么防止 Agent 伪造测试结果声称“已全部修复”？

#### 解决方案
激活 `verification-before-completion` 证据门禁：
> ✔ *“在声称任务完成之前，必须严格执行 `verification-before-completion` 技能：运行实际测试命令，并在回复中截取包含执行耗时和 PASS 状态的原始真实终端输出，未提供客观证据前不得结束任务。”*

---

## 第五部分：Git 安全操作与拦截 QA

### Q10: 为什么 Agent 尝试提交时会被 Hook 强行拦截并退出（exit 2）？

#### 现象
Agent 准备提交代码时，终端弹窗拦截：
```text
[Claude Hook Guard] BLOCKED: Direct commits to protected branch 'main' are forbidden!
```

#### 根因剖析
`agent-harness` 部署了客户端 PreToolUse 安全钩子（`.claude/hooks/guard.mjs`），执行跨项目 Git 钢铁纪律：
1. **受保护分支强隔离**：严禁直接在 `main`、`master`、`develop`、`release*` 等分支执行 commit；
2. **严禁破坏性指令**：永久拦截 `git push --force`、强制分支删除、`git reset --hard`；
3. **严禁盲目暂存**：拦截 `git add .`、`git add -A`，必须显式指定文件路径暂存。

#### 正确引导 Agent
> ✔ *“你当前处于受保护分支。请先检出一个以 `feat/` 或 `fix/` 开头的临时特性分支，使用显式路径暂存修改，并在验证通过后通过 PR 或 fast-forward 合并。”*

---

## 附录：高频场景精准 Prompt 模板速查

| 场景 | 推荐 Prompt 模板 |
|---|---|
| **增量代码审查** | `请调用 open-code-review 技能，对当前分支相对于 main 分支的 diff 进行行级规则审查与风险评估。` |
| **全库架构分析** | `请使用 codegraph 技能梳理整体调用拓扑与核心架构；结合 dispatching-parallel-agents 针对核心模块分流审查。` |
| **疑难缺陷排障** | `请使用 systematic-debugging 技能调查此问题，在确认根本原因并出具证据前，不要修改任何业务代码。` |
| **功能前置设计** | `在开始写代码前，请使用 brainstorming 技能，梳理 2-3 个可行性方案并生成权衡对比。` |
| **测试驱动编码** | `请严格遵循 test-driven-development 技能，先写失败测试，再给最小实现。` |
| **任务收尾验证** | `请按照 verification-before-completion 技能，在终端完整执行测试套件，并在回答中出示可复现的验证日志。` |
| **持久记忆保存** | `请使用 cross-tool-memory 技能，将本次会话的关键决策与验证断点同步固化到 SESSION_STATE.md 中。` |
