# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Releases are tagged `vX.Y.Z` from `main` by the maintainer.

## [Unreleased]
### Added
- **Phase 2（共识方案 v3）：门禁变真**：`--strict` 落到 pipeline 与工具（`run-pipeline.sh` / `.ps1`，`sync-skills.py`、`doc-impact.py`；失败在 strict 下记 FAIL、退出 1，默认 advisory 下记 WARN、退出 0，永不记 PASS）；comet 供应链 pin（实测 2026-10-28：`npm view @rpamis/comet version` → 0.5.1，`tools/check-comet.py` 为运行时门禁；codegraph / rtk 安装脚本改为下载后 SHA256 校验才执行，`curl | sh` / `irm | iex` 已清零；lock 幽灵元条目标注 `meta: true` 不删除）；hooks 补齐五事件（新增 SessionStart 恢复摘要、PostToolUse 成本记账，CI 现跑全部四个 hook 测试文件）；Guard 分级加固（展开 `$(...)` / 反引号 / `eval` / `sh -c` 间接执行，解析失败仍 fail-open 但记日志，绝不一刀切 fail-closed）；成本护栏（`tools/cost-ledger.py`：代理指标记账 + 预算检查，超预算只告警并记 `budget_exceeded` 事件、永不自动停止；统一 token 台账因无宿主提供可编程 token API 而推迟，见 `docs/internal/token-adapters.md`）。验证记录见 `docs/internal/phase2-verification.md`；决策 D9–D13。
- **Phase 1（共识方案 v3）：`gate/` 门禁层**：`gate/feature_list.schema.json`（功能清单状态机：not_started / in_progress / blocked / passing，WIP=1，passing 须带证据、不可逆除非带理由 reopen）；`gate/pass-gate.py`（只用 Python 标准库：init / add / start / verify / block / unblock / reopen / override / status / check-clean / events）；`gate/init.template.sh`（新项目脚手架 + 一次 smoke 验证，占位符未填则 init 失败）；`gate/events.jsonl`（只追加事件日志）；`gate/README.md`（用法、防篡改三件套与诚实列出的缺口、人工兜底通道）。
- **Phase 1 防篡改三件套（纵深防御，不承诺防住）**：`.claude/hooks/guard-feature-list.mjs`（PreToolUse 拦截对 `feature_list.json` 的直接写，仅 Claude Code 生效）；`tests/repo_checks.py` §3k（CI 二次核对：重跑 passing 项的验收命令 + 事件日志单调性与覆盖）；`gate/events.jsonl` 留痕。Dogfood 实测两次拦截虚假通过（见 `docs/internal/phase1-dogfood.md`）。
- **Phase 1 Stop 钩子兜底通道**：`.claude/hooks/stop-gate.mjs`（有 in_progress 项时阻止停止；`GATE_ALLOW_STOP=1` + 非空 `GATE_STOP_REASON` 可放行并记 `stop_override` 事件）；`pass-gate.py override`（人工放行须带理由，证据里可见 `override`）。
- **Phase 1 会话模板（仅 EN + ZH，非中英冻结）**：`templates/SESSION_STATE.template.md` / `.zh.md` 改为 ≤1 页断点格式；新增 `templates/DECISIONS.template.md` / `.zh.md`；本仓 `docs/internal/SESSION_STATE.md` 已按新格式迁移（dogfood 1）。
- **Phase 0（共识方案 v3）**：技能计数单一事实源（`tools/count-skills.py` + `tests/repo_checks.py` §3i，磁盘实测 40 个 skill）；技能引用/占位符 CI 检查（§3j）；`DECISIONS.md`（D1–D4、N1/N3/N4、N5、U1–U3 书面记录）；`THIRD-PARTY-LICENSES.md`（42 行，与 `skills-lock.json` 1:1）；`docs/internal/users-and-change-cost.md`（暂定用户画像 + 一次规则改动的实测触及面）；`docs/internal/ai-memory-routing.md`（ai-memory 路由块自根 `AGENTS.md` 移出，根文件 156 行 → 61 行）。
- **部署脚本 opt-in 重型技能**：`--include-heavy-skills` / `-IncludeHeavySkills`（`docx` 约 1.3 MB、`brainstorming` 含本地服务 `server.cjs` 默认不再部署；`skills-lock.json` 仍保留两者）。
- **部署目标目录不存在时自动创建**（`mkdir -p` / `New-Item -Force`；已存在但不是目录时仍报错退出）。
- **研发全生命周期角色协同与阶段门禁（Phase Gates）**：在 `Global AGENTS` 与 `Project AGENTS`（5 种语言模板）中全面引入五大核心角色（PM、架构师、程序员、代码审查员、QA）的协同闭环，规范“需求 ➔ 架构 ➔ 编码 ➔ 审查 ➔ 测试 ➔ 交付”的环环相扣准出门禁。
- **专家团队评审法定席位（Mandatory Expert Panel）**：在模板中确立多专家评审执行契约，强制要求架构师、安全审计员、技术实现专家、QA 测试专家（需求阶段含产品经理）必须出席并出具 `File:Line` 行级证据与明确裁决，杜绝大模型无依据的泛泛角色扮演。
- **Agent 正确触发与常见问题排查指南 (FAQ)**：新增 `docs/guides/Agent Triggering and FAQ Guide.zh.md`（及软链 `docs/FAQ.zh.md`），系统梳理代码审查工具错配、AI 记忆占位符跳过、Comet 状态机唤醒、TDD/科学调试与证据门实践等核心高频问题，并提供开箱即用的精准 Prompt 模板速查库。

