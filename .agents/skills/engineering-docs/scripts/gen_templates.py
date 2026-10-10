#!/usr/bin/env python3
"""Generate 15 bilingual engineering document templates for engineering-docs skill."""
from pathlib import Path

OUT = Path(__file__).parent.parent / "references" / "templates"

# Each template: (filename, title_cn, title_en, doc_name, phase, covers, doc_id, doc_type, depends_on, sections)
# sections: list of (cn_title, en_title, guidance_cn)
TEMPLATES = [
    ("01-project-proposal.md", "项目立项建议书", "Project Proposal",
     "项目立项建议书 / 立项论证报告", "立项 Initiation",
     "项目立项建议书、立项论证报告",
     "PROP-XXX", "specs", [],
     [
         ("项目背景", "Background", "项目提出的背景、政策依据、市场或业务驱动因素。"),
         ("问题与机会", "Problem & Opportunity", "当前存在的问题、痛点，立项要抓住的机会。"),
         ("项目目标", "Objectives", "总体目标与分阶段目标，尽量量化。"),
         ("可行性分析", "Feasibility", "技术可行性、经济可行性、资源可行性、风险初步评估。"),
         ("方案概述", "Proposed Approach", "拟采用的技术路线、实施方案概要。"),
         ("投资估算", "Budget Estimate", "总投资、资金来源、分项估算。"),
         ("预期效益", "Expected Benefits", "经济效益、社会效益、量化指标。"),
         ("风险与对策", "Risks & Mitigations", "主要风险及应对措施。"),
         ("结论与建议", "Conclusion", "是否建议立项、下一步工作。"),
     ]),
    ("02-project-approval.md", "项目立项审批文件", "Project Approval Documents",
     "立项评审报告 / 立项审批报告 / 会签评审表", "立项 Initiation",
     "项目立项评审报告、项目立项审批报告、会签评审表",
     "APPR-XXX", "specs", ["docs/specs/PROP-XXX.md"],
     [
         ("评审基本信息", "Review Info", "评审时间、地点、主持人、参会人员、评审对象。"),
         ("评审材料清单", "Materials Reviewed", "本次评审所依据的材料列表。"),
         ("评审意见", "Review Comments", "各评审人意见，按条编号。"),
         ("结论", "Conclusion", "通过 / 有条件通过 / 不通过，附条件说明。"),
         ("审批意见", "Approval", "审批人、审批日期、审批结论。"),
         ("会签记录", "Sign-off Records", "| 部门/角色 | 签署人 | 日期 | 意见 |"),
     ]),
    ("03-project-task-book.md", "项目任务书", "Project Task Book",
     "项目任务书 / 项目工作任务书", "立项 Initiation",
     "项目任务书、项目工作任务书",
     "TASK-XXX", "specs", ["docs/specs/APPR-XXX.md"],
     [
         ("任务背景", "Background", "任务来源、上级要求或立项依据。"),
         ("任务目标", "Objectives", "要达成的目标，量化、可验收。"),
         ("工作内容", "Scope of Work", "具体工作项列表，编号。"),
         ("交付物", "Deliverables", "| 交付物 | 形式 | 完成标准 | 截止日期 |"),
         ("进度要求", "Schedule", "关键里程碑与时间节点。"),
         ("资源与分工", "Resources & Roles", "人力、经费、设备，职责分工表。"),
         ("考核标准", "Acceptance Criteria", "验收方式与通过标准。"),
     ]),
    ("04-user-requirements.md", "用户需求说明书", "User Requirements Specification",
     "用户需求说明书", "需求 Requirements",
     "用户需求说明书",
     "URS-XXX", "specs", [],
     [
         ("引言", "Introduction", "目的、范围、读者、术语。"),
         ("用户概况", "User Profile", "用户角色、数量、使用场景。"),
         ("业务现状", "Current Situation", "现有流程、痛点。"),
         ("功能需求", "Functional Requirements", "按用户故事描述：作为…我想要…以便…。"),
         ("非功能期望", "Non-functional Expectations", "性能、易用性、可靠性等方面的用户期望。"),
         ("约束与假设", "Constraints & Assumptions", "用户侧的约束条件。"),
         ("验收标准", "Acceptance Criteria", "用户可观察的验收条件。"),
     ]),
    ("05-product-spec.md", "产品规格说明书", "Product Specification",
     "产品规格说明书", "需求 Requirements",
     "产品规格说明书",
     "PRD-XXX", "specs", ["docs/specs/URS-XXX.md"],
     [
         ("产品概述", "Overview", "产品定位、目标用户、价值主张。"),
         ("产品架构", "Product Architecture", "功能模块划分、模块关系图。"),
         ("功能规格", "Feature Specifications", "每个功能的输入/处理/输出、业务规则。"),
         ("界面规格", "UI Specifications", "关键界面布局、交互说明（或引用 UIRD）。"),
         ("数据规格", "Data Specifications", "核心数据对象、数据字典引用。"),
         ("非功能规格", "Non-functional Specs", "性能、安全、兼容性指标。"),
         ("版本规划", "Release Plan", "MVP 范围、后续版本规划。"),
     ]),
    ("06-srs.md", "软件需求规格说明", "Software Requirements Specification (SRS)",
     "软件需求规格说明 / 开发需求细化表", "需求 Requirements",
     "软件需求规格说明、开发需求细化表",
     "SRS-XXX", "specs", ["docs/specs/PRD-XXX.md"],
     [
         ("引言", "Introduction", "目的、范围、定义、参考资料。"),
         ("总体描述", "Overall Description", "产品视角、用户特征、约束、假设。"),
         ("功能需求", "Functional Requirements", "编号 FR-001…：输入、前置条件、处理、输出、后置条件。"),
         ("接口需求", "Interface Requirements", "用户界面、硬件接口、软件接口、通信接口。"),
         ("非功能需求", "Non-functional Requirements", "性能、安全、可靠性、可维护性，量化指标。"),
         ("数据需求", "Data Requirements", "数据模型、数据字典引用。"),
         ("需求追溯", "Traceability", "需求编号 ↔ 用户需求/产品规格的追溯表。"),
         ("附录", "Appendix", "需求细化表（可拆分为独立 xlsx）。"),
     ]),
    ("07-solution-design.md", "方案设计报告", "Solution Design Report",
     "方案设计报告", "设计 Design",
     "方案设计报告",
     "ARCH-SOL-XXX", "architecture", ["docs/specs/SRS-XXX.md"],
     [
         ("设计目标", "Design Goals", "方案要解决的问题、达成的目标。"),
         ("设计原则", "Principles", "遵循的设计原则与约束。"),
         ("备选方案", "Alternatives", "方案 A/B/C 的对比：优劣、成本、风险。"),
         ("推荐方案", "Recommended Solution", "选定的方案及理由。"),
         ("总体架构", "High-level Architecture", "系统组成、关键技术选型。"),
         ("实施计划", "Implementation Plan", "阶段划分、里程碑。"),
         ("风险评估", "Risk Assessment", "技术风险与应对。"),
     ]),
    ("08-hld.md", "软件概要设计说明书", "High-Level Design (HLD)",
     "软件概要设计说明书", "设计 Design",
     "软件概要设计说明书",
     "HLD-XXX", "architecture", ["docs/specs/SRS-XXX.md"],
     [
         ("概述", "Overview", "目的、范围、设计约束。"),
         ("架构目标", "Architecture Goals", "质量属性目标：性能、可扩展性、安全性等。"),
         ("系统架构", "System Architecture", "架构风格、 C4 图（上下文/容器/组件）。"),
         ("子系统划分", "Subsystem Decomposition", "各子系统职责、接口、依赖。"),
         ("关键设计决策", "Key Decisions", "ADR 引用或内联决策记录。"),
         ("数据架构", "Data Architecture", "数据流、存储选型、缓存策略。"),
         ("部署架构", "Deployment", "部署拓扑、环境规划。"),
         ("安全设计", "Security", "认证授权、数据保护。"),
     ]),
    ("09-lld.md", "软件详细设计说明书", "Low-Level Design (LLD)",
     "软件详细设计说明书", "设计 Design",
     "软件详细设计说明书",
     "LLD-XXX", "architecture", ["docs/architecture/HLD-XXX.md"],
     [
         ("概述", "Overview", "目的、范围、引用 HLD 章节。"),
         ("模块划分", "Module Breakdown", "模块列表、职责、对应 HLD 子系统。"),
         ("模块详细设计", "Module Details", "每个模块：接口定义、内部类/函数、核心算法（伪代码或流程图）。"),
         ("数据结构", "Data Structures", "关键数据结构定义。"),
         ("异常处理", "Error Handling", "异常分类、处理策略。"),
         ("追溯表", "Traceability", "LLD 模块 ↔ HLD 子系统 ↔ SRS 需求编号。"),
     ]),
    ("10-interface-spec.md", "接口与数据库设计说明", "Interface & Database Specification",
     "接口说明书 / 数据库设计说明书", "设计 Design",
     "接口说明书、数据库设计说明书",
     "REF-IF-XXX", "reference", ["docs/architecture/HLD-XXX.md"],
     [
         ("接口总览", "Interface Overview", "接口清单、版本、协议。"),
         ("接口详细定义", "Interface Details", "每个接口：路径/方法、请求参数表、响应结构、错误码、示例。"),
         ("数据模型", "Data Model", "ER 图（mermaid）、表清单。"),
         ("表结构定义", "Table Definitions", "每张表：字段名、类型、约束、说明。"),
         ("索引与约束", "Indexes & Constraints", "索引设计、外键约束。"),
         ("数据迁移", "Migration", "初始化数据、版本迁移策略。"),
     ]),
    ("11-project-plan.md", "项目计划", "Project Plan",
     "项目计划", "管理 Management",
     "项目计划",
     "PLAN-XXX", "guide", ["docs/specs/SRS-XXX.md"],
     [
         ("项目目标", "Objectives", "范围、成功标准。"),
         ("工作分解", "WBS", "工作包列表、编号、负责人。"),
         ("进度计划", "Schedule", "甘特/里程碑表：任务、起止、依赖。"),
         ("资源计划", "Resources", "人力、设备、经费。"),
         ("质量计划", "Quality Plan", "评审点、测试策略引用。"),
         ("风险计划", "Risk Plan", "风险登记册：风险、概率、影响、应对。"),
         ("沟通计划", "Communication", "例会、报告机制、干系人。"),
     ]),
    ("12-project-report.md", "项目报告", "Project Report",
     "项目进展报告 / 项目总结报告 / 试运行报告 / 评审报告 / 会议纪要", "管理 Management",
     "项目进展报告、项目总结报告、试运行报告、评审报告、会议纪要",
     "REP-XXX", "guide", ["docs/guides/PLAN-XXX.md"],
     [
         ("基本信息", "Basic Info", "报告类型、报告期、编写人、日期。"),
         ("总体状态", "Status Overview", "🟢/🟡/🔴 总体状态一句话。"),
         ("进展情况", "Progress", "本期完成工作、里程碑达成情况。"),
         ("问题与风险", "Issues & Risks", "阻塞问题、新增风险、应对措施。"),
         ("下期计划", "Next Steps", "下期工作安排。"),
         ("决策事项", "Decisions", "需领导/干系人决策的事项。"),
         ("会议纪要附则", "Minutes Appendix", "仅会议纪要：时间地点、参会人、议题、决议、行动项（负责人+截止）。"),
     ]),
    ("13-test-plan.md", "软件测试计划", "Software Test Plan",
     "软件集成测试计划 / 软件系统测试计划", "测试 Testing",
     "软件集成测试计划、软件系统测试计划",
     "TEST-PLAN-XXX", "reference", ["docs/specs/SRS-XXX.md"],
     [
         ("测试目标", "Objectives", "测试要验证什么。"),
         ("测试范围", "Scope", "测试/不测试的功能列表。"),
         ("测试策略", "Strategy", "测试级别、方法（黑盒/白盒）、自动化比例。"),
         ("测试环境", "Environment", "硬件、软件、数据、工具。"),
         ("测试用例设计", "Test Design", "用例设计方法、覆盖率要求。"),
         ("进度安排", "Schedule", "测试阶段、轮次、时间。"),
         ("出入口准则", "Entry/Exit Criteria", "开始/结束测试的条件。"),
         ("风险与应对", "Risks", "测试风险及预案。"),
     ]),
    ("14-test-report.md", "软件测试报告", "Software Test Report",
     "软件单元测试报告 / 集成测试报告 / 系统测试报告 / 性能测试报告 / 软件测试用例", "测试 Testing",
     "软件单元测试报告、软件集成测试报告、软件系统测试报告、软件性能测试报告、软件测试用例",
     "TEST-REP-XXX", "reference", ["docs/reference/TEST-PLAN-XXX.md"],
     [
         ("测试概述", "Overview", "测试对象版本、测试时间、测试人员。"),
         ("测试环境", "Environment", "实际测试环境描述。"),
         ("用例执行", "Execution", "| 用例编号 | 覆盖需求 | 前置条件 | 步骤 | 预期 | 实际 | 结果 |"),
         ("缺陷统计", "Defects", "缺陷数、严重级别分布、遗留缺陷。"),
         ("覆盖率", "Coverage", "需求覆盖率、用例通过率。"),
         ("性能数据", "Performance", "仅性能测试：响应时间、吞吐量、资源占用。"),
         ("结论", "Conclusion", "是否达到发布标准、遗留风险。"),
     ]),
    ("15-delivery-docs.md", "软件交付文档", "Software Delivery Documents",
     "软件版本说明 / 软件用户手册", "交付 Delivery",
     "软件版本说明、软件用户手册",
     "GUIDE-DELIVERY-XXX", "guide", ["docs/reference/TEST-REP-XXX.md"],
     [
         ("版本信息", "Version Info", "版本号、发布日期、适用范围。"),
         ("更新内容", "Changelog", "新增/优化/修复列表。"),
         ("安装部署", "Installation", "环境要求、安装步骤、配置说明。"),
         ("使用指南", "User Guide", "按用户角色组织的操作说明。"),
         ("常见问题", "FAQ", "FAQ 列表。"),
         ("已知问题", "Known Issues", "已知缺陷及规避方法。"),
         ("技术支持", "Support", "联系方式、服务承诺。"),
     ]),
]

