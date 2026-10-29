# agent-harness 裁决与修复记录 — 2026-10-29

> 分支：`feat/merge-v3`，本文档定稿时 HEAD `a76430b`（合并基线 `dbe9c5f` 之上 20 个提交）。
> 本记录的用途：**以用户原话为准，一次性定死此前有争议的政策项，杜绝后人再翻旧记录翻案。**
> 效力说明：此前合并时记为“暂定”的裁决（D26–D35 等），一律以本记录的终裁为准；旧暂定措辞只保留为历史，不再作为依据。
> 本记录另有一份内容一致的副本在分支内 `docs/internal/merge-rulings-and-fixes-2026-10-29.md`。
> 状态：未推远端、未合 main、未打 tag、VERSION 仍 0.2.1（见第 3 节）。

## 1. 用户终裁总表（2026-10-29，原话为准）

| # | 用户原话 | 终裁内容 | 取代的暂定裁决 | DECISIONS | 落点（文件） | 验证 |
|---|---|---|---|---|---|---|
| 1 | “硬停 ON” | 成本硬停开启：移植云逸 `cost.py` check 门禁 + D23 上限 | 合并暂定 OFF（告警-only） | D57 | `eval/cost.py`、`eval/cost-budget.json`、`tests/cost_test.py`（5/5）；`tools/cost-ledger.py` 仍只警告——两账本、两角色，骨干 D12 与云开 D-007 在各自工具上仍然成立 | repo_checks `cost-gate:*` 守卫；本轮 671 PASS 含此项 |
| 2 | “archive 是 automatic” | 模板默认值改回 automatic | 合并 D26 的 required | D26 | `templates/comet.config.yaml:54` required → automatic；D4 保留为 Phase 0 历史，模板向前以 automatic 为准；已部署项目不受影响（部署仅在目标缺失时复制模板）；本仓无自有 `.comet/config.yaml`（Phase 0 已去重删除） | 模板实测 automatic |
| 3 | “FR/DE 删” | 删除 18 个 FR/DE 文件并清理引用 | 合并 D27 的冻结保留 | D27 | 删除清单见分支记录 §3；引用清理含 repo_checks §3h、i18n-check、i18n-status、README/指南切换器、deploy 与 pipeline 语言菜单（fr/de 输入回落 EN）、CONTRIBUTING 表、count-skills、向导语言列表；ZH-TW 保持冻结 | 跟踪文件实测无 FR/DE 残留 |
| 4 | “graph/loop 降到 standard+ 再发布” | minimal 档只带门禁本身，不带 graph/loop；standard/full 带 | 合并时 minimal 默认带 graph/loop | D58 | deploy 双脚本档位分发（`TierGateGraphLoop` PARITY 行）；repo_checks §3t 按档位断言文件集；文档档位叙事：minimal=门禁本身，standard=门禁+编排，full=全部 | 三档实测：minimal 无 `gate/graph.py`、无 `tools/loop.py`、0 loop 模板；standard/full 全有；exit 均为 0 |
| 5 | “先定常态咨询级，后面条件成熟再真人评审” | rubric 常态咨询级：只提供咨询意见，永不自动放行；`--gate` 继续恒拒绝（exit 2）；真人二审延后、不是取消 | 合并 D28 的 provisional“还差一轮真人二审” | D28 | `eval/rubric-status.json`：status provisional → advisory-only，`confirmation_round_required` true → false；发布说明与 QUALITY_SCORE 措辞同步为“只提供咨询意见，不自动放行”；repo_checks `eval:rubric-advisory-only` 钉住该裁决 | 状态文件实测 advisory-only |
| 6 | “先不着急发版本，先确认是否达到发版的时机了” | VERSION 切换与打 tag 不单独再裁：号已是 v0.3.0（C10），切换与打 tag 等用户批了合 main + 发布后，作为同一个已批准动作的一部分执行；当前不执行 | ——（此前误列为“待裁决”，用户指出后纠正：数字无需再裁，只差时机） | D35 | 当前 VERSION 仍 0.2.1、未打 tag；`tools/check-release.py` 现状通过（VERSION/CHANGELOG/lock 一致，42 lock 条目）；`docs/internal/release-checklist.md` 载有流程（进 main 的 PR 须用户明确批准，main 冻结中） | check-release 实测 OK |

