# Project AGENTS.md

## 繼承與定位

- 本文件是當前專案的根指令文件，補充 [Global AGENTS.md] 的通用底線，提供本專案專有的工程上下文。
- 採用**漸進式揭露（Progressive Disclosure）**架構，本專案的高頻紅線與命令在此維護，細粒度規則存放於 `.agents/rules/`，Agent 僅在需要時按需查閱。

## 專案概覽

- **專案名稱**：`<PROJECT_NAME>`
- **業務定位**：`<PROJECT_PURPOSE>`（一句話說明核心業務場景與目標受眾）
- **核心維護者**：`<OWNERS>`
- **程式碼倉庫與預設分支**：`<REPOSITORY_URL>`；預設分支 `<DEFAULT_BRANCH>`（以遠端 `origin/HEAD` 為準）

## 常用開發命令（CLI 上下文）

> 執行命令前先確認工作目錄。必須採用過濾參數防日誌刷屏，嚴禁將全量日誌直接倒入上下文。

```bash
# 1. 依賴管理 / 建置配置
<INSTALL_COMMAND>                  # 例：npm ci / poetry install / cmake -B build / go mod download / cargo check

# 2. 本地開發與編譯建置
<DEV_COMMAND>                      # 例：npm run dev / python main.py / cargo run
<BUILD_COMMAND>                    # 例：npm run build / cmake --build build / go build ./... / cargo build --release

# 3. 精準單測與驗證（改動後必須執行，輸出須精簡）
<UNIT_TEST_COMMAND>                # 例：npm test -- --reporter=dot / pytest -q / ctest --output-on-failure
<TARGETED_TEST_COMMAND>            # 針對單文件的測試：npm test -- <path> / pytest <path> -q / ctest -R <test_name>
<INTEGRATION_TEST_COMMAND>         # 整合測試：npm run test:e2e

# 4. 程式碼品質、Lint 與靜態檢查
<LINT_COMMAND>                     # 例：npm run lint / ruff check . / clang-tidy / golangci-lint run / cargo clippy
<FORMAT_COMMAND>                   # 例：npm run format / black . / clang-format -i / gofmt -w . / cargo fmt
<TYPE_CHECK_COMMAND>               # 例：npm run typecheck / mypy .

# 5. 資料庫遷移與發布（高危操作需確認）
<MIGRATION_COMMAND>                # 例：npm run db:migrate / alembic upgrade head
```

## 技術棧與執行環境

| 類別 | 技術選型與版本 | 補充說明 |
|---|---|---|
| **語言 & 標準/執行環境** | `<LANGUAGE_AND_VERSION>` | 例：C++20 / Python 3.11 / TypeScript 5.4 (Node 20) / Go 1.22 / Rust 1.78 |
| **套件管理器 / 建置工具** | `<PACKAGE_MANAGER>` | 例：CMake+Ninja / Conan / Poetry / pnpm / Cargo / Go Modules |
| **核心框架 / 第三方函式庫** | `<FRAMEWORK>` | 例：Qt 6 / Boost / FastAPI / Next.js / Gin / Tokio |
| **持久層 & 儲存** | `<DATABASE_AND_CACHE>` | 例：PostgreSQL 16 / SQLite 3 / Redis 7 |
| **CI/CD 配置** | `<CI_PATH>` | 例：`.github/workflows/ci.yml` / `.gitlab-ci.yml` |

## 架構核心紅線

1. **單向分層依賴**：上層呼叫下層，底層嚴禁反向引用上層業務，嚴禁模組間循環依賴。
2. **統一例外流**：業務錯誤必須拋出統一封裝的業務例外，嚴禁靜默吞掉例外；非同步必須包含錯誤攔截。
3. **配置隔離**：所有配置透過統一環境變數/配置模組讀取，嚴禁深層硬編碼或直接讀取原生 env。
4. **日誌去敏**：任何印出到終端機或日誌的敏感欄位（PII、Token、密碼）必須遮罩去敏。
5. **風險分級**：按 `.agents/rules/security-boundary.md` 區分提醒、告知與必須授權的操作；文件數量本身不構成確認門檻。
6. **Git 受保護分支隔離**：禁止在受保護分支（develop/master/main）直接改程式碼，改動一律切臨時分支，嚴禁 `git add .` 防誤提交。

## 子級規則與工程技能調度矩陣（按需查閱與喚醒）

為避免上下文單次載入膨脹，以下細粒度規約與專業技能存放在 `.agents/rules/` 與 `.agents/skills/`，相關場景按需查閱或呼叫；需要外部 CLI / MCP 的技能僅在其已安裝並配置後可執行：

