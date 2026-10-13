# Git Workflow & Authorization Model (Git 工作流与授权模型)

> **适用场景**：任何 Git 操作、分支管理、代码提交与远端推送。
> **核心原则**：**AI 仅被允许在本地修改与临时分支上操作；触碰共享远端（Push / Merge / 删除远端分支）一律必须人类明确授权。**
>
> 本文件只收录**常驻约束**（每次会话必须遵守）。低频操作手册
> （冲突解决、cherry-pick、bisect 等）已拆分为按需加载的 `git-advanced` skill。

---

## 1. 核心授权矩阵（做什么、要不要授权）

| 操作类别 | 具体操作 | 是否需授权 | 行为规范与硬拦截 |
|---|---|---|---|
| **本地读取** | `git status`, `git log`, `git diff`, `git fetch` | 否 | 放行（只读操作，鼓励先查后动） |
| **本地分支** | `git checkout -b <type>/xxx` | 否 | 放行（新需求一律走临时分支） |
| **临时分支提交** | 在临时分支改代码 / `git commit` | 按用户指令与项目政策 | 用户已明确要求提交时直接执行；否则交付 Diff，不把每次提交默认设为确认门 |
| **本地冲突处理** | 临时分支上 `git merge origin/<protected>` | 否（本地） | 放行（**严禁在受保护分支上解冲突**） |
| **受保护分支直改** | **在 develop / master / main / release* 上直接 commit** | — | **永久禁止（Hook 硬拦截 exit 1）** |
| **推送/合入共享分支** | 推送到受保护分支或合入受保护分支 | **必须人类明确授权，或用户当前指令已明确授权** | 看清目标分支和 refspec；仅在当前分支判断不足以确认目标 |
| **临时分支推送** | 推送本地临时分支到共享远端 | **必须人类明确授权，或用户当前指令已明确授权** | 仅保留本地直到获授权 |
| **历史改写** | **`git push --force` / `-f` / `--force-with-lease`** | — | **永久禁止（Hook + 规则硬拦截 exit 1）** |
| **受保护分支 rebase** | **在受保护分支上执行 `git rebase`** | — | **永久禁止（Hook 硬拦截 exit 1）** |
| **删除受保护远端** | `git push origin --delete develop/master/main...` | — | **永久禁止（Hook 硬拦截 exit 1）** |
| **删除临时远端分支** | `git push origin --delete feature/xxx` | **必须人类明确授权** | 先确认该分支已合并：`git branch -r --merged origin/<DEFAULT_BRANCH>` |
| **绕过式推送** | `git push origin <A>:<DEFAULT_BRANCH>` | 同「推送受保护分支」 | **必须人类明确授权** |

---

## 2. 四大钢铁纪律（Iron Laws）

1. **受保护分支零直接提交**：
   - `develop` / `master` / `main` / `release*` / `staging` 分支只能通过 `merge` 合入，严禁直接在上面改代码并 commit。
2. **严禁历史改写与强制推送**：
   - 永久禁止 `force push`、`git rebase` 受保护分支。
   - 线上已合入代码的回滚一律使用 `git revert`（在临时分支上执行，走正常合入流程，见 §7）。
3. **防误提交纪律（禁止盲目 `git add .` / `git add -A`）**：
   - 严禁全量 add！本纪律用于防止将本地临时大文件、自动保存文件（如 `*.autosave`）、构建产物（`image/`、`build/`、`dist/`）、以及含敏感配置的本地文件误带入仓库；
   - 必须通过 `git add <明确路径>` 单独添加预期文件。
4. **冲突一律在临时分支解决，且必须与人类协同**：
   - 遇到合并冲突时，必须在 feature 临时分支上 `merge origin/<DEFAULT_BRANCH>` 解决并验证，绝不在 `<DEFAULT_BRANCH>` 主干上解冲突；
   - **AI 永远不自动选择一方覆盖另一方**（详细协议见 `git-advanced` skill）。

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

钢铁纪律是"不能做什么"，本清单是"动手前必须确认什么"：

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

- 一律小写短横线分隔，禁用中文与空格；
- 分支名即意图声明，`feature/` 前缀的分支只做该功能，不顺手修无关 Bug。

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

- **口令模糊陷阱**：用户输入"提交推送"时可能指"提交当前改动"，也可能指"合入主干并推送到远端"。**务必先确认目标分支与推送意图再动手**。
- **分支混淆检查**：提交任何改动前，必须自检 `git branch --show-current`，确保不在受保护分支上。
- **Hook 生效机制**：`.claude/settings.json` 或 `.ww/settings.json` 中的 Hook 脚本在客户端启动会话时加载；修改 Hook 配置后需重开会话方能生效。
- **Rebase vs Merge**：临时分支同步主干用 `merge`（保留历史）；**永远不要在受保护分支上 rebase**。
- **Revert 后再次 merge 陷阱**：revert 了 feature 的 merge 后再次 merge 同一分支，改动会"消失"（git 认为已在历史中）。解决：先 revert 那个 revert commit，再 merge。详见 `git-advanced` §2。
