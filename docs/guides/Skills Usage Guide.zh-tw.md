# Skills 使用指南

> **Language / 語言**: [English](Skills%20Usage%20Guide.md) | [簡體中文](Skills%20Usage%20Guide.zh.md) | **繁體中文**

39 個內建 skill 在實戰中如何運作：哪些會自動觸發、哪些需要你明確調用，以及各自的使用時機。

## Skill 觸發機制

Claude Code 透過兩種方式決定載入 skill：

| 模式 | 方式 | 範例 |
|---|---|---|
| **自動 (Auto)** | Claude 讀取 skill 的 `description`，當你的請求相符時自動調用 | 你說「修這個 bug」→ `systematic-debugging` 自動載入 |
| **顯式 (Explicit)** | 你輸入斜線命令或直接點名 skill | 你輸入 `/comet` 或說「用 comet 處理這個任務」 |
| **混合 (Hybrid)** | 兩種皆可——上下文相符時自動觸發，亦可直接調用 | 你說「review 這個 PR」→ `open-code-review` 載入；或直接輸入 `/open-code-review` |

**關鍵洞見：** 自動觸發取決於每個 skill 的 `SKILL.md` 中的 `description` 欄位。
若 Claude 未按預期載入某個 skill，直接點名即可。

<!-- profiles:begin -->
## 部署設定檔

`deploy-agents.sh` / `deploy-agents.ps1` 會按層級部署 skills（Phase 4）。
預設層級為 `minimal`（15 個 skills）。使用
`--profile minimal | standard | full`（PowerShell：`-Profile`）選擇層級。成員關係
定義於 `skills-profiles.json`；下列清單必須與之相符
（CI §3r 會檢查這一點）。理由與每個 skill 的證據：
`docs/internal/skill-tiers.md`。

### minimal (default — 15 skills)

`verification-before-completion`、`systematic-debugging`、
`test-driven-development`、`living-documentation`、`writing-plans`、
`executing-plans`、`using-git-worktrees`、`subagent-driven-development`、
`requesting-code-review`、`codegraph`、`openspec-new-change`、
`openspec-propose`、`openspec-apply-change`、`openspec-verify-change`、
`openspec-archive-change`

### standard (20 skills)

Minimal 再加上：`comet`、`openspec-continue-change`、`openspec-update-change`、
`finishing-a-development-branch`、`dispatching-parallel-agents`

### full (39 skills)

`.agents/skills/` 中的全部 39 個 skill 目錄（見下方目錄）。
`docx` 與 `brainstorming` 是重量級 skills，只有同時傳入
`--include-heavy-skills` / `-IncludeHeavySkills` 時才會複製；若無該旗標，
full 只部署 37 個。
<!-- profiles:end -->

## Skill 分類目錄

> **Skill 領域**（限定範圍載入的命名空間）：每個 skill 屬於一個領域，
> 記錄於 `skills-lock.json` 並由 CI 強制校驗。只需要部分功能時，按領域載入，而非全量。
>
> | 領域 | Skills | 用途 |
> |---|---|---|
> | `openspec` | 17 | OpenSpec 規格驅動工作流程家族 |
> | `superpowers` | 15 | obra/superpowers 方法論家族 |
> | `local` | 6 | 倉庫自研（engineering-docs、living-documentation、open-code-review、option-review、cross-tool-memory、git-advanced） |
> | `document` | 2 | 文件處理（docx、pdf） |
> | `integration` | 2 | 外部工具整合（comet、codegraph） |
> | `utility` | 3 | 單一用途工具（caveman、ponytail、rtk） |
>
> **數量說明**：`skills-lock.json` 有 41 個條目，但本目錄只列 39 個 skill。
> 多出的 2 個（`openspec`、`superpowers`）是來源倉庫的 meta 條目——
> 僅作來源標記，非可安裝 skill。

