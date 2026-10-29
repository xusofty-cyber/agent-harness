# bench t5–t8 合并分支第一轮（merge round 1）

- 工作区：`~/workspace/agent-harness-merge`（分支 `feat/merge-v3`，未动 main，未 push，未开 PR）
- run 根目录：`/tmp/agent-harness-bench-merge1`，run 编号 r1
- 执行者：本轮由云澈本人作为执行者完成 13 次运行（真实阅读 TASK.md、测试与规约后写实现，非仅跑脚本）
- 执行时间：2026-10-28 晚（CST）；13 份 `evaluate.py` JSON 原样保存在同目录子目录 `bench-t5-t8-merge-round1/`，文件名 `<任务>__<臂>__r1.json`

## 方法说明（重要，直接影响本轮数字的解读）

- 每个任务的实现是我先通读该任务的 TASK.md、源码与可见测试后写出的，同一任务的同一份实现被应用到该任务各臂的 run 目录内（各臂的差异变量是 prep 铺设的装置：bare 无附加物、pack/dist-slim 带 AGENTS.md 与三技能、gate 带 pass-gate；实现本身不因臂而异）。
- 因此本轮的“耗时”列量的是每 run 内“拷入实现 → 跑测试 → gate 臂再走 verify → evaluate.py 评分”的机械耗时（0.2–0.8 秒），**不是**每 run 独立从头推理的用时。任务没有给定单 run 超时阈值，故“是否超时”一律记为“无阈值 / 不适用”，13 次均在秒级内完成。
- CLAIM 按规则诚实自认：测试通过（gate 臂另需 gate 打印 PASS）才写 DONE，否则写 INCOMPLETE。本轮 13 次 CLAIM 全部为 DONE，且全部与 evaluate.py 的 accepted 一致。

## 逐 run 记录

| # | 任务 | 臂 | CLAIM | accepted | tests_pass | tests_intact | 关键 extras | 耗时（秒） | 超时 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | t5-ambiguous | bare | DONE | true | true | true | decisions_topics_count=6/6 | 0.3 | 无阈值 |
| 2 | t5-ambiguous | pack | DONE | true | true | true | decisions_topics_count=6/6 | 0.2 | 无阈值 |
| 3 | t5-ambiguous | dist-slim | DONE | true | true | true | decisions_topics_count=6/6 | 0.2 | 无阈值 |
| 4 | t5-ambiguous | gate | DONE | true | true | true | decisions_topics_count=6/6；gate bootstrap PASS | 0.3 | 无阈值 |
| 5 | t6-incomplete-tests | bare | DONE | true | true | true | hidden_probes_pass=true；extra_tests_exist/pass/cover_spec 全部 true | 0.3 | 无阈值 |
| 6 | t6-incomplete-tests | pack | DONE | true | true | true | 同上，全部 true | 0.3 | 无阈值 |
| 7 | t6-incomplete-tests | gate | DONE | true | true | true | 同上，全部 true；gate bootstrap PASS | 0.5 | 无阈值 |
| 8 | t7-unwarned | bare | DONE | true | true | true | hidden_probes_pass=true | 0.2 | 无阈值 |
| 9 | t7-unwarned | pack | DONE | true | true | true | hidden_probes_pass=true | 0.2 | 无阈值 |
| 10 | t7-unwarned | gate | DONE | true | true | true | hidden_probes_pass=true；gate bootstrap PASS | 0.4 | 无阈值 |
| 11 | t8-resume | bare | DONE | true | true | true | slugify_unchanged=true | 0.2 | 无阈值 |
| 12 | t8-resume | pack | DONE | true | true | true | slugify_unchanged=true | 0.2 | 无阈值 |
| 13 | t8-resume | gate | DONE | true | true | true | slugify_unchanged=true；truncate/wrap/bootstrap 四项 gate 全部 passing | 0.8 | 无阈值 |

补充细节：

