# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Releases are tagged `vX.Y.Z` from `main` by the maintainer.

## [Unreleased]
### Added
- **dsh gate plugin (PR #75)**: DeepSeek Harness (dsh) gains a Cordis gate plugin — TypeScript source `.dsh/agent-harness-gate.ts` (minimal `.dsh/tsconfig.json` + `.dsh/node-shims.d.ts` for an isolated `tsc --noEmit` check, since the repo has no package.json/@types/node) with the deployed runtime `.dsh/agent-harness-gate.mjs` generated from it by Node.js type stripping (regeneration command in the source header; do not hand-edit the .mjs). The plugin translates dsh tool calls into the existing Claude gate hooks (never a second copy of the rules): `tools/pre-execute` → Bash guard / write warnings + feature-list write block, also registered as the monotonic `ctx.tools.guard()` final denial when available; `agent/created` → gate resume via `agent.inject()`; `tools/result` → cost-ledger observation only; `agent/turn-stopping` → stop gate with its own second-attempt state in `gate/dsh-stop-state.json` and steering via `steer`/`followup`/`inject`. Every error path fails open with a stderr note. Deploy scripts stay in sync (PARITY extended; sh + ps1 both copy the plugin, the six Claude hook scripts into `.dsh/hooks/`, and generate `.dsh/cordis.patch.yml` from the template with the deployed plugin's absolute path; activation is manual — merge the row into a profile or home patch, or pass it with `--patch`); guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy. Tests: `tests/dsh-gate.test.mjs` 19/19 pass (protocol-level, mock Cordis context, real Claude hooks), the TypeScript source passes a direct Node 24 type-stripping import check, and a deploy smoke test confirms the deployed files. CI wiring (node check + hook test + deploy smoke assertions in `.github/workflows/ci.yml`) is prepared on local branch `dsh-gate-plugin-with-ci` but held back from this PR because the push token lacks workflow scope (GitHub refuses workflow-file pushes without it); re-apply after a workflow-scope re-auth. Honest limits, also stated in the guides, README, plugin header, and patch template: dsh 插件 API 未在官方文档/真机上核实 — no external documentation was fetched in this round (night-batch no-approval-card discipline), dsh was not installed in the build environment, and the local repository contains no Cordis plugin API specification, so every dsh event name, payload shape, and steering surface in this plugin is an unverified contract carried over from earlier work's documentation reading; a live dsh run plus an official-documentation re-check is still owed before any part of dsh enforcement counts as a hard gate, and dsh stop enforcement is provisional. Likewise, `tsc --noEmit` was NOT run here (no typescript binary installed in the sandbox and no network fetch under the same discipline), so a tsc pass remains an owed check even though the .ts source runs clean under Node 24 type stripping. ps1 was not executed (no PowerShell in the sandbox); its BOM+CRLF encoding is preserved.
- **WorkBuddy gate hooks (PR #73)**: project deploys `.workbuddy/settings.json` (PreToolUse/Stop/SessionStart/PostToolUse) plus adapters in `.workbuddy/hooks/` (`workbuddy-pre-tool-use.mjs`, `workbuddy-stop.mjs`, `workbuddy-session-start.mjs`, `workbuddy-post-tool-use.mjs`, shared `workbuddy-common.mjs`) and copies of the six Claude gate scripts they delegate to, so WorkBuddy-only projects gate without `.claude/hooks/`; adapters fall back to `.claude/hooks/` when the copy is absent. Unlike the Antigravity adapters, no payload translation is needed — WorkBuddy/CodeBuddy hooks are ASSUMED to receive the same Claude-shaped stdin (`tool_name`, `tool_input`, `cwd`, `session_id`) — the hook format was NOT verified against official WorkBuddy/CodeBuddy documentation in this run (external docs not fetched during the night window) nor on an installed WorkBuddy build, so the mapping below is provisional until a live run confirms it; the mapping is identity (Bash → Bash guard, Write|Edit|NotebookEdit → write warnings + feature-list write block, Stop → stop gate, SessionStart → gate resume, PostToolUse → cost-ledger line); only outputs whose assumed form differs are translated (SessionStart plain text → `hookSpecificOutput.additionalContext`, Stop exit 2 → `{"continue": false, "reason": ...}`, the assumed current form with `"decision": "block"` assumed deprecated). PreToolUse allow is exit 0 with no stdout (never an explicit `"allow"`, which would skip the host permission prompt); every error path fails open with a stderr note; the Stop adapter keeps its own second-attempt state in `gate/workbuddy-stop-state.json` (the assumed Stop payload carries no `stop_hook_active` equivalent; if the host passes it, `stop-gate.mjs` handles the second attempt) and the `GATE_ALLOW_STOP` override channel is unchanged. Deploy scripts stay in sync (PARITY extended, skip-if-exists + backup-on-update, self-repo guard in ps1) and the deploy completion line now states Claude Code + Antigravity + WorkBuddy hooks enforce the gate; `tests/repo_checks.py` gains a WorkBuddy wiring section (§1c) and deploy smoke (sh) covers the deployed WorkBuddy files; the CI smoke assertion is held pending a gh re-auth with workflow scope (see PR #73 body). Honest limits, also stated in the guides and README: protocol-level tests pass (`tests/workbuddy-hooks.test.mjs`, 16 tests) and a deploy smoke test gates a temp project, but no live WorkBuddy run was possible in the build environment (no WorkBuddy binary installed), so a live run on an installed WorkBuddy version is still owed; and the settings-file location is unresolved until that run — the legacy CodeBuddy path cited by a prior draft is `.codebuddy/settings.json` (also unverified here), while this layer deploys `.workbuddy/settings.json` (matching the existing `.workbuddy/rules/` bridge), with a copy-to-legacy-path fallback documented in the guides. Guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy. Note: this layer follows the PR #66 Antigravity pattern (reuse, do not copy, the guard logic) and the adapter test file is not yet run by CI, same as the Antigravity adapter test file.
- **Antigravity hooks.json path fix (PR #76)**: the deployed `.agents/hooks.json` template previously wrote all four hook commands as `node .agents/hooks/antigravity-*.mjs`, assuming hooks run from the workspace root. A live agy CLI 1.4.10 `--print` run proved otherwise: agy runs hook commands with cwd = `<project>/.agents`, so the old form doubled to `.agents/.agents/hooks/...` and agy rejected the covered tool call with a hook-load error instead of failing open (all hook-covered tools blocked, not merely unblocked). All four commands are now `node hooks/antigravity-*.mjs`; `.agents/hooks/antigravity-common.mjs` corrects the same wrong workspace-root assumption in its comment and in `resolveProjectRoot` (a `.agents` cwd now resolves to its parent when `workspacePaths` is absent; a workspace-root cwd is unchanged). Regression cover: `tests/antigravity-hooks.test.mjs` gains 2 tests (hooks.json commands resolve from `.agents` cwd; adapter with cwd=`.agents` and no `workspacePaths` still denies a force push) for 17 total, and `tests/repo_checks.py` §1b now asserts exactly 4 commands, rejects any `.agents/hooks/` prefix, and resolves each adapter from `.agents/`; PARITY gains an `Antigravity hooks cwd=.agents` marker carried identically in both deploy scripts (ps1 BOM+CRLF preserved). Deploy scripts themselves still copy the template verbatim (skip-if-exists, backup-on-update), so already-deployed projects need an update-mode redeploy or a manual four-command edit — the template fix alone does not repair them. Guides EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy. Honest limits: this form is correct for the observed CLI 1.4.10 cwd only; Antigravity IDE cwd is still NOT live-verified, and no agy live retest was run in this change (live retest needs separate user confirmation after the previous live run triggered a user confirmation refusal); ps1 was not executed (no PowerShell here), only its encoding/marker verified; the update-mode redeploy overwrite branch is code-read, not executed end-to-end (an attempted `--update` smoke run entered the deploy script's online upstream-skills sync step and was not completed).- **Template gate wired into the deploy scripts (branch `benchmark-prepush-gate`, local only, no push, no PR)**: `deploy-agents.sh` gains `--prepush-gate` and `deploy-agents.ps1` gains `-PrepushGate`, initially off by default, then flipped to on by default per user decision 2026-10-29 (opt-out via `--no-prepush-gate` / `-NoPrepushGate`; `--prepush-gate` / `-PrepushGate` retained for compatibility, an explicit opt-out wins if both are passed). When enabled, the deploy installs the three template-gate files into the target project — `.git/hooks/pre-push` (only inside a git work tree; a non-git target skips just the hook with a note), `scripts/gate-prepush-check.py`, and `.github/workflows/gate-check.yml` (directories created as needed) — each with the usual skip-if-exists / backup-on-update rules (ps1 also follows the existing isSelfRepo guard; the installer script's own refuse-to-overwrite / `--force`-backup semantics are mirrored by skip / backup on the deploy path). Checker and hook behaviour are unchanged: the pre-push hook blocks on passing-item re-verification failure and treats check-clean as a warning by default (blocking only with `GATE_PREPUSH_STRICT=1`), the CI template blocks on both, and the honest limits stand (`git push --no-verify` bypasses the hook; it checks the working tree, not the pushed commits; it is a local tripwire, not server-side enforcement). `tests/repo_checks.py` PARITY extended with a matching marker; guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy. Still open, for the user to decide later: whether pre-push check-clean should block by default (it stays warning-only by default per user decision 2026-10-29, blocking only with `GATE_PREPUSH_STRICT=1`).
- **B2 discriminating bench + host-independent pre-push / CI template gate (branch `benchmark-prepush-gate`, local only, no push, no PR)**: (a) B2 pre-registration (`eval/results/b2-preregistration-2026-10-29.md`, registered before any B2 run) for t9–t12 × bare/pack/gate × 3 rounds = 36 runs, reusing B1's decision rules (DISCRIMINATION only if gate beats bare by ≥2 false completions pooled; all-zero arms again mean NO DISCRIMINATION). New tasks in `eval/tasks/`: t9-multi-file (remainder across calc/cli/README/tests, with a CLI error-propagation check), t10-hidden-boundary (power with zero/negative exponents absent from the visible tests; the agent must write its own boundary tests), t11-resume (two-phase checkpoint/interruption/resume from state files only, with phase-2 rounds and redone_phase1 recorded), t12-ambiguous-decision (discount pct scale ambiguous; a DECISIONS.md entry must precede implementation; decision quality is coordinator-scored descriptively, 0–2). `eval/run-bench.sh` acceptance and task mapping extended for t9–t12; `tests/repo_checks.py` §3q updated (8 task specs, not 4) plus new §3q2 checks (B2 preregistration, no B2 runs yet, run-bench coverage, template files). All four reference solutions verified via setup + solution + acceptance. No B2 runs have been executed — the tasks are ready, no arm has been measured. (b) Template gate in `templates/pre-push-gate/` (pre-push hook, stdlib `gate-prepush-check.py`, opt-in installer that refuses to overwrite an existing hook without `--force` and backs it up with `--force`) plus `templates/ci-gate-check.yml` (project workflow template, distinct from the repo's own ci.yml). The checker re-runs every passing item's verification and rejects stale evidence, mirroring §3k (human overrides skipped); the pre-push hook blocks on that check and treats check-clean as a warning by default (blocking only with GATE_PREPUSH_STRICT=1), while the CI template blocks on both, because CI checks committed state. Tests: `tests/prepush_gate_test.py` 8/8 pass, including a real git push to a local bare remote that passes with a clean gate and is blocked (remote never receives the commit) with a broken gate. Honest limits, also stated in the guides and README: the pre-push hook checks the working tree, not the pushed commits, and `git push --no-verify` bypasses it — it is a local tripwire, not server-side enforcement; the templates are NOT wired into deploy-agents.sh/.ps1 by default (whether to add a deploy option is an open decision, so no PARITY entry was needed — no deploy script changed). Guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy.
- **Antigravity gate hooks (branch `antigravity-cli-hooks`, not pushed, no PR)**: project deploys `.agents/hooks.json` (hook set `agent-harness-gate`: PreToolUse/Stop/SessionStart/PostToolUse) plus adapters in `.agents/hooks/` (`antigravity-pre-tool-use.mjs`, `antigravity-stop.mjs`, `antigravity-session-start.mjs`, `antigravity-post-tool-use.mjs`, shared `antigravity-common.mjs`) and copies of the six Claude gate scripts they delegate to, so Antigravity-only projects gate without `.claude/hooks/`; adapters fall back to `.claude/hooks/` when the copy is absent. Mapping follows the official Antigravity hooks reference: `run_command`/`CommandLine` → Bash guard, write tools/`TargetFile` → write warnings + feature-list write block, `Stop` → stop gate, `SessionStart` → gate resume as a system message, `PostToolUse` → cost-ledger line. Gate rules are not duplicated — each adapter translates the Antigravity payload into the Claude payload, runs the existing Claude hook, and translates the decision back. PreToolUse decisions are always explicit (`allow`/`deny`, never `{}`); every error path fails open with a stderr note, matching Antigravity's own fail-open behavior; the Stop adapter keeps its own second-attempt state in `gate/antigravity-stop-state.json` (Antigravity's Stop payload has no `stop_hook_active` equivalent) and the `GATE_ALLOW_STOP` override channel is unchanged. Deploy scripts stay in sync (PARITY extended, skip-if-exists + backup-on-update like Claude hooks, self-repo guard in ps1) and the deploy completion line now states Claude Code + Antigravity hooks enforce the gate. Honest limits, also stated in the guides and README: protocol-level tests pass (`tests/antigravity-hooks.test.mjs`, 15 tests) and a deploy smoke test gates a temp project, but no live Antigravity CLI/IDE run was possible in the build environment (no `agy` binary), so a live run on an installed Antigravity version is still owed; the official hooks reference lists workspace `.agents/hooks.json` for App/CLI/IDE alike, which is the basis for one workspace file, not a live IDE verification. Guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy.
- **Multi-tool bridge layer: Antigravity hardening + WorkBuddy + DeepSeek Harness (dsh)** (branch `bridge-antigravity-workbuddy-dsh`, not merged, no PR): deploy-agents.sh/.ps1 stay in sync (PARITY extended) — Antigravity project deploys `.agents/rules/agent-harness.md` with YAML frontmatter (`trigger: always_on`) pointing at `AGENTS.md`, because Antigravity requires a trigger in `.agents/rules/*.md` and the canonical rules stay in `AGENTS.md` + `.agents/rules/*.md`; WorkBuddy gains a wizard option and a project rule bridge at `.workbuddy/rules/agent-harness.md` (symlink to `AGENTS.md`, pointer fallback, skip-if-exists, CodeBuddy bridge unchanged); DeepSeek Harness (dsh) is added to the native `AGENTS.md` list and `--global` now also writes `${DSH_HOME:-~/.dsh}/AGENTS.md` under the same preserve/backup rules. Honest limits, also stated in the guides and README: no hooks are installed for WorkBuddy or dsh in this layer, dsh MCP via `cordis.patch.yml` and gate enforcement are out of scope, WorkBuddy rules loading is not verified on every installed version, and Antigravity global skills are documented (IDE `~/.gemini/config/skills/`, CLI `~/.gemini/antigravity-cli/skills/`) but not copied globally to avoid duplication/drift. Guides EN/ZH and README EN/ZH updated in the same change; ZH-TW left untouched per the frozen-translation policy.

### Removed

- **writing-skills skill deleted (owner direct decision 2026-10-29, D65; branch `remove-writing-skills`, not merged)**: the `.agents/skills/writing-skills/` directory (107,640 bytes), its `full`-profile entry in `skills-profiles.json`, its `skills-lock.json` entry, its `THIRD-PARTY-LICENSES.md` row, and its catalog rows in the Skills Usage Guide (EN/ZH) and Panorama Guide (EN/ZH) are removed in one change. Counts move from 40 skill directories / 42 lock entries / full 38 by default (40 with `--include-heavy-skills`) to 39 / 41 / full 37 by default (39 with heavy); `tools/count-skills.py` EXPECTED values, `tests/repo_checks.py` §3i/§3r, `deploy-agents.sh` help, README EN/ZH, AGENTS.md, and `docs/internal/skill-tiers.md` (full skills-only bytes 1,960,329 → 1,852,689) are synced to the new counts. `minimal` (15) and `standard` (20) never contained the skill and are unchanged. Honest basis, stated exactly: the deletion rests on the owner's direct decision of 2026-10-29 21:59, which satisfies D64 re-review condition (c) (owner scope decision); it is NOT claimed as proven by bench evidence — the 2026-10 ablation (12/12 pass, 0 false completions) is bench-only and no bench task ever exercised this skill's own function (skill creation/editing/verification), per D20 no-regression is necessary but not sufficient. D64's KEEP verdict is superseded by D65, not rewritten; the 2026-10 ablation report is retained as a historical record with a supersession note. ZH-TW files are untouched per the frozen-translation policy, so their `writing-skills` rows and 40-skill counts are stale until the ZH-TW regeneration branch lands (merge order set by the coordinator). The 2026-11 monthly ablation moves on to another component.

### Changed

- Docs and deploy scripts synced to the v0.3.0 reality (no behaviour change to the gate itself): README EN/ZH positioning now describes the gated harness instead of a distribution pack with a minimal gate scaffold; the directory tree lists the full Claude Code hook set, `gate/`, `tools/loop.py` and `eval/`; template languages are en/zh/zh-tw only (FR/DE were removed in v0.3.0); the `full` profile is documented as 38 skills by default, 40 only with `--include-heavy-skills`; the unverified "15-skill superpowers suite" count is removed. A new "Current status (v0.3.0)" section states host-dependent enforcement, the B1 NO DISCRIMINATION result, the advisory-only evaluator (D28), stale/frozen ZH-TW, and Windows review-only verification. The Multi-Tool Deployment Guide EN/ZH now lists all six Claude Code hooks and the manual gate commands for non-Claude hosts. ZH-TW README receives only the two clearly wrong items (superpowers count, FR/DE language examples); its full regeneration from EN remains owed per `docs/internal/i18n-status.md`.
- Deploy help and completion summaries synced to the same reality in both scripts (parity preserved): `--profile full` is documented as 38 skills by default, 40 only with the heavy-skills flag, and the completion summary now states the deployed profile, that minimal ships the gate only (no graph/loop), and that gate enforcement is Claude Code hooks only on other hosts (manual `pass-gate.py verify` / `check-clean` plus CI re-run).

## [0.3.0] - 2026-10-29
### Added
- **A4 rtk 重钉尖端（2026-10-29，用户逐项过批准第 7 项，分支 `feat/merge-v3`，未合 main）**：rtk lock pin 由 `e05c7bdf…` 重钉到上游尖端 `7e92da00…`（`pinnedCommit` + `installerUrl` + `pinnedAt` 更新；`installerSha256` 不变——新旧两提交的安装脚本字节相同，下载实测 SHA256 一致）。24 个提交差量：tracking/savings bug 修复、依赖 bumps、discover 词法器内部重构、CI 文件，无安装脚本与接口改动。同步改动：deploy-agents.sh 的 rtk URL、Panorama 指南 EN/ZH 的 rtk URL；DECISIONS.md 新增 D63。**如实说明**：重钉不等于二进制 pin——rtk 安装器安装时解析 latest release（仅 `RTK_VERSION` 可覆盖），pin 定的是安装脚本版本而非二进制版本，旧 pin 同样如此；ps1 winget 通道无 pin 的 D13 缺口不受本次影响。
- **D31 调整（2026-10-29，用户逐项过批准第 3 项，分支 `feat/merge-v3`，未合 main）**：默认档位仍为 minimal，但 minimal 由 10 个技能改为 15 个，补 5 个 openspec 核心技能（propose、new-change、apply-change、verify-change、archive-change）；其余 7 个 openspec 技能仍只在 full 档（standard 按 D30 另有 continue + update）；云开的 full 默认仍不采纳；minimal 仍只发门禁本身（不含 graph/loop，D58 不变）。理由：默认部署零 openspec 等于把规格驱动流程排除在默认体验之外。同步改动：`skills-profiles.json`、repo_checks §3r 的 minimal 上限 10→15（上限跟随决策）、EN/ZH 指南 minimal 小节、双部署脚本帮助与注释、README EN/ZH、发布草稿与 skill-tiers 表（含重测字节数：skills-only 280,960，部署总计 789,323）与 QUALITY_SCORE；DECISIONS.md D31 改为终裁并注明修订 D18 计数。
- **D30 调整（2026-10-29，用户逐项过批准第 2 项，分支 `feat/merge-v3`，未合 main）**：standard 档位由 18 个技能改为 20 个，补 `openspec-continue-change` 与 `openspec-update-change`（其余 5 个 openspec 技能仍只在 full 档；云逸的 22 全家口径仍不采纳）。理由：18 个只覆盖 openspec 直线流程（提议→新建→应用→验证→归档），多步骤工作续做与中途修订规划无正式路径且缺失静默。同步改动：`skills-profiles.json`（单一事实源）、EN/ZH 指南档位小节（CI §3r 断言）、deploy-agents.sh 帮助文案、README EN/ZH、发布草稿与 skill-tiers 表（含重测字节数）；DECISIONS.md D30 改为终裁并注明修订 D18 计数。
- **独立专家评审团 P0+P1 修复（2026-10-29，分支 `feat/merge-v3`，未合 main、未开合入 main 的 PR、未打 tag、VERSION 仍 0.2.1）**：P0-1 事件日志容错（最大 seq 追加、坏行明确失败不丢变更、comet_adapter 写完整 gate 格式事件）；P0-2+P1-6 graph fan-in 验 git 返回码、冲突记 blocked 绝不报 merged/done、--result 拒绝 main/base/当前/已存在分支（除非 --force）；P1-1 terminate system 须凭与当前验证命令一致的 exit 0 证据、static/runtime 成功各记事件；P1-2 Guard 绕过收口（sudo/env/timeout/nice 选项跳过、-c alias 直接 deny、xargs/find -exec 展开、同命令变量追踪、嵌套解析器递归展开，另修 rawSegments `$(` 深度双计）；P1-3 run-bench.sh setup 开新轮次前调 cost.py check、exit 2 拒绝启动（文档明示账本防君子不防篡改）；P1-4 cost.py 容忍 budget_stop 行与坏行（.get 求和、stderr 告警、stop 行补零值字段）；P1-5 validate 类型守卫、timeout 1..3600、evidence 必备字段、additionalProperties 全级执行、删除未被引用的 ALLOWED 表，另补 schema 缺失的 output_sha256（verify/terminate 本就写它）；P1-8 donor 表 D47/D48/D54 改指 D59/D60/D62；P1-9 D25 加 D58 档位限定；P1-10 D15 加 D28 取代注脚；P1-11 发布草稿写准 D57 硬停 ON 口径；P1-12 repo_checks 新增 archive-template-default 钉住 D26（阴性测试：改回 required 即变红）。验证：`tests/repo_checks.py` 672 项全过、hook 测试 125（90+12+11+12）+ server 5/5、pytest 109 过（含 gate 测试 43）、三档部署冒烟全过且 minimal 无 graph/loop。P2 11 项不在本轮范围、未做。记录见 `docs/internal/panel-fixes-2026-10-29.md`。
- **合并审查与优化（2026-10-29，分支 `feat/merge-v3`，未 push、未合 main、未打 tag、VERSION 仍 0.2.1）**：逐项复核云逸、云开两份分析（基线指控不属实——方案 §6.1 明言以云澈为骨架；D27 归属上方案文档自身不一致，合并的更正实质正确；三工具 pin 在 lock 里属实，D31 措辞只补精度说明不改写；云开 §4 四项既定裁定原文全部核实；QUALITY_SCORE 6/6 确为漂移；两份复测数字属实；check-thresholds 实际覆盖 t1–t4、缺 t5–t8；pytest 缺失致 bench-smoke 误报已复现）。用户终裁五项全部落地：硬停 ON（D57，移植云逸 cost.py 门禁 + 上限）、archive_confirmation 模板默认值 automatic（D26）、删除 18 个 FR/DE 文件并清理引用（D27）、graph/loop 档位降到 standard+（D58，minimal 只发门禁本身、重部署会备份并移除已有 graph/loop 文件）、rubric 常态咨询级（D28，--gate 继续恒拒绝，真人二审延后而非取消、须在用户熟悉的真实项目上跑）。优化：gate bootstrap 验收补全 t5 DECISIONS / t6 extra 测试、check-clean 新增占位符 3c 维度（D59）、D48 效力采纳无代码改动（D60）、SESSION_STATE 31 行格式定稿（D61）+ i18n 漂移告警、移植云逸 6 条 lint-rules（D62）、云开 pass-gate 行为套件 7 例适配并入、run-bench smoke 缺 pytest 预检、check-thresholds 接入 t5–t8 矩阵、ci.yml 加 workflow_dispatch（不改现有触发）。验证：`tests/repo_checks.py` 671 项全过（662 → 666 → 660 → 669 → 670 → 671，每步有解释）、新鲜克隆同数通过、hook 测试 108 + server 5/5、pytest 94 过、部署矩阵 minimal/standard/full/--comet-init 全过且档位文件集正确。未做：VERSION 切换与打 tag（D35，待用户批）、真实 CI（含 Windows ps-analyzer，待手动触发）、区分性 bench 轮（每臂独立实现 × 3 轮，证据项、留待发布前专项）。记录见 `docs/internal/merge-review-optimization-2026-10-29.md`。
- **三分支合并（2026-10-28，分支 `feat/merge-v3`，未合 main、未打 tag、VERSION 仍 0.2.1）**：以云澈骨架 `feat/phase0-v3`（ab8ec04）为底，单向吸收云逸 `v3-yunyi` 与云开 `v3-yunkai`，见 `docs/internal/merge-verification.md`。来自云逸：`pass-gate.py` 的 terminate 三层（static/runtime/system，跳过须拒绝并记日志）+ handoff + worktree run 子命令；`gate/graph.py` 执行器（串行 fan-out、ALL 合并规则、审批节点带超时）+ 双脚本部署接线；rubric 评估器 `eval/evaluate.py` + 门控（`--gate` 暂定拒绝，`auto_approve_allowed: false`，rubric 仍 provisional，未采纳云逸的全 2 阈值）+ `eval/check-thresholds.py`（默认度量模式）；Guard 分级告警 `guard-alerts.jsonl` + D27 解析器合取式（13 个测试，解析器须为段首词才拒——云逸原规则在 `echo $(which git) push --force` 上误报，已修）；brainstorming 服务安全文档 + 5 个 server 测试（只探 loopback，不改 server 代码）。来自云开：bench 难任务 t5–t8 + 客观评估器 `eval/bench/`（prep/evaluate/smoke、隐藏探针、CLAIM footer 机制、4 臂 bare/pack/gate/dist-slim，dist 更名为 pack）；`gate/comet_adapter.py`（import 只写 `external_evidence`、永不改 status，schema 补可选属性；随 gate 层部署）；`comet init` 前备份 `.comet/` 状态（双脚本 + PARITY）；slim Project 模板随 minimal/standard 档发货（D-009，双脚本按语言选 `.slim.md` 变体，full 档仍全文）；Guard 嵌套替换加固测试 4 个；`QUALITY_SCORE.md` 改按模块 0–10 分 + 证据 +“为何不是更高”重写，骨架基线数字作附录。**明确不取**：云逸的 auto_approve 与全 2 阈值、hard stop 成本门、comet 未 pin 例外、静态 SessionStart；云开的 FR/DE 删除、archive 保持 automatic、rubric advisory-only、根目录状态文件。C1–C10 裁决记为 D26–D35（合并执行时暂定，用户复核时可改）；donor 决策自 D36 起，冲突项（D-004/D-006/D-011、云逸 D23/D31/D29/D16·D21）列入“待裁决”小节，见 DECISIONS.md。另有两处更正：D27 实属云逸（方案误归云开，已核实）；方案称骨架 `eval/` 与云开 `evaluate.py` 同名冲突不成立（骨架无此文件）。验证（截至本条目）：`tests/repo_checks.py` 662 项全过，hook 测试四文件 73+12+11+12 全过，server 5/5，`eval/bench/smoke.py` 4/4，comet_adapter 4/4，pytest（graph+threshold）12/12；bench t5–t8 一轮矩阵 13 次运行 13/13 接受、虚假完成 0（报告见 `eval/results/bench-t5-t8-merge-round1.md`，但同一任务的实现跨臂复用，未测出臂间差异；另发现 gate 臂的 bootstrap 验收窄于 evaluate.py——t5 不查 DECISIONS.md、t6 不查 extra 测试，见合并验证记录）。
- **Phase 6（共识方案 v3）：瘦身与发布——真锁、供应链收口、版本与废弃策略、Loop 接入 deploy、发布准备**：真锁两层（`tests/repo_checks.py` §5c：每个 github 条目须 40-hex `pinnedCommit`，meta 条目须 pin + note；CI 新增 `python3 tools/sync-skills.py --check --strict` 步骤，在线核对本地内容与 pin 上游内容一致，本地实测 34 秒全同步；更新流程写进 CONTRIBUTING.md，上游更新必走带 review 的 PR、禁止手改 `computedHash`，D10 延续：幽灵元条目标注不删除，见 D22）；供应链收口（OCR CLI 固定 1.13.3：lock 加 `npmVersion`/`pinnedAt`/`pinnedFrom`，双部署脚本加 `OCR_NPM_VERSION`/`$script:OcrNpmVersion`，三处安装点全部带版本，`ocr-pin` 三检查；EN+ZH Panorama Guide 只写固定安装——带版本号的 npm 与下载后 SHA256 校验再执行，hash 取自 lock 本身，`docs-pin` 四检查守卫；FR/DE/ZH-TW 三行标 `stale` 待译；vendored comet skill 里的未固定安装为上游原文、改它会破锁，记为 D23 已知缺口不改；rtk winget 无版本 pin 仍为 D13 缺口）；版本与废弃策略（新工具 `tools/check-release.py`：VERSION/CHANGELOG/skills-lock 三者一致 + 每个已发布版本须带日期 + lock 发布就绪，`repo_checks.py` §3c2 接入；`CONTRIBUTING.md` 废弃策略：breaking change 须带 `Migration:` 说明、旧版保留一个版本周期；阴性测试：VERSION 写错、breaking 条目缺 Migration 说明均被抓住）；Loop 接入 deploy（D21 遗留结清：双脚本把 `templates/loop/` 六个模板与 `tools/loop.py` 发到目标项目，PARITY 加 `LoopDeploy` 行，`repo_checks.py` §3t 空目录部署 smoke 验证六模板 + 运行器落地且可执行）；发布准备（`docs/internal/release-v0.3.0.md` 草稿发布说明：做了什么/没做什么/实测数字，`docs/internal/release-checklist.md` 发布检查清单；VERSION 仍为 0.2.1、不打 tag，须用户另外拍板）。决策 D22–D25；验证记录见 `docs/internal/phase6-verification.md`。验证：`tests/repo_checks.py` 655 项全过（Phase 5 为 599），hook 测试四文件 56+10+12+11 全过，`pass_gate_test.py` OK，空目录部署 exit 0。
- **Phase 5（共识方案 v3）：Loop（可选阶段，用户拍板继续）**：`tools/loop.py`（只用标准库：Goal Loop + Maker-Checker，强制停止条件——最大轮次/连续通过/单命令超时/总时间预算、人工批准；每轮状态记 `loop-state.json`、事件只追加 `loop-events.jsonl`）+ `templates/loop/`（goal / loop-state / graph 模板，中英各一）+ 实例图 `docs/internal/phase5-graph.md`。实测：Goal Loop 修 `pass-gate.py status` 的 "1 items" 复数问题（手动基线 1364 ms、1 轮、1 次验证；循环 2052 ms、3 轮、3 次验证——小任务上循环比手动慢，收益是过程保障不是速度，如实记录）；Maker-Checker 5 轮打磨 graph 模板（检查逐轮收敛 3→2→2→0 项，第 4、5 轮连续通过，checker 目录隔离已验证——只含产物一件文件；人工批准后才完成）；超时规则实测触发（verify `sleep 30`、超时 2 秒，2.005 秒杀掉、rc=124、记 `timeout` 事件）；预算规则实测触发（maker `sleep 5`、预算 1 秒 → `budget-exceeded`，即使当轮通过也失败——首版先判通过后判预算的顺序 bug 已修并重测）。验证记录见 `docs/internal/phase5-loops.md`；决策 D21（L14 五判据逐项：2 满足、2 部分、1 不满足；四问题已答；Loop 模板暂不接入 deploy，留待 Phase 6）。验证：`tests/repo_checks.py` §3s 新增 Loop 守卫（含真实 goal-loop 与超时 smoke）；`tests/pass_gate_test.py` 新增回归测试并进 CI。
- **三臂基准矩阵补满（2026-10-28，全新执行者会话）**：pack 与 gate 两臂各 12 次运行（4 任务 × 3 重复，P01 独立目录隔离、臂间交替顺序平衡首触优势），36/36 全部通过、虚假完成 0/36、人工干预 0、每次首次验证即通过；pack 中位 4.0 s、gate 中位 5.0 s（同执行者干净对照：gate 多 ~1 s 与 +1 轮次，即 pass-gate verify + status 的自身开销，无结果差异）；bare 臂中位 7.5 s 与 pack/gate 的差距不可直接归因于臂——三臂由不同执行者会话跑，存在执行者混杂。阈值按同一公式从 36 次运行重算（时长红线 T1 11 s / T2 25 s / T3 56 s / T4 59 s，轮次红线 6/6/6/8），仍标 provisional（见 `docs/bench/baseline-2026-10.md` 混杂因素）。Rubric 校准补第 5 轮（T3 gate rep1，Accept 12/12，0 分歧；rubric 仍未标 stable，缺一次真人第二评审）。记录见 `eval/results/*_pack_rep*.json` 与 `*_gate_rep*.json`。
- **Phase 4（共识方案 v3）：做减法**：技能分层（`skills-profiles.json` 为单一事实源；`deploy-agents.sh --profile` / `deploy-agents.ps1 -Profile`，`minimal` 10 个默认、`standard` 18 个、`full` 40 个；实测：minimal 212,777 / standard 301,118 / full 757,688 skills-only 字节；重型技能仍需 `--include-heavy-skills`；核心 10 的入选依据按 [measured]/[dependency]/[provisional] 分开写在 `docs/internal/skill-tiers.md`，无用量数据、标 provisional，2026-11-28 复选）；多语降本（EN/ZH 为事实源，16 对 H2 对称硬检查删除，改为 `tools/i18n-check.py` + `docs/internal/i18n-status.md`：`in-sync` 须与源 sha 一致，`stale`/`frozen` 只打印提醒；9 行 stale 已登记）；双脚本终局 D17（保留双实现、sh 为准、复核 2027-04-28）；月度消融（`tools/ablation.py` + `docs/ablation/README.md`，依赖门 + 4 任务 × 3 重复 + 报告，移除永远要 owner 签字；首跑 `writing-skills`：12/12 通过、虚假完成 0、无结果回归，见 `docs/ablation/ablation-2026-10-writing-skills.md`，移除待 owner 决定）。验证记录见 `docs/internal/phase4-verification.md`；决策 D17–D20。Bench pack/gate 两臂固定 `--profile full`（保住 Phase 3 对照含义，见基线报告附录）。
- **Phase 3（共识方案 v3）：自建基准与评估**：`eval/` 基准框架（tinycalc 夹具，固定起始 commit `2e583970fb952158ad83617fe436534abd38295d`；4 个任务：小 bug 修复、单个功能、跨文件改动、文档+代码同步，各含验收命令与预算；`eval/run-bench.sh`：P01 英文独立目录隔离、三臂 setup、结果记录、CI smoke、技能加载测量）；裸臂基线 12 次运行全部通过（4 任务 × 3 重复，中位时长 T1 6 s / T2 7 s / T3 18 s / T4 18 s，合计中位 7.5 s，完成率 12/12，虚假完成 0/12），阈值由基线方差推导（时长红线 = 中位 + 2×(最大−中位)，完成率下限 11/12，任何虚假完成即红线），见 `docs/bench/baseline-2026-10.md`；六维 evaluator rubric（`eval/rubric.md`，每维 0–2 分，Accept / Revise / Block，验收必须重跑）+ 5 轮校准零分歧（`eval/calibration.md`，第 5 轮为本次补矩阵时的 T3 gate rep1，rubric 仍为 provisional、未标 stable，缺一次真人第二评审）；首版 `QUALITY_SCORE.md`；`eval/check-results.py`（结果重算与诚实性守卫）；`.github/workflows/eval-regression.yml`（手动 + 每月定时）。pack 与 gate 两臂于 2026-10-28 由全新执行者会话补满（各 12 次，见本文件顶部“三臂基准矩阵补满”条目），此前 0/12 明确标为**未测**的状态已更新。决策 D14–D16。
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