- **git-workflow.md 大幅增强**（借鉴 liangxin-lrjcs/skill-git-workflow 的策略，改编为通用模板）：新增 Commit/Push 自查清单、冲突协同解决协议、Cherry-pick 与回退矩阵（含 revert-the-revert 陷阱）、分支命名规范、提交信息正文纪律、禁止操作速查、常用命令速查；Bisect/Reflog 拆分为按需加载的 `git-forensics` skill。
- **ai-memory Docker deployment guide**: Documented official Docker container deployment patterns and volume mapping guidelines (fixing in-container `/data` mount path, loopback binding for security, and client-server scope decoupling via `.ai-memory.toml`) across deployment guides and READMEs.
- **Automatic target project `.gitignore` scaffold & protection**:
  Updated `deploy-agents.ps1`, `deploy-agents.sh`, `run-pipeline.ps1`, and `run-pipeline.sh`
  to automatically create or idempotently append Agent Harness ignore rules (`.claude/skills/`,
  `.comet/*`, `!.comet/config.yaml`, machine-specific IDE hooks in `.codex/hooks.json` /
  `.trae/hooks.json` / etc., `*.bak-*`, `/.ai-memory.toml`, `scratch/`) to downstream projects'
  `.gitignore`. Prevents deployment artifacts, local state, and absolute-path machine configs from being
  accidentally committed to git.
- **Comet Workflow Engine deep integration (Native & Classic dual-mode)**:
  - **Phase 1 (Rules & Skills)**: Enriched `.agents/rules/engineering-spec.md` with Decision Ownership (investigable facts, user choices, implementation choices) and Independent Verifier Protocol. Upgraded `.agents/skills/comet/SKILL.md` into a full-featured dual-mode guide covering Native goal loops, Classic phase state machines, crash recovery, and living documentation bindings.
  - **Phase 2 (Scaffolding)**: Added `templates/comet.config.yaml` standard configuration template (`comet.project.v1`, Native default, Dual-mode enabled, local knowledge corpus integrated with living-doc directories). Updated `deploy-agents` and `run-pipeline` (both Bash and PowerShell) to automatically detect Comet CLI and scaffold `.comet/config.yaml` if missing, preventing missing-config warnings.
  - **Phase 3 (Diagnostic Probes)**: Integrated non-blocking `comet doctor` cross-platform diagnostic reports (checking 37+ platform rules, skills, and hooks health) alongside `comet status` into `run-pipeline.sh` and `run-pipeline.ps1`, with `--brief-probe` / `-BriefProbe` support for concise CI output.
- **Engineering rule alias & IDE hook exclusions**:
  - Added `.agents/rules/engineering.md` symbolic link alias pointing to `engineering-spec.md` for seamless compatibility with third-party prompt shorthands.
  - Added ignore rules for machine-specific agent hook configurations (`.codex/hooks.json`, `.trae/hooks.json`, `.devin/hooks.json`, etc.) in `.gitignore`.
- **`engineering-docs` native skill & Comet workflow deep integration**:
  Introduced the `engineering-docs` skill (v0.1.0) providing 15 bilingual phase-gate templates
  covering 31 R&D document types from project initiation to delivery. Seamlessly connects
  with `/comet` workflow phases (Open -> 04/05/06 requirements specs, Design -> 07/08/09/10
  architecture and interface specs, Build -> 10/11/12 implementation and reports, Verify ->
  13/14 test plans and reports, Archive -> 15 delivery docs) and enforces YAML Frontmatter
  traceability with `living-documentation` (`doc-impact.py`). Synced skill counts (43 native skills)
  across all 5 languages in READMEs, Skills Usage Guides, and Panorama Guides.
- **9 new agent-tool bridges** (both deploy scripts, TUI-selectable):
  Gemini CLI (`GEMINI.md`), Qwen Code (`QWEN.md`), CodeBuddy (`CODEBUDDY.md`),
  Windsurf (`.windsurf/rules/`), Cline (`.clinerules/`), Roo Code (`.roo/rules/`),
  Kiro (`.kiro/steering/`), Continue.dev (`.continue/rules/`), Trae (`.trae/rules/`).
  Rule-directory bridges symlink `../../AGENTS.md` with `@AGENTS.md` pointer fallback.
