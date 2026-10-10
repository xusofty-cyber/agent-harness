# Agent Harness

> **Language / 語言**: [English](README.md) | [簡體中文](README_zh.md) | **繁體中文** | [Français](README.fr.md) | [Deutsch](README.de.md)

> **可複用的 AI 程式設計規範範本、Claude Code 安全攔截鉤子與多工具部署指令碼**

本專案提供全域、專案和目錄級規範範本、Claude Code PreToolUse 鉤子、技能檔案，以及 Windows/Linux/macOS 部署指令碼。各工具的規則載入方式和鉤子能力不同；請以支援矩陣和部署指令碼實際行為為準。鉤子屬於客戶端機制，不是作業系統或伺服器端安全邊界。

---

## 核心特性

1. **三級 AGENTS.md 漸進式揭露架構**：
   - **全域級（[`Global AGENTS.zh-tw.md`](Global%20AGENTS.zh-tw.md)）**：跨專案通用工程憲法，涵蓋溝通、實現、上下文與 Git 授權邊界。
   - **專案級（[`Project AGENTS.zh-tw.md`](Project%20AGENTS.zh-tw.md)）**：可自訂裁剪的專案工程範本，提供 CLI 命令、技術棧、架構邊界和按需規則索引。
   - **目錄級（[`Directory AGENTS.zh-tw.md`](Directory%20AGENTS.zh-tw.md)）**：Monorepo / 獨立子模組的微型邊界修補程式（In/Out Scope、依賴隔離與極速測試）。
   - **細粒度子規則庫（[`.agents/rules/`](.agents/rules/)）**：按需動態查閱，涵蓋 `token-discipline.md`、`engineering-spec.md`、`security-boundary.md` 與 `git-workflow.md`。

