# 评审角色 skills 设计方案（2026-10-08）

## 一句话

补仓库的空白：现有 `requesting-code-review` / `receiving-code-review`（vendored）
审的是**已完成的代码**；新 skill 审的是**未做的决策**——agent 摆出多方案时，
各评审角色从不同角度并行分析，输出一张决策矩阵，用户只做最后一选。

## 从 mattpocock/skills 借鉴什么（只借机制，不借内容）

| 机制 | 来源 | 怎么用 |
|---|---|---|
| User-invoked vs Model-invoked 分层 | README 全局架构 | 编排型 skill（用户敲）vs 纪律型 skill（agent 按需取）；前者可调后者，不可调另一个前者 |
| 并行隔离评审 | `code-review` 双轴并行 | 每个评审角度跑独立 subagent，"so neither pollutes the other"——防锚定，这是多方案评审的核心 |
| Frontier rounds | `grilling` 的设计树 | 评审前先把"待确认事实"与"待做决策"分开；事实由 agent 自己查，不问用户 |
| One-way / two-way door | `pr` skill | 可逆性作为一等评审维度：不可逆方案默认降级 |

不借鉴：具体角色话术（为 Matt 个人调参）、整包 vendor、
访谈式 grill 本体（方向与"无需人为介入"相反，但 frontier 机制可用）。

## 我们的特色：`option-review`

### 与现有 skill 的关系

- `requesting-code-review`：代码写完后审 diff（单视角、事后）
- **`option-review`：决策前审方案（多视角、事前）** ← 新增
- `receiving-code-review`：收到评审意见后怎么处理（事后）

三者正好覆盖决策前 → 执行后 → 反馈处理，不重叠。

### 双模式（借用分层思想）

- **Model-invoked（主）**：agent 生成 ≥2 个可行方案时，**自动** fan-out 评审，
  用户一次看到"方案 + 决策矩阵"，无需中途介入，只做最后一选。
  ——这正是你说的场景。
- **User-invoked（辅）**：`/option-review`，用户贴出方案或指向一个待决策点时手动触发。

### 评审维度（agents-living 口味）

1. **Security**：攻击面、凭证处理、注入风险；对齐 `.agents/rules/security-boundary.md`
2. **Engineering**：可维护性、与仓库既有模式的一致性、可测试性
3. **Reversibility**：单向门 vs 双向门；blast radius；错了好不好回滚
4. **Simplicity**：YAGNI， moving parts 最少的优先
5. **Cross-tool**：在 Claude Code / Codex / Antigravity 下是否都成立（我们的独特维度）

### 关键规则（防评审走形）

1. **信息隔离**：每个 reviewer 只拿到"中性描述的方案 + 自己的 rubric"，
   拿不到 session 历史——agent 不能把自己的倾向 leaking 给 reviewer
   （借自 `requesting-code-review` 的 "never your session's history"）。
2. **真并行**：用 `dispatching-parallel-agents` 的模式一次 fan-out，
   reviewer 之间不许通气，分歧如实上浮，不许平均掉。
3. **矩阵先行**：输出顺序永远是决策矩阵 → 推荐 → 分歧点；
   用户先看全景，再看 agent 的倾向。

### 输出格式

```text
| 方案 | Security | Engineering | Reversibility | Simplicity | Cross-tool |
|------|----------|-------------|---------------|------------|------------|
| A    | ✅       | ⚠️ 接口稍宽 | ❌ 单向门      | ✅         | ✅         |
| B    | ⚠️ 新增面 | ✅          | ✅ 双向门      | ⚠️ 多一步  | ✅         |

推荐：B（唯一分歧：Security 认为 A 的面更小，但 Reversibility 一票否决了 A）
```

### 文件清单

- `.agents/skills/option-review/SKILL.md`（`version: 0.1.0`，按新规范）
- `.agents/skills/option-review/references/rubrics.md`（五个维度的评分标准）
- `skills-lock.json`：`sourceType: local` + `version`
- `tests/repo_checks.py`：现有 `skill-version` 检查自动覆盖，无需改
- `CONTRIBUTING.md` / `CHANGELOG.md`：按现有流程更新

### 不做的

- 不做访谈式 grill（`grill-me` 本体）：与"无需人为介入"场景方向相反；
  以后若要补"对齐阶段"，单独立项。
- reviewer 不拆成独立 skills：先以内嵌 rubric 起步，
  某个维度被证明可复用时再拆（避免一次建 5 个 skill 的重资产开局）。