**未来触发条件（第 5 项附带，用户原话的延伸记录）：** 真人二审条件成熟时再做，且必须是在用户熟悉的真实项目上跑——bench 小任务不算数，在 toy 任务上补一轮二审测不出分辨力；只有那样一轮真的跑过且一致性达标，才重新讨论 stable 与自动放行。在此之前，本项不欠任何作业。

**迁移提示（第 4 项附带，原文）：** 此前以 minimal 部署过、已带有 graph/loop 文件的项目，以 minimal 重新部署后这些文件会被移除（事先备份为 `.bak.` 时间戳文件）；如需保留，请改用 `--profile standard` 重新部署。

## 2. 本轮修复总表（合并基线 dbe9c5f → a76430b，20 个提交）

政策落地 5 项即上表第 1–5 项（`ca3013c`、`d0f7d9a`、`eeff670`、`6f04832`、`4ea74ce`）。其余修复：

| 提交 | 修复 | 来源 | 验证 |
|---|---|---|---|
| `7f23a9f` | QUALITY_SCORE 数字漂移 6/6 → 3/3（合并分支 feature_list 实为 3 条，全 passing）；pin 精度说明补记（见补注）；ci.yml 加 `workflow_dispatch`（不改现有触发、不自动跑） | 云开 §5#1、云逸 P0#3、云逸 P1#9 | 数字实测 3/3；触发条件实测仅新增 dispatch |
| `f785acb` | Gate bootstrap 验收补全：t5 纳入 DECISIONS.md（≥5/6 主题组，与 evaluate.py 同组）、t6 纳入 `tests_median_extra`；Gate PASS ≠ 任务全过的缺口补上 | 云逸 P0#4（取优先方案：纳入验收，而非仅文档说明） | 新增 `tests/bench_bootstrap_verify_test.py` 4/4（缺 extra 则 FAIL、有则 PASS） |
| `0c03da7` | D47/D48 落定不再挂候选：D47 采纳——check-clean 新增 3c 维（占位 FAIL）；D48 实质采纳、无代码改动（实测无检查依赖 gitignored 文件） | 云逸 P1#8 | `tests/check_clean_test.py` 4/4；新鲜克隆验证 D48 |
| `0834664` | SESSION_STATE 格式定稿：骨干 31 行 EN 格式为最终版（与 D29 骨干 schema 一致），云逸 11 行格式不采纳；i18n-check 增加行数漂移提醒（>5 行告警、不阻塞） | 云逸 P0#5（取 (b) 方案） | ZH-TW 46 vs 31 打印 [drift] 提醒、exit 仍 0；ZH 27 vs 31 在容差内 |
| `b5c0c4a` | 移植云逸 6 条 lint-rules（骨干适配）+ repo_checks 门禁（D62） | 云逸 P1#6（逐条对账，非“部分采纳”） | `tests/lint_rules_test.py` 3/3；`tools/lint-rules.py` 5 PASS + LINT-006 WARN（预期内 ZH-TW 漂移），exit 0 |
| `876b5f2` | 旧 eval 测试断言 provisional，跟随 D28 改为 advisory-only | 第 5 项裁决的跟随修复 | pytest 94/94 含此项 |
| `cb1f6d2` | bench smoke 缺 pytest 时快速失败并给出明确诊断 + 安装提示，不再误报 1 FAIL | 云开 §5#3（实测复现过该误报） | 以 stub python 实测 PREFLIGHT FAILED + 安装行、exit 1 |
| `9eec6c2` | 移植云开 pass-gate 行为套件 7 例（骨干 schema 适配，不发明新门禁功能） | 云开 §5#4 | `tests/pass_gate_test.py` 10/10（含原有 3 例） |
| `aafc6a6` | t5–t8 矩阵结果接入 check-thresholds（此前只覆盖 t4 记录） | 云逸 P1#7 后半段 | t1–t4 12 组 ok，t5–t8 13 组“无结论”（各仅 1 条记录），无 breach；新增阈值测试 2 例 |
| `7e74217`、`e486268`、`d381774`、`5a79181`、`10bfcac`、`a76430b` | Sweep 跟随清理：向导与 deploy/pipeline 帮助去掉 fr/de、陈旧文档措辞同步到已终裁项、删除孤立的 D27 暂定行、C1–C10 引言加“暂定”限定；审查记录、CHANGELOG、发布检查清单同步 | 模块 sweep | 全部 --help exit 0；本记录即 sweep 产物 |