- **Native-reader notice**: OpenCode, Aider, Qoder and Pi read `AGENTS.md`
  natively (zero config) — listed as auto-supported in the wizard alongside
  Codex, Antigravity and Zed. Total: 19 tools covered (12 bridge + 7 native).
- **Automatic project memory scaffold (`PROJECT_CONTEXT.md` & `SESSION_STATE.md`)**:
  Both pipeline runners (`run-pipeline.sh`, `run-pipeline.ps1`, and shortcuts `pipeline.sh`, `pipeline.ps1`)
  and deploy scripts (`deploy-agents.sh`, `deploy-agents.ps1`) now detect whether `PROJECT_CONTEXT.md`
  and `SESSION_STATE.md` exist in the target project. Missing files are automatically scaffolded
  from production-grade multilingual templates (`templates/PROJECT_CONTEXT.template.*.md` and
  `templates/SESSION_STATE.template.*.md` in EN, ZH, ZH-TW, FR, DE), synthesizing architecture facts,
  tech stack matrices, Ponytail decision ladders, strict verification evidence gates, and session breakpoints.

- **Interactive TUI step-by-step wizards**: Added interactive terminal selection wizards
  (↑↓ arrow navigation, space toggle, enter confirm, with automatic non-TTY numbered fallbacks)
  across `deploy-agents.sh`, `deploy-agents.ps1`, `setup-ai-memory.sh`, `setup-ai-memory.ps1`,
  `tools/sync-skills.py`, and `tools/doc-impact.py`. Supports single-choice language/scope selection,
  multi-choice agent tools configuration (Claude Code, Codex, Antigravity, GitHub Copilot, Cursor, Zed),
  and optional workflow integrations, avoiding parameter omissions while keeping full CLI flag compatibility.
- **Multilingual documentation & AGENTS templates matrix**:
  Expanded all three core guides (`README`, `Multi-Tool Deployment and Configuration Guide`,
  and `Tools Practical Usage and Skills Panorama Guide`) with full Traditional Chinese
  (`.zh-tw.md`), French (`.fr.md`), and German (`.de.md`) counterparts, maintaining
  header navigation and strict structural parity checked by `tests/repo_checks.py`.
  Added native English (`.en`), Traditional Chinese (`.zh-tw`), French (`.fr`),
  and German (`.de`) templates for `Global AGENTS.md`, `Project AGENTS.md`, and
  `Directory AGENTS.md`. `deploy-agents.sh` and `deploy-agents.ps1` provide
  `--lang` / `-l` (PowerShell `-Language`) option defaulting to English (`en`),
  with fallback to existing root default templates.
- `tools/sync-skills.py`: external skill self-update — `--check` reports
  vendored skills differing from upstream, `--apply` updates files and
  refreshes `computedHash` (SHA256). Manual via CLI, automatic via new
  weekly GitHub Action (`.github/workflows/skill-update-check.yml`) that
  opens a `skill-update` issue when updates are available. Deploy `-Update`
  now offers skill sync (opt-in).
- `deploy-agents.sh` / `.ps1` `guide_optional_cli_tools`: added Comet CLI
  detection + install prompt, and version display for detected CLIs
  (codegraph/rtk/ocr/comet).

- **Skills Usage Guide** (new, EN + ZH + ZH-TW + FR + DE): documents all 42 skills by trigger mode
  (Auto / Explicit `/command` / Hybrid), with per-skill "when to use" guidance,
  cross-language header navigation, and structural parity enforcement across 5 languages.
  Covers `/comet` workflow setup, OpenSpec lifecycle, code review gates, and more.
- **Project memory bootstrap docs**: `PROJECT_CONTEXT.md` / `SESSION_STATE.md`
  creation guide with copy-paste templates. Clarifies these are NOT auto-created —
  the `cross-tool-memory` skill reads them, but the user must create initial versions.

- **engineering-docs skill v0.1.0** (new, 43rd native skill): 15 bilingual
  templates covering 31 R&D document types across 6 lifecycle phases
  (initiation → requirements → design → management → testing → delivery).
  Includes 31→15 decision tree, requirement discipline (explicit/derived/
  assumption/unknown), and `rendering-spec.md` (heading sizes, CN/EN fonts,
  paragraph styles) for consistent output across agents. Optional pandoc
  Word-rendering guidance included.

