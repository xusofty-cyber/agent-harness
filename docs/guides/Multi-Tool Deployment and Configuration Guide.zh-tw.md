# 多工具（Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed）AI 工程部署與配置指南

> **Language / 語言**: [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [简体中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | **繁體中文** | [Français](Multi-Tool%20Deployment%20and%20Configuration%20Guide.fr.md) | [Deutsch](Multi-Tool%20Deployment%20and%20Configuration%20Guide.de.md)

本指南提供端到端的規範說明，闡述如何在 **OpenAI Codex / GitHub Copilot**、**Claude Code**、**Google Antigravity IDE** 以及 **Zed IDE** 中部署、配置並協同運用 **三層式 AGENTS.md 架構**（全域層、專案層與目錄層），針對以軟體工程為主、兼顧專業技術文件處理的實際場景。

---

## 目錄

1. [架構與分層定位（Harness + 漸進式揭露）](#1-架構與分層定位harness--漸進式揭露)
2. [各工具的配置範圍](#2-各工具的配置範圍)
3. [Claude Code 用戶端 Hooks：PreToolUse（.claude/settings.json）](#3-claude-code-用戶端-hooks-pretooluse-claudesettingsjson)
4. [跨工具部署與範本更新（deploy-agents）](#4-跨工具部署與範本更新deploy-agents)
   - 4.1 腳本核心架構與流水線
   - 4.2 Windows 部署（`deploy-agents.ps1`）
   - 4.3 Linux / macOS 部署（`deploy-agents.sh`）
   - 4.4 符號連結 vs. 目錄 Junction 機制
5. 四層規則深度解析
   - 5.1 全域憲法：`Global AGENTS.md`
   - 5.2 專案路由器：`Project AGENTS.md`
   - 5.3 模組化子規則：`.agents/rules/`
   - 5.4 微邊界補丁：`Directory AGENTS.md`
6. 雙軌實戰工作流程：「工程優先，文件次之」
7. 常見問題與最佳實踐（FAQ）
8. 實戰用法與技能全景指南參考

---

## 1. 架構與分層定位（Harness + 漸進式揭露）

本倉庫將可重用的規則組織為**專案進入點加上按需載入的子規則**，讓團隊能夠調整基準線並避免載入無關的指引。實際的探索行為與上下文成本取決於宿主工具：

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Global Level (Global AGENTS.md)                                     │
│    - Role: Cross-project engineering constitution & security baseline │
│    - Content: Reusable engineering baseline, Git safety, concise communication │
│    - Scope: System-wide resident across all user projects (~1000 Tok) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Inherited (non-redundant)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Project Root Level (Project AGENTS.md)                              │
│    - Role: Deterministic engineering context & sub-rule/skill router   │
│    - Content: Concrete CLI slots, tech stack, red lines, state memory  │
│    - Scope: Repository-wide; loading depends on the host tool          │
│    - Bridges: CLAUDE.md / .github/copilot-instructions.md              │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Progressive On-Demand Reading   │ Only as needed in submodules
┌──────────────────▼───────────────┐ ┌───────────────▼───────────────────┐
│ 3. Sub-Rules (.agents/rules/)    │ │ 4. Directory Level (Directory AGENTS.md)│
│  - token-discipline.md           │ │    - Role: Micro-boundary patch   │
│  - engineering-spec.md (SDD/TDD) │ │    - Content: In/Out scope, isolated│
│  - security-boundary.md          │ │            dependencies, fast tests│
│  - git-workflow.md (Auth model)  │ └───────────────────────────────────┘
└──────────────────────────────────┘
```

### 核心優勢
1. **共享基準線**：將可重用的規則保存在 Markdown 範本中，並在支援的地方使用工具專屬的橋接檔案；驗證每個宿主的探索行為，而非假設所有工具都載入相同的檔案。
2. **漸進式揭露**：
   - 規則在特定場景觸發時動態載入。
   - Skill 的探索、載入與提示快取行為取決於宿主工具及其配置；部署檔案並不保證會自動載入。
3. **用戶端風險護欄**：Claude Code hooks 可以拒絕選定的相符工具呼叫或發出警告。這些是用戶端檢查，並非作業系統或伺服器端的安全控制。

---

## 2. 各工具的配置範圍

規則探索、繼承、全域設定與記憶機制因產品和版本而異。下表區分了腳本寫入的路徑與宿主探索行為；檔案部署不等同於載入驗證。

| 工具/介面 | 本倉庫提供或寫入的內容 | 載入說明 |
| :--- | :--- | :--- |
| Codex (local app / IDE / CLI) | Global `$CODEX_HOME/AGENTS.md` (default `~/.codex/AGENTS.md`); project and directory `AGENTS.md` | `-Global` creates the global file; `-Global -Update` backs up and replaces the active global instruction file. Codex uses a non-empty `AGENTS.override.md` in Codex home in preference to `AGENTS.md` |
| Claude Code | `CLAUDE.md` bridge, `~/.claude/CLAUDE.md`, project hooks/skills | `CLAUDE.md` is an instruction entry point; Claude Auto memory is a separate optional machine-local project memory, not shared across tools |
| Antigravity 2.0 | Project `AGENTS.md` / `GEMINI.md` / `.agents/rules/`; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer | Current docs list both global names; older releases can follow the pointer to the canonical file |
| Antigravity CLI | Project/directory rules; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer; optional `~/.gemini/antigravity-cli/rules/*.md` | Common rules use the canonical entry; configure CLI-only rules separately |
| Antigravity IDE / extensions | Project/directory rules; global `~/.gemini/AGENTS.md` and `GEMINI.md` compatibility pointer | Current IDE supports both global names; older IDE generations can follow the pointer |
| GitHub Copilot | `.github/copilot-instructions.md` bridge | Confirm loading in Copilot's current product settings/docs |
| Zed / Pi / OpenCode | Reusable Markdown only; no dedicated setup from this repository | Do not infer automatic discovery or global loading from file presence |

References: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---

## 3. Claude Code 用戶端 Hooks：PreToolUse（.claude/settings.json）

### 能力邊界
`.claude/settings.json` 中的 hooks 是 Claude Code 專屬的，僅在相符的工具呼叫之前執行。`guard.mjs` 會拒絕選定的命令模式；許多其他情況僅發出警告。正則匹配無法識別所有 shell 包裝器、別名或命令形式，因此這不是完整的安全邊界。Hooks 不會收集或傳輸記憶資料。Claude Code Auto memory 是獨立的本機專案功能，使用者可用 `/memory` 檢視/管理；本倉庫不對其進行配置。對於共享倉庫，請使用伺服器端分支保護和最小權限憑證。

### 配置與實作

安裝程式會複製 [`.claude/settings.json`](../../.claude/settings.json) 並部署 [`.claude/hooks/guard.mjs`](../../.claude/hooks/guard.mjs) 與 [`guard-write.mjs`](../../.claude/hooks/guard-write.mjs)。請直接檢視這些原始檔；不要從舊版指南複製 hook 範例，因為協定和實作可能會變更。

### 其他工具的對應方案（擴充點）

PreToolUse hooks 是 Claude Code 專屬的；安裝程式不會為其他工具安裝攔截器。若要達到同等保護，請接上各工具自身的 hook/審批機制：`guard.mjs` 中的決策邏輯（受保護分支、危險命令模式）是純 Node.js——重用其正則表達式和分支表，並調整以適應目標工具的 hook 進入點。無論在哪一層掛接 hook，都無法取代伺服器端分支保護；用戶端攔截只是縱深防禦中的一層。

---

## 4. 跨工具部署與範本更新（deploy-agents）

腳本將檔案部署到配置的路徑。檔案部署並不保證工具特定的載入行為。`-Global` 會初始化缺失的全域規則檔案並保留現有檔案。組合使用 `-Global -Update` 會先建立時間戳記備份，然後用當前範本取代作用中的全域規則。Antigravity 會收到規範的 `~/.gemini/AGENTS.md` 加上一個小型的 `GEMINI.md` 相容性指針，而非重複的完整規則集。Codex 在設定了 `$CODEX_HOME` 時使用該路徑（否則使用 `~/.codex`）；如果其中存在非空的 `AGENTS.override.md`，則會備份並更新該作用中檔案，而非 `AGENTS.md`：
- **Windows PowerShell**：[`deploy-agents.ps1`](../../deploy-agents.ps1)
- **Linux / macOS Bash**：[`deploy-agents.sh`](../../deploy-agents.sh)

### 4.1 腳本核心架構與流水線

```text
[ Execute Deployment Script ]
       │
       ├─ [Zero arguments in terminal OR with -Interactive / --interactive]
       │       ▼
       │  Phase 0: Interactive Step-by-Step Terminal Wizard (TUI Arrow-Key & Checkboxes)
       │    ├─ [1/5] Select Template Language (English / 简体中文 / 繁體中文 / Français / Deutsch)
       │    ├─ [2/5] Select Deployment Scope (Target Project only / Global Rules only / Both)
       │    ├─ [3/5] Enter Target Project Path (defaults to current directory [.])
       │    │        (Note: Codex, Antigravity, Zed natively read AGENTS.md without bridges)
       │    ├─ [4/5] Multi-Select Agent Bridge Files (Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy)
       │    └─ [5/5] Multi-Select Optional Workflows (Update mode / Project fact scan / ai-memory / Comet)
       │
       ▼
 Phase 1: Template Repository Update (-Update)
   └─ Fast-forward update of this template repository (`git pull --ff-only`); no global CLI upgrade or third-party updater in the caller directory
       │
       ▼
 Phase 2: User Global Rules (-Global)
   ├─ Initialize Claude Code (~/.claude/CLAUDE.md) only if the target is absent
   ├─ Initialize Antigravity (~/.gemini/AGENTS.md) only if the target is absent
   └─ Preserve existing files; with -Update write adjacent *.template.md files for manual merge
       │
       ▼
 Phase 3: Project Rules & Cross-Tool Bridges
   ├─ Root AGENTS.md (generates AGENTS.template.md if already exists)
   ├─ CLAUDE.md -> AGENTS.md (symlink/reference)
   ├─ .github/copilot-instructions.md -> ../AGENTS.md
   ├─ Zed uses the provided AGENTS.md; no Zed-specific configuration is created
   └─ Claude Code PreToolUse client hooks: .claude/settings.json
       │
       ▼
 Phase 4: Sub-Rules (.agents/rules/*.md)
       │
       ▼
 Phase 5: Skills Library (.agents/skills/ & .claude/skills/)
   ├─ Copy skills to .agents/skills/
   ├─ Link to .claude/skills/ (Windows: Junction, Linux/macOS: Symlink)
   └─ Copy skills-lock.json metadata
       │
       ▼
 Phase 6: Dynamic Task Tracking Scaffold
   ├─ tasks/lessons.md (mistake notebook)
   └─ tasks/todo.md (checklist)
       │
       ▼
 Phase 7: OpenSpec Scaffold (docs/openspec/changes/)
       │
       ▼
 Phase 8: Optional Comet CLI Init (-CometInit)
   └─ Runs `comet init` only when explicitly requested
       │
       ▼
 Phase 9: Optional ai-memory Init (-AiMemoryInit)
   └─ Initializes .ai-memory.toml for cross-tool memory when explicitly requested
       │
       ▼
 Phase 10: Probe Optional CLIs & Interactive Prompts
   ├─ Offer CodeGraph / RTK / Open Code Review (ocr) / Comet install if missing
   ├─ Ask whether to wire CodeGraph agents / index project
   ├─ Ask whether to run rtk init; skipped in non-interactive mode
   ├─ Installing ocr enables Tier A delegation review; Tier B works offline without it
   └─ Installing Comet CLI enables subsequent workflow initialization via --comet-init
```

---

### 4.2 Windows 部署（`deploy-agents.ps1`）

**用法**：
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <target-path>] [-Global] [-Update] [-Interactive] [-CometInit] [-AiMemoryInit] [-Pipeline]
```

**參數**：
- `-ProjectPath`（位置參數 0）：目標專案的路徑。若與 `-Global` 同時省略，則僅更新使用者全域規則。
- `-Global`（`-g`）：初始化缺失的 `~/.claude/CLAUDE.md`、`~/.gemini/AGENTS.md` 以及 Codex 的 `$CODEX_HOME/AGENTS.md`（預設為 `~/.codex/AGENTS.md`）。若未使用 `-Update`，現有檔案會被保留。
- `-Language`（`-l`）：選擇範本語言（`en`、`zh`、`zh-tw`、`fr`、`de`；預設為 `en`）。
- `-Interactive`（`-i`）：啟動逐步互動式選擇精靈（單選語言與範圍，多選 Agent 橋接檔案與選項）。在互動式終端中以零參數執行時會自動觸發。
- `-Update`（`-u`）：快轉更新範本倉庫，自動呼叫 `tools/sync-skills.py --check` 掃描外部 skills 的上游更新並進行互動式確認，然後將檔案同步到目標。與 `-Global` 組合使用時，會備份並取代現有的全域規則檔案。Codex 的非空 `$CODEX_HOME/AGENTS.override.md` 具有優先權，會作為作用中檔案進行更新。現有的專案管理規則、hooks、skills 和鎖定中繼資料遵循其文件中記載的備份/更新行為。不會升級全域 CLI。
- `-CometInit`（`-c`）：若已安裝 Comet CLI，自動在目標專案中執行 `comet init`。
- `-AiMemoryInit`（`-m`）：自動在目標專案中初始化 `.ai-memory.toml`（推斷 `workspace` 和 `project`），用於跨工具 ai-memory 整合。
- `-Pipeline`：直接將執行委派給統一流水線執行器（[`run-pipeline.ps1`](../../run-pipeline.ps1)）。

**統一流水線執行器（Windows）**：
```powershell
# Interactive step-by-step wizard (select language, project, stages, detail mode):
.\run-pipeline.ps1

# Unattended full pipeline execution in one shot:
.\run-pipeline.ps1 -All -Yes

# Run specific stages:
.\run-pipeline.ps1 -Stages "deploy,skills,docs"
```

**範例**：
```powershell
# Scenario 0: Interactive wizard (zero-argument execution)
.\deploy-agents.ps1

# Deploy to a new project
.\deploy-agents.ps1 "D:\Projects\my-project"

# Deploy project and update global rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global

# Online update skills and sub-rules
.\deploy-agents.ps1 "D:\Projects\my-project" -Global -Update

# Initialize with Comet terminal hooks
.\deploy-agents.ps1 "D:\Projects\my-project" -CometInit

# Initialize with cross-tool ai-memory configuration
.\deploy-agents.ps1 "D:\Projects\my-project" -AiMemoryInit

# Launch unified pipeline directly
.\deploy-agents.ps1 -Pipeline

# Update global rules only
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Linux / macOS 部署（`deploy-agents.sh`）

```bash
chmod +x ./deploy-agents.sh ./run-pipeline.sh

# Scenario 0: Interactive wizard (zero-argument execution)
./deploy-agents.sh

# Deploy to project
./deploy-agents.sh /path/to/my-project

# Deploy and update global rules
./deploy-agents.sh /path/to/my-project --global

# Online update
./deploy-agents.sh /path/to/my-project --global --update

# Deploy with Comet CLI init
./deploy-agents.sh /path/to/my-project --comet-init

# Launch unified pipeline directly
./deploy-agents.sh --pipeline
```

**統一流水線執行器（Linux / macOS）**：
```bash
# Interactive step-by-step wizard (language, project, stages, mode):
./run-pipeline.sh

# Unattended full pipeline execution in one shot:
./run-pipeline.sh --all -y

# Run specific stages:
./run-pipeline.sh --stages deploy,skills,docs
```

### 使用 ai-memory 初始化進行部署
```bash
./deploy-agents.sh /path/to/my-project --ai-memory-init
```

---

### 4.4 符號連結 vs. 目錄 Junction 機制

為了讓 Claude Code 能夠探索位於 `.agents/skills/` 中的 skills：
- **Linux / macOS**：使用標準的相對符號連結：
  `ln -sf "../../.agents/skills/${name}" ".claude/skills/${name}"`
- **Windows**：一般使用者帳戶在沒有開發人員模式或管理員權限的情況下無法建立目錄符號連結。`deploy-agents.ps1` 透過使用 **NTFS 目錄 Junctions** 來解決此問題：
  `New-Item -ItemType Junction -Path ".claude\skills\$name" -Target ".agents\skills\$name"`
  - 無需提權即可運作；
  - 即時目錄映射，無需檔案重複；
  - 若不支援 junctions，自動退回為遞迴複製。

---

## 5. 四層規則深度解析

### 5.1 全域規則範本：`Global AGENTS.md`
- **用途：** 可重用的跨專案工程基準線。宿主是否載入它、以及載入的優先順序，取決於該宿主和使用者的配置。
- **共享邊界：** 保持共享範本的通用性；不要在其中放入個人偏好、專案事實或敏感資訊。僅在明確要求時，才將個人偏好儲存在使用者控制的本機位置。
- **記憶層：**
  1. 任務開始時，在相關的情況下讀取 `PROJECT_CONTEXT.md`（已驗證的持久專案事實）和 `SESSION_STATE.md`（當前檢查點），然後驗證影響工作的事實。
  2. 在有意義的任務/工作階段邊界，更新 `SESSION_STATE.md` 並移除過時狀態。僅在持久的專案知識變更時才更新 `PROJECT_CONTEXT.md`；無實質變更的工作階段不需要空更新。
  3. `PROJECT_CONTEXT.md` 是專案摘要和導航輔助，並非凌駕於程式碼、配置或維護中文件的單一事實來源。當前使用者指示和可重現的證據優先於記憶。
  4. 標註不確定性以及可能變更的日期/來源事實。絕不儲存憑證、私鑰、原始個人資料、完整對話/工具日誌或不必要的個人資訊。

**選定的可選後端：[ai-memory](https://github.com/akitaonrails/ai-memory)。** 其本地模式提供基於 Markdown 的專案記憶、全文字檢索和跨代理交接，無需 LLM 或 API 金鑰。一般使用不需要它。本倉庫提供明確的設定助手，但在正常部署期間絕不安裝或啟動後端、建立本地 opt-in 標記，或變更工具配置。

> **供應鏈注意事項**：ai-memory 是帶有提示讀取 hooks 的第三方原生二進位檔。僅從官方 Releases 頁面下載，並驗證已發布的 SHA256 校驗和（若使用 `cargo install`，請確認 crate 名稱為 `ai-memory`）。`setup-ai-memory.*` 刻意不會為您下載它，會在配置任何內容之前驗證其為原生可執行檔（拒絕包裝腳本），並鎖定已驗證的版本（目前為 **v2.6.0**——版本不符將拒絕配置）。升級前請查看上游發行說明，並在提升版本鎖定前重新驗證安裝旗標。

#### 明確的專案 opt-in 與設定

1. 依照其[官方安裝指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md)單獨安裝並啟動 ai-memory。若要使用免費的零金鑰路徑，請不要配置 LLM 和 embedding 提供者。
2. 檢視 `.ai-memory.toml.example`，將其複製為 `.ai-memory.toml`，並取代其中的兩個名稱。`.ai-memory.toml` 被 Git 忽略；刻意避免提交此 opt-in 檔案。
3. 在 Linux/macOS/WSL2 上執行 `./setup-ai-memory.sh <claude-code|codex|antigravity|antigravity-ide|antigravity-cli>`，或在 PowerShell 中使用對應的 `-Agent` 值。Antigravity 2.0 使用 `antigravity`，IDE 使用 `antigravity-ide`；兩者都會配置 MCP 和受管指示。CLI 目標還會額外安裝 allowlist hooks。原生可執行檔和 hook 模式預檢適用於 hook 目標；僅 MCP 的目標不需要。該助手不會下載軟體或啟動伺服器。
4. Keep the server bound to loopback for same-machine use. Default data locations are `~/.local/share/ai-memory` on Linux, `~/Library/Application Support/ai-memory` on macOS, and typically `%LOCALAPPDATA%\ai-memory` on Windows; `AI_MEMORY_DATA_DIR` can override them.
   - **Docker 部署（用於 Antigravity IDE HTTP MCP）**：
     ```bash
     # In-container storage path must be /data; binds to loopback 127.0.0.1
     mkdir -p "${HOME}/env/ai-memory-data"
     docker run -d --name ai-memory \
       --restart unless-stopped \
       -p 127.0.0.1:49374:49374 \
       -v "${HOME}/env/ai-memory-data:/data" \
       docker.io/akitaonrails/ai-memory:latest
     ```
     *注意：Docker 容器不需要掛載倉庫目錄樹或 `.ai-memory.toml`。Antigravity IDE 透過 MCP 工具呼叫傳遞專案上下文（`workspace`/`project`）。*
   - Back up with `ai-memory --data-dir <data-dir> backup --to <archive-path>` (for Docker deployments, use the upstream container command). `ai-memory uninstall --apply` removes managed client integrations but does not delete the data. To erase memory, stop the service and remove its configured data directory only after confirming the backup and target. See the [official installation/operations guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

#### 宿主邊界

- **Claude Code:** upstream MCP/hooks; ai-memory owns only its entries and preserves unrelated hooks. The existing Claude `PreToolUse` security hook remains separate. Claude Code's default auto-memory is also separate and machine-local.
- **Codex CLI:** upstream `--client codex` / `--agent codex` integration. **Codex desktop:** uses the local Codex configuration surface where supported; verify the installed app's hook/MCP availability instead of assuming every CLI version behaves identically.
- **Antigravity CLI:** upstream `antigravity-cli` MCP/hooks. On Windows, run setup in the same environment that launches the agent.
- **Antigravity 2.0 and IDE:** the helper uses the upstream Antigravity MCP installer to write the shared `~/.gemini/config/mcp_config.json` and managed project instructions. The current ai-memory upstream has no dedicated 2.0/IDE lifecycle-hook target, so this is MCP-only and does not automatically capture session events. Manual MCP setup uses `serverUrl=http://127.0.0.1:49374/mcp`; see [Antigravity MCP docs](https://www.antigravity.google/docs/mcp).
- **ChatGPT web:** the no-key, loopback setup has no direct connection to a remote web chat. Use a concise Markdown handoff manually. Remote MCP/write access is outside this free local setup.
- **Windows:** upstream documents both WSL2 and native Windows. Install and configure ai-memory in the same environment that launches each agent; do not mix WSL and Windows hook paths. Review the [Windows guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md) for client-specific support.

ai-memory allowlist mode only guarantees no capture for repositories without a marker when the installed native hook enforces capture policy. Its path exclusions do not redact arbitrary prompt text; never include secrets in prompts. See the [marker-file reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md).

### 5.2 專案路由器：`Project AGENTS.md`
- 可調整的倉庫級範本。
- Add `-Initialize` / `--initialize` to deployment to generate a draft from verifiable local facts and a pending-items checklist. `-DirectoryPath <relative-path>` / `--directory <relative-path>` also initializes an existing module directory. The scripts do not guess project purpose, owners, or module boundaries. Existing `AGENTS.md` files are preserved; generated review copies use `AGENTS.generated.md`.
- Detected `package.json` scripts and common framework/storage dependencies appear as review suggestions, not verified facts; confirm them before relying on those commands or boundaries.
- Run `-Check` / `--check` (optionally with the directory parameter) to scan for unresolved template fields before adopting the generated rules; the command returns a nonzero exit status when it finds any.
- Provides standard CLI command slots (install, dev, build, targeted test, lint, format, migration), architecture red lines, the **Rule & Skill Dispatching Matrix**, selective Markdown memory rules, and optional ai-memory integration guidance.

---

### 5.3 模組化子規則：`.agents/rules/`
按需漸進式載入：
- **`token-discipline.md`**: Restricts reading, fetching, and speaking; mandates AST index over blind grep;
- **`engineering-spec.md`**: SDD spec-first (In/Out scope), TDD verification gate (physical proof required);
- **`security-boundary.md`**: 8 high-risk operations confirmation matrix, zero credentials leak, large file safety;
- **`git-workflow.md`**: Protected branch isolation (zero direct commits), mandatory authorization for remote push, commit format `{type}: {description}`.

---

### 5.4 微邊界補丁：`Directory AGENTS.md`
- 僅在**必要時**於 monorepo 套件（`packages/*`）或隔離的子模組中建立。
- Generate one with `-Initialize -DirectoryPath <relative-path>` (PowerShell) or `--initialize --directory <relative-path>` (Bash); the target must already exist inside the project root. Module path/name are detected, while responsibility and boundaries remain explicit review items.
- Defines In/Out scope, permitted/forbidden dependencies, and targeted local test commands (e.g., `pytest tests/submodule -q`).

---

## 6. 雙軌實戰工作流程：「工程優先，文件次之」

### 1. 軟體工程軌（嚴格閘門）
- 範圍：API、功能、錯誤修復、重構。
- Rules:
  - Read `PROJECT_CONTEXT.md` and `SESSION_STATE.md` at task start only when present and relevant, then verify material facts;
  - Always work on temporary branches (`feature/*`, `fix/*`);
  - TDD red-green cycle, verify with actual test runs;
  - Follow Git authorization model;
  - **Selective memory updates**: Update `SESSION_STATE.md` at meaningful closeout; update `PROJECT_CONTEXT.md` only when durable project facts change.

### 2. 技術文件軌（輕量旁路）
- 範圍：Markdown 文件、README、API 規格、Word/PDF 報告。
- Rules: **Exempt from running test suites**; leverage specialized skills (`docx`, `pdf`, `write-openspec-docs`); maintain GitHub Flavored Markdown standards.

---

## 7. 常見問題與最佳實踐（FAQ）

### Q1：為什麼不把所有專案命令都放入 `Global AGENTS.md`？
> **答**：全域規則常駐於機器上的所有工作階段。加入專案特定的命令會造成跨專案的上下文污染並浪費提示 tokens。

### Q2：線上更新（`-Update`）如何保護自訂的專案配置？
> **Answer**: Existing project `AGENTS.md` is preserved and an `AGENTS.template.md` is generated for review. `-Global` initializes missing Claude Code, Antigravity, and Codex global instructions while preserving existing files. Combining `-Global -Update` makes timestamped backups and replaces those global files with the current template; Codex's active non-empty `AGENTS.override.md` is updated in place of `AGENTS.md`.

### Q3：40+ 個 skills 如何避免撐爆上下文視窗？
> **答**：取決於宿主如何探索和載入 Skills。不要假設固定的中繼資料成本或快取折扣；僅保持有用的 Skills 啟用，並在目標宿主中驗證行為。

### Q4：什麼是 8 項高風險操作保護矩陣？
> **答**：定義於 `security-boundary.md`，在以下操作前需要人工確認：
> 1. Modifying build configs (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
> 2. Introducing new third-party dependencies;
> 3. Modifying global public data structures (`public_struct.h`, `types.ts`);
> 4. Changing core dispatch singletons or public service interfaces;
> 5. Modifying communication protocols or wire contracts (`protofile/`);
> 6. Altering license, cryptography, or auth code;
> 7. Modifying `.gitignore` or CI/CD pipelines;
> 8. High-impact cross-module changes affecting shared contracts or requiring broad coordination; file count alone is not a risk trigger.

### Q5：何時應該更新 `PROJECT_CONTEXT.md` 和 `SESSION_STATE.md`？
> 在有意義的任務/工作階段邊界，用已完成的工作、實際驗證證據、剩餘步驟和仍相關的風險更新 `SESSION_STATE.md`。僅在持久的架構、約束或已確認的決策變更時才更新 `PROJECT_CONTEXT.md`。不要建立無實質變更的更新。這兩個檔案都是專案記憶的摘要；它們不會覆蓋當前使用者指示、程式碼、配置或可重現的證據。絕不儲存憑證、原始個人資料或完整對話/工具日誌。

---

## 8. 實戰用法與技能全景指南參考

有關 Slash Commands（`/comet`、`/plan`、`/opsx`）、CodeGraph、TDD 以及完整端到端執行演練的詳細教學，請參閱：
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