**审查结论摘要（两份分析的核查结果，证据见分支记录 §1）：**

- 云逸“方案推荐 v3-yunyi 做骨架”**不属实**：对比方案 §6.1 明言以云澈 `feat/phase0-v3` 为骨架，合并选 `ab8ec04` 是遵方案。
- D27 归属：方案文档自身不一致——§6.3 把 D27 Guard + 13 测试归于云开，但云开 DECISIONS 只有 D-001–D-011、并无 D27；云逸 D27 经远端分支核实确实存在。双方各对一半，已在本记录与分支记录中纠正，D27 归属云逸无争议。
- 云逸 P0#3 **不属实（本记录初版写错，2026-10-29 晚间已更正）**：云澈直接查 `skills-lock.json` 实测，三工具**都在** 42 条目内且有 pin——codegraph：pinnedCommit `01e0ac3a…` + installerSha256（sh 与 ps1 双通道）；comet：npmVersion 0.5.1 + pinnedCommit `35c9860b…`；rtk：pinnedCommit `e05c7bdf…` + installerSha256。DECISIONS 原句“都 pin 在 lock 里”为真，`7f23a9f` 只补了精度说明（rtk 的 ps1 winget 通道仍无 pin，属 D13 已知缺口；上游 tip 与 pin 不一致是按设计，不算过期）。云逸原文称“42 条目无此三名”与实测不符，初版记录采信该说法是云澈的核查失误，特此更正。rtk SHA 在 merge-v3（`e05c7bdf…`）与云逸分支（`753a3b0e…`）不同一事仍成立，发布前以 rtk 上游尖端复核一次（见第 4 节）。
- 云开 §4 四项“用户既定裁定”经核对原文成立（D-004、D-006、D-007、D-011 均见于云开分支记录），本轮第 1、2、3、5 项终裁与之对齐；硬停一项三方记录曾互相矛盾（云逸 D23 称用户选 ON、骨干 D12 与云开 D-007 称只警告），现以用户 2026-10-29 终裁 ON 为准。
- 两份分析的复测数字（repo_checks 662、hooks 108、pytest 69、bench smoke 4/4、deploy smoke）抽查复跑属实。

**模块 sweep（本轮已列项之后逐模块复扫，方法与结论见分支记录 §7）：** gate、hooks 与 guard、deploy 双脚本与 PARITY、三档分发、bench/eval、loop、成本账本、真锁、check-release、i18n、文档——已扫，无新增问题；“无问题”指按所列方法实测过，不是跳过。

## 3. 本轮验证数字（云澈独立重跑，非复述执行者自述）

