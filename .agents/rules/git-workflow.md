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
| **删除临时远端分支** | `git push origin --delete feature/xxx` | **必须人类明确授权** | 先确认该分支已合并：`git branch -r --merged origin/develop` |
| **绕过式推送** | `git push origin <A>:<develop>` | 同「推送受保护分支」 | **必须人类明确授权** |

---

## 2. 标准协作流程（Feature 合入主干）

```
[确保工作区干净] → [git fetch origin] → [对齐主干: git checkout develop && git merge --ff-only]
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
[拉取远端最新变化并在 feature 分支解冲突: git merge origin/develop]
       │
       ▼
[向人类请求合入与推送授权] ──(未获授权)──► [停下并输出待执行命令]
       │ (已获明确授权)
       ▼
[回受保护分支 merge 并推送]:
  git checkout develop
  git merge --no-ff {type}/short-description
  git push origin develop
  git branch -d {type}/short-description
```

---

## 3. 四大钢铁纪律（Iron Laws）

1. **受保护分支零直接提交**：
   - `develop` / `master` / `main` / `release*` / `staging` 分支只能通过 `merge` 合入，严禁直接在上面改代码并 commit。
2. **严禁历史改写与强制推送**：
   - 永久禁止 `force push`、`git rebase` 受保护分支。
   - 线上已合入代码的回滚一律使用 `git revert -m 1`，保持历史线性透明。
3. **防误提交纪律（禁止盲目 `git add .` / `git add -A`）**：
   - 严禁全量 add！本纪律用于防止将本地临时大文件、自动保存文件（如 `*.autosave`）、构建产物（`image/`、`build/`、`dist/`）、以及含敏感配置的本地文件误带入仓库；
   - 必须通过 `git add <明确路径>` 单独添加预期文件。
4. **冲突一律在临时分支解决**：
   - 遇到合并冲突时，必须在 feature 临时分支上 `merge origin/develop` 解决并验证，绝不在 develop 主干上解冲突。

---

## 4. 提交信息（Commit Message）格式规范

统一遵循 Conventional Commits：`<type>[optional scope]: <description>`，例如 `feat(api): add export endpoint`、`fix: handle empty input`、`docs: clarify setup`。

---

## 5. 常见踩坑防护（Gotchas）

- **口令模糊陷阱**：用户输入“提交推送”时可能指“提交当前改动”，也可能指“合入主干并推送到远端”。**务必先确认目标分支与推送意图再动手**。
- **分支混淆检查**：提交任何改动前，必须自检 `git branch --show-current`，确保不在受保护分支上。
- **Hook 生效机制**：`.claude/settings.json` 或 `.ww/settings.json` 中的 Hook 脚本在客户端启动会话时加载；修改 Hook 配置后需重开会话方能生效。