| 研發場景 | 綁定規則 / 技能 | 喚醒語法與觸發動作 | 預期行為規範 |
|---|---|---|---|
| **分支流轉 / 提交 / 推送** | `git-workflow.md` | 涉及任何 `git commit` / `git push` / 分支切換 | 嚴格在臨時分支提交；禁止 `git add .`；觸碰共享遠端必須明確授權；禁 force push |
| **高危操作 / 核心結構變更** | `security-boundary.md` | 觸發規則定義的授權門檻 | 按風險等級說明影響；僅明確要求授權的操作暫停等待 |
| **複雜需求 / 架構改造** | `engineering-spec.md` + 可選 `comet` / `openspec` 工作流 | 使用者指定工作流或專案已配置該工作流 | 遵守所選工具當前版本的流程與狀態文件；未配置時按任務需要規劃，不假定自動守衛 |
| **程式碼依賴 / 尋找符號引用** | `token-discipline.md` + 可選 `codegraph` | CodeGraph MCP 可用時進行語意探索；否則用限定範圍的 `rg` | CodeGraph CLI/MCP 未安裝配置時，不假設可呼叫；搜尋範圍應與問題相關 |
| **功能實現 / 編碼階段** | `engineering-spec.md` + `ponytail` + `test-driven-development` | 按需查閱已部署的 Skill；測試按任務風險和專案要求執行 | 先理解現有實現，再選最小正確方案；遵循適用的 Ponytail 階梯驗證 |
| **複雜 Bug / 偶發排障** | `engineering-spec.md` + `systematic-debugging` | 貼上完整報錯 Trace | 嚴禁創可貼盲修；必須先收集證據、建立假設、定位根因再寫修復 |
| **超長輸出 / 測試批次執行** | `token-discipline.md` + 可選 `rtk` | RTK Hook 已配置時由其改寫支援的命令；否則使用 CLI 原生精簡參數 | 不假定命令會被自動改寫；必要時將長日誌儲存在本地並只回報相關摘要 |
| **Token 告急 / 精簡輸出** | `Global AGENTS.md` + 可選 `caveman` | 宿主工具支援並載入該 Skill 時按需啟用 | 精簡表達但保留安全說明、必要上下文和技術準確性 |
| **文件建立 / 架構與追溯同步** | `engineering-spec.md` + 可選 `living-documentation` | `/living-documentation` / 需求架構與詳細參考歸檔 | 依據 L0/L1/L2 門檻同步四階文件，維護 Frontmatter 程式碼與文件雙向追溯引用 |
| **程式碼審查 / 合併前品質門禁** | `open-code-review` + `requesting-code-review` | 完成功能或合併前 | 規則先行、行號錨定、全量覆蓋；`ocr` CLI 已裝走 Tier A 委託，否則走 Tier B 方法論 |

---

## 動態記憶與任務追蹤

- **會話啟動**：在文件存在且與任務相關時，查閱 `PROJECT_CONTEXT.md` 與 `SESSION_STATE.md`；核實會影響當前工作的分支、狀態、配置和實現事實。
- **專案長期記憶**：`PROJECT_CONTEXT.md` 記錄經驗證且跨任務有用的架構事實、硬約束、技術決策及其理由。它是專案摘要與導航入口，不取代程式碼、配置或正式設計文件；盡量附上來源路徑或決策記錄。
- **會話斷點**：在有意義的任務/會話邊界更新 `SESSION_STATE.md`，記錄已完成工作、實際驗證證據、未完成步驟和仍有效的環境風險。新會話開始時核實其內容，並刪除已過期的斷點；沒有實質變化時不製造空更新。
- **更新範圍**：只有專案長期事實發生變化時才改 `PROJECT_CONTEXT.md`；只改當前斷點時只更新 `SESSION_STATE.md`。任務較小且沒有新的持久事實時，不要求同步改寫兩者。
- **複用經驗**：專案使用 `tasks/lessons.md` 時，僅記錄尚未進入規則或專案文件的可複用經驗；使用 `tasks/todo.md` 或工具計畫記錄進行中事項，避免重複維護進度。
- **來源與時效**：把推斷標記為推斷；易變化的事實記錄日期或來源。記憶與當前使用者指令、程式碼、配置或可複現證據衝突時，以當前指令和證據為準，並在適當時修正記憶。
- **隱私與安全**：不儲存憑證、私鑰、原始個人資料、完整對話/工具日誌或不必要的個人資訊；共享倉庫不儲存使用者私人偏好。
- **可選長期記憶**：跨工具記憶僅使用本地 ai-memory 方案；預設不部署、不啟動，亦不要求 API Key。需要自動採集時，先按《多工具部署配置指南》顯式安裝原生 hooks/MCP，並建立本機忽略的 `.ai-memory.toml`；未啟用或服務不可用時繼續依靠本倉庫 Markdown，不得阻塞任務。
- **共享記憶技能**：涉及跨會話延續、長期專案決策、研究或文件/設計方案時，按需使用 `.agents/skills/cross-tool-memory/SKILL.md`；不儲存完整對話、憑證或未經核實的結論。
- **活體文件與程式碼追溯**：專案長期技術文件統一維護於 `docs/` 下（需求 `docs/specs/`、架構 `docs/architecture/`、介面與配置參考 `docs/reference/`、使用者操作指南 `docs/guides/`）。各文件頭部 Frontmatter 聲明 `modules`（關聯程式碼路徑）與 `depends_on`。詳見 `.agents/skills/living-documentation/SKILL.md`。

## 目錄級規則索引

當專案為 Monorepo 或存在高隔離獨立子模組時，僅在必要子目錄下按需建立 `AGENTS.md`：
- 在確有獨立邊界的子模組中新增其 `AGENTS.md`，定義專屬 In/Out Scope 與快速驗證命令；普通目錄直接繼承本文件，避免重複根規則。