- `python3 tests/repo_checks.py`：**671 PASS / 0 FAIL**（合并基线 662 → 666 成本门 +4 → 660 FR/DE −6 模板检查 → 669 档位 +8 §3t +1 PARITY → 670 lint-rules 检查 → 671 rubric 检查；每步有解释，无静默漂移）。
- 新鲜克隆 repo_checks：**671 PASS**（同时证实 D48：无检查依赖 gitignored 文件）。
- Hooks：73 + 11 + 12 + 12 = **108 全过**，server **5/5**。
- pytest：**94 passed**（合并时 69 + 成本 5 + bootstrap 4 + check-clean 4 + lint-rules 3 + pass-gate 行为 7 + 阈值归一化 2 = 94，算术相符）。
- 三档部署：minimal / standard / full / `--comet-init` 全部 exit 0；minimal 无 graph/loop、standard/full 全有；已部署的 runner `--help` 全部 exit 0；minimal 覆盖 standard 的迁移实测：graph/loop 文件先备份（`.bak.`）再移除。
- `check-thresholds.py`：t1–t4 12 组 ok，t5–t8 13 组无结论，无 breach。
- `check-release.py`：OK（VERSION 0.2.1、CHANGELOG 最新 0.2.1、lock 42 条目）。
- `lint-rules.py`：5 PASS + LINT-006 WARN（预期内 ZH-TW 漂移），exit 0；`i18n-check.py`：通过（5 提醒 + 1 [drift]）。
- CI：本分支至今无 GitHub CI 运行（ci.yml 原触发不含该分支；本轮已加 `workflow_dispatch`，尚未触发）；ps1 改动仅静态验证（本机无 pwsh，CRLF+BOM 保留、PARITY 标记齐全），以 CI 为准。

## 4. 仍未决事项与发版前剩余清单

**政策项：用户明确提出异议的 6 项已全部终裁；D29–D34 仍为合并时暂定（未再起争议，随发布批准一并确认）。** D29–D34 即合并时 C1–C10 映射中除 D26–D28 外的部分（骨干 schema 为标准、standard 档 18 技能、默认 minimal、状态文件放 `gate/`、DECISIONS 在根目录、Loop/Graph 进 v0.3.0），用户未再提出异议，但也未经用户终裁确认，发布批准时一并确认；D35（VERSION/tag）见上表第 6 项。

发版前剩余清单（按顺序，均未执行）：

1. **发版时机判定**：由用户根据本记录与就绪检查定（用户原话：“先不着急发版本，先确认是否达到发版的时机了”）。
2. **真实 CI 运行**：在 GitHub Actions 上对本分支手动触发 `workflow_dispatch`，须含 Windows `ps-analyzer` 任务；本地按 CI 形式跑过不能替代。
3. **rtk SHA 上游复核**：发布前以 rtk 上游尖端复核一次 merge-v3 的 pin 值，确认不是过期值（云逸 P0#3 的跟随项）。
4. **区分性 bench 轮（证据项，不是工具可用性项）**：每臂独立实现 × 3 轮（t5–t8，如重定基线则含 t1–t4）。现有矩阵有天花板效应（任务太简单、同一实现多臂复用），不能证明门禁降低了误完成率；本轮故意未跑（需全新执行者，属发版专项、非代码改动）。发布文案在跑出该轮之前，不得宣称“门禁降低了误完成率”，只能说“器械跑通、0 误完成”。
5. **进 main 的 PR 与合并**：须用户明确批准（main 自 2026-10-28 冻结）；注意 revert-the-revert：main 上的 revert 提交 `1d3ecb7`（`88c8b79`）须先单独 revert，否则 `feat/merge-v3` 的内容无法落地。
6. **VERSION 切换 + 打 tag + 发布**：用户批了合 main + 发布后，作为同一个已批准动作执行（VERSION 0.2.1 → 0.3.0、打 `v0.3.0` tag、发 Release）；发布当天数字须重验，不得照抄本记录。

## 5. 争议预防声明

此前争议的根源，是三方记录对“用户到底怎么裁定的”记载互相矛盾（硬停、archive、FR/DE、rubric 四项皆然），而合并时的“暂定”又给了旧记载继续存在的空间。本记录的处理方式：

- 每项终裁以用户原话为准，附日期与 DECISIONS 编号；
- 被取代的暂定裁决明文写出“被取代”，不删除历史、但不再作为依据；
- 今后任何一方再拿旧记录翻案，以本记录为准。