### 1. 工作流程與流程控制

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `comet` | 顯式 | `/comet` | 版本化工作流程狀態機（階段、閘門、歸檔）。需要已安裝 Comet CLI，且專案中有 `.comet/config.yaml`。 | 專案使用 Comet 執行分階段任務時。每個專案先跑一次 `/comet init` 初始化，之後用 `/comet` 進入工作流程模式。未安裝 CLI 時，skill 會說明限制並回退至一般流程。 |
| `openspec-new-change` | 自動 | — | 啟動新的 OpenSpec 變更（規格驅動開發）。 | 開始需要先寫規格的功能／修復時。說「use openspec」或直接描述功能。 |
| `openspec-propose` | 自動 | — | 一步生成全部 OpenSpec 製成品。 | 想要快速產出規格草稿，跳過完整探索週期。 |
| `openspec-explore` | 混合 | — | 探索構想的思考夥伴模式。 | 需求模糊時。說「let's explore this with openspec」。 |
| `openspec-apply-change` | 自動 | — | 按既有 OpenSpec 變更實施任務。 | 規格通過後：「implement the openspec change」。 |
| `openspec-continue-change` | 自動 | — | 為進行中的變更建立下一個製成品。 | 恢復 OpenSpec 工作時：「continue the openspec change」。 |
| `openspec-update-change` | 混合 | — | 修訂既有 OpenSpec 製成品。 | 實施中途需要調整規格時。 |
| `openspec-verify-change` | 自動 | — | 驗證實作與規格製成品一致。 | 收尾前：「verify against the openspec」。 |
| `openspec-sync-specs` | 自動 | — | 把增量規格同步回主規格。 | 變更完成合併後。 |
| `openspec-archive-change` | 自動 | — | 歸檔已完成的變更。 | 合併後的最終清理。 |
| `openspec-bulk-archive-change` | 自動 | — | 批次歸檔多個已完成變更。 | 批次清理。 |
| `openspec-ff-change` | 自動 | — | 快進跳過製成品建立。 | 想跳過儀式感、直接開工時。 |
| `openspec-onboard` | 混合 | — | OpenSpec 工作流程引導。 | 第一次使用 OpenSpec 時：「onboard me to openspec」。 |
| `living-documentation` | 混合 | — | 維護規格／架構／參考／指南，帶追溯關係。 | 持續進行。文件任務會自動啟動；說「update living docs」可強制觸發。 |

### 2. 程式碼品質與審查

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `requesting-code-review` | 自動 | — | 決定**何時**需要審查（時機閘門）。 | 完成重要工作時自動觸發。 |
| `open-code-review` | 自動 | — | 確定性審查**方法**（檔案選取、規則比對、行級發現）。 | Diff/PR 時自動觸發。顯式調用：「review this diff with open-code-review」。 |
| `receiving-code-review` | 自動 | — | 在實作前處理收到的審查意見。 | 貼上審查意見時自動分診。 |
| `systematic-debugging` | 自動 | — | 結構化除錯：重現 → 隔離 → 假設 → 修復 → 驗證。 | 任何 bug、測試失敗或異常行為。在你提出修復方案前觸發。 |
| `test-driven-development` | 自動 | — | 強制紅—綠—重構循環。 | 實作功能／修復 bug 時。先寫測試。 |
| `verification-before-completion` | 自動 | — | 完成前檢查清單：執行測試、驗證聲明。 | 說「做完了」之前——強制用證據說話，而非斷言。 |

### 3. 規劃與設計

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `brainstorming` | 自動 | — | 在實作前探索意圖、需求與設計。**創造性工作前必須使用。** | 任何新功能、元件或行為變更。若 Claude 直接寫程式碼，說「brainstorm first」。 |
| `writing-plans` | 自動 | — | 從規格建立結構化實施計畫。 | 多步驟任務。有需求但尚無計畫時觸發。 |
| `executing-plans` | 自動 | — | 按計畫擔任實施者執行。 | 計畫通過後：「execute the plan」。 |
| `option-review` | 自動 | — | 對比 2 個以上可行方案，輸出決策矩陣。 | 難以抉擇時：「should I do A or B？」 |
| `dispatching-parallel-agents` | 自動 | — | 將獨立任務拆分給並行 subagent。 | 2 個以上獨立任務。說「do these in parallel」。 |
| `subagent-driven-development` | 自動 | — | 透過 subagent 編排實施。 | 大型計畫的獨立元件。 |
| `using-git-worktrees` | 自動 | — | 用 git worktree 隔離功能開發。 | 需要與當前分支隔離的工作開始前。 |
| `finishing-a-development-branch` | 自動 | — | 決定整合策略（merge/rebase/squash）。 | 實作完成且測試通過後。 |

