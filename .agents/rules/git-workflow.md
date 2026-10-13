# Git Workflow & Authorization Model (Git 工作流与授权模型)

> **适用场景**：任何 Git 操作、分支管理、代码提交与远端推送。
> **核心原则**：**AI 仅被允许在本地修改与临时分支上操作；触碰共享远端（Push / Merge / 删除远端分支）一律必须人类明确授权。**
>
> **读者说明**：本文面向 AI Agent；人类贡献者同样遵守约束条款——其中的"人类明确授权"
> 即指你本人确认，AI 专属动作步骤（如"向人类出具 Diff 概览"）可忽略。
> 人类快速通道：`git checkout -b feature/xxx` → 改代码 → `git commit` →
> `git push origin feature/xxx` → GitHub 网页开 PR。
>
> **术语**：`<protected>` = 受保护分支（`develop`/`master`/`main`/`release*`/`staging`）；
> `<DEFAULT_BRANCH>` = 本仓库主干（此处为 `main`；其他项目以其 `Project AGENTS.md` 为准）。
>
> 本文件只收录**常驻约束**（每次会话必须遵守）。低频操作手册
> （冲突解决、cherry-pick、bisect 等）已拆分为按需加载的 `git-advanced` skill。
>
> ⚠️ "Hook 硬拦截"仅在 **Claude Code** 下生效（`.claude/hooks/guard.mjs`）；
> 其他工具无 Hook 机制，"永久禁止"依赖 Agent 自觉遵守本文件约束。

---

## 1. 核心授权矩阵（做什么、要不要授权）

| 操作类别 | 具体操作 | 是否需授权 | 行为规范与硬拦截 |
|---|---|---|---|
| **本地读取** | `git status`, `git log`, `git diff`, `git fetch` | 否 | 放行（只读操作，鼓励先查后动） |
| **本地分支** | `git checkout -b <type>/xxx` | 否 | 放行（新需求一律走临时分支） |
| **临时分支提交** | 在临时分支改代码 / `git commit` | 按用户指令与项目政策 | 用户已明确要求提交时直接执行；否则交付 Diff，不把每次提交默认设为确认门 |
| **本地冲突处理** | 临时分支上 `git merge origin/<protected>` | 否（本地） | 放行（**严禁在受保护分支上解冲突**） |
| **受保护分支直改** | **在 develop / master / main / release* / staging 上直接 commit** | — | **永久禁止（Hook 硬拦截）** |
| **推送/合入共享分支** | 推送到受保护分支或合入受保护分支 | **必须人类明确授权，或用户当前指令已明确授权** | 看清目标分支和 refspec；仅在当前分支判断不足以确认目标 |
| **临时分支推送** | 推送本地临时分支到共享远端 | **必须人类明确授权，或用户当前指令已明确授权** | 仅保留本地直到获授权 |
| **历史改写** | **`git push --force` / `-f` / `--force-with-lease`** | — | **永久禁止（Hook + 规则硬拦截）** |
| **受保护分支 rebase** | **在受保护分支上执行 `git rebase`** | — | **永久禁止（Hook 硬拦截）** |
| **删除受保护远端** | `git push origin --delete develop/master/main...` | — | **永久禁止（Hook 硬拦截）** |
| **删除临时远端分支** | `git push origin --delete feature/xxx` | **必须人类明确授权** | 先确认该分支已合并：`git branch -r --merged origin/<DEFAULT_BRANCH>` |
| **绕过式推送** | `git push origin <A>:<DEFAULT_BRANCH>` | 同「推送受保护分支」 | **必须人类明确授权** |

---

## 2. 四大钢铁纪律（Iron Laws）

> §1 的浓缩版——记住这四条即记住核心：

1. **受保护分支零直接提交**（`develop`/`master`/`main`/`release*`/`staging` 只能 merge 合入）。
2. **严禁历史改写与强制推送**（`force push`、受保护分支 `rebase` 永久禁止；回滚用 `git revert`）。
3. **防误提交纪律**：禁止 `git add .` / `git add -A`；必须通过 `git add <明确路径>` 逐个添加。
4. **冲突一律在临时分支解决，且必须与人类协同**（AI 永远不自动选一方；详细协议见 `git-advanced` skill）。

---

## 3. 禁止操作速查（Never List）

```bash
# ❌ 永远禁止，无需请示、直接拒绝：
git push --force / git push -f          # 破坏远端历史（§1）
git push origin --delete main           # 删除受保护远端分支（§1）
git clean -xdf                          # 删除 .gitignore 外所有文件（Hook 硬拦截）

# 🔒 未经人类明确授权时禁止（授权后按 §4 流程执行）：
git push origin main                    # 直接推受保护分支（§1：需授权）
git push origin <A>:main                # 绕过式推送到受保护分支（§1：需授权）

# ⚠️ 需人类明确确认后才可执行：
git reset --hard HEAD~N                 # 丢失提交（仅限恢复本地误操作）
git commit --amend                      # 仅允许修改尚未 push 的提交
```

---

## 4. 标准协作流程（Feature 合入主干）

> `<DEFAULT_BRANCH>` 指本项目的主干分支（如 `main` / `master` / `develop`），
> 以 `Project AGENTS.md` 中声明的为准；下文命令中的占位符请替换为实际分支名。

