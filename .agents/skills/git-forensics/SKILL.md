---
name: git-forensics
description: Use when you need to find which commit introduced a bug (git bisect), recover lost commits or branches (git reflog), or investigate repository history forensics. Low-frequency advanced Git operations — not for everyday commit/push workflows (see git-workflow.md rules instead).
version: 0.1.0
---

# Git Forensics — Bisect & Reflog

Advanced Git investigation tools for bug hunting and disaster recovery.
For everyday workflows (commit, push, branch, merge, conflict resolution),
follow `.agents/rules/git-workflow.md` instead.

---

## Git Bisect — 二分定位引入 Bug 的 commit

```bash
git bisect start
git bisect bad                    # 当前 HEAD 有 bug
git bisect good <known-good>      # 标记一个已知正常的 commit
# Git 自动 checkout 中间点，测试后标记 good/bad，重复直到找到 first bad commit
git bisect reset                  # 结束，回到原分支
```

**自动化**：`git bisect run ./test.sh` — 脚本返回 0=good，非 0=bad，125=skip（无法测试）。

```bash
# 只在某个路径范围内 bisect（缩小范围）
git bisect start -- src/

# bisect 中途发现当前 commit 无法编译，跳过
git bisect skip

# 查看 bisect 过程中的所有标记
git bisect log
```

**实用技巧**：
- 选择 `good` 基准时，尽量选离 HEAD 较近的已知正常点，减少二分步数；
- 自动化脚本中，编译失败应返回 125（skip）而非 1（bad），避免误判。

---

## Git Reflog — 恢复误操作

Reflog 记录 HEAD/分支的每次移动（commit、reset、rebase、checkout……），即使 commit 已不在任何分支上：

```bash
git reflog                        # 查看操作历史
git reflog --date=relative        # 带相对时间戳
git reset --hard HEAD@{1}         # 回到上一次操作前的状态（⚠️ 需人类确认）
git branch recovery <hash>        # 从 reflog 找回误删分支的 tip
git show HEAD@{2.hours.ago}       # 时间表达式
```

### 常见恢复场景

| 场景 | 操作 |
|---|---|
| 误 `git reset --hard` | `git reflog` 找到 reset 前的 hash → `git reset --hard <hash>` |
| 误删分支 | `git reflog --all \| grep <branch>` 找到 tip → `git branch <name> <hash>` |
| rebase 出错 | `git reflog` 找到 `rebase (start)` 之前的状态 → `git reset --hard HEAD@{N}` |
| amend 后想找回原 commit | `HEAD@{1}` 即 amend 前的版本 |

### ⚠️ Reflog 限制

- **本地独有**：不推送远端，每台机器独立；
- **有过期时间**：默认 90 天（`gc.reflogExpire` 可配置）；
- 新 clone 的仓库没有历史 reflog。
