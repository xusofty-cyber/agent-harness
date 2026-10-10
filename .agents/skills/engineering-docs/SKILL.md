---
name: engineering-docs
description: 研发全生命周期文档模板库。Use when writing project proposals, requirements (URS/SRS), architecture/design docs (HLD/LLD), interface/DB specs, test plans/reports, or delivery docs. Provides 15 bilingual phase-gate templates ensuring consistent output across agents. Covers 31 document types from initiation to delivery.
version: 0.1.0
license: MIT
---

# Engineering Docs

研发文档模板库：15 个中英双语模板，覆盖 31 种研发文档，
保证不同 Agent 产出的文档**结构一致、格式一致**。

## 31 → 15 映射决策树

**需要什么文档？→ 用哪个模板：**

```
立项 Initiation
├── 要建议立项 / 做可行性论证？     → 01-project-proposal.md
├── 要评审记录 / 审批 / 会签？       → 02-project-approval.md
└── 要下达任务？                    → 03-project-task-book.md

需求 Requirements
├── 用户视角的需求？                 → 04-user-requirements.md
├── 产品视角的规格？                 → 05-product-spec.md
└── 开发视角的形式化规格？           → 06-srs.md

设计 Design
├── 总体技术方案？                   → 07-solution-design.md
├── 架构级设计？                     → 08-hld.md
├── 模块级设计？                     → 09-lld.md
└── 接口 / 数据库？                  → 10-interface-spec.md

管理 Management
├── 项目计划？                       → 11-project-plan.md
└── 进展/总结/试运行/评审/会议纪要？ → 12-project-report.md

测试 Testing
├── 测试计划？                       → 13-test-plan.md
└── 测试报告 / 测试用例？            → 14-test-report.md

交付 Delivery
└── 版本说明 / 用户手册？            → 15-delivery-docs.md
```

## 工作流

1. **识别**：从上面的决策树找到对应模板。
2. **加载**：读取 `references/templates/<nn>-*.md`。
3. **访谈**：向用户提问填补 `[占位符]`；未知项标 `TODO: <说明>`，**绝不编造**。
4. **生成**：按模板章节输出，遵循 `references/rendering-spec.md` 的格式规范。

## 需求纪律（writing docs 时强制）

区分四类内容，绝不混淆：

| 类型 | 定义 | 处理 |
|---|---|---|
| 显式需求 | 用户直接陈述的 | 直接写入 |
| 派生需求 | 为满足显式需求所必需的 | 写入并标注"派生" |
| 假设 | 信息缺失时代入的 | 写入并标注"假设待确认" |
| 未知项 | 无法验证的 | 标 `TODO`，不编造 |

**铁律**：绝不把假设静默转为需求。

## 渲染规范

所有模板输出必须遵循 `references/rendering-spec.md`：
标题层级字号、段落格式（首行缩进/段间距）、中英文字体（中文宋体/黑体、英文 Times New Roman）、
表格/代码块样式。保证不同 Agent 产出的文档视觉一致。

需要交付 Word 版时：用 Markdown 生成内容，再经 pandoc + 中文 Word 参考模板转换
（详见 rendering-spec.md 的"交付为 Word"节）。

## 与其他 skill 的关系

| Skill | 职责 | 边界 |
|---|---|---|
| `living-documentation` | 文档生命周期管理（四阶模型） | 不管具体模板内容 |
| `openspec-*` | Spec 驱动开发流程 | 不管传统 PRD/SRS/SAD 格式 |
| `engineering-docs`（本） | 31 种文档的内容模板 | 不管流程，只管"写什么章节" |

## 模板一览

| # | 模板 | 阶段 | 覆盖文档数 |
|---|---|---|---|
| 01 | project-proposal | 立项 | 2 |
| 02 | project-approval | 立项 | 3 |
| 03 | project-task-book | 立项 | 2 |
| 04 | user-requirements | 需求 | 1 |
| 05 | product-spec | 需求 | 1 |
| 06 | srs | 需求 | 2 |
| 07 | solution-design | 设计 | 1 |
| 08 | hld | 设计 | 1 |
| 09 | lld | 设计 | 1 |
| 10 | interface-spec | 设计 | 2 |
| 11 | project-plan | 管理 | 1 |
| 12 | project-report | 管理 | 5 |
| 13 | test-plan | 测试 | 2 |
| 14 | test-report | 测试 | 5 |
| 15 | delivery-docs | 交付 | 2 |

共 15 个模板，覆盖 31 种文档。