- **Review follow-ups** (from 4-expert audit of 65f0446):
  - `sync-skills.py`: local skill integrity check (`tampered-local` status).
    Previously only github skills were verified; the 5 local skills had no
    tamper detection despite having locked hashes.
  - `comet/SKILL.md`: converged remaining `docs/management/` / `docs/tests/`
    references to the 4-tier model (`docs/guides/` / `docs/reference/`).
  - CI: install PyYAML (enables comet.config.yaml validation); run
    `tests/sync_skills_test.py`.

- **Six-tier document model** (方案A): expand living-documentation from 4 to 6 tiers,
  adding `docs/management/` (project governance) and `docs/tests/` (verification).
  Reassign 8 engineering-docs template types to match semantics (no more stuffing
  initiation docs into specs/ or weekly reports into guides/). Update
  `doc-impact.py`, `repo_checks.py`, and both skill mapping tables; add
  cross-validation check (3f2) preventing comet/engineering-docs path divergence.
- **Review follow-ups round 2**: unit tests for `check_local_skill` (4 new cases);
  Skills Usage Guide adds 4 missing openspec-docs skills; comet PATH trust note;
  template format hints (table vs headings guidance); one-click Word template
  fetch script (`scripts/fetch-word-template.sh`).

- **Strategic hardening**:
  - `lock-history` consistency check (5b): CI fails if a skill's `computedHash`
    changed vs the base ref without the corresponding `SKILL.md` changing —
    prevents silent lock edits. Override base with `LOCK_CHECK_BASE` env.
  - **Skill domains** (namespaces): every skill in `skills-lock.json` now declares
    a `domain` (`openspec` ×17, `superpowers` ×16, `local` ×5, `document` ×2,
    `integration` ×2, `utility` ×3), enforced by CI. Enables scoped loading as
    the catalog grows beyond 43 skills.

- **Polish round**:
  - 3g check warns (not silently skips) when PyYAML is missing locally.
  - Format hints added to all 15 engineering-docs templates (was 6).
  - Worked PRD example: `references/examples/05-product-spec-example.md`
    (team task board, fully filled, linked from decision tree).

- **Provenance enforcement**: new `provenance:*` checks — every skill must have
  `version` or `computedHash` in lock (meta entries exempt).
- **Word template SHA256 pin**: `fetch-word-template.sh` verifies download integrity.
- **i18n sync**: DE/FR/ZH-TW guides gain 4 openspec-docs skills + domain table +
  meta-entry note; EN/ZH gain meta-entry note.

- **Six-tier migration completion** (from external audit):
  - `gen_templates.py`: metadata updated to 6-tier (regeneration no longer
    reverts types/paths); verified generator output matches all 15 templates.
  - `deploy-agents.sh/.ps1`: scaffold now creates all 7 tier dirs
    (added `management`, `tests`); new `deploy-scaffold:*` CI checks enforce parity.
  - Template `depends_on` paths fixed (02/03→management, 12→management,
    14/15→tests); new `depends_on-tier` CI validation.
  - `fetch-word-template.sh` added to exec-bit patrol.

### Removed
- **冗余流水线包装脚本收敛**：移除 `pipeline.sh` 和 `pipeline.ps1` 包装入口，统一保留功能完备、参数全面的标准执行器 `run-pipeline.sh` 与 `run-pipeline.ps1`；同步清理 5 语言 README、多工具部署与全景实战指南中的历史引用。

### Fixed
- **CI 红灯修复（markdownlint + ShellCheck）**：合并 `[Unreleased]` 下重复的 `### Added` / `### Fixed` 章节（MD024）；将各语言 README 与指南的目录链接改为指向译文标题锚点（MD051，共 16 处）；清理连续空行（MD012）与 `README.md` 标题层级跳级（MD001，并为四个译本 README 补齐缺失的前置要求章节以保持 `##` 章节对齐）；`run-pipeline.sh` 的 `-I/--interactive` 标志此前只赋值从未生效，现已接入向导触发条件（强制启动 6 步向导、与执行前确认互斥，`-y` 优先），消除 ShellCheck SC2034 警告。
- **流水线模板路径与作用域修复**：修复 `run-pipeline.sh` / `run-pipeline.ps1` 在模板迁移至 `templates/agents/` 后的全局模板解析告警与 `.ai-memory.toml.example` 查找失败；修复 `run-pipeline.sh` 附加探针中顶层非函数作用域使用 `local` 变量的问题；完善 `deploy-agents.sh` / `deploy-agents.ps1` 模板路径回退兼容；`repo_checks.py` 增加 15 个模板完整性校验与流水线全局模板解析对齐校验。

