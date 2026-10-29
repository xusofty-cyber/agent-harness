# AI 工具與技能全景實戰指南（Claude Code / Codex / Antigravity IDE / Zed IDE）

> **Language / 語言**: [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [簡體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | **繁體中文**

本指南為使用 AI 代理進行軟體工程與技術文件撰寫提供全面的手冊：**應安裝哪些 skills 和 Harness 工具、底層的 token 經濟學、工具配置與接線、何時以及如何呼叫核心斜線命令（例如 `/comet`、`/plan`、`/opsx`、`codegraph`），以及端到端的實戰演練。**

---

## 目錄

1. [核心架構與工具矩陣（誰負責什麼）](#1-核心架構與工具矩陣誰負責什麼)
2. [Skills 與生態系工具盤點](#2-skills-與生態系工具盤點)
   - 2.1 39 個內建原生 Skills 分類
   - 2.2 版本鎖定、線上更新與 Skill 同步（`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`）
   - 2.3 可選的 Harness CLI 工具
   - 2.4 Skill 載入與可選 CLI 設定
   - 2.5 工程 Skills 與規則分派矩陣
3. [核心 Harness 工具與斜線命令深度解析](#3-核心-harness-工具與斜線命令深度解析)
   - 3.1 Comet：版本化工作流程進入點
   - 3.2 OpenSpec：規格驅動開發（`/opsx:propose`、`/opsx:apply` 等）
   - 3.3 Superpowers：TDD、系統化除錯與驗證閘門
   - 3.4 CodeGraph：可選的 MCP 程式碼圖整合
   - 3.5 Ponytail：最小實作階梯（生成閘門）
   - 3.6 Caveman：極致壓縮輸出（溝通閘門）
   - 3.7 RTK：輸出截斷與日誌遮蔽（執行閘門）
   - 3.8 Git 授權模型與受保護分支工作流程
   - 3.9 專案記憶與工作階段檢查點（`PROJECT_CONTEXT.md` / `SESSION_STATE.md`）
   - 3.10 8 項高風險操作保護矩陣
4. [平台特定的原生命令與最佳實踐](#4-平台特定的原生命令與最佳實踐)
   - 4.1 Google Antigravity CLI 與 IDE
   - 4.2 Claude Code 與 PreToolUse 用戶端 Hook
   - 4.3 ChatGPT 中的 Codex、Codex CLI 與 GitHub Copilot
   - 4.4 Zed IDE
5. [端到端實戰演練（真實功能開發）](#5-端到端實戰演練真實功能開發)
6. [每日健康檢查與故障排除](#6-每日健康檢查與故障排除)

---

## 1. 核心架構與工具矩陣（誰負責什麼）

若無實體邊界，AI 輔助開發經常會偏離方向、過度工程化或破壞向後相容性。我們的 Harness 架構強制執行五道連續的閘門：

```text
       [ User Request ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. Process & State Gate: Comet (/comet) + OpenSpec SDD │
       └──────┬─────────────────────────────────────────────────┘
              │ Scope locked; begin exploration & discovery
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. Optional semantic retrieval: CodeGraph MCP, if configured │
       └──────┬─────────────────────────────────────────────────┘
              │ Symbol dependencies clear; design & code
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. Code Gate: Superpowers (TDD red-green) + Ponytail   │
       └──────┬─────────────────────────────────────────────────┘
              │ Run tests & build commands
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. Optional command filtering: RTK CLI + agent hook          │
       └──────┬─────────────────────────────────────────────────┘
              │ Deliver & commit
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. Communication & Git: Caveman guidance (if loaded) + Git  │
       └────────────────────────────────────────────────────────┘
```

### 責任矩陣

| 元件 | 核心責任 | 解決的痛點 | 介面 |
|---|---|---|---|
| **Comet** | 版本化的 Native/Classic 工作流程 | 可續跑、可驗證的任務工作流程 | 遵循已安裝版本與 `.comet/config.yaml` |
| **OpenSpec** | 規格驅動開發（SDD） | 需求失憶、未追蹤的增量變更 | `/opsx:propose`、`docs/openspec/` 活文件 |
| **Superpowers** | TDD 與驗證證據閘門 | 幻覺式任務完成、缺少實體證明 | 紅色測試 $\rightarrow$ 綠色測試 $\rightarrow$ 驗證報告 |
| **CodeGraph** | 可選的語義程式碼搜尋整合 | 需要 CLI、agent MCP 接線與專案索引 | 透過已配置的 CodeGraph MCP 工具查詢 |
| **Ponytail** | 最小實作指引 Skill | 不必要的依賴與抽象 | 僅在宿主載入該 Skill 時提供指引 |
| **Caveman** | 精簡溝通指引 Skill | 過長的回應 | 載入時提供風格指引；保留清晰度與安全細節 |
| **RTK** | 可選的 Rust Token Killer CLI | 冗長的終端機輸出 | 需要安裝 CLI 與支援的 agent hook |
| **Git Auth** | 受保護分支指引外加有限的用戶端鉤子檢查 | 防止意外的共享分支操作 | 規則、Claude Code 用戶端鉤子與伺服器端分支保護 |

### 各程式設計工具的規則與記憶範圍

| 工具/介面 | 指示進入點 | 記憶範圍 |
|---|---|---|
| Codex desktop app | 專案 `AGENTS.md`；在已安裝應用程式暴露已配置 MCP/hooks 的地方，ai-memory 可以使用本地 Codex 整合 | 驗證確切的桌面版版本；ChatGPT 網頁版對話記憶是獨立的 |
| Codex CLI | Codex 家目錄，以及從倉庫根目錄到目前目錄的 `AGENTS.md` 檔案；ai-memory 上游安裝器支援 MCP/hooks | 專案上下文／檢查點檔案仍由倉庫管理 |
| Claude Code | 使用者／專案／目錄 `CLAUDE.md` 或支援的 `AGENTS.md` | 可選的 Auto memory 僅限本機且為 Claude 專屬；`/memory` 開啟其控制項 |
| Antigravity CLI | 全域、工作區與目錄 `AGENTS.md` / `.agents/rules/*.md`；ai-memory 上游支援 MCP/hooks | 在與 CLI 相同的環境中執行設定 |
| Antigravity IDE | 專案 Markdown 規則／技能，外加手動配置的 ai-memory MCP 伺服器 | MCP 提供明確的檢索／寫入工具；不宣稱會自動擷取生命週期 |

部署腳本負責寫入路徑；在假設檔案已被取用之前，請先查閱各宿主的最新文件和已載入的上下文。

---

## 2. Skills 與生態系工具盤點

### 2.1 39 個內建原生 Skills 分類

安裝程式將倉庫的 skill 目錄複製到 `.agents/skills/`；實際的探索行為取決於宿主工具及其配置。

#### 1. 版本化工作流程進入點
- **`comet`**：Comet CLI 提供版本化的 Native 和 Classic 工作流程。本倉庫僅提供進入點指南；不實作 Comet 階段守衛。

#### 2. OpenSpec 規格驅動套件（12 個 skills）
- **`openspec`**：核心架構。
- **`openspec-propose`**：一次性提出包含設計、規格和任務的變更。
- **`openspec-new-change`**：逐步建立產物。
- **`openspec-continue-change`**：將變更推進到下一個產物。
- **`openspec-ff-change`**：快速推進產物生成。
- **`openspec-apply-change`**：實作作用中變更的任務。
- **`openspec-verify-change`**：依據增量規格驗證程式碼。
- **`openspec-sync-specs`**：將增量規格同步到主規格。
- **`openspec-archive-change`**：封存已完成的變更。
- **`openspec-bulk-archive-change`**：平行封存多個變更。
- **`openspec-explore`**：建立變更前的互動式思考夥伴。
- **`openspec-onboard`**：引導式互動演練。
- **`write-openspec-docs`**：以內部風格撰寫文件。
- **`draft-openspec-docs`**：協作式逐節起草。
- **`verify-openspec-docs`**：事實查核文件聲明。
- **`release-openspec`**：發行稽核與變更集管理。

#### 3. Superpowers 工程品質套件（15 個 skills）
- **`superpowers`**：品質憲法。
- **`using-superpowers`**：Skills 探索與呼叫守衛。
- **`brainstorming`**：實作前的設計探索。
- **`writing-plans`**：逐步執行規劃。
- **`executing-plans`**：嚴格執行計畫。
- **`test-driven-development`**：TDD 紅綠循環。
- **`systematic-debugging`**：修改程式碼前的根本原因分析。
- **`verification-before-completion`**：聲稱完成前的強制證明。
- **`dispatching-parallel-agents`**：產生隔離的並行子代理。
- **`subagent-driven-development`**：子代理計畫執行框架。
- **`using-git-worktrees`**：隔離的實體工作區。
- **`finishing-a-development-branch`**：合併與整合決策。
- **`requesting-code-review`**：合併前審查驗證。
- **`open-code-review`**：確定性程式碼審查——規則優先、行錨定、覆蓋率強制。Tier A 透過 `ocr` CLI 委派，Tier B 為純方法論。
- **`receiving-code-review`**：對人工審查意見的技術評估。
- **`diagnosing-superpowers`**：稽核工作階段漂移或成本。

#### 4. 極簡程式碼與語法圖
- **`ponytail`**：最小實作階梯（標準函式庫優先，YAGNI）。
- **`codegraph`**：可選的 CodeGraph CLI/MCP 設定指引；安裝和代理接線是獨立步驟。

#### 5. 輸出過濾與簡潔交付
- **`rtk`**：可選的 Rust Token Killer CLI 指引；命令重寫需要已配置的代理 hook。
- **`caveman`**：超壓縮電報式輸出。

#### 6. 專業文件處理
- **`docx`**：Word 文件生成、編輯與樣式設定。
- **`pdf`**：PDF 文字/表格擷取與處理。

#### 7. 決策前審查、跨工具記憶與活文件（倉庫內 Skills）
- **`cross-tool-memory`**：跨工具專案範圍記憶導航與回憶輔助（搭配本地 ai-memory 後端）。
- **`option-review`**：決策前多選項審查，生成隔離的五維度決策矩陣。
- **`living-documentation`**：四層活文件套件（specs/architecture/reference/guides），具備基於 frontmatter 的程式碼-文件雙向追溯，支援 L0/L1/L2 變更影響閾值。
- **`engineering-docs`**：研發生命週期文件範本（31 種文件類型，15 個雙語階段閘門範本），確保跨 AI 代理的一致輸出，並與 Comet 階段閘門和活文件無縫整合。

---

### 2.2 版本鎖定、線上更新與 Skill 同步（`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`）

1. **`skills-lock.json`**：
   - 記錄外部 vendored skills 的上游來源與經 LF 正規化的 SHA256 完整性雜湊；
   - 區分本地撰寫的核心 skills（`sourceType: local`）與外部上游 skills（`sourceType: github`）。
2. **外部 Skill 上游同步（`tools/sync-skills.py`）**：
   - 內建的外部 vendored skills 更新器；
   - **檢查模式**：`python3 tools/sync-skills.py --check`（唯讀，比較本地與上游 `SKILL.md` 的雜湊，回報 🟢 已同步／🟡 已過時）；
   - **套用模式**：`python3 tools/sync-skills.py --apply`（就地更新過時的 `SKILL.md` 檔案並重新整理鎖定雜湊；本地撰寫的 skills 受到嚴格保護）；
   - 不帶參數呼叫時，由 `tools/tui.py` 驅動互動式終端機 UI；
   - 支援 `--skill <name>` 進行針對性更新，以及 `--json` 供自動化使用。
3. **活文件影響分析（`tools/doc-impact.py`）**：
   - 依據活文件追溯中繼資料分析程式碼變更（`docs/{specs,architecture,reference,guides,adr}/`）；
   - 支援工作樹檢查、提交基準線（`--since`）、明確檔案清單和互動式精靈模式（`--interactive`）。
4. **統一流水線執行器（`run-pipeline.sh` / `run-pipeline.ps1`）**：
   - 將完整工作流程串連為各作業系統的單次執行（部署 → AI 記憶 → Skills 同步 → 活文件影響）；
   - 互動式精靈：`./run-pipeline.sh`（Linux/macOS）或 `.\run-pipeline.ps1`（Windows）；
   - 無人值守自動化：`./run-pipeline.sh --all -y` 或 `.\run-pipeline.ps1 -All -Yes`。
5. **終端互動式 TUI 元件（`tools/tui.py`）**：
   - 提供鍵盤驅動的單選（方向鍵＋Enter）與多選（方向鍵＋空白鍵核取方塊切換＋Enter 確認）互動式選單；
   - 內建 TTY 與 ANSI 相容性偵測，在非互動式或非 ANSI 管道中優雅地退回為編號文字提示，作為所有部署與維護工具的基礎。
6. **整合式線上更新流程**：
   ```powershell
   # Windows
   .\deploy-agents.ps1 -ProjectPath "." -Update

   # Linux / macOS
   ./deploy-agents.sh . --update
   ```
   - 部署腳本會快轉範本倉庫，提示檢查/套用外部 skill 更新，並將受管檔案同步到目標專案，同時建立 `.bak.<timestamp>` 備份。

---

### 2.3 可選的 Harness CLI 工具

Skill 的可用性取決於宿主工具及其配置。終端層級的 CLI 工具為可選：
- **Comet CLI**：透過 `npm install -g @rpamis/comet@0.5.1` 安裝（2026-10-28 釘選；必須與 `skills-lock.json` 的 `comet.npmVersion` 相符）；提供 native/classic 工作流程執行與 `--comet-init` 初始化。
- **CodeGraph CLI**：絕不要把安裝器用管線傳給 shell。macOS/Linux——下載 `skills-lock.json` 中釘選的安裝器（`codegraph.installerUrl`），驗證其 SHA256 後再執行：
  ```bash
  curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/01e0ac3aa7419a7ab75583963e8a95359f3af1d3/install.sh -o /tmp/codegraph-install.sh
  echo "e8bbcc694584d5c88fa7c25103fc0f9c238d63a86c1494ca03448b680dbcc86e  /tmp/codegraph-install.sh" | sha256sum -c -
  sh /tmp/codegraph-install.sh
  ```
  或執行 `npm install -g @colbymchenry/codegraph@1.6.2`。Windows PowerShell——下載釘選的 `install.ps1`（`codegraph.installerUrlPs1`），驗證其 SHA256（`024091f428cac6eaa217bae8f840a9572a91daab974a8354085ba72f86f6aee1`）後再執行，或使用相同版本號的 npm 安裝。執行 `codegraph install` 接線 agent，並在專案中執行 `codegraph init`。
- **RTK (Rust Token Killer) CLI**：絕不要把安裝器用管線傳給 shell。macOS/Linux——下載 `skills-lock.json` 中釘選的安裝器（`rtk.installerUrl`），驗證其 SHA256 後再執行：
  ```bash
  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/7e92da00a5cf737dc87850505aa3dea603454613/install.sh -o /tmp/rtk-install.sh
  echo "7ca3997314f631b8ad267e5add9af4b7a2f0351bdab0b1c5a9b7ed4008d0434a  /tmp/rtk-install.sh" | sha256sum -c -
  sh /tmp/rtk-install.sh
  ```
  Windows：`winget install rtk-ai.rtk`（winget 沒有版本釘選——已知缺口，D13）。使用 `rtk gain` 驗證。在專案中執行 `rtk init` 以設定 agent hooks。
- **Open Code Review (OCR) CLI**：透過 `npm install -g @alibaba-group/open-code-review@1.13.3` 安裝（2026-10-28 釘選；必須與 `skills-lock.json` 的 `open-code-review.npmVersion` 相符）；透過 `open-code-review` skill 啟用 Tier A 零 LLM 成本委派審查。

部署腳本在初始設定期間會自動偵測這些可選的 CLI，並在適當時機引導安裝。

---

### 2.4 Skill 載入與可選 CLI 設定

Skill 的探索與上下文成本取決於宿主代理及其配置。僅有檔案存在並不保證 Skill 會被載入。Ponytail 和 Caveman 是隨專案複製的指引型 Skills；CodeGraph 和 RTK 還需要各自獨立的 CLI 和代理整合步驟。其效果取決於專案、宿主和設定，因此本指南不做固定的 token 節省承諾。

---

### 2.5 工程 Skills 與規則分派矩陣

| 場景 | 規則 / Skill | 觸發條件 / 關鍵字 | 預期行為 |
|---|---|---|---|
| **分支／提交／推送** | [`git-workflow.md`](../../.agents/rules/git-workflow.md) | `git commit` / `git push` | 僅在臨時分支上提交；不得 `git add .`；遠端推送需要人工授權 |
| **高風險操作** | [`security-boundary.md`](../../.agents/rules/security-boundary.md) | 修改建置配置、協定、公開結構 | 暫停並與人工確認影響 |
| **複雜需求** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` 或 "use openspec" | 在 `docs/openspec/changes/` 下提出變更；等待確認 |
| **符號探索** | [`token-discipline.md`](../../.agents/rules/token-discipline.md) + 可選的 `codegraph` | 已配置時的 CodeGraph MCP；否則使用限定範圍的 `rg` | 不要假設已安裝或可用 CodeGraph |
| **功能實作** | `ponytail` + `test-driven-development` | 視情況諮詢已載入的 Skills | 理解現有程式碼，然後選擇最小的正確實作與適當的驗證 |
| **Bug 調查** | `systematic-debugging` | 貼上錯誤追蹤 | 收集證據 $\rightarrow$ 形成假設 $\rightarrow$ 最小重現 $\rightarrow$ 修復 |
| **冗長終端機輸出** | 可選的 `rtk` | 僅在已安裝且其 agent hook 已配置時 | 否則使用原生的簡潔旗標；保留必要的驗證並保存相關日誌 |
| **Token 節省** | `caveman` | 僅在宿主載入該 Skill 或外掛時 | 保持簡潔，同時保留必要的上下文、技術準確性與安全細節 |
| **文件處理** | `docx` / `pdf` | 提及 `.docx` 或 `.pdf` | 專業排版，不執行程式碼測試套件 |
| **活文件與可追溯性** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `living-documentation` | `/living-documentation`／同步追溯文件 | 透過 L0/L1/L2 影響閾值與 frontmatter 可追溯性，維護四層文件（specs/architecture/reference/guides） |
| **階段閘門文件／範本** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `engineering-docs` | `/engineering-docs`／SRS/HLD/spec 請求 | 以 15 個雙語階段閘門範本統一各階段 AI agent 的輸出，並將 Comet 產物與活文件連結 |
| **程式碼審查與品質閘門** | `open-code-review` + `requesting-code-review` | 合併前或任務完成後 | 規則優先、行級錨定、覆蓋率強制；若存在 `ocr` CLI 則採 Tier A 委派，否則採 Tier B 方法 |
| **任務完成** | `verification-before-completion` | 任務結束時 | 出示實際命令執行證據 |

---

## 3. 核心 Harness 工具與斜線命令深度解析

### 3.1 Comet：版本化工作流程進入點

Comet 是獨立版本化的工作流程工具。請查看專案的 `.comet/config.yaml` 和已安裝的 CLI 版本，然後遵循該版本支援的 Native 或 Classic 工作流程。本倉庫的 Comet skill 僅為進入點指南；它不會建立 Comet 狀態檔或強制執行階段閘門。若未安裝或配置 Comet，請使用專案現有流程或制定適合任務的計畫。當與 `engineering-docs` 搭配使用時，每個階段（Open、Design、Build、Verify、Archive）都使用標準化的閘門範本以確保交付物的一致性。

```text
/comet Add date-range filtered CSV export for the order service
```

有關版本特定的進入點、配置、產物路徑和封存行為，請參閱 Comet 最新的上游文件。

---

### 3.2 OpenSpec：規格驅動開發

- `/opsx:propose <name>`：在 `docs/openspec/changes/` 下提出新的變更；
- `/opsx:apply`：實作已核准的變更；
- `/opsx:verify`：將實際實作與增量規格比較；
- `/opsx:sync`：將增量規格同步到主文件；
- `/opsx:archive`：將已完成的變更移至 `docs/openspec/changes/archive/`。

---

### 3.3 Superpowers：TDD、系統化除錯與驗證閘門

1. **TDD 紅綠循環**：
   - 根據規格場景撰寫失敗的測試；
   - 執行測試並觀察預期的失敗；
   - 撰寫最小程式碼使其通過；
   - 重構並執行驗證。
2. **系統化除錯**：
   - 步驟 1：追蹤收集；
   - 步驟 2：形成假設；
   - 步驟 3：最小重現測試；
   - 步驟 4：修復根本原因並驗證。
3. **驗證證據閘門**：
   - 沒有實體終端輸出證據，任務就不算完成。

---

### 3.4 CodeGraph：可選的 MCP 程式碼圖整合

```bash
# 探索呼叫鏈與架構
向為目前 agent 設定的 CodeGraph MCP 工具查詢：「使用者驗證與 JWT token 流程」。

# 尋找定義與全部呼叫參照
向已設定的 CodeGraph MCP 工具查詢 `OrderService::calculateDiscount`。
```

---

### 3.5 Ponytail：最小實作階梯

1. 這個功能真的需要存在嗎？（YAGNI）；
2. 是否有現成的工具可以重用？
3. 語言標準函式庫能做到嗎？
4. 重寫 10 行之前先改 1 行；
5. 修復錯誤時絕不順手重構。

---

### 3.6 Caveman：極致壓縮輸出

- 消除廢話：「好的，我來幫您處理」、「請注意這需要謹慎」；
- 交付：結論與影響 $\rightarrow$ Diff $\rightarrow$ 驗證證據。

---

### 3.7 RTK：可選的 Rust Token Killer CLI

- RTK 僅在已安裝並與作用中代理整合時才重寫支援的命令。僅有倉庫中的 Skill 並不會過濾終端輸出。
- 使用 `rtk gain` 驗證產品正確性；使用 `rtk init` 初始化支援的專案 hooks。
- 若未配置 RTK，請使用原生的簡潔旗標和有界的日誌處理。

- 絕不執行未加修飾的冗長命令；
- 始終使用 `git status -s`、`pytest -q`、`ctest --output-on-failure`；
- 將數百行的日誌重定向到本地暫存檔，僅截取失敗的追蹤部分。

---

### 3.8 Git 授權模型與受保護分支工作流程

1. **臨時分支隔離**：
   - 所有工作都在 `feature/*`、`fix/*`、`refactor/*` 中進行；
   - 絕不直接提交到 `develop`、`master`、`main`、`release*`、`staging`。
2. **遠端推送授權**：
   - AI 可以建立分支並在本地提交；
   - 推送到遠端或合併到受保護分支需要明確的人工確認。
3. **鐵律**：
   - `git push --force` 被永久禁止；
   - 禁止對受保護分支執行 rebase；
   - 禁止使用 `git add .` 進行盲目暫存（請使用 `git add <明確路徑>`）；
   - 提交訊息規範：`{type}: {description}`。

---

### 3.9 專案記憶與工作階段檢查點（`PROJECT_CONTEXT.md` / `SESSION_STATE.md`）

將記憶視為可驗證的摘要和導航輔助，而非程式碼或維護中文件的替代品：
1. **任務開始：** 僅在存在且相關時，才讀取 `PROJECT_CONTEXT.md`（已驗證的持久專案事實）與 `SESSION_STATE.md`（目前檢查點）；驗證影響任務的分支、配置與實作事實。
2. **工作期間：** 在多步驟工作需要時保留計畫。不要自動擷取提示、工具輸入／輸出、原始檔或終端機命令。
3. **有意義的收尾：** 以已完成的工作、實際驗證證據、剩餘步驟與仍相關的風險更新 `SESSION_STATE.md`；移除過時項目。僅在持久架構、約束或已確認決策變更時才更新 `PROJECT_CONTEXT.md`。無實質變更的工作階段不需要空更新。
4. **來源與衝突：** 標註不確定性，以及可能變更的日期／來源事實。目前的使用者指示與目前的程式碼／配置／可重現證據優先於記憶摘要。
5. **隱私：** 不要記錄憑證、私鑰、原始個人資料、完整對話／工具日誌或不必要的個人資訊。共享的全域範本絕不能包含私人使用者偏好。
6. **目錄範圍：** 目錄 `AGENTS.md` 只包含本地邊界與約束。預設不要建立目錄記憶檔案；專案事實與檢查點保留在其根目錄檔案中。

**Claude Code 原生 Auto memory** 是獨立的本機專案記憶，可以用 `/memory` 檢視、編輯或刪除。它不跨工具或機器共享，也不能取代上述專案檔案。Claude Code 負責管理此功能；本倉庫的部署器不會啟用、停用或擷取它。詳見 [Claude Code memory 文件](https://code.claude.com/docs/en/memory)。

#### 可選的跨 agent 記憶：ai-memory

本倉庫僅選擇 [ai-memory](https://github.com/akitaonrails/ai-memory) 作為可選的跨 agent 後端。它的本地 Markdown 與全文檢索路徑不使用 LLM、embedding 提供者或 API 金鑰。本倉庫不會自動安裝或啟動它。

若要讓一個倉庫選擇加入，請將 `.ai-memory.toml.example` 複製為被忽略的 `.ai-memory.toml`，取代 workspace/project 名稱，然後執行 `setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` 或 `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>`。輔助工具需要現有的 ai-memory 安裝，並將配置委派給其上游合併式命令。請檢視鉤子能力輸出；allowlist 模式僅對強制執行原生擷取政策的鉤子有效。

設定內容包括 Claude Code 與 Codex CLI 的 MCP/hooks，以及 Antigravity CLI 的 MCP/hooks。Codex 桌面版支援取決於已安裝的桌面版是否暴露本地 Codex 整合；請在應用程式中驗證。Antigravity IDE 僅支援 MCP：透過其 MCP 設定或記載的設定檔，將 `http://127.0.0.1:49374/mcp` 加入為 `serverUrl`。Docker 部署請執行 `docker run -d --name ai-memory --restart unless-stopped -p 127.0.0.1:49374:49374 -v "${HOME}/env/ai-memory-data:/data" docker.io/akitaonrails/ai-memory:latest`（容器儲存路徑固定為 `/data`）。ChatGPT 網頁版在免費本地設定中使用人工 Markdown 交接。

Windows 在上游同時支援 WSL2 與原生模式。請在啟動 agent 的同一個環境中安裝並設定 ai-memory；詳見 [Windows 指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md)。路徑排除不會塗銷任意的提示文字。使用 `ai-memory --data-dir <data-dir> backup --to <archive-path>` 備份；解除安裝會移除整合但不刪除資料。在刻意刪除之前，請先停止服務並驗證設定的資料目錄。關於平台路徑與 Docker 命令，詳見 [marker 參照](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md)與[安裝指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md)。

### 3.10 8 項高風險操作保護矩陣

在以下操作前必須經過人工確認：
- [ ] 1. 修改建置配置（`package.json`、`CMakeLists.txt`、`.pro`、`Cargo.toml`）；
- [ ] 2. 新增第三方依賴；
- [ ] 3. 修改全域公開資料結構（`public_struct.h`、`types.ts`）；
- [ ] 4. 修改核心分派單例或公開服務 API；
- [ ] 5. 變更線路協定或序列化契約（`protofile/`）；
- [ ] 6. 變更授權、密碼學或驗證程式碼；
- [ ] 7. 修改 `.gitignore` 或 CI/CD 流水線；
- [ ] 8. 影響共享契約或需要廣泛協調的高影響跨模組變更（僅檔案數量本身不是風險觸發條件）。

---

## 4. 平台特定的原生命令與最佳實踐

### 4.1 Google Antigravity CLI 與 IDE
- CLI 以 `agy` 執行；桌面版 IDE 是另一個介面。兩者都以檔案記載工作區／全域規則，但 CLI 斜線命令與 IDE 控制項各屬其介面。
- `/plan`：$\ge 3$ 個步驟的結構化任務規劃；
- `/goal`：直至驗證完成為止的無人值守自主迴圈；
- `/grill-me`：需求不明確時的互動式探索訪談；
- `/learn`：將經驗教訓記錄到 `tasks/lessons.md`；
- `/schedule`：背景計時器與週期性 cron 監控。

### 4.2 Claude Code 與 PreToolUse 用戶端 Hook
- `/compact`：token 數量偏高時壓縮對話歷史；
- `/cost`：即時的工作階段 token 用量；
- `/review`：審查工作副本的 diff；
- `@<path>`：按需動態載入特定規則。
- **安全鉤子**：`.claude/settings.json` 會對相符的工具呼叫執行 Claude Code 用戶端檢查。它可以拒絕選定的模式或發出警告；它不是作業系統控制項，也不是記憶收集器。

### 4.3 ChatGPT 中的 Codex、Codex CLI 與 GitHub Copilot
- Codex CLI 的文件記載 `AGENTS.md` 會從 Codex 家目錄與倉庫路徑一路探索到目前目錄。不得據此推斷 ChatGPT／桌面版有完全相同的行為；請查核其目前的產品行為與設定。
- `/hooks`：檢查並信任生命週期鉤子；
- `$comet`：在 Codex CLI 中觸發 Comet 狀態機；
- `@workspace`：在 VS Code 中掃描工作區上下文。

### 4.4 Zed IDE
- 沿用專案的 `AGENTS.md`；此安裝器不會建立 Zed 專用檔案；
- `Ctrl+Enter`（Inline Assist）搭配 `follow ponytail principles`；
- Assistant Panel（`Ctrl+?`）用於多輪架構規劃。

---

## 5. 端到端實戰演練（真實功能開發）

**需求**：「為訂單服務新增一個支援日期範圍篩選的 CSV 匯出端點。」

```text
Step 1: Session Ceremony & Breakpoint Awareness (Session Start)
  ├─ Prioritize reading PROJECT_CONTEXT.md & SESSION_STATE.md to restore architecture & resume from breakpoint
  ├─ Check tasks/lessons.md and tasks/todo.md (if present)
  └─ git checkout -b feature/order-csv-export

Step 2: Scoping & Change Creation (Comet + OpenSpec SDD)
  ├─ /comet Add date range CSV export endpoint
  ├─ Generated: docs/openspec/changes/add-csv-export/
  └─ Confirm Proposal with human

Step 3: Optional semantic retrieval (CodeGraph, if configured)
  ├─ Prohibited: grep -rn "export" .
  └─ Query configured CodeGraph MCP; otherwise use scoped code search
      └─ Located: router.py, order_repo.py, types.ts

Step 4: Red Test (Superpowers TDD)
  ├─ tests/test_export.py: Write failing test with invalid date range check
  └─ pytest tests/test_export.py -q -> FAILED (Red)

Step 5: Minimal Implementation (Ponytail)
  ├─ Python stdlib: import csv, datetime (no heavy export package)
  └─ Add filter condition in order_repo.py and route in router.py

Step 6: Green Verification (RTK)
  ├─ pytest tests/test_export.py -q -> PASSED (Green, 2 passed in 0.3s)
  └─ npm test -- packages/order --reporter=dot

Step 7: Delivery, Safe Commit & Selective Memory Closeout (Session Finish)
  ├─ Output: Concise diff and passing test evidence
  ├─ git add tests/test_export.py api/router.py repo/order_repo.py
  ├─ git commit -m "feat: add date-range CSV export endpoint"
  ├─ Ask human before git push
  ├─ Selective memory closeout:
  │   ├─ Update SESSION_STATE.md at meaningful task boundaries with actual evidence and remaining work
  │   └─ Update PROJECT_CONTEXT.md only when durable project facts change; skip empty updates
  ├─ Update tasks/todo.md
  └─ Archive OpenSpec change
```

---

## 6. 每日健康檢查與故障排除

### 每日健康檢查：
```bash
Check the installed Comet version and project configuration before using Comet-specific commands.
Read `tasks/lessons.md` when it is relevant to the task.
```

### 參考文件：
- 統一流水線執行器：
  - Windows: [`run-pipeline.ps1`](../../run-pipeline.ps1)
  - Linux / macOS: [`run-pipeline.sh`](../../run-pipeline.sh)
- 一鍵部署腳本：
  - Windows: [`deploy-agents.ps1`](../../deploy-agents.ps1)
  - Linux / macOS: [`deploy-agents.sh`](../../deploy-agents.sh)
- 維護工具：
  - 終端 UI 函式庫： [`tools/tui.py`](../../tools/tui.py)
  - Skill 同步工具： [`tools/sync-skills.py`](../../tools/sync-skills.py)
  - 活文件影響閘門： [`tools/doc-impact.py`](../../tools/doc-impact.py)
- 部署與配置指南：
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md)
- 規則架構：
  - [`Global AGENTS.md`](../../templates/agents/Global%20AGENTS.md)
  - [`Project AGENTS.md`](../../templates/agents/Project%20AGENTS.md)
  - [`Directory AGENTS.md`](../../templates/agents/Directory%20AGENTS.md)
