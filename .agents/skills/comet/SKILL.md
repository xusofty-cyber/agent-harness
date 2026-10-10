---
name: comet
description: Use Comet when this project has it configured or the user explicitly requests it. Check the installed version and project configuration before following version-specific steps.
license: Apache-2.0
---

# Comet Workflow Integration (Comet 智能体研发流协同)

Comet 是面向软件工程的智能体工作流执行引擎与评估框架（`@rpamis/comet`）。
本技能作为宿主 Agent 接入 Comet 运行时的全功能协议指引，支持 **Native 模式（强模型目标驱动）** 与 **Classic 模式（阶段过程治理）**。

官方文档：<https://docs.comet.rpamis.com/> | 仓库：<https://github.com/rpamis/comet>

---

## 1. 核心模式选择（Native vs Classic）

| 模式 | 核心理念 | 适用模型与场景 | 流程阶段 | 产物位置 |
| :--- | :--- | :--- | :--- | :--- |
| **Native 模式** *(新项目默认推荐)* | **目标驱动（Goal/Evidence Loop）**：以 `brief.md` 与目标 Specs 固化需求，实现方式由模型 ReAct 自主规划，由独立只读 Verifier 严格验收 | 前沿强模型（Fable 5, GPT-5.6, Claude 3.7+）；节省 76.8% Token，轮次减少 57.4% | `Shape` $\to$ `Build` $\to$ `Verify` $\to$ `Archive` | `.comet/changes/<name>/` 或 `docs/openspec/` |
| **Classic 模式** | **阶段治理（Phase-Guarded State Machine）**：OpenSpec (WHAT) + Superpowers (HOW) 强约束状态机，强制 Handoff Hash 与门禁流转 | 弱/中等模型，或要求严格研发工序、审计合规的企业项目 | `Open` $\to$ `Design` $\to$ `Build` $\to$ `Verify` $\to$ `Archive` | `docs/openspec/changes/<name>/` |

### 轻量预设（Classic Presets）
- `/comet-hotfix`：Bug 修复轻量流（Open $\to$ Build $\to$ Verify $\to$ Archive），跳过 design 与复杂计划，但保留状态机与根因复测；
- `/comet-tweak`：轻中量配置/文档/Prompt 调整，跳过 design，直接通过 Spec Apply 实现。

---

## 2. Native 工作流核心协议

### ① Shape 阶段（需求固化与动态澄清树）
- **澄清三界线**：
  1. **可调查事实**：通过代码与环境可查明的信息，Agent 必须自主调查并出示依据，**严禁向用户提问**；
  2. **用户选择**：仅针对业务目标、范围边界、产品交互与关键架构取舍，列出明确选项与影响后请示用户；
  3. **实现选择**：专业技术实现细节（算法、数据结构、内部命名）由模型自主决策，严禁甩给用户。
- **输出产物**：`brief.md`（目标、范围、非目标与确认决定）+ 完整目标 Specs + 逐项可验证验收标准。

### ② Build 阶段（自主实现与插件技能协同）
- 模型以 ReAct 方式自主选用已部署的工程技能：
  - TDD 驱动：按需加载 `test-driven-development` 技能；
  - 复杂任务拆分：使用 `subagent-driven-development` 或 Supervisor Change（结合 `using-git-worktrees`）；
  - 遇到异常：强制加载 `systematic-debugging` 查明根因再修。
- **Builder 产物定性**：实现代码仅为“候选版本（Candidate）”，等待 Verify 裁决。

### ③ Verify 阶段（独立只读核验员与证据门）
- **认知隔离原则**：为避免实现者产生“确认偏差（Confirmation Bias）”，Verify 阶段必须以全新只读视角（或派发只读子代理 Verifier）介入；
- **逐项核验**：对照完整验收项、Spec 及运行检查物理证据进行裁决；
- **失败重试**：任何未通过项连同具体失败原因自动带回 Build 修复，修复后重新进行全量回归。

### ④ Archive 阶段（沉淀与交付）
- 生成 `verification.md`，固化需求、验证证据与结论；
- 根据 Change 的隔离方式（current / branch / worktree）确认交付动作（本地合并 / 推送 / 创建 PR）；
- 结合 `living-documentation` 刷新模块追溯 Frontmatter 与版本号。

---

## 3. 活体文档与工程模板（`engineering-docs`）无缝绑定

执行 Comet 研发流程时，必须与本工程的四阶活体文档及 15 套门禁模板建立端到端映射：

| Comet 阶段 | 活体文档对应层级 | 推荐调用的 `engineering-docs` 模板 |
| :--- | :--- | :--- |
| **Open / Shape** | `docs/specs/` (需求层) | `04-user-requirements.md` (URS), `05-product-spec.md` (PRD), `06-srs.md` (SRS) |
| **Design** | `docs/architecture/` (架构层) + `docs/reference/` (详细设计层) | `07-solution-design.md`, `08-hld.md` (HLD) → architecture；`09-lld.md` (LLD), `10-interface-spec.md` → reference |
| **Build** | `docs/management/` (管理层) + `docs/reference/` (参考层) | `10-interface-spec.md` (接口/DB定义) → reference；`11-project-plan.md`, `12-project-report.md` → management |
| **Verify** | `docs/tests/` (测试层) | `13-test-plan.md` (测试计划), `14-test-report.md` (测试报告/用例) |
| **Archive** | `docs/guides/` (指南层) | `15-delivery-docs.md` (交付版本说明/用户手册) |

> 模板最顶部均已原生内置标准 YAML Frontmatter（`id`, `title`, `type`, `status`, `modules`, `depends_on`），与 `tools/doc-impact.py` 双向关联分析完全兼容。

---

## 4. 状态崩溃恢复机制（Crash-Safe State）

若会话中断、窗口关闭或设备切换，按如下规则无缝恢复：
1. **主状态定位**：读取 Change 目录下的 `comet-state.yaml`；
2. **指针识别**：检查 `.comet/current-change.json` 获取当前活跃 Change；
3. **恢复探测指令**：运行 `comet resume-probe` 或 `comet status`，自动识别中断点并从最后安全的阶段节点继续执行，严禁推翻已通过的阶段。

---

## 5. 核心 CLI 命令速查

> **安全提示**：确保 `comet` 来自可信安装源（`npm install -g @rpamis/comet`），
> 警惕 PATH 劫持——不要运行来源不明的 `comet` 二进制。

当环境中已安装 `comet` CLI 时，可调用以下指令协同：
- `comet status`：查看活跃 Change、当前阶段及下一步推荐；
- `comet doctor`：诊断 37+ 平台 Rules/Skills/Hooks 挂载健康状况与修补建议；
- `comet resume-probe`：只读探测自然语言意图是否应恢复已有 active change；
- `comet dashboard`：启动本地浏览器可视化工作流看板；
- `comet init [path]`：初始化工程级 `.comet/config.yaml` 配置文件。
