# Comet 与 Living Documentation 深度集成规范

本文档规范 `/comet` 经典流程（Open $\to$ Design $\to$ Build $\to$ Verify $\to$ Archive）各阶段与长期文档资产的协同门禁。

## 1. 阶段门禁矩阵

| Comet 阶段 | 输入 | 核心文档操作（规范与模板选用） | 产出与门禁检查 |
| :--- | :--- | :--- | :--- |
| **Open** | 用户需求 / Bug 描述 | 1. 判定变更等级（L0 / L1 / L2）<br>2. 若为 L2 重大需求，在 `docs/specs/` 初始化或关联对应需求说明，选用 `engineering-docs` 模板（`04-user-requirements.md` / `05-product-spec.md` / `06-srs.md`） | `proposal.md` 必须标明目标 SRS 路径与受影响模块 |
| **Design** | `proposal.md`、需求说明 | 1. 架构方案沉淀至 `docs/architecture/`，选用 `engineering-docs` 模板（`07-solution-design.md` / `08-hld.md` / `09-lld.md`）<br>2. 接口与数据字典沉淀至 `docs/reference/`（选用 `10-interface-spec.md`）<br>3. 识别受改动影响的存量文档，列出 **Document Impact Matrix** | `design.md` 包含受影响文档清单与 Frontmatter 依赖声明 |
| **Build** | `design.md`、代码上下文 | 1. 编写代码与单元测试<br>2. 若触发 L1 变更（新增配置、改动接口），**同步修改 `docs/reference/`**（对照 `10-interface-spec.md` 格式） | 提交代码时，详细设计/API/配置文档与代码变更处于同一步长 |
| **Verify** | 构建产物与测试用例 | 1. 运行功能测试与自动化脚本，测试记录可选用 `engineering-docs` 模板（`13-test-plan.md` / `14-test-report.md`）<br>2. **核对代码与文档一致性**（如配置文件与字典表格对照）<br>3. 运行 `python3 .agents/skills/living-documentation/scripts/doc-impact.py`（或 `tools/doc-impact.py`）确认无 🔴 must-update 残留<br>4. **代码审查门禁**：按 `open-code-review` skill 执行确定性代码评审（`ocr` CLI 已装则走 Tier A 委托，否则走 Tier B 方法论）；Critical/High 发现须修复或在 `verification.md` 中书面豁免 | `verification.md` 记录功能测试结果、“代码-文档一致性”检查项与代码评审结论 |
| **Archive** | 已通过验收的变更分支 | 1. 提取操作手册与版本说明沉淀至 `docs/guides/`，选用 `engineering-docs` 模板（`15-delivery-docs.md`）<br>2. 更新所有改动文档的 Frontmatter `version` 与 `last_verified_commit`（此时应等于合入的 commit）<br>3. 归档当前变更快照 | 长期文档库更新完成，`doc-impact.py` 输出无 must-update |

## 2. 避免文档漂移（Drift Prevention）原则
- **代码变，文档必须变**：禁止“先合入代码，以后再补文档”的推迟模式。
- **单篇聚焦，拒绝大而全**：按子模块拆分架构说明，单个文档聚焦单一模块，更新成本极低。
- **Delta 资产化**：Comet 阶段生成的局部方案（Delta），在 Archive 时必须合入 `docs/` 下的长期真理源（Living Truth），不能只锁在历史归档目录中。
