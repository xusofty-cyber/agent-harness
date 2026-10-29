# 图 — <LOOP_NAME>

> **循环**：<goal-loop | maker-checker> | **目标**：`<goal.md 路径>`
> **规则**：这张图就是契约。超时与停止条件由 runner 强制执行，批准节点
> 由人把关。图与 runner 不一致时，以 runner 的事件日志为准——改图。

## 节点

| 节点 | 类型 | 负责人 | 说明 |
|---|---|---|---|
| maker | agent | <maker> | 产出或修改产物 |
| verify | deterministic | runner | 跑 verify/checker 命令，退出 0 = 通过 |
| timeout-enforcer | deterministic | runner | 超时的命令直接杀掉，记一条 timeout 事件 |
| event-log | deterministic | runner | 每轮/每次状态变化记一条事件，永不改写 |
| approval | human | <批准人> | 决定采纳还是打回（见“批准”一节） |
| merge | deterministic | runner | 合并：只有满足合并规则才执行 |

类型：`agent`（做判断）、`deterministic`（同样输入同样输出——命令、检查、日志）、`human`（只负责批准）。

## 边

| 从 | 到 | 条件 |
|---|---|---|
| maker | verify | maker 退出 0 |
| maker | maker | maker 失败——下一轮修改 |
| verify | approval | verify 连续通过 N 轮 |
| verify | maker | verify 失败或超时——下一轮修改 |
| approval | merge | 人批准 |
| approval | maker | 人打回——下一轮修改 |
| verify | human-escalation | 到最大轮次仍未满足通过条件 |

## 共享状态字段

- `loop-state.json`：kind、goal_id、status、round、consecutive_passes、
  max_rounds、timeout_s、max_seconds、rounds[]（每轮一条记录）
- `loop-events.jsonl`：只追加、序号单调；审计链
- `maker/` 与 `checker/`：工作目录（maker-checker 类型）；
  checker 永远只能看到列出的产物，每轮新复制

## 路由规则

- 一轮通过只看 verify 退出 0；超时算失败，要记录。
- 连续通过 N 轮、到最大轮次、或到总时间预算——先到先停。到最大轮次
  或预算而停是失败，不是完成。
- maker 绝不写 checker 的结论；checker 绝不改产物。

## 批准

- 发生了什么：<循环在第 N 轮达到通过条件>
- 改了什么：<循环产出或修改的文件>
- 为什么需要人：<为什么这事得人来定、不是 runner——如“把一条新仓库检查合进分支”>
- 批准：<后果——如“合并进行，结果提交”>
- 打回：<后果——如“循环回到 maker，打回记为一条事件”>

## 超时

- 单条命令超时：60 秒（默认值——按你的循环调整；runner 强制执行；超时会
  杀掉命令并记一条 `timeout` 事件——已用比超时更长的 `sleep` 实测验证，
  见阶段记录）。
- 总时间预算：<N> 秒（0 = 不限）；超了记一条 `budget_exceeded`
  事件，循环失败。

## 并行展开 / 合并

- 并行展开：<并行分支，各自在独立的 git worktree 里，目录隔离、不共享文件>
- 合并规则：<all must pass | any one passes>——全部通过才合并（all must
  pass），或一个分支通过就够（any one passes）。
- 合并：<分支结果如何合回——如“把各分支改过的文件拷回主 clone，重跑 repo_checks，按分支提交”>