HEADER = """---
id: {doc_id}
title: "[模块/系统名称] {title_cn}"
type: {doc_type}
status: draft
modules:
  - "src/your_module/**"
depends_on:{depends_on_block}
version: 0.1.0
last_verified_commit: HEAD
---

# {title_cn}
# {title_en}
"""

for fname, t_cn, t_en, doc_name, phase, covers, doc_id, doc_type, deps, sections in TEMPLATES:
    if deps:
        deps_block = "\n" + "\n".join(f'  - "{d}"' for d in deps)
    else:
        deps_block = " []"

    header_text = HEADER.format(
        doc_id=doc_id,
        title_cn=t_cn,
        title_en=t_en,
        doc_type=doc_type,
        depends_on_block=deps_block,
    )
    lines = [header_text.strip()]
    lines.append("")
    lines.append(f"> **文档类型**：{doc_name}  ")
    lines.append(f"> **适用阶段**：{phase}  ")
    lines.append(f"> **覆盖**：{covers}  ")
    lines.append("> **渲染规范**：参见 `../rendering-spec.md`（标题字号/段落/字体）；未知项标 `TODO: <说明>`，不要编造。")
    lines.append("")
    for i, (cn, en, guide) in enumerate(sections, 1):
        lines.append(f"## {i}. {cn} / {en}")
        lines.append("")
        lines.append(f"<!-- {guide} -->")
        lines.append("")
        lines.append(f"[{cn}内容]")
        lines.append("")
    (OUT / fname).write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ {fname}")

print(f"\nDone: {len(TEMPLATES)} templates")
