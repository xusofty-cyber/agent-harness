# Skills 使用指南

> **Language / 语言**: [English](Skills%20Usage%20Guide.md) | [简体中文](Skills%20Usage%20Guide.zh.md) | **繁體中文** | [Français](Skills%20Usage%20Guide.fr.md) | [Deutsch](Skills%20Usage%20Guide.de.md)

42 個內建 skill 在實戰中如何運作：哪些自動觸發、哪些需要顯式調用，以及各自的使用時機。

## Skill 觸發機制

Claude Code 透過兩種方式決定載入 skill：

| 模式 | 方式 | 範例 |
|---|---|---|
| **自動 (Auto)** | Claude 讀取 skill 的 `description`，當你的請求相符時自動調用 | 你說「修這個 bug」→ `systematic-debugging` 自動載入 |
| **顯式 (Explicit)** | 你輸入斜線命令或直接點名 | 你輸入 `/comet` 或說「用 comet 處理這個任務」 |
| **混合 (Hybrid)** | 兩種皆可——上下文相符時自動觸發，亦可直接調用 | 你說「review 這個 PR」→ `open-code-review` 載入；或直接輸入 `/open-code-review` |

**關鍵：** 自動觸發依賴每個 skill 的 `SKILL.md` 中的 `description` 欄位。
若 Claude 未按預期載入某個 skill，直接點名即可。

## Skill 分類速查

### 1. 工作流與流程控制

| Skill | 觸發 | 命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `comet` | 顯式 | `/comet` | 版本化工作流狀態機（階段、閘門、歸檔）。需安裝 Comet CLI 且專案中有 `.comet/config.yaml`。 | 專案使用 Comet 執行分階段任務時。每個專案先跑一次 `/comet init` 初始化，之後用 `/comet` 進入工作流模式。未安裝 CLI 時 skill 會說明限制並回退至普通流程。 |
| `openspec-new-change` | 自動 | — | 啟動新的 OpenSpec 變更（規格驅動開發）。 | 開始需要先寫規格的功能/修復時。說「use openspec」或直接描述功能。 |
| `openspec-propose` | 自動 | — | 一步生成全部 OpenSpec 製成品。 | 想要快速產出規格草稿，跳過完整探索週期。 |
| `openspec-explore` | 混合 | — | 探索構想的思考夥伴模式。 | 需求模糊時。說「用 openspec 探索一下」。 |
| `openspec-apply-change` | 自動 | — | 按既有 OpenSpec 變更實施任務。 | 規格通過後：「implement the openspec change」。 |
| `openspec-continue-change` | 自動 | — | 為進行中的變更建立下一個製成品。 | 恢復 OpenSpec 工作時：「continue the openspec change」。 |
| `openspec-update-change` | 混合 | — | 修訂既有 OpenSpec 製成品。 | 實施中途需要調整規格。 |
| `openspec-verify-change` | 自動 | — | 驗證實作與規格製成品一致。 | 收尾前：「verify against the openspec」。 |
| `openspec-sync-specs` | 自動 | — | 把增量規格同步回主規格。 | 變更完成合併後。 |
| `openspec-archive-change` | 自動 | — | 歸檔已完成的變更。 | 合併後的最終清理。 |
| `openspec-bulk-archive-change` | 自動 | — | 批次歸檔多個已完成變更。 | 批次清理。 |
| `openspec-ff-change` | 自動 | — | 快進跳過製成品建立。 | 想跳過儀式感、直接開工。 |
| `openspec-onboard` | 混合 | — | OpenSpec 工作流引導。 | 第一次使用：「onboard me to openspec」。 |
| `living-documentation` | 混合 | — | 維護規格/架構/參考/指南，帶溯源關係。 | 持續。文檔任務自動啟動；說「update living docs」強制觸發。 |

### 2. 程式碼品質與審查

| Skill | 觸發 | 命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `requesting-code-review` | 自動 | — | 決定**何時**需要審查（時機閘門）。 | 完成重要工作時自動觸發。 |
| `open-code-review` | 自動 | — | 確定性審查**方法**（檔案選取、規則比對、行級發現）。 | Diff/PR 時自動觸發。顯式：「用 open-code-review 審查這個 diff」。 |
| `receiving-code-review` | 自動 | — | 處理收到的審查意見。 | 貼上審查意見時自動分診。 |
| `systematic-debugging` | 自動 | — | 結構化除錯：重現→隔離→假設→修復→驗證。 | 任何 bug、測試失敗、異常行為。在你提出修復方案前觸發。 |
| `test-driven-development` | 自動 | — | 強制紅-綠-重構循環。 | 實作功能/修復 bug 時。先寫測試。 |
| `verification-before-completion` | 自動 | — | 完成前檢查清單：跑測試、驗證斷言。 | 說「做完了」之前——強制用證據說話。 |

### 3. 規劃與設計

