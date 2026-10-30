# SESSION_STATE — 會話斷點

> **更新**：<YYYY-MM-DD> | **專案**：<PROJECT_NAME>
> **功能清單**：`gate/feature_list.json`（狀態以 `python3 gate/pass-gate.py status` 為準）
> **規則**：最多一頁。本文件超過一頁時，把已完成的工作移到
> `CHANGELOG.md`，這裡只留斷點。歷史不是狀態。

## Goal

- <本次會話要交付什麼，一行寫完>

## In progress

- `<feature_list id>`：<一行狀態>（或：無 — 執行 `pass-gate.py start --id <id>`）

## Next

- [ ] <下一個具體步驟>
- [ ] <下一個具體步驟>

## Blocked

- <阻塞項，或「無」>

## Last verification

- <最後執行的命令與結果，或「尚無」>
- 證據在 `gate/feature_list.json`（`evidence` 欄位）與
  `gate/events.jsonl`，不在這裡的文字裡。這裡的文字
  與功能清單不一致時，以功能清單為準。