- **Markdownlint CI blocker (P0)**: Unified heading in all 15 engineering document templates from dual H1s to single bilingual `# {title_cn} / {title_en}` (MD025) and added language identifier to `SKILL.md` decision tree fenced code block (MD040), eliminating 31 markdownlint errors in CI.
- **Traceability path alignment (P1-1)**: Converged recommended document output paths in `engineering-docs/SKILL.md` and `comet/SKILL.md` to the standard 4-tier living-doc hierarchy (`docs/{specs,architecture,reference,guides}/`), ensuring all generated docs are discovered by `doc-impact.py`.
- **Canonical document type enforcement (P1-2)**: Restored strict equality checking for `TIER_TYPES` in `tests/repo_checks.py`, enforcing exact canonical document types (`specs`, `architecture`, `reference`, `guide`, `adr`) across all templates and docs.
- **Skill lock tamper verification (P1-3)**: Enhanced `tools/sync-skills.py` to validate `computedHash` from `skills-lock.json`, distinguishing local unauthorized modifications (`tampered`) from upstream releases (`outdated`), with unit test coverage and refreshed SHA256 hashes across all 43 skills.
- **CI coverage & pipeline parity (P1-4)**: Added static frontmatter schema verification for all 15 document templates in `tests/repo_checks.py`, YAML syntax validation for `templates/comet.config.yaml`, stage parity verification between `run-pipeline.sh` and `run-pipeline.ps1`, and added Comet config verification in CI smoke tests.
- **Comet config & pipeline runner hardening (P2)**: Defaulted `templates/comet.config.yaml` active workflows to native only (classic commented out); permitted `.comet/config.yaml` in `.gitignore` for team version control; safely escaped special characters (`&`, `/`, `\`) in `sed` replacement; condensed `comet doctor` output in `run-pipeline` to highlight issues and summarize passed checks; fixed lingering English guide prompts and duplicate blank lines.
- **Windows PowerShell BOM encoding**: Saved all PowerShell scripts (`run-pipeline.ps1`,
  `pipeline.ps1`, `deploy-agents.ps1`) with UTF-8 BOM (`utf-8-sig`) to prevent
  Windows PowerShell 5.1 from misinterpreting Chinese characters and quotes under
  default ANSI/GBK code page 936.
- `deploy-agents.ps1`: fixed Bashism parameter expansion syntax (`${var:+ ...}`) in CLI version string formatting.
- `deploy-agents.sh`: restored executable file mode (100755).
- `deploy-agents.sh` / `deploy-agents.ps1`: sync `.agents/review-sensitive-paths.json` to deployed projects and track in PARITY table.
- `.claude/hooks/guard.mjs`: fallback `pushedFiles` to compare against default remote branches or HEAD commit when branch has no upstream tracking branch (`@{u}`), suppressing git error stderr leakage.
- `open-code-review/scripts/group-diff.py`: enhanced cross-directory implementation<->test pairing (e.g. `tests/...` <-> `src/...`) and expanded noise patterns for binary/build artifacts.
- Documentation sync: updated skill directory count from 41 to 42 across READMEs and Panorama Guides; added code review row to Section 2.6/2.5 dispatching matrices.
- `open-code-review`: added C/C++ (`cpp.md`) and TypeScript/JavaScript (`typescript.md`) rulebooks under `references/rules/`.

- **TUI input validation**: `prompt_select`/`prompt_multiselect` non-TTY fallbacks
  in `deploy-agents.sh` now reject non-numeric input (previously a stray string
  silently selected the last option via bash arithmetic). Aligned with the
  PowerShell `TryParse` behavior.
- **TUI tool selection honesty**: the wizard's agent-tool multiselect no longer
  lists Codex/Antigravity/Zed as configurable — they read `AGENTS.md` natively.
  The wizard now shows native readers as auto-supported and only asks about
  tools that actually need bridge files.
- **Shared TUI module**: extracted the duplicated `tui_select` from
  `tools/sync-skills.py` and `tools/doc-impact.py` into `tools/tui.py`.

- **Pipeline Stage 4 `--root` fix**: `run-pipeline.sh`/`run-pipeline.ps1` now always
  pass `--root <target>` to `doc-impact.py` (previously dropped in `--interactive`
  mode, causing the wrong repo to be analyzed).
- **Pipeline `--check-only` implemented**: the documented read-only flag now actually
  works — `sync-skills.py` gained `--check-only` (forces check in wizard and CLI),
  pipeline passes it through in both scripts.
- **Pipeline Stage 2 multi-agent**: `setup-ai-memory.sh`/`.ps1` now accept multiple
  agents (previously only `$1` was used, silently ignoring the rest); pipeline
  defaults to `claude-code codex antigravity-ide` in unattended mode.
- **`tui_multiselect` non-TTY fallback**: invalid tokens are now skipped individually
  instead of nuking the entire selection.

### Changed
- **法语 Guide 翻译**：`Multi-Tool Deployment and Configuration Guide.fr.md` 与
  `Tools Practical Usage and Skills Panorama Guide.fr.md` 全文翻译为法语（此前为英文原文）。
- **Hook 安全加固**：修复 3 个 P0 旁路——git 缩写选项（`--forc`）、环境变量前缀
 （`FOO=bar git push`）、内联 alias（`git -c alias.p=push`）；加 4 个回归测试（42/42）。
- **skills-lock 真版本锁定**：37 个外部 skill 新增 `pinnedCommit` 字段（commit SHA），
  `sync-skills.py` 优先从 pin 的 commit 拉取，不再静默跟随上游 tip；lock 版本升至 v2。
- **de/fr README 补全**：ai-memory 4 步详细配置完整翻译（此前压缩为 19 行代码块）。
- **Hook 安全回归修复**（P0）：`--force-with-lease=<ref>` 带等号值形式绕过 force 检测，
  改为 `startsWith` 匹配；加回归测试（38/38）。
- **Hook 性能优化**：`getCurrentBranch()` 单次调用内缓存；`getRepoRoot()` 优先
  `__dirname` 推导（各省 ~11ms）；无 ReDoS 风险。
- **模板目录整理**：15 个 AGENTS 模板（Global/Project/Directory × 5 语言）
  移入 `templates/agents/`；deploy 双脚本路径同步；根目录 38→23 文件。
- **可访问性提升**：Hook 报错双语化（EN+ZH）；新增 `docs/glossary.md` 术语表；
  README 5 语言加 30 秒上手 TL;DR + mermaid 架构图。
- **专家遗留项收尾**：Guide 5 语言加触发语过宽警告（ponytail/using-superpowers，
  外部 skill 不直接改以保同步）；repo_checks.py 新增 markdown 内链检查
  （修复 Guide 移动导致的 131 个断链）；CI 移除已合并分支触发。
- **仓库结构整理**：15 个 Guide 移入 `docs/guides/`（根目录 53→38 文件）；
  `README_zh.md` 重命名为 `README.zh.md`（统一命名规范）；中文 Guide 标注"扩展版"。
- **项目级评审优化**：Panorama Guide 5 语言 skill 计数 43→44；Hook 测试 25→37
  （非首命令段、删除变体、警告分支、误伤测试）；Global AGENTS 5 语言 Git 章节
  压缩为指针（消除与 git-workflow.md 的三层重复）。
- **Hook 安全加固**（红队评审）：命令归一化预处理（防引号/转义/`-c`插队绕过）；
  补 force 语义（`+refspec`、`-vf` 捆绑）；`update-ref` 覆盖受保护 ref；
  分支检查跟随 `-C`/`--git-dir`；测试 17→25。
- **一致性修复**：11 处补 `staging`（rule/README/Panorama/部署指南）；
  `Skills Usage Guide.zh.md` 补域汇总表。
- **新人上手**：头部加读者身份说明、人类 PR 快速通道、`<protected>`/`<DEFAULT_BRANCH>` 定义。
- **git-workflow.md 三专家评审优化**：新增 Hook 覆盖声明（"Hook 硬拦截"仅 Claude Code 生效，
  修正 exit code 表述）；§8 新增"提交/回退"意图消歧表与决策树；精益删除冗余 20+ 行
  （钢铁纪律浓缩、删除重复 Gotchas）。
- **git-workflow.md 架构重组**（三专家评审）：12 节→8 节（268→176 行），安全约束集中前三节
  （授权矩阵→钢铁纪律→Never List）；§7/§8/§11 的手册内容并入 `git-advanced` skill；
  `git-forensics` 更名为 `git-advanced`（覆盖冲突/cherry-pick/bisect/速查）。
- **git-workflow.md 瘦身优化**：§9 Bisect/Reflog 拆分为按需加载的 `git-forensics` 本地 skill
  （规则文件 283→~240 行，降低每次会话 token 成本）；§8 新增 revert/reset 一句话决策线；
  修复 3 处内部一致性问题（revert 语义、rebase 上下文、reset --hard 确认提醒）。
- **Project renamed `agents-living` → `agent-harness`**: 27 references updated
  across 13 files (READMEs, guides, AGENTS.md, CONTRIBUTING.md, skills-lock.json
  source fields, tool docstrings/User-Agents, CI config). Dated historical
  notes in `docs/internal/` intentionally unchanged. GitHub repo rename
  (`xusofty-cyber/agent-harness`) to be done via Settings; old URLs redirect
  automatically.
- **Eliminated redundant skill directory backups on update**: Removed per-skill directory `.bak.<timestamp>` creation in `deploy-agents.sh` and `deploy-agents.ps1`. Managed skills in `.agents/skills/` are now overwritten cleanly upon update (matching `.claude/skills/`), preventing dozens of stale `.bak.*` directories from polluting project trees and causing duplicate skill indexing in AI agent harnesses.
- **Physical copy for Claude Code skills deployment**: Changed `deploy-agents.ps1` and `deploy-agents.sh` to deploy skills into `.claude/skills/` via physical directory copies (with automatic cleanup of legacy NTFS junctions / symlinks). Eliminates path traversal and junction crossing errors (`crosses a symbolic link or junction`) during `comet init` and `run-pipeline` runs regardless of execution order.
- **Native YAML Frontmatter in 15 `engineering-docs` templates**: Upgraded headers of all 15 Markdown template files in `.agents/skills/engineering-docs/references/templates/` (and generator `gen_templates.py`) to native YAML Frontmatter blocks with schema metadata (`id`, `title`, `type`, `status`, `modules`, `depends_on`, `version`, `last_verified_commit`). Ensures any AI agent copying templates defaults to complete traceability metadata for downstream `living-documentation` and `doc-impact.py` analysis.

## [0.2.1] - 2026-10-09

### Added
- Claude Code hook: sensitive-path commit/push advisory (open-code-review
  Phase 2). `.claude/hooks/guard.mjs` now warns (non-blocking, exit 0) when
  `git commit`/`git push` touches files matching
  `.agents/review-sensitive-paths.json` patterns (built-in defaults cover
  `auth/`/`crypto/`/`security/`/`payment/`/credentials/etc.), suggesting the
  `open-code-review` skill before proceeding. Deterministic only — zero LLM
  calls inside the hook.
- New `open-code-review` skill (`version: 0.1.0`): deterministic code review
  methodology adapted from alibaba/open-code-review (Apache-2.0, see
  `ATTRIBUTION.md`). Three tiers: Tier A `ocr` CLI delegation (zero LLM cost),
  Tier B built-in methodology when the CLI is absent, Tier C direct mode.
  Ships rule-first review rules (`security`/`python`/`shell`), a `group-diff.py`
  bundling helper, and Comet Verify wiring. `requesting-code-review` now
  delegates the "how" to this skill.
- `deploy-agents.sh` / `.ps1`: optional Open Code Review CLI (`ocr`) detection
  in `guide_optional_cli_tools` / `Guide-OptionalCliTools` (no forced install).

## [0.2.0] - 2026-10-09

### Added
- `living-documentation` skill (`version: 0.2.0`): new §7 documents the bundled
  `scripts/doc-impact.py` (previously undiscoverable from the skill body).
- `tests/repo_checks.py`: `doc-impact:sync` check — `tools/doc-impact.py` and
  the skill-bundled `scripts/doc-impact.py` must stay byte-identical.
- `tools/doc-impact.py`: living-documentation impact analysis — matches changed
  files against doc `modules` globs, walks `depends_on` upward, and reports
  staleness via `last_verified_commit` (🔴 must-update / 🟡 review / 🟢 in-sync);
  advisory only, wired into comet Verify/Archive gates.
- `tests/repo_checks.py`: `doc-frontmatter` check — `docs/{specs,architecture,
  reference,guides,adr}/` markdown files must declare valid traceability
  frontmatter (`id`/`type`/`status`/`modules`), with `type` matching its tier.
- New local skill `living-documentation` (`version: 0.1.1`): 4-tier living documentation suite (`docs/{specs,architecture,reference,guides}`) with YAML frontmatter-based code-doc bidirectional traceability (`modules`, `depends_on`), L0/L1/L2 change impact thresholds, and deep integration with Comet change lifecycle (Open/Build/Verify/Archive) and OpenSpec workflows.
- Four production-grade templates under `.agents/skills/living-documentation/templates/`: `srs.template.md`, `architecture.template.md`, `reference.template.md`, and `guide.template.md`.
- Two reference guides under `.agents/skills/living-documentation/references/`: `comet-integration.md` and `traceability-matrix.md`.
- `deploy-agents.sh` and `deploy-agents.ps1`: initialized living documentation scaffold (`docs/{specs,architecture,reference,guides,adr}`) on deployment; added `LivingDocScaffold` parity check in `tests/repo_checks.py`.
- Updated `Project AGENTS.md` and `.agents/rules/engineering-spec.md` with living documentation and code-doc traceability gates.
- `deploy-agents.sh` and `deploy-agents.ps1`: added `-m` / `--ai-memory-init` (`-AiMemoryInit`) flag to optionally initialize `.ai-memory.toml` for target projects (inferring `workspace` and `project`), and sync `.ai-memory.toml.example` as reference.
- New local skill `option-review` (`version: 0.1.1`): pre-decision review of
  multiple candidate approaches. Fans out isolated reviewers across five
  dimensions (security, engineering, reversibility, simplicity, cross-tool)
  and returns a decision matrix; includes single-agent CoT fallback when subagents
  are unavailable, and impact thresholding to avoid over-triggering on minor code choices;
  complements `requesting-code-review` (which reviews completed work).
- `VERSION` file (single source of truth for the release version);
  `tests/repo_checks.py` checks it matches the newest `CHANGELOG.md` version.
- `tests/repo_checks.py`: `skill-version` check — in-repo-authored skills must
  declare semver `version:` in `SKILL.md` frontmatter, matching `skills-lock.json`.
- `cross-tool-memory` skill: `version: 0.1.0` (first versioned skill).

### Changed
- Synced 41 native skills count and in-repo skills descriptions across
  `README.md`, `README_zh.md`, root `AGENTS.md`, and the bilingual
  `Tools Practical Usage and Skills Panorama Guide` pairs.

### Fixed
- `deploy-agents.sh`: restored `100755` executable bit in git index.
- `tools/doc-impact.py`: fixed unverified documents (`last_verified_commit: ""`) falsely reporting as `in-sync`; added directory glob matching support and auto-detection of workspace git root.
- `living-documentation`: distributed `scripts/doc-impact.py` directly inside skill package so it is bundled to all downstream projects.
- `setup-ai-memory.sh` / `.ps1`: pass `--no-skills` to
  `ai-memory install-instructions` — this repo curates `cross-tool-memory`
  as its only memory skill; upstream managed skills must not be dropped
  into `.agents/skills/` (they would break the `skills-lock.json`
  consistency check and leak into downstream deploys).
- `tests/repo_checks.py`: new `exec-bit` guard asserting `deploy-agents.sh`
  and `setup-ai-memory.sh` are `100755` in the git index — the GitHub
  contents API resets the exec bit to `100644` on every content push, so
  restore locally with `git update-index --chmod=+x` after API-driven PRs.
- `docs/internal/SESSION_STATE.md`: updated from the stale
  pre-merge state to the `v0.1.0` closed state.

## [0.1.0] - 2026-10-08

First tagged release.

### Added
- GitHub Actions CI (`.github/workflows/ci.yml`): markdownlint, shellcheck,
  `node --check`, hook behavior tests, repo static checks, and a
  `deploy-agents.sh` smoke test on ubuntu; PSScriptAnalyzer (Error gate) on Windows.
- `tests/hooks.test.mjs`: 12 black-box tests driving `.claude/hooks/guard.mjs`
  through the Claude Code PreToolUse stdin JSON protocol.
- `tests/repo_checks.py`: JSON/TOML validity, `SKILL.md` frontmatter
  (`name`/`description`), `deploy-agents.ps1`/`.sh` feature-parity markers,
  and `skills-lock.json` ↔ skill directory consistency.
- `tests/repo_checks.py`: bilingual `##` section-count parity check for the
  EN/ZH guide pairs.
- `setup-ai-memory.sh` / `setup-ai-memory.ps1`: pin the validated ai-memory
  version (currently `2.6.0`); refuse to configure on mismatch unless
  `AI_MEMORY_ALLOW_OTHER_VERSION=1` is set.
- `CONTRIBUTING.md`: bilingual doc sync policy, template-genericity rule,
  dual-script parity rule.
- `docs/internal/`: home for this repository's own dev notes
  (`PROJECT_CONTEXT.md`, `SESSION_STATE.md`, `SESSION_RESUME.md`), moved out of
  the distribution root.
- Root `AGENTS.md`: dogfood entry point describing this repository for tools
  that auto-load it.
- `skills-lock.json`: added missing `cross-tool-memory` entry.

### Changed
- Chinese guide filenames are now ASCII with a `.zh.md` suffix
  (`Multi-Tool Deployment and Configuration Guide.zh.md`,
  `Tools Practical Usage and Skills Panorama Guide.zh.md`); all cross-references updated.
- Removed the two `docs/BRANCH_COMPARISON*` documents: the branches are merged,
  and their content is summarized in this changelog.
- Merged `long-term-memory-governance`: cross-tool memory governance
  (`cross-tool-memory` skill, optional local ai-memory backend),
  safe global-rule sync (preserve by default, timestamped backup on `-Update`),
  Codex global support, Antigravity 2.0/CLI/IDE dual entry, and Honest Limits.
- `.claude/hooks/guard.mjs`: fixed `git add .` never matching
  (`(-A|\.)\b` has no word boundary after `.`); `rm` guard now covers `-R`
  and `-r` at end-of-command, without flagging files like `rm -report`.
- `.agents/rules/git-workflow.md`: trunk branch is now a `<DEFAULT_BRANCH>`
  placeholder instead of hardcoded `develop`.
- README skill count corrected to the actual number of skill directories.

### Fixed
- 4 broken table-of-contents anchors, 10 fenced code blocks missing language
  tags, duplicate headings, and list-style inconsistencies found by markdownlint.
- 2 shellcheck warnings in `deploy-agents.sh` (SC2034 unused `line`, SC2155
  `local` masking return value).
