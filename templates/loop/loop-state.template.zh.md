# 循环状态 — <LOOP_NAME>

> **类型**：maker-checker | **目标**：`<goal.md 路径>`
> **状态**：running | awaiting-approval | complete | failed
> **规则**：每轮一行，由 runner 写——绝不手工改。Checker 每轮只能看到
> 列出的产物（新复制进 `checker/`），看不到 maker 的笔记。一轮是否通过，
> 只看 checker 命令是否真正退出 0。

## 目标

- <一句话：这个循环在产出什么>

## 各轮

| 轮次 | Maker 改了什么 | Checker 发现了什么 | 结果 | 下一步 |
|---|---|---|---|---|
| 1 | <maker 的改动> | <checker 的发现> | pass / fail / timeout | <下一步，停止则写“—”> |

## 连续通过

- <n> / <要求轮数>——达到要求轮数停止，或到最大轮次 <N>

## 批准

- 申请：<轮次，或“—”> | 批准人：<名字，或“—”> | 备注：<文字>

## 最近一次验证

- <最近一次 checker 命令及结果，或“尚未验证”>
- 完整记录：`loop-state.json`（各轮）与 `loop-events.jsonl`（只追加的事件）。
  文字与 JSON 不一致时，以 JSON 为准。