| Skill | 觸發 | 命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `brainstorming` | 自動 | — | 在實作前探索意圖、需求和設計。**創造性工作前必須使用。** | 新功能、元件、行為變更。若 Claude 直接寫程式碼，說「先 brainstorm」。 |
| `writing-plans` | 自動 | — | 從規格生成結構化實施計畫。 | 多步驟任務。有需求但無計畫時觸發。 |
| `executing-plans` | 自動 | — | 按計畫實施。 | 計畫通過後：「execute the plan」。 |
| `option-review` | 自動 | — | 對比 2+ 可行方案，輸出決策矩陣。 | 難以抉擇時：「A 還是 B 好？」 |
| `dispatching-parallel-agents` | 自動 | — | 將獨立任務拆分給並行 subagent。 | 2+ 獨立任務。說「並行做」。 |
| `subagent-driven-development` | 自動 | — | 透過 subagent 編排實施。 | 大型計畫的獨立元件。 |
| `using-git-worktrees` | 自動 | — | 用 git worktree 隔離功能開發。 | 需要與當前分支隔離的工作。 |
| `finishing-a-development-branch` | 自動 | — | 決定整合策略（merge/rebase/squash）。 | 實作完成、測試通過後。 |

### 4. 記憶與上下文

| Skill | 觸發 | 命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `cross-tool-memory` | 自動 | — | 跨工具載入/保存持久專案記憶。ai-memory MCP 不可用時回退至 `PROJECT_CONTEXT.md` / `SESSION_STATE.md`。 | 繼續先前工作時。自動載入相關上下文；說「記住這個」顯式保存。詳見下方[專案記憶設定](#專案記憶設定)。 |
| `using-superpowers` | 自動 | — | 會話開始時建立 skill 發現協議。 | 會話開始時自動觸發。確保 Claude 回覆前先檢查可用 skill。 |

### 5. 開發工具

| Skill | 觸發 | 命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `codegraph` | 自動 | — | 透過 CodeGraph MCP 進行語義程式碼探索。需安裝 CodeGraph CLI。 | 「X 在哪被使用」/「Y 的調用者有哪些」。未安裝 CLI 時回退至 grep。 |
| `rtk` | 自動 | — | Rust Token Killer：將冗長終端輸出改寫為精簡版。需 RTK CLI。 | 自動壓縮吵雜輸出。說「disable rtk」查看原始輸出。 |
| `docx` | 混合 | — | 建立/讀取/編輯 Word 文件。 | 「生成 .docx 報告」或「讀取這個 Word 檔案」。 |
| `pdf` | 混合 | — | 讀取/擷取 PDF 文字/表格。 | 「總結這個 PDF」或「擷取表格」。 |
| `caveman` | 混合 | — | 超壓縮輸出模式（節省 token）。 | 「簡潔點」/「caveman mode」。分級：lite、full、ultra。 |
| `ponytail` | 混合 | — | 強制最簡可行方案（反過度設計）。 | 「保持簡單」/ Claude 過度設計時。 |

### 6. 元技能

| Skill | 觸發 | 命令 | 作用 | 使用時机 |
|---|---|---|---|---|
| `writing-skills` | 自動 | — | 指導 skill 的建立/編輯/驗證。 | 在 `.agents/skills/` 下建立或修改 skill 時。 |
| `diagnosing-superpowers` | 自動 | — | 診斷 superpowers 工作流出錯的原因。 | Claude 忽視計畫、重複工作、表現異常時。說「診斷哪裡出問題了」。 |

## 專案記憶設定

### `PROJECT_CONTEXT.md` 和 `SESSION_STATE.md`

這是 ai-memory MCP 服務不可用時的檔案回退方案。
`cross-tool-memory` skill 會自動讀取它們。在執行 `deploy-agents.sh / .ps1` 或 `run-pipeline.sh / .ps1`（及快捷入口 `pipeline.sh / .ps1`）時，若目標專案缺少這兩個檔案，指令碼會**自動從範本初始化建立**。亦可在任何時候透過問答或下方範本手動初始化。

**何時建立：**
- `PROJECT_CONTEXT.md`：每個專案一次，架構穩定後建立。只在持久事實變更時更新（技術棧、約束、關鍵決策）。
- `SESSION_STATE.md`：每次重要工作會話結束時，或交接時更新。記錄完成的工作、驗證證據、下一步。

**如何建立初始版本：**

直接問 Claude：
```text
按 cross-tool-memory skill 的格式，為這個專案建立 PROJECT_CONTEXT.md。
```

或複製以下範本：

#### `PROJECT_CONTEXT.md` 範本

```markdown
# PROJECT_CONTEXT.md

> 持久專案事實。只在架構、約束或確認決策變更時更新。
> 會話級狀態放 SESSION_STATE.md，不要放這裡。

## 技術棧
- 語言/框架：
- 建置：
- 測試：

## 架構
- （關鍵元件及職責）

## 約束
- （不可協商的技術或政策約束）

## 關鍵決策
- YYYY-MM-DD：（決策及理由）
```

#### `SESSION_STATE.md` 範本

```markdown
# SESSION_STATE.md

> 當前檢查點。在有意義的任務邊界更新。
> 刪除過時項，保持可掃讀。

## 最後更新
- YYYY-MM-DD：（本次會話簡述）

## 已完成
- （做了什麼，附驗證證據）

## 進行中
- （正在做什麼）

## 下一步
- （還剩什麼，按優先順序）

## 開放風險 / 問題
- （未解決的問題或待決策事項）
```

**放哪裡：** 專案根目錄。`cross-tool-memory` skill 會在根目錄找尋它們。

**目錄作用域：** 不要建立按目錄的記憶檔案。專案事實放根目錄檔案；
目錄級 `AGENTS.md` 只放本地邊界和約束。
