# SESSION_STATE — 会话断点

> **更新日期**：<YYYY-MM-DD> | **项目**：<PROJECT_NAME>
> **功能清单**：`gate/feature_list.json`（状态见 `python3 gate/pass-gate.py status`）
> **规则**：最多一页。超过一页时，把已完成的工作移到 `CHANGELOG.md`，这里只留断点。历史不是状态。

## 目标

- <本次会话要交付的东西，一句话>

## 进行中

- `<feature_list id>`：<一句话状态>（或：无——用 `pass-gate.py start --id <id>` 开始一项）

## 下一步

- [ ] <下一步具体动作>
- [ ] <下一步具体动作>

## 阻塞

- <阻塞项，或“无”>

## 最近一次验证

- <最近跑过的命令及结果，或“尚未验证”>
- 证据在 `gate/feature_list.json`（`evidence` 字段）和 `gate/events.jsonl` 里，不写在这份文件的散文里。本文件与功能清单不一致时，以功能清单为准。