```text
[确保工作区干净] → [git fetch origin] → [对齐主干: git checkout <DEFAULT_BRANCH> && git merge --ff-only]
       │
       ▼
[切临时分支: git checkout -b {type}/short-description]
       │
       ▼
[本地实现代码 + 运行单测通过]
       │
       ▼
[向人类出具 Diff 概览与 Commit 提议] ──(确认后)──► [执行 git commit]
       │
       ▼
[拉取远端最新变化并在 feature 分支解冲突: git merge origin/<DEFAULT_BRANCH>]
       │
       ▼
[向人类请求合入与推送授权] ──(未获授权)──► [停下并输出待执行命令]
       │ (已获明确授权)
       ▼
[回受保护分支 merge 并推送]:
  git checkout <DEFAULT_BRANCH>
  git merge --no-ff {type}/short-description
  git push origin <DEFAULT_BRANCH>
  git branch -d {type}/short-description
```

---

## 5. Commit 前 / Push 前自查清单

```text
Commit 前自查:
- [ ] git branch --show-current 确认不在受保护分支上？
- [ ] git fetch origin 已执行，远端无领先提交（或已在临时分支同步）？
- [ ] git status 确认只含预期文件（无构建产物、临时文件、敏感配置）？
- [ ] 相关测试已通过（单测 / repo_checks / lint，按项目要求）？
- [ ] 用户已明确要求提交（或当前指令已授权）？

Push 前自查:
- [ ] git fetch origin 已执行，本地不落后于远端？
- [ ] 推送目标分支确认无误（看清 refspec，尤其 <A>:<B> 形式）？
- [ ] 用户已明确授权此次推送（或当前指令已授权）？
- [ ] 推送的是临时分支，而非受保护分支？
```

---

## 6. 命名与提交规范

### 分支命名

| 类型 | 格式 | 示例 |
|---|---|---|
| 功能开发 | `feature/<short-description>` | `feature/export-endpoint` |
| Bug 修复 | `fix/<short-description>` | `fix/empty-input-crash` |
| 热修复 | `hotfix/<short-description>` | `hotfix/auth-bypass` |
| 重构 | `refactor/<short-description>` | `refactor/split-pipeline` |
| 文档/杂项 | `docs/<short-description>`、`chore/<short-description>` | `docs/update-readme` |

- 一律小写短横线分隔，禁用中文与空格。

### 提交信息

统一遵循 Conventional Commits：`<type>[optional scope]: <description>`，
例如 `feat(api): add export endpoint`、`fix: handle empty input`、`docs: clarify setup`。

**正文纪律**：正文建议包含测试结果，便于审查者判断变更可信度：

```text
<type>[scope]: <一句话描述，动词开头，<72字符>

- 变更点1：做了什么，为什么

Test-Result:
- <测试项>: <结果>
```

**类型前缀**：`feat`/`add`（新功能）、`fix`/`resolve`（Bug）、`refactor`（重构）、
`perf`（性能）、`docs`/`chore`（文档/配置）、`remove`（删除）。

---

## 7. 高级操作（按需加载 skill）

以下低频操作已拆分为 `git-advanced` skill，需要时调用：

| 场景 | Skill 章节 | 安全要点（常驻） |
|---|---|---|
| 冲突解决 | §1 冲突协同协议 | 永远不自动选一方；仅在临时分支解决 |
| Cherry-pick | §2 Cherry-pick 与回退 | 禁止直接 cherry-pick 到受保护分支后 push |
| 回退 | §2 回退矩阵 | 已 push→`revert`；未 push→`reset`；单文件→`restore --source` |
| Bug 定位 | §3 Git Bisect | — |
| 灾难恢复 | §4 Git Reflog | `reset --hard` 需人类确认 |
| 命令速查 | §5 速查表 | — |

---

## 8. 常见踩坑防护（Gotchas）

### 意图消歧："提交"一词三义

| 用户说法 | 默认解释 | 授权要求 |
|---|---|---|
| "提交一下" / "commit 一下" | `git commit`（本地，不 push） | 按 §1"临时分支提交"；先出 Diff 概览再执行 |
| "推送" / "推上去" / "push" | `git push`（远端） | 必须人类明确授权 |
| "合并" / "合入" / "合到主干" | §4 完整流程 | 必须人类明确授权 |

### 意图消歧："回退"决策树

用户说"回退"时按顺序确认：

1. **哪个提交？**（默认 HEAD；多个本地提交时向人类确认 hash）
2. **Push 过吗？**（`git log origin/<branch>..HEAD --oneline` 只读检查）
   - 已 push → 必须 `git revert`（在临时分支执行，走 §4 流程）
   - 未 push → 可 `git reset`
3. **改动还要吗？**（仅未 push 时问）
   - 保留 → `git reset --soft HEAD~1`
   - 丢弃 → `git reset --hard HEAD~1`（⚠️ 需人类明确确认）

### 其他陷阱

- **口令模糊陷阱**：用户输入"提交推送"时可能指"提交当前改动"，也可能指"合入主干并推送到远端"。**务必先确认目标分支与推送意图再动手**。
- **Hook 生效机制**：`.claude/settings.json` 或 `.ww/settings.json` 中的 Hook 脚本在客户端启动会话时加载；修改 Hook 配置后需重开会话方能生效。
- **Revert 后再次 merge 陷阱**：revert 了 feature 的 merge 后再次 merge 同一分支，改动会"消失"（git 认为已在历史中）。解决：先 revert 那个 revert commit，再 merge。详见 `git-advanced` §2。
