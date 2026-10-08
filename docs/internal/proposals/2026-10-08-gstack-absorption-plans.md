# gstack 吸收项实施方案（2026-10-08）

> 背景：对 `garrytan/gstack`（136k stars，Garry Tan 的 Claude Code 工具集）的分析结论——
> 与本仓库互补（角色型 skill vs 工程底座），可吸收的是机制设计。以下三项的实施方案。

---

## 方案一：hooks 前移评估

### 调研结论

1. **机制真实存在**：Claude Code 支持在 `SKILL.md` frontmatter 中声明 `hooks:`（gstack 的 `guard`/`careful`/`freeze` 为实证），格式：
   ```yaml
   hooks:
     PreToolUse:
       - matcher: "Bash"
         hooks:
           - type: command
             command: "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.mjs"
   ```
   `${CLAUDE_PROJECT_DIR}` 环境变量可解决相对路径问题（gstack 用 `$HOME` 绝对路径，不适合我们"部署到任意项目"的模型）。
2. **激活语义已查实（2026-10-08，多信源收敛）**：
   - skill frontmatter hooks **绑定 skill 生命周期**：skill 被调用/加载时注册，完成后注销（dev.to 实测、`parseHooksFromFrontmatter()` 源码分析、liatrio-labs 研究报告一致）。
   - `settings.json` hooks 才是**会话级常驻**。
   - jakelin 的 effective-claude-code 明确写道：*"Reserve `settings.json` hooks for guarantees that should apply across every session — protected-branch guards…"* ——这正是 `guard.mjs` 的用例；skill-scoped hooks 适用于 `/careful`、`/freeze` 这类"特定工作流才需要的 guardrails"。

   **结论**：B 方案（迁移 `guard.mjs`）**否决**——会把无条件安全网降级为"skill 激活期间才有"，产生安全空洞。
3. **跨工具死结**：Codex / Antigravity 不识别 skill frontmatter hooks。`settings.json` 仍是唯一的跨工具声明路径（虽然目前也只有 Claude Code 实现 PreToolUse）。

### 建议：混合方案（不迁移现有 hooks，新增 opt-in 严格模式）

| 方案 | 做法 | 结论 |
|---|---|---|
| A 维持现状 | hooks 留在 `.claude/settings.json` | ✅ 安全底线不动 |
| B 全量迁移 | guard.mjs → skill frontmatter | ❌ 激活语义未明，有打穿风险；且丢跨工具性 |
| **C 混合** | **A 保留 + 新增 opt-in `strict-guard` skill** | ✅ 推荐 |

C 方案 = 借鉴 gstack `/guard`（= `/careful` + `/freeze` 组合）的"严格模式"思想，但做成**显式 opt-in**：
- 新 skill `.agents/skills/strict-guard/`：frontmatter 声明 `Edit|Write` matcher 的目录边界限制脚本 + `Bash` matcher 的扩展危险模式（在 guard.mjs 基础之上再加码，如 `git push --force` 二次确认、`.env` 写入拦截）。
- 脚本放在 skill 自带 `scripts/` 目录，command 用 `${CLAUDE_PROJECT_DIR}/.agents/skills/strict-guard/scripts/...` 引用。
- 现有 `.claude/hooks/guard.mjs` + `settings.json` 一行不动——强制底线与可选增强解耦。

### 先做验证实验（✅ 已完成，2026-10-08）

**结论**：无需运行实验——官方文档 + 多方独立信源已给出决定性答案（见上"激活语义已查实"）。
B 方案否决，C 方案确认可行。`strict-guard` skill 可直接按改动清单实施。

### 改动清单（C 方案）

- 新增 `.agents/skills/strict-guard/SKILL.md`（frontmatter 含 `version:` 见方案二、`hooks:`）
- 新增 `.agents/skills/strict-guard/scripts/check-boundary.mjs`、`check-bash-strict.mjs`
- `skills-lock.json`：加 `strict-guard` 条目（`sourceType: local`，见方案二）
- `tests/hooks.test.mjs`：为新脚本加 black-box 用例（复用现有 PreToolUse 协议 harness）
- `deploy-agents.*`：**零改动**（skill 走现有部署 + symlink bridge）
- 文档：中英部署指南"安全钩子"章节加一小节说明两档模式
- 工作量估计：约 0.5 天（含验证实验）

---

## 方案二：skill `version` 字段

### 规范

- `SKILL.md` frontmatter 新增可选字段 `version: 0.1.0`（semver，`^\d+\.\d+\.\d+$`）。
- **适用范围**：
  - **必填**：`sourceType: local` 的自研 skill（当前仅 `cross-tool-memory`；未来的 `strict-guard` 等）。
  - **禁止**：vendored skill（openspec/superpowers/…）——版本归属上游，我们不自封版本号；上游版本（如有）记录在 `skills-lock.json` 的 `upstreamVersion` 字段（可选）。
- `skills-lock.json`：`local` 条目加 `"version": "0.1.0"`，与 SKILL.md frontmatter 一致。

### 校验（`tests/repo_checks.py` 新增）

```python
# local skill 必须有合法 version；vendored skill 有 version 字段则警告（不阻断）
```

### 版本递进规则（写入 CONTRIBUTING.md）

- skill 行为变更 → bump 其 `version`（patch：文案/阈值调整；minor：新增触发场景；major：行为不兼容变更）；
- skill 的 `version` bump **不强制**触发仓库 `VERSION` bump（仓库版本见方案三，按发布节奏走）。

### 改动清单

- `.agents/skills/cross-tool-memory/SKILL.md`：加 `version: 0.1.0`
- `skills-lock.json`：`cross-tool-memory` 条目加 `"version": "0.1.0"`
- `tests/repo_checks.py`：加 `skill-version` 检查
- `CONTRIBUTING.md`：加一小节说明规范
- 工作量估计：约 1 小时

---

## 方案三：`VERSION` 文件

### 规范

- 仓库根目录新增 `VERSION` 纯文本文件，内容为 `0.1.0`（+ 换行），与当前 git tag `v0.1.0` 对齐。
- 三位一体：`VERSION` 文件 = 唯一事实源；`CHANGELOG.md` 的 `## [x.y.z]` 标题与之对应；发布时打 `v<VERSION>` tag。

### 校验（`tests/repo_checks.py` 新增）

```python
# VERSION 文件内容必须等于 CHANGELOG.md 中最新的 ## [x.y.z] 版本号
```

（tag 一致性不在 CI 查——CI checkout 默认不拉全量 tags；发布 checklist 里人工核对。）

### 发布流程（写入 CONTRIBUTING.md）

1. `CHANGELOG.md` `[Unreleased]` 下记 entry；
2. 定版时：`[Unreleased]` → `## [x.y.z] - YYYY-MM-DD`，同步更新 `VERSION`；
3. 合并后打 tag `vx.y.z` 并推 tag。

### 改动清单

- 新增 `VERSION`（内容 `0.1.0`）
- `tests/repo_checks.py`：加 `version-file` 检查（VERSION ↔ CHANGELOG 最新版本号一致）
- `CONTRIBUTING.md`：发布流程小节
- 工作量估计：约 30 分钟

---

## 决策建议

| 方案 | 建议 | 理由 |
|---|---|---|
| 一（hooks） | C 方案确认，直接实施 `strict-guard` | B 已否决；skill-scoped hooks 只适合 opt-in 增强 |
| 二（skill version） | ✅ 已实施（本 PR） | 成本极低，收益明确 |
| 三（VERSION） | ✅ 已实施（本 PR） | 30 分钟，与现有 CHANGELOG/tag 体系互补 |