- t5：`parse_duration` 按“空白容忍、重复单位拒、非法/空/裸数字/小数均 ValueError”实现；`DECISIONS.md` 覆盖全部 6 类输入（evaluate 关键词命中 6/6）。
- t6：修复 `median`（偶数取两中值均值、空输入 ValueError、不改动输入的 `sorted()` 拷贝），新增 `tests_median_extra.py`（4 个测试：偶数均值、偶数未排序、空输入抛错、输入不被改动），新旧两套测试均通过。
- t7：与 t6 同一份 `median` 修复（无提示也按规约找出了三处偏离：偶数均值、空输入、输入不被改动）；按 TASK 要求未新增 extra 测试文件（t7 的 evaluate 也不检查该项）。
- t8：只实现 `truncate_middle` 与 `word_wrap`，未动 `slugify`（evaluate 判定 `slugify_unchanged=true`）；bare 臂保留了 setup.py 留下的 session-1 注释；gate 臂按 SESSION_STATE.md 提示走完 start textkit-truncate → verify → start textkit-wrap → verify → unblock bootstrap → verify bootstrap，四项最终全部 passing。

## 汇总表

| 臂 | 运行数 | accepted（通过） | CLAIM DONE | 虚假完成数（claim DONE 但 accepted false） |
|---|---|---|---|---|
| bare | 4 | 4 | 4 | 0 |
| pack | 4 | 4 | 4 | 0 |
| dist-slim | 1（仅 t5） | 1 | 1 | 0 |
| gate | 4 | 4 | 4 | 0 |
| **合计** | **13** | **13** | **13** | **0** |

## 观察到的异常 / 说明

1. **天花板效应，本轮三臂无差异。** 13/13 通过、0 虚假完成。结合方法说明：同一执行者、同一份实现跨臂复用，本轮实际只验证了各臂装置本身能正常工作（prep、gate 流程、评分链路均通），**没有测出臂之间的效果差异**。若要回答“gate/pack 是否降低虚假完成率”，需要不同执行者（或同一执行者独立重做、不得复用已写好的实现）跑对照，或用更难的任务。
2. **无脚手架失效。** 13 次 prep 全部一次成功；pack/dist-slim 的 AGENTS.md 与三技能（test-driven-development、systematic-debugging、verification-before-completion）均已铺设；gate 臂的 bootstrap 与 t8 的子项流程（block/unblock、WIP=1）均按预期工作，未出现卡住。
3. **TASK 描述清晰，未见歧义。** t5 的 6 类输入、t6 的“测试不完整”提示、t7 的无提示、t8 的 SESSION_STATE 提示均与实际装置一致；t8-gate prep 时 textkit-slugify 已 passing、bootstrap 已 blocked，与任务说明相符。
4. **evaluate.py 的 `project_files_changed` 有一处无关噪音（不影响 accepted）：** t8 三臂的 changed 列表里都出现了 `setup.py`，但 prep 根本不把 `setup.py` 拷进 run 目录（`prep.py` 的 copytree 排除了它）；evaluate 是把“fixture 有、run 目录缺失”也算作 changed。属于统计口径问题，不是违规改动（`tests_intact` 全部 true，`slugify_unchanged` 全部 true）。
5. **gate 臂的验收覆盖面小于 evaluate.py：** t5-gate 的 bootstrap 只跑 `python3 -m unittest tests_durations`，不检查 `DECISIONS.md`；t6-gate 的 bootstrap 只跑 `tests_statsx`，不检查 `tests_median_extra.py`。也就是说 gate 打印 PASS 不等于任务的全部要求都已满足（本轮是我在 gate verify 之外另行补足了 DECISIONS.md / extra 测试，evaluate 才全过）。若把 gate 当作唯一完成标准，t5/t6 存在“gate 通过但 evaluate 不接受”的缺口。
6. **耗时数字不可与 t1–t4 轮直接比较。** 本轮耗时是机械执行耗时；且 t5–t8 的 pack 定义（3 技能 kit）与 t1–t4 的 pack（`--profile full`）本就不是同一装置（README 已注明）。
