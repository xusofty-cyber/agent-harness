# Git Workflow & Authorization Model (Git 工作流与授权模型)

> **适用场景**：任何 Git 操作、分支管理、代码提交与远端推送。
> **核心原则**：**AI 仅被允许在本地修改与临时分支上操作；触碰共享远端（Push / Merge / 删除远端分支）一律必须人类明确授权。**

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

## 2. 标准协作流程（Feature 合入主干）

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

## 3. 四大钢铁纪律（Iron Laws）

1. **受保护分支零直接提交**：
   - `develop` / `master` / `main` / `release*` / `staging` 分支只能通过 `merge` 合入，严禁直接在上面改代码并 commit。
2. **严禁历史改写与强制推送**：
   - 永久禁止 `force push`、`git rebase` 受保护分支。
   - 线上已合入代码的回滚一律使用 `git revert`，保持历史线性透明（见 §8）。
3. **防误提交纪律（禁止盲目 `git add .` / `git add -A`）**：
   - 严禁全量 add！本纪律用于防止将本地临时大文件、自动保存文件（如 `*.autosave`）、构建产物（`image/`、`build/`、`dist/`）、以及含敏感配置的本地文件误带入仓库；
   - 必须通过 `git add <明确路径>` 单独添加预期文件。
4. **冲突一律在临时分支解决**：
   - 遇到合并冲突时，必须在 feature 临时分支上 `merge origin/<DEFAULT_BRANCH>` 解决并验证，绝不在 `<DEFAULT_BRANCH>` 主干上解冲突。

---

## 4. 提交信息（Commit Message）格式规范

统一遵循 Conventional Commits：`<type>[optional scope]: <description>`，例如 `feat(api): add export endpoint`、`fix: handle empty input`、`docs: clarify setup`。

**正文纪律**：提交信息正文建议包含测试结果，便于审查者判断变更可信度：

```text
<type>[scope]: <一句话描述，动词开头，<72字符>

- 变更点1：做了什么，为什么
- 变更点2：做了什么，为什么

Test-Result:
- <测试项>: <结果>
```

### 类型前缀参考

| 场景 | 推荐前缀 |
|---|---|
| 新功能 | `feat`, `add` |
| Bug 修复 | `fix`, `resolve` |
| 重构 | `refactor`, `simplify` |
| 性能 | `perf`, `optimize` |
| 文档/配置 | `docs`, `chore` |
| 删除/清理 | `remove`, `cleanup` |

---

## 5. 分支命名规范

| 类型 | 格式 | 示例 |
|---|---|---|
| 功能开发 | `feature/<short-description>` | `feature/export-endpoint` |
| Bug 修复 | `fix/<short-description>` | `fix/empty-input-crash` |
| 热修复 | `hotfix/<short-description>` | `hotfix/auth-bypass` |
| 重构 | `refactor/<short-description>` | `refactor/split-pipeline` |
| 文档/杂项 | `docs/<short-description>`、`chore/<short-description>` | `docs/update-readme` |

- 一律小写短横线分隔，禁用中文与空格；
- 分支名即意图声明，`feature/` 前缀的分支只做该功能，不顺手修无关 Bug。

---

## 6. Commit 前 / Push 前自查清单

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

## 7. 冲突解决协议（与人类协同）

**核心原则：每个冲突必须与人类协同解决，AI 永远不自动选择一方覆盖另一方。**

```bash
git status                    # "both modified" = 冲突文件
git diff <conflict-file>      # 查看具体冲突内容
# 手动编辑解决后：
git add <resolved-file>
git merge --continue          # 或 git rebase --continue / git cherry-pick --continue
# 放弃：git merge --abort / git rebase --abort / git cherry-pick --abort
```

### 冲突标记含义

```text
<<<<<<< HEAD
（当前分支的代码）
=======
（incoming：远端或被合并分支的代码）
>>>>>>> origin/main
```

### 协同决策流程

1. 向人类报告：冲突文件列表 + 每个冲突块的两边含义；
2. 两边是独立功能 → 建议都保留；
3. 同一行双方都改 → 合并语义（不是简单二选一）；
4. 不确定时 → 问人类，不猜。

### 特殊情况

- **二进制文件冲突**（如图片、压缩包）：无法文本合并，必须问人类选哪一方（`git checkout --ours/--theirs` 仅在人类明确指示后使用）；
- **stash pop 冲突**：解决后 `git add` 即可，无需 commit，手动 `git stash drop` 清理；
- **重复冲突**：可启用 `git config --global rerere.enabled true` 让 Git 记住解决方式。

---

## 8. Cherry-pick 与回退（Revert）

