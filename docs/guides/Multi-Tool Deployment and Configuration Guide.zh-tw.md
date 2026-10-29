# 多工具（Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed）AI 工程部署與配置指南

> **Language / 語言**: [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [簡體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | **繁體中文**

本指南提供端到端的規範說明，闡述如何在 **OpenAI Codex / GitHub Copilot**、**Claude Code**、**Google Antigravity IDE** 以及 **Zed IDE** 中部署、配置並協同運用 **三層式 AGENTS.md 架構**（全域層、專案層與目錄層），針對以軟體工程為主、兼顧專業技術文件處理的實際場景。

---

## 目錄

1. [架構與分層定位（Harness + 漸進式揭露）](#1-架構與分層定位harness--漸進式揭露)
2. [各工具的配置範圍](#2-各工具的配置範圍)
3. [Claude Code 用戶端 Hooks：PreToolUse（.claude/settings.json）](#3-claude-code-用戶端-hookspretooluseclaudesettingsjson)
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
| Codex (local app / IDE / CLI) | 全域 `$CODEX_HOME/AGENTS.md`（預設 `~/.codex/AGENTS.md`）；專案與目錄 `AGENTS.md` | `-Global` 會建立全域檔案；`-Global -Update` 會備份並取代作用中的全域指示檔案。Codex 會優先使用 Codex 家目錄中非空的 `AGENTS.override.md`，而非 `AGENTS.md` |
| Claude Code | `CLAUDE.md` 橋接、`~/.claude/CLAUDE.md`、專案鉤子／技能 | `CLAUDE.md` 是指示進入點；Claude Auto memory 是獨立的可選本機專案記憶，不跨工具共享 |
| Antigravity 2.0 | 專案 `AGENTS.md` / `GEMINI.md` / `.agents/rules/`；全域 `~/.gemini/AGENTS.md` 與 `GEMINI.md` 相容性指針；已部署的 `.agents/rules/agent-harness.md`（觸發條件：always_on）；已部署的 `.agents/hooks.json` 閘門鉤子 | 目前的文件列出兩個全域名稱；較舊版本可以跟隨指針找到規範檔案。Antigravity 要求 `.agents/rules/*.md` 具備含觸發條件的 YAML frontmatter，因此已部署的轉接器只是一個指向 `AGENTS.md` 的小型 always_on 指針，而非重複的規則集。閘門鉤子（PreToolUse/Stop/SessionStart/PostToolUse）會將 Antigravity 酬載轉譯為 Claude 閘門鉤子；建置環境中未驗證過實際的 Antigravity CLI/IDE 執行，協定層級測試通過 |
| Antigravity CLI | 專案／目錄規則；全域 `~/.gemini/AGENTS.md` 與 `GEMINI.md` 相容性指針；可選的 `~/.gemini/antigravity-cli/rules/*.md` | 通用規則使用規範進入點；CLI 專用規則請另外設定 |
| Antigravity IDE / extensions | 專案／目錄規則；全域 `~/.gemini/AGENTS.md` 與 `GEMINI.md` 相容性指針 | 目前的 IDE 支援兩個全域名稱；較舊世代的 IDE 可以跟隨指針 |
| WorkBuddy | `.workbuddy/rules/agent-harness.md` 規則橋接（指向 `AGENTS.md` 的符號連結，備援為指針）；已部署 `.workbuddy/settings.json` 閘門鉤子及 `.workbuddy/hooks/` 下的轉接器與六個 Claude 閘門指令碼副本 | Tencent CodeBuddy 的後繼者。橋接檔案部署不等同於載入驗證；請在已安裝的 WorkBuddy 版本上確認。閘門鉤子（PreToolUse/Stop/SessionStart/PostToolUse）把 Claude 形酬載原樣交給 Claude 閘門鉤子；建置此層的環境中無法進行 WorkBuddy 真機執行驗證，協定層級測試通過。設定檔位置另有說明：鉤子格式與設定檔位置本輪均未對照官方文件或真機核實（見下方 WorkBuddy 一節）；本倉庫發到 `.workbuddy/settings.json` |
| DeepSeek Harness (dsh) | 透過 `-Global` 設定全域 `${DSH_HOME:-~/.dsh}/AGENTS.md`；專案 `AGENTS.md` 原生讀取；技能透過 `.agents/skills/`；另部署 `.dsh/agent-harness-gate.mjs` Cordis 閘門外掛（TypeScript 原始碼 `.dsh/agent-harness-gate.ts`）+ `.dsh/cordis.patch.yml` 掛載行 | dsh 會原生讀取 `AGENTS.md`，因此不會建立專案橋接檔案。閘門外掛把 dsh 工具呼叫轉譯為 Claude 閘門鉤子；啟用需手動（把掛載行併入 profile 或 home patch，或以 `--patch` 傳入），且 dsh 外掛 API 未在官方文件／真機上核實，仍欠一次真機執行與文件複核——見下方 dsh 閘門段落 |
| GitHub Copilot | `.github/copilot-instructions.md` 橋接 | 請在 Copilot 目前的產品設定／文件中確認載入行為 |
| Zed / Pi / OpenCode | 僅可重複使用的 Markdown；本倉庫不提供專用設定 | 不得僅憑檔案存在就推斷會自動探索或全域載入 |

References: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---

## 3. Claude Code 用戶端 Hooks：PreToolUse（.claude/settings.json）

### 能力邊界
`.claude/settings.json` 中的 hooks 是 Claude Code 專屬的，僅在相符的工具呼叫之前執行。`guard.mjs` 會拒絕選定的命令模式；許多其他情況僅發出警告。正則匹配無法識別所有 shell 包裝器、別名或命令形式，因此這不是完整的安全邊界。Hooks 不會收集或傳輸記憶資料。Claude Code Auto memory 是獨立的本機專案功能，使用者可用 `/memory` 檢視/管理；本倉庫不對其進行配置。對於共享倉庫，請使用伺服器端分支保護和最小權限憑證。

### 配置與實作

安裝程式會複製 [`.claude/settings.json`](../../.claude/settings.json)（它接線了全部五個 Claude Code 鉤子事件），並部署 [`.claude/hooks/`](../../.claude/hooks/) 中的完整鉤子集：[`guard.mjs`](../../.claude/hooks/guard.mjs)（PreToolUse Bash 守衛）、[`guard-write.mjs`](../../.claude/hooks/guard-write.mjs)（Write/Edit 警告）、[`guard-feature-list.mjs`](../../.claude/hooks/guard-feature-list.mjs)（拒絕直接編輯 `feature_list.json`）、[`stop-gate.mjs`](../../.claude/hooks/stop-gate.mjs)（Stop 閘門）、[`session-start.mjs`](../../.claude/hooks/session-start.mjs)（SessionStart 續跑）與 [`post-tool-use.mjs`](../../.claude/hooks/post-tool-use.mjs)（成本帳本遙測）。請直接檢視這些原始檔；不要從舊版指南複製 hook 範例，因為協定和實作可能會變更。在 Claude Code、Antigravity、WorkBuddy 與 dsh 之外的宿主上，這些鉤子都不會執行，因此在它們上面請手動使用 `gate/pass-gate.py verify` / `check-clean`，並依賴 [`gate/README.md`](../../gate/README.md) 中所述的 CI 重新執行。

與宿主無關的第二道閘門（pre-push＋CI 範本）：對於沒有執行期鉤子的宿主，本倉庫提供一道完全不依賴任何宿主的閘門——只依賴 git、Python 3 與專案自身的 `gate/` 目錄。`templates/pre-push-gate/` 包含一個 `pre-push` 鉤子範本、其檢查器 `gate-prepush-check.py`，以及安裝器 `install-pre-push-gate.sh`；`templates/ci-gate-check.yml` 是 GitHub Actions 工作流程範本，請複製到專案的 `.github/workflows/gate-check.yml`。檢查器會重新執行每個 `passing` 項目的驗證命令，並拒絕過時的證據（evidence.command 必須等於 verification.command），呼應本倉庫自身的 CI 重新驗證（`tests/repo_checks.py` §3k）；人工覆寫的證據會被跳過，如 §3k 所述。獨立安裝器的安裝是明確選擇加入，而部署指令碼則預設開啟，分兩種形式：自行執行安裝器（除非傳入 `--force`，否則它會拒絕覆寫現有的鉤子；傳入 `--force` 時會先備份舊鉤子），或直接執行部署指令碼，部署指令碼會以慣常的「已存在則跳過／更新時備份」規則安裝這三個檔案（`.git/hooks/pre-push`、`scripts/gate-prepush-check.py`、`.github/workflows/gate-check.yml`）；傳入 `--no-prepush-gate`（PowerShell 為 `-NoPrepushGate`）可跳過它們（保留 `--prepush-gate` / `-PrepushGate` 以相容）。這道閘門的兩項誠實限制，無論在哪裡描述它都必須一併附上：它檢查的是工作樹的閘門狀態，而不是被推送提交的閘門狀態；而且 `git push --no-verify` 會完全繞過它，因此它只是本地的絆線，而非伺服器端控制——請搭配 CI 範本與伺服器端分支保護。pre-push 鉤子預設將 `check-clean` 作為警告執行（進行中的工作樹本來就不一定是可交接的乾淨狀態），只有設定 `GATE_PREPUSH_STRICT=1` 時才會因此阻擋；CI 範本則會在兩個步驟上都阻擋，因為 CI 檢查的是已提交的狀態。

Antigravity 閘門鉤子（專案 `.agents/hooks.json`，鉤子集 `agent-harness-gate`，遵循官方 [Antigravity hooks 參照](https://antigravity.google/docs/hooks/)）：部署指令碼會複製 [`.agents/hooks.json`](../../.agents/hooks.json) 與 [`.agents/hooks/`](../../.agents/hooks/) 中的轉接器（`antigravity-pre-tool-use.mjs`、`antigravity-stop.mjs`、`antigravity-session-start.mjs`、`antigravity-post-tool-use.mjs`，外加共用的 `antigravity-common.mjs`），以及它們所委派的六個 Claude 閘門指令碼的副本，因此僅有 Antigravity 的專案不需 `.claude/hooks/` 也能設閘門。對應關係為：`run_command`（參數 `CommandLine`）→ Bash 守衛；`write_to_file` / `replace_file_content` / `multi_replace_file_content`（參數 `TargetFile`）→ 寫入警告外加功能清單寫入阻擋；`Stop` → 停止閘門；`SessionStart` → 以系統訊息注入的閘門續跑；`PostToolUse` → 成本帳本記錄。閘門規則沒有重複：每個轉接器會將 Antigravity 酬載轉譯為 Claude 酬載，執行現有的 Claude 鉤子，再把決定轉譯回去。兩項形塑實作的協定事實絕不能被「簡化」掉：PreToolUse 的決定是必要且明確的——轉接器絕不會為 PreToolUse 印出 `{}`（它在各 Antigravity 版本中的處理方式仍有爭議），而是印出 `{"decision":"allow"}` 或 `{"decision":"deny","reason":...}`；而且鉤子在 Antigravity 本身是 fail-open 的（缺少二進位檔、逾時或無效 JSON 都只會記錄並讓工作階段繼續），因此每個轉接器的錯誤路徑同樣是 fail-open，並會在 stderr 上說明。Stop 轉接器會在 `gate/antigravity-stop-state.json` 中保存自己的第二次嘗試狀態（Antigravity 的 Stop 酬載沒有相當於 Claude Code `stop_hook_active` 旗標的欄位），因此工作階段不會被困在 `continue` 迴圈中；人工覆寫通道（`GATE_ALLOW_STOP=1`＋`GATE_STOP_REASON`）不變。驗證狀態如實陳述：協定層級測試通過（[`tests/antigravity-hooks.test.mjs`](../../tests/antigravity-hooks.test.mjs)，15 項測試：deny/allow、stop 先 continue 再 allow、工作階段續跑、帳本、fail-open），外加 2026-10-29 路徑修復的 2 項 cwd 回歸測試（共 17 項），部署冒煙測試也確認已部署的檔案能為臨時專案設閘門——但在建置此層的環境中無法進行實際的 Antigravity CLI/IDE 執行（沒有 `agy` 二進位檔），因此在稱此強制執行為久經考驗之前，仍欠一次在已安裝 Antigravity 版本上的實際執行。官方 hooks 參照將工作區 `.agents/hooks.json` 介面同時列給 App、CLI 與 IDE；這就是出貨單一工作區檔案的依據，而非實際的 IDE 驗證。鉤子命令 cwd 修復（2026-10-29，agy CLI 1.4.10 `--print` 實測）：agy 以 cwd = `<專案>/.agents` 執行這些命令，因此四條命令統一寫作 `node hooks/<轉接器>.mjs`；舊的 `node .agents/hooks/...` 寫法會在該 cwd 下翻倍為 `.agents/.agents/hooks/...`，agy 隨後以鉤子載入錯誤拒絕被覆蓋的工具呼叫，而不是 fail-open——所以這個 bug 是「擋住了工具」，而不只是「攔不住」。同理修正了轉接器的專案根回退邏輯（`workspacePaths` 缺失時，cwd 為 `.agents` 則取其父目錄）。取捨如實說明：該寫法只對實測的 CLI 1.4.10 cwd 正確；Antigravity IDE 的 cwd 仍未真機驗證，若將來 IDE 實測顯示其 cwd 為工作區根，則一份共用 hooks.json 無法用一條相對路徑同時服務兩種 cwd——屆時須另行處理（例如分宿主檔案或探測包裝），不能為了一邊而悄悄給另一邊加回前綴。本地倉庫檔案中沒有記載 hooks.json 相對變數，因此這裡不聲稱存在一種 cwd-proof 的單條命令。已部署專案不會僅因範本改動而自動修復：部署指令碼在非更新模式下會跳過已存在的 `.agents/hooks.json`，已有部署須以更新模式重部署（程式碼路徑：先備份再覆蓋）或手動改四條命令。

WorkBuddy 閘門鉤子（專案 `.workbuddy/settings.json`，採用假定的 Claude Code 相容鉤子協定——本輪未驗證：官方 WorkBuddy／CodeBuddy 鉤子文件在本輪並未抓取（夜間窗口內不做外部抓取），也沒有已安裝的 WorkBuddy 可供真機驗證，因此以下鉤子格式、設定檔位置與輸出形式在已安裝版本的真機執行確認之前都只是暫定；先前的草稿曾為此形式引用 [Hooks Reference](https://staging-codebuddy.tencent.com/docs/cli/hooks) 與 [Plugin Reference](https://www.workbuddy.ai/docs/cli/plugins-reference)，但本輪並未重新抓取或驗證這兩個連結）：選取 WorkBuddy 時，部署指令碼會複製 [`.workbuddy/settings.json`](../../.workbuddy/settings.json) 與 [`.workbuddy/hooks/`](../../.workbuddy/hooks/) 下的轉接器（`workbuddy-pre-tool-use.mjs`、`workbuddy-stop.mjs`、`workbuddy-session-start.mjs`、`workbuddy-post-tool-use.mjs`，外加共用的 `workbuddy-common.mjs`），以及它們所委派的六個 Claude 閘門指令碼的副本，因此僅有 WorkBuddy 的專案不需 `.claude/hooks/` 也能設閘門。與 Antigravity 不同，這裡假定不需要酬載轉譯：WorkBuddy／CodeBuddy 鉤子假定收到的是同樣的 Claude 形 stdin（`tool_name`、`tool_input`、`cwd`、`session_id`），因此對應關係是恆等——`Bash` → Bash 守衛，`Write|Edit|NotebookEdit` → 寫入警告外加功能清單寫入阻擋，`Stop` → 停止閘門，`SessionStart` → 閘門續跑，`PostToolUse` → 成本帳本記錄。只有輸出形式與 Claude 不同的兩處做了轉譯：SessionStart 的純文字會被包成 `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`，Stop 的 exit 2 會變成 `{"continue": false, "reason": "..."}`（假定的現行形式；`"decision": "block"` 假定已廢棄）。兩項形塑實作的協定事實絕不能被「簡化」掉：PreToolUse 的放行是 exit 0 且無 stdout——走正常的權限流程，轉接器絕不印出顯式的 `"allow"`，因為顯式放行會憑閘門一己之力跳過宿主的權限確認；而且每個轉接器的錯誤路徑都是 fail-open 並在 stderr 上說明，與 `guard.mjs` 的分級策略一致。Stop 轉接器會在 `gate/workbuddy-stop-state.json` 中保存自己的第二次嘗試狀態（這裡假定的 Stop 酬載沒有相當於 Claude Code `stop_hook_active` 旗標的欄位；若宿主確實傳了它，`stop-gate.mjs` 自己會處理第二次嘗試），`GATE_ALLOW_STOP` 覆寫通道不變。驗證狀態如實陳述：協定層級測試通過（[`tests/workbuddy-hooks.test.mjs`](../../tests/workbuddy-hooks.test.mjs)，16 項測試：deny/allow、stop 先攔再放行、工作階段續跑、帳本、fail-open），部署冒煙測試也確認已部署的檔案能為臨時專案設閘門——但在建置此層的環境中無法進行實際的 WorkBuddy 執行（沒有安裝 WorkBuddy 二進位檔），因此在稱此強制執行為久經考驗之前，仍欠一次在已安裝 WorkBuddy 版本上的實際執行。設定檔位置的疑點同樣要等到那次真機執行才能了結：先前草稿引用的舊 CodeBuddy 路徑是 `.codebuddy/settings.json`（使用者級 `~/.codebuddy/settings.json`，本輪同樣未核實），而本倉庫把 WorkBuddy 建置的設定發到 `.workbuddy/settings.json`，與本倉庫已有的 `.workbuddy/rules/` 橋接一致。若已安裝的 WorkBuddy 仍讀舊路徑，把已部署的 `.workbuddy/settings.json` 複製到 `.codebuddy/settings.json` 即可——鉤子命令是專案根相對路徑（`node .workbuddy/hooks/...`），不需改動。WorkBuddy 在此層沒有全域鉤子檔案；它的專案橋接仍是 `.workbuddy/rules/agent-harness.md`，若想要機器層級的 WorkBuddy 規則檔案，請手動在 `~/.workbuddy/rules/` 下建立。

dsh 閘門外掛（專案 `.dsh/agent-harness-gate.mjs`，TypeScript 原始碼 `.dsh/agent-harness-gate.ts`，Cordis 外掛；按下文實作形態的外掛契約均未驗證，見本段末尾的驗證狀態）：dsh 沒有 `hooks.json` 介面——一切都是經 Cordis patch 行掛載的外掛——因此部署指令碼會複製外掛檔案、六個 Claude 閘門指令碼的副本（放入 `.dsh/hooks/`，備援為 `.claude/hooks/`），以及一份產生的 `.dsh/cordis.patch.yml`，其 `__PLUGIN_PATH__` 佔位符會填入已部署外掛的絕對路徑。啟用是手動的，因為 dsh profile 存在 `$DSH_HOME` 下，部署執行時可能還不存在：把產生的行併入 `$DSH_HOME/profiles/<profile>/cordis.patch.yml`（僅該 profile）、`$DSH_HOME/cordis.patch.yml`（所有 profile），或每次啟動時以 `dsh --profile <profile> --patch .dsh/cordis.patch.yml` 傳入。按實作的對應關係為：`tools/pre-execute`（waterfall，`{ kind: "deny", reason }` 回傳——契約未驗證，見下方）→ `bash`／`pwsh` 命令的 Bash 守衛，以及檔案寫入的寫入警告外加功能清單寫入阻擋，同樣的轉譯在可用時也會註冊為單調的 `ctx.tools.guard()` 最終拒絕；`agent/created` → 經 `agent.inject()` 注入的閘門續跑（dsh 沒有 SessionStart 鉤子；工作階段歷史本身會從 dsh 的僅附加日誌原生續跑）；`tools/result` → 成本帳本記錄（僅觀察，絕不做決定）；`agent/turn-stopping`（serial，無 `next()`）→ 停止閘門，在 `gate/dsh-stop-state.json` 中保存自己的第二次嘗試狀態，經公開的 Agent 介面導向。閘門規則沒有重複：外掛把 dsh 執行轉譯為 Claude 酬載，執行現有的 Claude 鉤子，再把決定轉譯回去，而且它只 import Node.js 內建模組，因此不需要 npm install 步驟。驗證狀態如實陳述：協定層級測試通過（[`tests/dsh-gate.test.mjs`](../../tests/dsh-gate.test.mjs)，19 項測試：deny/allow、單調守衛、帳本、續跑、停止先導向再放行、fail-open），TypeScript 原始碼通過直接的 Node 24 型別剝離 import 檢查，部署冒煙測試也確認了已部署的檔案——但 dsh 外掛 API 在本輪並未對照官方文件或真機執行驗證（dsh 外掛 API 未在官方文件／真機上核實）：本輪在夜間批次不彈批准卡的紀律下沒有抓取外部文件，建置環境中也沒有安裝 dsh，而且本地倉庫中沒有 Cordis 外掛 API 規格，因此此外掛中的每個事件名稱、酬載形狀與導向介面——包括 `tools/pre-execute` 的 deny 回傳——都是從先前工作的文件閱讀沿用而來的未驗證契約，而非重新驗證過的事實。在稱 dsh 強制執行的任何部分為硬閘門之前，仍欠一次在已安裝 dsh 版本上的真機執行，以及一次對照官方文件的複核，而且由於 dsh 仍處於開發者預覽階段、預期會有破壞性變更，外掛必須對照已安裝的 dsh 版本重新檢查。

### 其他工具的對應方案（擴充點）

PreToolUse 風格的攔截不再是 Claude Code 專屬：安裝程式現在也會部署上述的 Antigravity 與 WorkBuddy 鉤子以及 dsh 閘門外掛。無論在哪一層掛接 hook，都無法取代伺服器端分支保護；用戶端攔截只是縱深防禦中的一層。

---

## 4. 跨工具部署與範本更新（deploy-agents）

腳本將檔案部署到配置的路徑。檔案部署並不保證工具特定的載入行為。`-Global` 會初始化缺失的全域規則檔案並保留現有檔案。組合使用 `-Global -Update` 會先建立時間戳記備份，然後用當前範本取代作用中的全域規則。Antigravity 會收到規範的 `~/.gemini/AGENTS.md` 加上一個小型的 `GEMINI.md` 相容性指針，而非重複的完整規則集。DeepSeek Harness（dsh）會在相同的保留／備份規則下，從 `$DSH_HOME`（預設為 `~/.dsh`）收到一份全域 `AGENTS.md`。WorkBuddy 在此層沒有全域鉤子檔案；它的專案橋接是 `.workbuddy/rules/agent-harness.md`，選取 WorkBuddy 時還會部署專案鉤子 `.workbuddy/settings.json` + `.workbuddy/hooks/`（見 §3），若想要機器層級的 WorkBuddy 規則檔案，請手動在 `~/.workbuddy/rules/` 下建立。Codex 在設定了 `$CODEX_HOME` 時使用該路徑（否則使用 `~/.codex`）；如果其中存在非空的 `AGENTS.override.md`，則會備份並更新該作用中檔案，而非 `AGENTS.md`：
- **Windows PowerShell**：[`deploy-agents.ps1`](../../deploy-agents.ps1)
- **Linux / macOS Bash**：[`deploy-agents.sh`](../../deploy-agents.sh)

### 4.1 腳本核心架構與流水線

```text
[ Execute Deployment Script ]
       │
       ├─ [Zero arguments in terminal OR with -Interactive / --interactive]
       │       ▼
       │  Phase 0: Interactive Step-by-Step Terminal Wizard (TUI Arrow-Key & Checkboxes)
       │    ├─ [1/5] Select Template Language (English / 简体中文 / 繁體中文)
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
- `-Language`（`-l`）：選擇範本語言（`en`、`zh`、`zh-tw`；預設為 `en`）。
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
4. 讓伺服器僅綁定 loopback，供同一台機器使用。預設資料位置在 Linux 上為 `~/.local/share/ai-memory`，在 macOS 上為 `~/Library/Application Support/ai-memory`，在 Windows 上通常為 `%LOCALAPPDATA%\ai-memory`；`AI_MEMORY_DATA_DIR` 可以覆寫它們。
   - **Docker 部署（用於 Antigravity IDE HTTP MCP）**：
     ```bash
     # 容器內儲存路徑必須為 /data；僅綁定 loopback 127.0.0.1
     mkdir -p "${HOME}/env/ai-memory-data"
     docker run -d --name ai-memory \
       --restart unless-stopped \
       -p 127.0.0.1:49374:49374 \
       -v "${HOME}/env/ai-memory-data:/data" \
       docker.io/akitaonrails/ai-memory:latest
     ```
     *注意：Docker 容器不需要掛載倉庫目錄樹或 `.ai-memory.toml`。Antigravity IDE 透過 MCP 工具呼叫傳遞專案上下文（`workspace`/`project`）。*
   - 使用 `ai-memory --data-dir <data-dir> backup --to <archive-path>` 備份（Docker 部署請使用上游的容器命令）。`ai-memory uninstall --apply` 會移除受管的用戶端整合，但不會刪除資料。若要清除記憶，請先確認備份與目標，再停止服務並移除其設定的資料目錄。詳見[官方安裝／操作指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md)。

#### 宿主邊界

- **Claude Code：** 上游 MCP/hooks；ai-memory 只擁有自己的條目，並保留無關的鉤子。現有的 Claude `PreToolUse` 安全鉤子維持獨立。Claude Code 預設的 auto-memory 同樣獨立且僅限本機。
- **Codex CLI：** 上游 `--client codex` / `--agent codex` 整合。**Codex desktop：** 在支援的地方使用本地 Codex 配置介面；請驗證已安裝應用程式的 hook/MCP 可用性，而非假設每個 CLI 版本的行為都相同。
- **Antigravity CLI：** 上游 `antigravity-cli` MCP/hooks。在 Windows 上，請在啟動 agent 的同一個環境中執行設定。
- **Antigravity 2.0 與 IDE：** 輔助工具使用上游 Antigravity MCP 安裝器，寫入共用的 `~/.gemini/config/mcp_config.json` 與受管的專案指示。目前的 ai-memory 上游沒有專門的 2.0/IDE 生命週期鉤子目標，因此這只是 MCP-only，不會自動擷取工作階段事件。手動 MCP 設定使用 `serverUrl=http://127.0.0.1:49374/mcp`；詳見 [Antigravity MCP 文件](https://www.antigravity.google/docs/mcp)。
- **ChatGPT web：** 零金鑰、loopback 的設定與遠端網頁聊天沒有直接連接。請手動使用簡潔的 Markdown 交接。遠端 MCP／寫入存取不在此免費本地設定的範圍內。
- **Windows：** 上游同時記載了 WSL2 與原生 Windows。請在啟動各 agent 的同一個環境中安裝並設定 ai-memory；不要混用 WSL 與 Windows 的鉤子路徑。關於用戶端特定的支援，請檢視 [Windows 指南](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md)。

ai-memory 的 allowlist 模式僅在已安裝的原生鉤子強制執行擷取政策時，才能保證不擷取沒有標記的倉庫。它的路徑排除不會塗銷任意的提示文字；絕不要在提示中包含機密。詳見 [marker-file 參照](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md)。

### 5.2 專案路由器：`Project AGENTS.md`
- 可調整的倉庫級範本。
- 在部署時加上 `-Initialize` / `--initialize`，可從可驗證的本地事實與待處理事項檢查清單產生草稿。`-DirectoryPath <relative-path>` / `--directory <relative-path>` 也會初始化現有的模組目錄。指令碼不會猜測專案用途、所有者或模組邊界。現有的 `AGENTS.md` 檔案會被保留；產生的審查副本使用 `AGENTS.generated.md`。
- 偵測到的 `package.json` 指令碼與常見框架／儲存依賴會顯示為待審查的建議，而非已驗證的事實；在依賴這些命令或邊界之前請先確認。
- 在採用產生的規則之前，執行 `-Check` / `--check`（可選擇性地加上目錄參數）掃描未解決的範本欄位；發現任何未解決欄位時，命令會以非零結束狀態回傳。
- 提供標準的 CLI 命令欄位（install、dev、build、針對性測試、lint、format、migration）、架構紅線、**規則與技能分派矩陣**、選擇性的 Markdown 記憶規則，以及可選的 ai-memory 整合指引。

---

### 5.3 模組化子規則：`.agents/rules/`
按需漸進式載入：
- **`token-discipline.md`**：限制讀取、擷取與表達；要求使用 AST 索引而非盲目 grep；
- **`engineering-spec.md`**：SDD 規格優先（In/Out scope）、TDD 驗證閘門（需要實體證明）；
- **`security-boundary.md`**：8 項高風險操作確認矩陣、憑證零洩漏、大檔案安全；
- **`git-workflow.md`**：受保護分支隔離（零直接提交）、遠端推送必須授權、提交格式 `{type}: {description}`。

---

### 5.4 微邊界補丁：`Directory AGENTS.md`
- 僅在**必要時**於 monorepo 套件（`packages/*`）或隔離的子模組中建立。
- 使用 `-Initialize -DirectoryPath <relative-path>`（PowerShell）或 `--initialize --directory <relative-path>`（Bash）產生一份；目標必須已存在於專案根目錄內。模組路徑／名稱會被偵測，而責任與邊界仍是明確的審查項目。
- 定義 In/Out scope、允許／禁止的依賴，以及針對性的本地測試命令（例如 `pytest tests/submodule -q`）。

---

## 6. 雙軌實戰工作流程：「工程優先，文件次之」

### 1. 軟體工程軌（嚴格閘門）
- 範圍：API、功能、錯誤修復、重構。
- 規則：
  - 僅在存在且相關時，才在任務開始時讀取 `PROJECT_CONTEXT.md` 與 `SESSION_STATE.md`，然後驗證實質事實；
  - 一律在臨時分支（`feature/*`、`fix/*`）上工作；
  - TDD 紅綠循環，以實際測試執行驗證；
  - 遵循 Git 授權模型；
  - **選擇性記憶更新**：在有意義的收尾時更新 `SESSION_STATE.md`；僅在持久專案事實變更時才更新 `PROJECT_CONTEXT.md`。

### 2. 技術文件軌（輕量旁路）
- 範圍：Markdown 文件、README、API 規格、Word/PDF 報告。
- 規則：**豁免執行測試套件**；善用專門技能（`docx`、`pdf`、`write-openspec-docs`）；維持 GitHub Flavored Markdown 標準。

---

## 7. 常見問題與最佳實踐（FAQ）

### Q1：為什麼不把所有專案命令都放入 `Global AGENTS.md`？
> **答**：全域規則常駐於機器上的所有工作階段。加入專案特定的命令會造成跨專案的上下文污染並浪費提示 tokens。

### Q2：線上更新（`-Update`）如何保護自訂的專案配置？
> **答**：現有的專案 `AGENTS.md` 會被保留，並產生一份 `AGENTS.template.md` 供審查。`-Global` 會在保留現有檔案的同時，初始化缺失的 Claude Code、Antigravity 與 Codex 全域指示。組合使用 `-Global -Update` 會建立時間戳記備份，並以當前範本取代這些全域檔案；Codex 作用中的非空 `AGENTS.override.md` 會就地更新，取代 `AGENTS.md`。

### Q3：39+ 個 skills 如何避免撐爆上下文視窗？
> **答**：取決於宿主如何探索和載入 Skills。不要假設固定的中繼資料成本或快取折扣；僅保持有用的 Skills 啟用，並在目標宿主中驗證行為。

### Q4：什麼是 8 項高風險操作保護矩陣？
> **答**：定義於 `security-boundary.md`，在以下操作前需要人工確認：
> 1. 修改建置配置（`package.json`、`CMakeLists.txt`、`.pro`、`Cargo.toml`）；
> 2. 引入新的第三方依賴；
> 3. 修改全域公開資料結構（`public_struct.h`、`types.ts`）；
> 4. 變更核心分派單例或公開服務介面；
> 5. 修改通訊協定或線路契約（`protofile/`）；
> 6. 變更授權、密碼學或驗證程式碼；
> 7. 修改 `.gitignore` 或 CI/CD 流水線；
> 8. 影響共享契約或需要廣泛協調的高影響跨模組變更；僅檔案數量本身不是風險觸發條件。

### Q5：何時應該更新 `PROJECT_CONTEXT.md` 和 `SESSION_STATE.md`？
> 在有意義的任務/工作階段邊界，用已完成的工作、實際驗證證據、剩餘步驟和仍相關的風險更新 `SESSION_STATE.md`。僅在持久的架構、約束或已確認的決策變更時才更新 `PROJECT_CONTEXT.md`。不要建立無實質變更的更新。這兩個檔案都是專案記憶的摘要；它們不會覆蓋當前使用者指示、程式碼、配置或可重現的證據。絕不儲存憑證、原始個人資料或完整對話/工具日誌。

---

## 8. 實戰用法與技能全景指南參考

有關 Slash Commands（`/comet`、`/plan`、`/opsx`）、CodeGraph、TDD 以及完整端到端執行演練的詳細教學，請參閱：
👉 [Tools Practical Usage and Skills Panorama Guide（繁體中文）](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md) | [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [簡體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
