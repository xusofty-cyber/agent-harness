# 文档与代码追溯矩阵规范 (Traceability Matrix Guide)

## 1. 核心映射逻辑
通过在每篇 Markdown 文档头部声明 Frontmatter，实现双向追溯检索：

```text
       ┌────────────────────────┐
       │ docs/specs/SRS-001.md  │
       └───────────┬────────────┘
                   │ depends_on
                   ▼
       ┌────────────────────────┐
       │ docs/architecture/     │
       │ ARCH-001-nrsec.md      │
       └───────────┬────────────┘
                   │ modules
                   ▼
       ┌────────────────────────┐
       │ apps/nrsecServer/**    │
       │ apps/config/system.ini │
       └────────────────────────┘
```

## 2. 字段规范说明
- `id` (字符串，必填)：全项目唯一标识，推荐格式：`[类型]-[编号]-[模块名]`（如 `ARCH-001-NRSEC`）。
- `title` (字符串，必填)：简短清晰的文档标题。
- `type` (枚举，必填)：`specs` | `architecture` | `reference` | `guide` | `adr`。
- `status` (枚举，必填)：`draft`（拟定中）| `active`（有效真理源）| `deprecated`（已过时废弃）。
- `modules` (字符串数组，必填)：本篇文档关联的代码路径或 Glob 规则（例如 `apps/nrsecServer/**`）。
- `depends_on` (字符串数组，选填)：上游依赖的文档相对路径列表。
- `version` (Semver 字符串，必填)：遵循语义化版本（如 `1.0.0`）。
- `last_verified_commit` (Git Commit Hash 或 HEAD，必填)：最后一次核对代码一致性的提交标识。

## 3. 影响面计算算法（Impact Analysis Algorithm）
当某次任务修改了代码文件集合 $F = \{f_1, f_2, ...\}$ 时：
1. 遍历 `docs/` 下所有 `.md` 文件，提取其 Frontmatter 中的 `modules` 列表；
2. 若任意 $f_i$ 匹配文档的任一 `module` Glob：
   - 将该文档加入**待审查列表（Impact List）**；
   - 沿 `depends_on` 向上标记可能受波及的架构/需求文档。
3. 形成 Impact Matrix 输出给开发者与 Agent，精准定向更新文档。