### Cherry-pick

```bash
git cherry-pick -x <commit-hash>    # -x 在 message 中记录来源，便于追溯
git cherry-pick A..B                # 批量（不含 A，含 B）
git cherry-pick -n <hash>           # --no-commit：只入暂存区，适合合并多个为一个 commit
```

- Cherry-pick 后**必须重新验证**（测试/检查）；
- **禁止直接 cherry-pick 到受保护分支后 push**——先在临时分支操作，走正常合入流程；
- 冲突时解决 → `git add` → `git cherry-pick --continue`（或 `--abort` 放弃）。

### 回退矩阵

| 场景 | 推荐操作 | 原因 |
|---|---|---|
| 回退已 push 的错误 commit | `git revert <hash>` | 不改写历史，安全 |
| 回退 merge commit | `git revert -m 1 <hash>` | `-m 1` 保留主干 parent |
| 回退未 push 的本地 commit | `git reset --soft HEAD~1` | 改动保留在暂存区 |
| 只回退某个文件 | `git restore --source=<commit> -- <path>` | 精确控制影响范围 |
| 批量回退 | `git revert -n A..B && git commit` | 合并为一个 revert commit |

### ⚠️ Revert 后再次 merge 陷阱

```text
场景：revert 了 feature 分支的 merge → 再次 merge 同一分支 → 改动"消失"了
原因：git 认为这些 commit 已在历史中（revert ≠ 没进来过）
解决：先 revert 那个 revert commit，再 merge
```

---

## 9. Bisect 与 Reflog（问题定位与恢复）

### Git Bisect — 二分定位引入 Bug 的 commit

```bash
git bisect start
git bisect bad                    # 当前 HEAD 有 bug
git bisect good <known-good>      # 标记一个已知正常的 commit
# Git 自动 checkout 中间点，测试后标记 good/bad，重复直到找到 first bad commit
git bisect reset                   # 结束，回到原分支
```

自动化：`git bisect run ./test.sh`（脚本返回 0=good，非 0=bad，125=skip）。

### Git Reflog — 恢复误操作

Reflog 记录 HEAD/分支的每次移动（commit、reset、rebase、checkout……），即使 commit 已不在任何分支上：

```bash
git reflog                        # 查看操作历史
git reset --hard HEAD@{1}         # 回到上一次操作前的状态
git branch recovery <hash>        # 从 reflog 找回误删分支的 tip
```

- Reflog 是本地独有，不推送远端；默认保留 90 天；
- `git reset --hard` 误操作后，第一反应应该是查 reflog 而不是 panic。

---

## 10. 禁止操作速查（Never List）

```bash
# ❌ 永远禁止，无需请示、直接拒绝：
git push --force / git push -f          # 破坏远端历史
git push origin main                    # 直接推受保护分支
git push origin <A>:main                # 绕过式推送到受保护分支
git push origin --delete main           # 删除受保护远端分支
git clean -xdf                          # 删除 .gitignore 外所有文件

# ⚠️ 需人类明确确认后才可执行：
git reset --hard HEAD~N                 # 丢失提交（仅限恢复本地误操作）
git commit --amend                      # 仅允许修改尚未 push 的提交
git revert                              # 回滚线上代码的标准方式（优先于 reset）
```

---

## 11. 常用命令速查

```bash
git fetch origin                                  # 同步远端引用（只读，鼓励先查后动）
git log HEAD..origin/main --oneline               # 远端是否领先（有输出=需先同步）
git branch --show-current                         # 当前分支（提交前必查）
git status --short                                # 工作区状态速览
git diff HEAD --stat                              # 当前改动概览
git log --oneline -20                             # 最近 20 条提交
git show <commit>                                 # 查看某提交详情
git log --follow -- <file>                        # 单文件变更历史
git stash push -m "WIP: xxx"                      # 暂存当前工作
git stash pop                                     # 恢复暂存
git restore --staged <file>                       # 取消 stage（不丢改动）
```

---

## 12. 常见踩坑防护（Gotchas）

- **口令模糊陷阱**：用户输入"提交推送"时可能指"提交当前改动"，也可能指"合入主干并推送到远端"。**务必先确认目标分支与推送意图再动手**。
- **分支混淆检查**：提交任何改动前，必须自检 `git branch --show-current`，确保不在受保护分支上。
- **Hook 生效机制**：`.claude/settings.json` 或 `.ww/settings.json` 中的 Hook 脚本在客户端启动会话时加载；修改 Hook 配置后需重开会话方能生效。
- **Rebase vs Merge**：临时分支同步主干用 `merge`（保留历史）；**永远不要在受保护分支上 rebase**。