### 4. 記憶與上下文

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `cross-tool-memory` | 自動 | — | 跨工具載入／儲存持久專案記憶。ai-memory MCP 不可用時回退至 `PROJECT_CONTEXT.md` / `SESSION_STATE.md`。 | 繼續先前工作時。自動載入相關上下文；說「remember this」可明確儲存。詳見下方[專案記憶設定](#專案記憶設定)。 |
| `using-superpowers` | 自動 | — | 在對話開始時建立 skill 探索協議。⚠️ 會在每次對話開始時觸發。 | 會話開始時自動觸發。確保 Claude 回覆前先檢查可用的 skills。 |

### 5. 開發工具

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `codegraph` | 自動 | — | 透過 CodeGraph MCP 進行語義程式碼探索。需要已安裝 CodeGraph CLI。 | 「Find where X is used」／「show callers of Y」。未安裝 CLI 時回退至 grep。 |
| `rtk` | 自動 | — | Rust Token Killer：將冗長的 CLI 輸出改寫為精簡形式。需要 RTK CLI。 | 自動壓縮吵雜的命令輸出。說「disable rtk」可查看原始輸出。 |
| `docx` | 混合 | — | 建立、讀取、編輯 Word 文件。 | 「Create a .docx report」或「read this Word file」。 |
| `pdf` | 混合 | — | 讀取／擷取 PDF 文字／表格。 | 「Summarize this PDF」或「extract tables from...」。 |
| `caveman` | 混合 | — | 超壓縮輸出模式（節省 token）。 | 「Be concise」／「caveman mode」。分級：lite、full、ultra。 |
| `ponytail` | 混合 | — | 強制採用最簡單可行的解法（反過度設計）。⚠️ 觸發範圍很廣（「任何程式設計任務」），可能意外觸發。 | 「Keep it simple」／Claude 過度設計時。 |
| `git-advanced` | 混合 | — | 進階 Git：衝突解決協議、cherry-pick/revert、`git bisect`、`git reflog`、命令速查。 | 「Resolve this merge conflict」／「cherry-pick this fix」／「which commit broke this？」。 |

### 6. Meta

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `diagnosing-superpowers` | 自動 | — | 診斷 superpowers 工作流程出錯的原因。 | Claude 忽視計畫、重複工作或表現異常時。說「diagnose what went wrong」。 |

### 7. 工程文件

| Skill | 觸發 | 斜線命令 | 作用 | 使用時機 |
|---|---|---|---|---|
| `engineering-docs` | 混合 | — | 15 個雙語範本，涵蓋 31 種研發文件類型（立項 → 需求 → 設計 → 測試 → 交付）。包含渲染規格（標題尺寸、字型、段落樣式），確保輸出一致。 | 撰寫任何正式研發文件時。說「write a PRD」／「write an HLD」，它會選用正確的範本。 |

## 專案記憶設定

### `PROJECT_CONTEXT.md` 和 `SESSION_STATE.md`

這是 ai-memory MCP 服務不可用時的檔案回退方案。
`cross-tool-memory` skill 會自動讀取它們。在執行 `deploy-agents.sh / .ps1` 或 `run-pipeline.sh / .ps1` 時，若目標專案缺少這兩個檔案，指令碼會**自動從範本初始化建立**。你也可以使用下方範本手動建立或自訂它們。

**何時建立：**
- `PROJECT_CONTEXT.md`：每個專案一次，架構穩定後建立。只在持久事實變更時更新（技術棧、約束、關鍵決策）。
- `SESSION_STATE.md`：每次重要工作會話結束時，或交接時更新。記錄已完成的工作、驗證證據與下一步。

**如何建立初始版本：**

直接問 Claude：
```text
Create PROJECT_CONTEXT.md for this project following the cross-tool-memory skill format.
```

或複製以下範本：

#### `PROJECT_CONTEXT.md` 範本

```markdown
# PROJECT_CONTEXT.md

> Durable project facts. Update only when architecture, constraints, or confirmed decisions change.
> Do not put session-specific status here — that goes in SESSION_STATE.md.

## Stack
- Language/framework:
- Build:
- Test:

## Architecture
- (Key components and their responsibilities)

## Constraints
- (Non-negotiable technical or policy constraints)

## Key Decisions
- YYYY-MM-DD: (Decision and rationale)
```

#### `SESSION_STATE.md` 範本

```markdown
# SESSION_STATE.md

> Current checkpoint. Update at meaningful task boundaries.
> Remove stale items; keep it scannable.

## Last Updated
- YYYY-MM-DD: (brief session summary)

## Completed
- (What was done, with verification evidence)

## In Progress
- (What's currently being worked on)

## Next Steps
- (What remains, in priority order)

## Open Risks / Questions
- (Unresolved issues or decisions needed)
```

**放在哪裡：** 專案根目錄。`cross-tool-memory` skill 會在根目錄找尋它們。

**目錄作用域：** 不要建立按目錄的記憶檔案。專案事實放在根目錄檔案中；
目錄級 `AGENTS.md` 只放本地邊界與約束。
