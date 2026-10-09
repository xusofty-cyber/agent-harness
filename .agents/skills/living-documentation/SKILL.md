---
name: living-documentation
description: Maintain agile living documentation across the development lifecycle (specs, architecture, reference, guides), establish code-doc traceability with Frontmatter metadata, and integrate document gates with Comet workflows.
version: 0.1.1
---

# Living Documentation & Traceability

Maintain documentation as an active, traceable engineering artifact rather than write-once-and-forget prose. This skill defines the four-tier document model, code-documentation traceability metadata, heuristic change thresholds, and tight lifecycle integration with `/comet`.

## 1. The Four-Tier Document Model

Organize project documentation under `docs/` according to Diátaxis and agile engineering practice:

| Tier | Directory | Document Type (`type`) | Focus & Audience | Template |
| :--- | :--- | :--- | :--- | :--- |
| **1. 需求说明** | `docs/specs/` | `specs` | 业务需求、功能范围、输入输出约束与验收标准（轻量 SRS/PRD） | `templates/srs.template.md` |
| **2. 概要架构** | `docs/architecture/` | `architecture` | 系统全景、模块拓扑、分层交互与数据流向（轻量 arc42 概要） | `templates/architecture.template.md` |
| **3. 详细设计** | `docs/reference/` | `reference` | 接口协议、报文格式、配置字典（如 `system.ini` 释义）与核心类定义 | `templates/reference.template.md` |
| **4. 用户指引** | `docs/guides/` | `guide` | 部署运维、环境准备、操作步骤与常见排障手册（How-To / Manual） | `templates/guide.template.md` |

> 重大架构选型与权衡记录单独存放于 `docs/adr/`（Architecture Decision Records）。

---

## 2. Code-Documentation Traceability (Frontmatter)

Every living document under `docs/` MUST declare metadata in its YAML frontmatter to establish bi-directional traceability with code modules:

```yaml
---
id: ARCH-001-NRSEC
title: 密码安全服务系统架构与通信设计
type: architecture          # specs | architecture | reference | guide | adr
status: active              # draft | active | deprecated
modules:                    # 关联的代码模块或路径（支持相对根目录 Glob）
  - apps/nrsecServer/**
  - apps/config/system.ini
depends_on:                 # 关联的上游需求或架构文档路径
  - docs/specs/SRS-001-sec-channel.md
version: 1.0.0
last_verified_commit: HEAD
---
```

### Traceability Benefits
- **Impact Analysis**: When code in `apps/nrsecServer/` changes, scan `docs/` for `modules` matching that path to determine which documents require review/updates.
- **Token Efficiency**: Agents only load documents linked to active modules, avoiding full-repository doc dump.

---

## 3. Heuristic Change Thresholds (分级变更门禁)

Do not generate or update full document suites on trivial changes. Apply tiered thresholds:

- **L0 微调 (Trivial Fix)**:
  - 范围：函数内局部修复、代码格式化、不改动对外接口与配置的 Bug 修复。
  - 文档要求：记录 `tasks/lessons.md`（错题本）或当前会话断点；**不修改 `docs/` 下的架构与用户文档**。
- **L1 局部更新 (Minor Feature / Config Change)**:
  - 触发条件：修改/新增 1~2 个外部接口、调整配置文件项（如 `system.ini`）、修改协议报文。
  - 文档要求：必须同步更新 `docs/reference/` 对应的接口/配置参考，并在对应文档 Frontmatter 更新版本号。
- **L2 重大架构/功能 (Major Feature / Module Refactor)**:
  - 触发条件：新建子模块/服务进程、重大架构重构、业务协议全面调整。
  - 文档要求：履约完整文档闭环（需求规格 SRS $\to$ 架构设计 $\to$ 详细接口/配置参考 $\to$ 用户操作指南）。

---

## 4. Integration with `/comet` Workflow

When working with `/comet`, bind documentation directly to the phase state machine:

1. **Open Phase**:
   - Determine whether the task introduces a new feature or scope.
   - For L2 changes, initialize/update `docs/specs/SRS-*.md` before entering design.
2. **Design Phase**:
   - Generate technical architecture in `docs/architecture/` with `modules` and `depends_on` declared.
   - Output a **Document Impact Matrix**: list existing documents impacted by this change.
3. **Build Phase**:
   - As code is modified, if L1/L2 thresholds are reached, update `docs/reference/` alongside source code.
4. **Verify Phase**:
   - Add documentation consistency verification to test checklist: verify that modified configurations and APIs match `docs/reference/`.
5. **Archive Phase**:
   - Extract user-facing commands, deployment changes, and operational guidance into `docs/guides/`.
   - Update `last_verified_commit` in the frontmatter of all modified documents.

See `references/comet-integration.md` for phase-by-phase details.

---

## 5. Brownfield Reverse-Engineering (逆向文档补全)

For existing codebases with missing or outdated documentation:
1. **Module Inventory**: Inspect directories, build scripts (`make_arm.sh`, `Makefile`, `CMakeLists.txt`), and configuration files (`system.ini`).
2. **Scaffold Structure**: Create standard directories under `docs/` (`specs/`, `architecture/`, `reference/`, `guides/`).
3. **Generate Overview**: Reverse-engineer system topology into `docs/architecture/overview.md`.
4. **Extract Reference**: Generate dictionary for configuration keys and exported APIs into `docs/reference/`.
5. **Bind Modules**: Add `modules: [...]` frontmatter linking existing source directories.

---

## 6. Technical Editor Quality Rules

- **Diagrams First**: Use Mermaid diagrams for architecture topologies, state machines, and sequence calls.
- **No Boilerplate Prose**: State inputs, outputs, errors, and rationale directly; eliminate filler phrases.
- **Preserve Decisions**: Document *why* an approach was chosen and what alternatives were rejected.