2. **Claude Code 客戶端鉤子（[`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/)）**：
   - 僅針對 Claude Code 中相符的工具呼叫執行，非作業系統層級防護；
   - 使用 Node.js 守衛指令碼透過 stdin JSON 讀取工具輸入（Claude Code 官方協定），以 `exit 2` / `permissionDecision: deny` 實現可靠阻斷；
   - 永久硬攔截（`exit 2`）：受保護分支（`develop`/`master`/`main`/`release*`）直接提交、`git push --force`、刪除受保護遠端分支、受保護分支 rebase；
   - 部分命令會直接拒絕，其他情況提供非阻斷警告；正則檢查無法涵蓋所有命令變形，亦無法取代 Git 伺服器端分支保護。

3. **42 個可複用技能目錄（[`.agents/skills/`](.agents/skills/)）**：
   - **Comet 整合指引**：引導檢查已安裝版本與專案配置；此技能本身不實作 Comet 狀態機或階段守衛。
   - **活體文件與程式碼追溯**：`living-documentation`（四階文件體系：specs/architecture/reference/guides，Frontmatter 雙向追溯關聯，L0/L1/L2 變更門禁與文件演進）。
   - **規範驅動開發（SDD）**：`openspec` 全套 16 個技能（提案、變更應用、驗證、主規格同步、歸檔）。
   - **測試驅動開發（TDD）**：`superpowers` 全套 15 個技能（TDD 紅綠循環、系統性排障、完工驗證證據門、工作區隔離）。
   - **實現與檢索指引**：`ponytail`（極簡實作決策階梯）與 `codegraph`（CodeGraph 可選整合指引；CLI/MCP 需單獨安裝配置）。
   - **輸出與表達指引**：`rtk`（Rust Token Killer 可選 CLI 指引；需配置命令重寫 Hook）與 `caveman`（精簡表達 Skill）。
   - **事前決策評審與共享記憶**：`option-review`（5 維度多候選方案事前獨立評審與決策矩陣）與 `cross-tool-memory`（跨工具專案長期記憶導航與經驗檢索）。
   - **專業文件處理**：`docx`（Word 專業排版）、`pdf`（結構化擷取與分析）；
   - **技能使用與觸發時機指南**：各 skill 的觸發機制（自動/顯式/混合）、分類速查與專案記憶使用說明詳見 [`Skills Usage Guide.zh-tw.md`](Skills%20Usage%20Guide.zh-tw.md)（[English](Skills%20Usage%20Guide.md) | [简体中文](Skills%20Usage%20Guide.zh.md) | [Français](Skills%20Usage%20Guide.fr.md) | [Deutsch](Skills%20Usage%20Guide.de.md)）。

4. **一鍵部署、互動精靈與統一流水線（`deploy-agents` & `pipeline`）**：
   - **互動式終端逐步選擇精靈**：執行指令碼時不帶任何參數（或顯式指定 `--interactive` / `-Interactive`）將自動拉起精靈（上下方向鍵選擇、空白鍵切選、Enter 確認），引導完成規則範本語言（`en`, `zh`, `zh-tw`, `fr`, `de`）、部署範圍（`project`, `global`, `both`）、目標專案路徑、12 種 Agent 橋接檔案多選（Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy）以及可選工作流程開關，徹底杜絕命令列參數遺漏與拼寫錯誤；
   - **跨平台統一工程流水線執行器**（[`run-pipeline.sh`](run-pipeline.sh) / [`pipeline.sh`](pipeline.sh) 與 [`run-pipeline.ps1`](run-pipeline.ps1) / [`pipeline.ps1`](pipeline.ps1)）：一鍵按序貫通 4 大工程生命週期階段（規則分發與橋接部署 → AI 跨工具長效記憶配置 → 外部技能同步與雜湊鎖定 → 活體文檔溯源分析與質檢門禁），同時支援互動式自選與全自動無人值守（`--all -y` / `-All -Yes`）模式；
   - Windows PowerShell（[`deploy-agents.ps1`](deploy-agents.ps1)，內建 UTF-8 相容與 Junction 免提權穿透）與 Linux/macOS Bash（[`deploy-agents.sh`](deploy-agents.sh)）；
   - 專案指令碼自動建立 `AGENTS.md`（若不存在）、Claude Code 與 Copilot 橋接，並部署 Claude Code 鉤子；支援多語言切換（`-Language` / `--lang`）；
   - `--global` 配置 Claude Code、Antigravity 與 Codex 全域規則；`--global --update` 覆蓋前自動備份；
   - `--update` 透過 fast-forward 更新範本倉庫並同步檔案；部署後可選偵測並配置 CodeGraph、RTK、Open Code Review 與 Comet CLI。

5. **可選跨工具專案記憶（`ai-memory`）**：
   - 本地優先方案；不配置 LLM、embedding provider 或 API Key 亦可使用；普通部署指令碼不強制常駐；
   - 自動擷取需透過被 Git 忽略的 `.ai-memory.toml` 顯式加入專案，並以 allowlist 模式安裝上游鉤子；
   - 專用輔助指令碼透過上游合併式 CLI 配置各客戶端；Antigravity 2.0 與 IDE 透過共用全域配置接入 MCP。

### 支援範圍

| 工具 | 本倉庫提供的配置/接線 | 狀態 |
|---|---|---|
| Claude Code | `CLAUDE.md` 橋接、`.claude/skills/` 連結、`.claude/settings.json` 鉤子 | 指令碼自動配置；鉤子僅在 Claude Code 客戶端執行 |
| Antigravity 2.0 / CLI / IDE 與擴充套件 | 專案規則/技能目錄；`--global` 寫入 `~/.gemini/AGENTS.md` 和 `GEMINI.md` 相容指標 | 支援雙全域檔名；早期 IDE 可跟隨指標讀取規範檔案 |
| Codex | 全域 `$CODEX_HOME/AGENTS.md`（預設 `~/.codex/AGENTS.md`）、專案 `AGENTS.md` 與 `.agents/skills/` | `-Global` 初始化全域檔案；`-Global -Update` 備份後覆蓋生效規則 |
| ai-memory | Claude Code、Codex CLI、Antigravity CLI 的可選 MCP/hooks；Antigravity 2.0 與 IDE 提供 MCP-only 設定 | 專案顯式選擇加入；ChatGPT 網頁版手動 Markdown 交接 |
| GitHub Copilot | `.github/copilot-instructions.md` 橋接 | 指令碼自動配置；具體行為依 Copilot 版本/模式 |
| Zed | `AGENTS.md` 檔案 | 提供可複用檔案；指令碼不建立 Zed 專屬配置 |
| Pi / OpenCode | 未提供專用入口或指令碼驗證 | 未適配；不可據此推斷自動載入 |

---

## 目錄結構

```text
agent-harness/
├── .agents/
│   ├── rules/                       # 細粒度工程子規則庫（按需漸進式載入）
│   │   ├── engineering-spec.md      # SDD 規範先行、TDD 驗證證據門
│   │   ├── git-workflow.md          # Git 授權模型、受保護分支強隔離、提交規範
│   │   ├── security-boundary.md     # 八大高風險操作防呆矩陣、憑證零洩漏
│   │   └── token-discipline.md      # 讀拿說三道閘門、上下文防漏與日誌截斷
│   └── skills/                      # 42 個原生工程技能庫（Comet, OpenSpec, Superpowers...）
├── .claude/
│   ├── settings.json                # Claude Code PreToolUse 安全攔截配置
│   └── hooks/                       # 安全攔截鉤子指令碼（Node.js，讀取 stdin JSON）
│       ├── guard.mjs                # Bash 工具守衛（exit 2 硬阻斷）
│       └── guard-write.mjs          # Write/Edit 工具守衛（高危預警）
├── Global AGENTS.md                 # 全域規則範本（部署至各工具全域入口）
├── Project AGENTS.md                # 專案根目錄標準範本與中樞路由器
├── Directory AGENTS.md              # Monorepo / 子模組邊界隔離微型修補程式
├── Multi-Tool Deployment and Configuration Guide.zh-tw.md # 跨工具部署與配置指南（繁體中文）
├── Multi-Tool Deployment and Configuration Guide.md       # 跨工具部署與配置指南（英文）
├── Tools Practical Usage and Skills Panorama Guide.zh-tw.md # 技能詳解與實戰流轉指南（繁體中文）
├── Tools Practical Usage and Skills Panorama Guide.md       # 技能詳解與實戰流轉指南（英文）
├── Skills Usage Guide.zh-tw.md                    # 各 skill 觸發機制與使用時機說明（繁體中文）
├── Skills Usage Guide.md                          # 各 skill 觸發機制與使用時機說明（英文）
├── run-pipeline.ps1 / pipeline.ps1  # Windows PowerShell 統一流水線執行指令碼
├── run-pipeline.sh / pipeline.sh   # Linux / macOS Bash 統一流水線執行指令碼
├── deploy-agents.ps1                # Windows 一鍵部署與線上更新自動化指令碼
├── deploy-agents.sh                 # Linux / macOS 一鍵部署與線上更新自動化指令碼
├── setup-ai-memory.ps1              # 單專案/單客戶端顯式安裝輔助指令碼
├── setup-ai-memory.sh               # Linux / macOS / WSL 顯式安裝輔助指令碼
├── tools/tui.py                     # 終端互動式單選/多選組件庫
├── tools/sync-skills.py             # 外部依賴技能庫同步與上游差異比對工具
├── tools/doc-impact.py              # 活體文檔影響分析與質檢門禁工具
├── .ai-memory.toml.example          # 本地顯式加入標記範例
├── skills-lock.json                 # 技能來源及檔案完整性元資料
├── README.md                        # 專案總覽（English）
└── README_zh.md                     # 專案總覽（簡體中文）
```

首次部署時可用 `-Initialize` / `--initialize` 生成帶專案事實和待確認清單的規則；使用 `-DirectoryPath` / `--directory` 指定現有模組目錄。已有 `AGENTS.md` 不會被覆蓋，改為生成 `AGENTS.generated.md` 供審閱。

---

## 快速開始

### 1. 統一工程流水線一鍵執行（推薦）

透過作業系統對應的原生流水線指令碼，按序貫通全部工程階段（規則與橋接部署 → AI 記憶配置 → 外部技能同步 → 活體文檔質檢）：

- **Linux / macOS 環境 (Bash)**:
  ```bash
  # 互動式精靈模式（單選語言、多選階段、選擇執行模式）：
  ./pipeline.sh
  # 無人值守一鍵全量流水線：
  ./pipeline.sh --all -y
  ```

- **Windows 環境 (PowerShell)**:
  ```powershell
  # 互動式精靈模式：
  .\pipeline.ps1
  # 無人值守一鍵全量流水線：
  .\pipeline.ps1 -All -Yes
  ```

### 2. 獨立部署規範與互動式精靈

- **互動式精靈（零參數啟動）**:
  ```bash
  # Linux / macOS:
  ./deploy-agents.sh
  # Windows:
  .\deploy-agents.ps1
  ```
  *自動拉起終端逐步選擇精靈：單選語言、單選部署範圍、輸入專案路徑、多選 Agent 工具橋接與可選工作流程。*

- **Windows 命令列 (PowerShell)**:
  ```powershell
  # 部署到指定專案（預設 en，可指定 -Language zh-tw / zh / fr / de）
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Global -Language zh-tw -Initialize -DirectoryPath "packages/core"
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Check -DirectoryPath "packages/core"
  ```

- **Linux / macOS 命令列 (Bash)**:
  ```bash
  chmod +x ./deploy-agents.sh
  # 支援多語言範本切換（預設 en，可選 --lang zh-tw / zh / fr / de）
  ./deploy-agents.sh /path/to/my-project --global --lang zh-tw --initialize --directory packages/core
  ./deploy-agents.sh /path/to/my-project --check --directory packages/core
  ```

### 3. 可選：啟用本地跨工具記憶（ai-memory）

本專案支援透過 [ai-memory](https://github.com/akitaonrails/ai-memory) 實現多 Agent 間無縫共享架構事實與會話斷點（本地優先，零 API Key，零 Embedding 成本）。

#### Step 1: 安裝前置 CLI 並就緒環境
- **透過 Rust Cargo 安裝**：
  ```bash
  cargo install ai-memory
  ```
- **或透過 GitHub Releases 下載原生二進位檔案**：
  - **Linux / macOS**:
    ```bash
    mkdir -p ~/.local/bin
    curl -fsSL https://github.com/akitaonrails/ai-memory/releases/latest/download/ai-memory-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin/
    chmod +x ~/.local/bin/ai-memory
    export PATH="$HOME/.local/bin:$PATH"
    ```
  - **Windows**:
    造訪 [Releases](https://github.com/akitaonrails/ai-memory/releases) 下載 `ai-memory-windows-x86_64.zip` 並加入系統 `PATH`。

#### Step 2: 初始化專案本地宣告標記（.ai-memory.toml）
- **Windows PowerShell**:
  ```powershell
  Copy-Item .ai-memory.toml.example .ai-memory.toml
  (Get-Content .ai-memory.toml) `
      -replace 'replace-with-workspace-name', 'default' `
      -replace 'replace-with-project-name', 'agent-harness' |
      Set-Content .ai-memory.toml
  ```
- **Linux / macOS (Bash)**:
  ```bash
  cp .ai-memory.toml.example .ai-memory.toml
  sed -i 's/replace-with-workspace-name/default/g; s/replace-with-project-name/agent-harness/g' .ai-memory.toml
  ```

#### Step 3: 執行單客戶端配置指令碼
```bash
./setup-ai-memory.sh antigravity-ide   # Linux / macOS
.\setup-ai-memory.ps1 -Agent antigravity-ide # Windows
```

#### Step 4: 啟動本地記憶引擎服務
```bash
ai-memory serve --transport http
```

### 3. 線上更新規範與技能庫

當上游規則或 GitHub 技能發生更新時，直接在專案根目錄執行：
```powershell
# Windows
.\deploy-agents.ps1 -ProjectPath "." -Update

# Linux / macOS
./deploy-agents.sh . --update
```

---

## 文件索引

- 📖 **部署與配置指南**：
  - [繁體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md) | [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [簡體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [Français](Multi-Tool%20Deployment%20and%20Configuration%20Guide.fr.md) | [Deutsch](Multi-Tool%20Deployment%20and%20Configuration%20Guide.de.md)
- 📖 **實戰使用與技能全景**：
  - [繁體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md) | [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [簡體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | [Français](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.fr.md) | [Deutsch](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.de.md)
- 📜 **三級規則架構**：
  - **全域憲法**：[`Global AGENTS.zh-tw.md`](Global%20AGENTS.zh-tw.md)（繁體中文）| [`English`](Global%20AGENTS.en.md) | [`簡體中文`](Global%20AGENTS.md) | [`Français`](Global%20AGENTS.fr.md) | [`Deutsch`](Global%20AGENTS.de.md)
  - **專案規範**：[`Project AGENTS.zh-tw.md`](Project%20AGENTS.zh-tw.md)（繁體中文）| [`English`](Project%20AGENTS.en.md) | [`簡體中文`](Project%20AGENTS.md) | [`Français`](Project%20AGENTS.fr.md) | [`Deutsch`](Project%20AGENTS.de.md)
  - **目錄規則**：[`Directory AGENTS.zh-tw.md`](Directory%20AGENTS.zh-tw.md)（繁體中文）| [`English`](Directory%20AGENTS.en.md) | [`簡體中文`](Directory%20AGENTS.md) | [`Français`](Directory%20AGENTS.fr.md) | [`Deutsch`](Directory%20AGENTS.de.md)

---

## 授權條款

本專案遵循 MIT 開源授權條款。各內建第三方技能遵循其各自的原生開源協定。
