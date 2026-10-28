# AI 工具與技能全景實戰指南（Claude Code / Codex / Antigravity IDE / Zed IDE）

> **Language / 語言**: [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [简体中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | **繁體中文** | [Français](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.fr.md) | [Deutsch](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.de.md)

本指南為使用 AI 代理進行軟體工程與技術文件撰寫提供全面的手冊：**應安裝哪些 skills 和 Harness 工具、底層的 token 經濟學、工具配置與接線、何時以及如何呼叫核心斜線命令（例如 `/comet`、`/plan`、`/opsx`、`codegraph`），以及端到端的實戰演練。**

---

## 目錄

1. [Core Architecture & Tool Matrix (Who Manages What)](#1-核心架構與工具矩陣誰負責什麼)
2. [Skills & Ecosystem Tools Inventory](#2-skills-與生態系工具盤點)
   - 2.1 44 Integrated Native Skills Categorized
   - 2.2 Version Locking, Online Updates & Skill Sync (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)
   - 2.3 Optional Harness CLI Tools
   - 2.4 Token Economics of Skills (Why 40+ Skills Do NOT Blow Up Context)
   - 2.5 Engineering Skills & Rules Dispatching Matrix
3. [Deep Dive into Core Harness Tools & Slash Commands](#3-核心-harness-工具與斜線命令深度解析)
   - 3.1 Comet: Versioned Workflow Entry Point
   - 3.2 OpenSpec: Spec-Driven Development (`/opsx:propose`, `/opsx:apply`, etc.)
   - 3.3 Superpowers: TDD, Systematic Debugging & Verification Gate
   - 3.4 CodeGraph: Optional MCP Code-Graph Integration
   - 3.5 Ponytail: Minimal Implementation Ladder (Generation Gate)
   - 3.6 Caveman: Ultra-Compressed Output (Communication Gate)
   - 3.7 RTK: Output Truncation & Log Shielding (Execution Gate)
   - 3.8 Git Authorization Model & Protected Branch Workflow
   - 3.9 3-Step Session Ceremony & Dynamic Memory Loop
   - 3.10 8 High-Risk Operations Protection Matrix
4. [Platform-Specific Native Commands & Best Practices](#4-平台特定的原生命令與最佳實踐)
   - 4.1 Google Antigravity IDE
   - 4.2 Claude Code & PreToolUse Hooks
   - 4.3 OpenAI Codex / GitHub Copilot
   - 4.4 Zed IDE
5. [End-to-End Practical Walkthrough (Real-World Feature Development)](#5-端到端實戰演練真實功能開發)
6. [Daily Health Checks & Troubleshooting](#6-每日健康檢查與故障排除)

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
| **Comet** | Versioned Native/Classic workflows | Resumable, verifiable task workflows | Follow installed version and `.comet/config.yaml` |
| **OpenSpec** | Spec-Driven Development (SDD) | Requirement amnesia, untracked delta changes | `/opsx:propose`, `docs/openspec/` live docs |
| **Superpowers** | TDD & Verification evidence gate | Hallucinated task completion, missing physical proof | Red test $\rightarrow$ Green test $\rightarrow$ Verification report |
| **CodeGraph** | Optional semantic code-search integration | Requires CLI, agent MCP wiring, and a project index | Query through configured CodeGraph MCP tools |
| **Ponytail** | Minimal-implementation guidance Skill | Unneeded dependencies and abstractions | Guidance only when the host loads the Skill |
| **Caveman** | Concise-communication guidance Skill | Overlong responses | Style guidance when loaded; preserve clarity and safety details |
| **RTK** | Optional Rust Token Killer CLI | Verbose terminal output | Requires CLI installation and a supported agent hook |
| **Git Auth** | Protected branch guidance plus limited client hook checks | Preventing accidental shared-branch operations | Rules, Claude Code client hook, and server-side branch protection |

### 各程式設計工具的規則與記憶範圍

| 工具/介面 | 指示進入點 | 記憶範圍 |
|---|---|---|
| Codex desktop app | Project `AGENTS.md`; ai-memory can use the local Codex integration where the installed app exposes configured MCP/hooks | Verify the exact desktop version; ChatGPT web conversation memory is separate |
| Codex CLI | Codex home and `AGENTS.md` files from repository root through the current directory; ai-memory upstream installer supports MCP/hooks | Project context/checkpoint files remain repository-managed |
| Claude Code | User/project/directory `CLAUDE.md` or supported `AGENTS.md` | Optional Auto memory is machine-local and Claude-specific; `/memory` opens its controls |
| Antigravity CLI | Global, workspace, and directory `AGENTS.md` / `.agents/rules/*.md`; ai-memory upstream supports MCP/hooks | Run setup in the same environment as the CLI |
| Antigravity IDE | Project Markdown rules/skills plus a manually configured ai-memory MCP server | MCP provides explicit retrieval/write tools; no automatic lifecycle capture is claimed |

部署腳本負責寫入路徑；在假設檔案已被取用之前，請先查閱各宿主的最新文件和已載入的上下文。

---

## 2. Skills 與生態系工具盤點

### 2.1 44 個內建原生 Skills 分類

安裝程式將倉庫的 skill 目錄複製到 `.agents/skills/`；實際的探索行為取決於宿主工具及其配置。

#### 1. 版本化工作流程進入點
- **`comet`**：Comet CLI 提供版本化的 Native 和 Classic 工作流程。本倉庫僅提供進入點指南；不實作 Comet 階段守衛。

#### 2. OpenSpec 規格驅動套件（16 個 skills）
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
- **`writing-skills`**：Skill 建立器與驗證器。
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
   - **Check mode**: `python3 tools/sync-skills.py --check` (read-only, compares local and upstream `SKILL.md` hashes, reports 🟢 in-sync / 🟡 outdated);
   - **Apply mode**: `python3 tools/sync-skills.py --apply` (updates outdated `SKILL.md` files in-place and refreshes lock hashes; locally-authored skills are strictly protected);
   - Interactive terminal UI powered by `tools/tui.py` when invoked without arguments;
   - Supports `--skill <name>` for targeted updates and `--json` for automation.
3. **活文件影響分析（`tools/doc-impact.py`）**：
   - 依據活文件追溯中繼資料分析程式碼變更（`docs/{specs,architecture,reference,guides,adr}/`）；
   - 支援工作樹檢查、提交基準線（`--since`）、明確檔案清單和互動式精靈模式（`--interactive`）。
4. **統一流水線執行器（`run-pipeline.sh` / `run-pipeline.ps1`）**：
   - 將完整工作流程串連為各作業系統的單次執行（部署 → AI 記憶 → Skills 同步 → 活文件影響）；
   - 互動式精靈：`./run-pipeline.sh`（Linux/macOS）或 `.\run-pipeline.ps1`（Windows）；
   - 無人值守自動化：`./run-pipeline.sh --all -y` 或 `.\run-pipeline.ps1 -All -Yes`。
5. **終端互動式 TUI 元件（`tools/tui.py`）**：
   - 提供鍵盤驅動的單選（方向鍵 + Enter）和多選（方向鍵 + 空白鍵核取方塊切換 + Enter 確認）互動式選單；
   - 內建 TTY 和 ANSI 相容性偵測，在非互動式或非 ANSI 管道中優雅地退回為編號文字提示，作為所有部署和維護工具的基礎。
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
- **Comet CLI**：透過 `npm install -g @rpamis/comet` 安裝；提供 native/classic 工作流程執行和 `--comet-init` 初始化。
- **CodeGraph CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh`; Windows PowerShell: `irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex`. Run `codegraph install` to wire agents and `codegraph init` in the project.
- **RTK (Rust Token Killer) CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh`; Windows: `winget install rtk-ai.rtk`. Verify with `rtk gain`. Run `rtk init` in the project to configure agent hooks.
- **Open Code Review (OCR) CLI**：透過 `npm install -g @alibaba-group/open-code-review` 安裝；透過 `open-code-review` skill 啟用 Tier A 零 LLM 成本委派審查。

部署腳本在初始設定期間會自動偵測這些可選的 CLI，並在適當時機引導安裝。

---

### 2.4 Skill 載入與可選 CLI 設定

Skill 的探索與上下文成本取決於宿主代理及其配置。僅有檔案存在並不保證 Skill 會被載入。Ponytail 和 Caveman 是隨專案複製的指引型 Skills；CodeGraph 和 RTK 還需要各自獨立的 CLI 和代理整合步驟。其效果取決於專案、宿主和設定，因此本指南不做固定的 token 節省承諾。

---

### 2.5 工程 Skills 與規則分派矩陣

| 場景 | 規則 / Skill | 觸發條件 / 關鍵字 | 預期行為 |
|---|---|---|---|
| **Branching / Commit / Push** | [`git-workflow.md`](../../.agents/rules/git-workflow.md) | `git commit` / `git push` | Commit only on temp branches; no `git add .`; human authorization required for remote push |
| **High-Risk Operations** | [`security-boundary.md`](../../.agents/rules/security-boundary.md) | Modifying build configs, protocols, public structs | Pause and confirm impact with human |
| **Complex Requirements** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` or "use openspec" | Propose change under `docs/openspec/changes/`; wait for confirmation |
| **Symbol Discovery** | [`token-discipline.md`](../../.agents/rules/token-discipline.md) + optional `codegraph` | CodeGraph MCP when configured; otherwise scoped `rg` | Do not assume CodeGraph is installed or available |
| **Feature Implementation** | `ponytail` + `test-driven-development` | Consult loaded Skills as appropriate | Understand current code, then choose the smallest correct implementation and suitable validation |
| **Bug Investigation** | `systematic-debugging` | Error trace pasted | Gather evidence $\rightarrow$ form hypothesis $\rightarrow$ minimal repro $\rightarrow$ fix |
| **Long Terminal Output** | optional `rtk` | Only when installed and its agent hook is configured | Otherwise use native concise flags; keep required validation and preserve relevant logs |
| **Token Conservation** | `caveman` | Only when the host loads the Skill or plugin | Be concise while preserving necessary context, technical accuracy, and safety details |
| **Document Processing** | `docx` / `pdf` | Mentions `.docx` or `.pdf` | Professional formatting without running code test suites |
| **Living Docs & Traceability** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `living-documentation` | `/living-documentation` / sync trace docs | Maintain 4-tier docs (specs/architecture/reference/guides) via L0/L1/L2 impact thresholds and frontmatter traceability |
| **Phase Gate Docs / Templates** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `engineering-docs` | `/engineering-docs` / SRS/HLD/spec requests | Standardize AI agent outputs across phases using 15 bilingual phase-gate templates, connecting Comet artifacts with living documentation |
| **Code Review & Quality Gate** | `open-code-review` + `requesting-code-review` | Before merge or after task completion | Rule-first, line-anchored, coverage-mandated; Tier A delegation if `ocr` CLI exists, otherwise Tier B methodology |
| **Task Completion** | `verification-before-completion` | End of task | Present physical command execution evidence |

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

- `/opsx:propose <name>`: Proposes new change under `docs/openspec/changes/`;
- `/opsx:apply`: Implements approved change;
- `/opsx:verify`: Compares actual implementation with delta specification;
- `/opsx:sync`: Syncs delta specifications into main docs;
- `/opsx:archive`: Moves finished change to `docs/openspec/changes/archive/`.

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
# Explore call chains and architecture
Query the CodeGraph MCP tool configured for the current agent: “User authentication and JWT token flow”.

# Find definitions and all call references
Query the configured CodeGraph MCP tool for `OrderService::calculateDiscount`.
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
1. **Task start:** Read `PROJECT_CONTEXT.md` (verified durable project facts) and `SESSION_STATE.md` (current checkpoint) only when present and relevant; verify branch, configuration, and implementation facts that affect the task.
2. **During work:** Keep plans when useful for multi-step work. Do not add automatic capture of prompts, tool inputs/outputs, source files, or terminal commands.
3. **Meaningful closeout:** Update `SESSION_STATE.md` with completed work, actual verification evidence, remaining steps, and still-relevant risks; remove stale items. Update `PROJECT_CONTEXT.md` only when durable architecture, constraints, or confirmed decisions change. No-op sessions need no empty update.
4. **Sources and conflicts:** Label uncertainty and date/source facts likely to change. Current user instructions and current code/configuration/reproducible evidence take precedence over memory summaries.
5. **Privacy:** Do not record credentials, private keys, raw personal data, full conversation/tool logs, or unnecessary personal information. Shared global templates must not contain private user preferences.
6. **Directory scope:** A directory `AGENTS.md` contains only local boundaries and constraints. Do not create directory memory files by default; keep project facts and checkpoints in their root files.

**Claude Code native Auto memory** is a separate machine-local project memory that can be inspected, edited, or deleted with `/memory`. It is not shared across tools or machines and does not replace the project files above. Claude Code manages this feature; this repository's deployer does not enable, disable, or capture it. See the [Claude Code memory docs](https://code.claude.com/docs/en/memory).

#### Optional cross-agent memory: ai-memory

This repository selects only [ai-memory](https://github.com/akitaonrails/ai-memory) as an optional cross-agent backend. Its local Markdown and full-text search path uses no LLM, embedding provider, or API key. The repository does not install or start it automatically.

To opt in one repository, copy `.ai-memory.toml.example` to the ignored `.ai-memory.toml`, replace the workspace/project names, then run `setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` or `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>`. The helper requires an existing ai-memory install and delegates configuration to its upstream merge-aware commands. Review the hook capability output; allowlist mode is effective only for hooks that enforce native capture policy.

The setup includes Claude Code and Codex CLI MCP/hooks, plus Antigravity CLI MCP/hooks. Codex desktop support depends on the installed desktop version exposing the local Codex integration; verify it in the app. Antigravity IDE is MCP-only: add `http://127.0.0.1:49374/mcp` as `serverUrl` through its MCP settings or the documented config file. For Docker deployment, run `docker run -d --name ai-memory --restart unless-stopped -p 127.0.0.1:49374:49374 -v "${HOME}/env/ai-memory-data:/data" docker.io/akitaonrails/ai-memory:latest` (the container storage path is fixed to `/data`). ChatGPT web uses manual Markdown handoff in the free local setup.

Windows supports both WSL2 and native modes upstream. Install and configure ai-memory in the same environment that launches the agent; see the [Windows guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md). Path exclusions do not redact arbitrary prompt text. Back up with `ai-memory --data-dir <data-dir> backup --to <archive-path>`; uninstall removes integrations but not data. Stop the service and verify the configured data directory before intentionally deleting it. See the [marker reference](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md) and [installation guide](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) for platform paths and Docker commands.

### 3.10 8 項高風險操作保護矩陣

在以下操作前必須經過人工確認：
- [ ] 1. Modifying build configs (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
- [ ] 2. Adding new third-party dependencies;
- [ ] 3. Modifying global public data structures (`public_struct.h`, `types.ts`);
- [ ] 4. Modifying core dispatch singletons or public service APIs;
- [ ] 5. Changing wire protocols or serialization contracts (`protofile/`);
- [ ] 6. Altering license, cryptography, or auth code;
- [ ] 7. Modifying `.gitignore` or CI/CD pipelines;
- [ ] 8. High-impact cross-module changes that affect shared contracts or require broad coordination (file count alone is not a risk trigger).

---

## 4. 平台特定的原生命令與最佳實踐

### 4.1 Google Antigravity CLI 與 IDE
- The CLI runs as `agy`; the desktop IDE is a separate surface. Both document file-based workspace/global rules, but CLI slash commands and IDE controls are surface-specific.
- `/plan`: Structured task planning for $\ge 3$ steps;
- `/goal`: Unattended autonomous loop until verified completion;
- `/grill-me`: Interactive discovery interview when requirements are ambiguous;
- `/learn`: Captures lessons learned into `tasks/lessons.md`;
- `/schedule`: Background timers and recurring cron monitoring.

### 4.2 Claude Code 與 PreToolUse 用戶端 Hook
- `/compact`: Compresses conversation history when token count is high;
- `/cost`: Real-time session token usage;
- `/review`: Reviews working copy diffs;
- `@<path>`: Dynamically loads specific rules on demand.
- **Security hook**: `.claude/settings.json` runs Claude Code client-side checks for matching tool calls. It can reject selected patterns or warn; it is not an operating-system control or memory collector.

### 4.3 ChatGPT 中的 Codex、Codex CLI 與 GitHub Copilot
- Codex CLI documents `AGENTS.md` discovery from Codex home and the repository path to the current directory. Do not infer that exact behavior for ChatGPT/desktop; check its current product behavior and configuration.
- `/hooks`: Inspects and trusts lifecycle hooks;
- `$comet`: Triggers Comet state machine in Codex CLI;
- `@workspace`: Scans workspace context in VS Code.

### 4.4 Zed IDE
- Reuse the project `AGENTS.md`; this installer does not create a Zed-specific file;
- `Ctrl+Enter` (Inline Assist) with `follow ponytail principles`;
- Assistant Panel (`Ctrl+?`) for multi-turn architectural planning.

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
