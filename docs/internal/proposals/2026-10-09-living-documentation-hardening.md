# Living Documentation 强化方案（2026-10-09）

## 背景

`living-documentation` skill（v0.1.0，2026-10-09 合入）建立了四阶文档模型、
frontmatter 追溯规范、L0/L1/L2 分级门禁，设计完整。但评审发现三处"执行层断点"：
规范写了，**没有可执行的强制力**——全靠 agent 自觉。本方案补上这三块。

## 强化项一：`tools/doc-impact.py`（影响面分析脚本）★核心

### 1.1 现状问题

`references/traceability-matrix.md` 定义了影响面计算算法，但仓库中无任何实现。
`last_verified_commit` 字段无人校验是否落后。

### 1.2 方案

新增 `tools/doc-impact.py`，纯标准库（`pathlib`/`fnmatch`，frontmatter 用正则解析），
无第三方依赖：

```text
usage: doc-impact.py [--changed-files F ...] [--since COMMIT] [--json]
```

**流程**：

1. 扫描 `docs/{specs,architecture,reference,guides,adr}/**/*.md`，解析 frontmatter
  （`id`/`type`/`status`/`modules`/`depends_on`/`last_verified_commit`）；
2. 变更文件集合 F：默认取 `git diff --name-only HEAD`（未提交变更），
   或 `--since COMMIT` 取区间变更；
3. 对每个 f ∈ F，用 `fnmatch` 匹配各文档的 `modules` Glob → 直接命中清单；
4. 沿 `depends_on` 向上遍历 → 间接受影响清单（标注传递深度）；
5. 对每篇命中文档，计算 `git rev-list --count <last_verified_commit>..HEAD` →
   落后提交数；`last_verified_commit` 缺失或非法记为 `unknown`；
6. 输出分级报告：
   - 🔴 直接命中 + 落后 > 0：必须同步更新
   - 🟡 间接影响：建议复核
   - 🟢 命中但 `last_verified_commit == HEAD`：已同步，无需动作

**接线位置**（分阶段）：

- 第一阶段（本方案）：agent 手动调用 + comet Verify/Archive 阶段调用（更新
  `references/comet-integration.md` 的门禁描述）；
- 第二阶段（可选）：CI 中作为 advisory 输出，不阻塞合并；
- 不做：pre-commit 强阻塞——文档更新常需人工判断，强阻塞会逼出敷衍的
  `last_verified_commit` 灌水。

### 1.3 验收标准

- `python3 tools/doc-impact.py --changed-files <任一代码文件>` 能正确命中
  声明了对应 `modules` 的文档；
- `depends_on` 传递标记深度正确，无循环依赖死循环；
- `--json` 输出可被其他工具消费。

## 强化项二：`repo_checks.py` 新增 `doc-frontmatter` 检查

### 2.1 现状问题

skill 以 MUST 要求 `docs/` 下每篇文档声明 frontmatter，但当前无任何校验。
三个月后一半文档缺字段，追溯体系名存实亡。

### 2.2 方案

在 `tests/repo_checks.py` 新增检查节（置于 skill 检查之后）：

```python
# --- 3d. Living-doc frontmatter ---
# docs/{specs,architecture,reference,guides,adr}/ 下的 .md 必须有合法 frontmatter
DOC_TYPES = {"specs", "architecture", "reference", "guide", "adr"}
DOC_STATUS = {"draft", "active", "deprecated"}
for tier in ("specs", "architecture", "reference", "guides", "adr"):
    for f in (ROOT / "docs" / tier).rglob("*.md"):
        # 必填：id / type / status / modules（非空）
        # type ∈ DOC_TYPES 且与所在目录一致（adr/ 下 type 必须为 adr，以此类推）
        # status ∈ DOC_STATUS
```

**细节决策**：

- `depends_on` / `version` / `last_verified_commit` 为选填（降低初次落地阻力，
  待强化项一跑顺后再收紧）；
- `type` 必须与所在目录一致，防止放错目录；
- 空目录（当前骨架刚建） natural pass，不报错；
- 模板文件在 skill 目录下，不在此检查范围内（它们是模板不是文档）。

### 2.3 验收标准

- 故意写一篇缺 `modules` 的文档 → 检查失败并指出文件与缺失字段；
- `type` 与目录不一致 → 失败；
- 现有空骨架 → 通过。

## 强化项三：deploy 骨架补 `docs/adr/`

### 3.1 现状问题

skill 明确"重大架构选型记录单独存放于 `docs/adr/`"，但 `deploy-agents.sh/ps1`
的 scaffold 循环只有 `specs architecture reference guides`，漏了 `adr`。

### 3.2 方案

- `deploy-agents.sh` 第 711 行循环加入 `adr`；
- `deploy-agents.ps1` 对应位置同步（parity 检查 `living-doc-scaffold` 条目已存在，
  无需改 `repo_checks.py`，但需跑一遍确认）；
- `README.md` / `README_zh.md` 中提及"四阶文档骨架"处，如有列举目录，同步加 `adr`。

### 3.3 验收标准

- deploy 冒烟：目标目录出现 `docs/adr/`；
- `parity:living documentation directory scaffold` 检查通过。

## 附带项：模板与 skill 版本联动规则

`templates/*.template.md` 更新时，`living-documentation` 的 `version:` 是否 bump？
建议写入 `CONTRIBUTING.md` 的 Skill versions 小节：

- 模板内容变更（字段增减、章节调整）→ minor bump；
- 仅措辞/示例微调 → patch bump；
- 与 skill 正文的联动变更合并计算，不重复 bump。

## 实施顺序与工作量

| 顺序 | 项 | 工作量 | 依赖 |
|---|---|---|---|
| 1 | 强化项三（adr 骨架） | 10 分钟 | 无 |
| 2 | 强化项二（frontmatter 检查） | 1 小时 | 无 |
| 3 | 强化项一（doc-impact.py） | 半天 | 建议在 2 之后（frontmatter 合规是输入质量保证） |
| 4 | 附带项（CONTRIBUTING 一句话） | 5 分钟 | 无 |

## 不做

- 不把 doc-impact 接入 pre-commit 强阻塞（理由见 1.2）；
- 不重写现有四套模板（质量已可）；
- 不动 skill 正文（v0.1.0 保持稳定，强化项全是外围执行层）。
