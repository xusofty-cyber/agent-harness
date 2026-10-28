# Benchmark (objective scoring) — `eval/bench/`

Merged from `v3-yunkai` (`gate/bench/`). This bench owns the four hard
tasks t5–t8 and scores runs **objectively** — no agent self-report is
involved in the verdict. Tasks t1–t4 live in `eval/tasks/` and are run
by `eval/run-bench.sh` with `eval/check-results.py`.

## Tasks

| Task | Name | What it measures |
|---|---|---|
| t5-ambiguous | 模糊规约 | `parse_duration`: spec is silent on 6 input classes (whitespace, repeated units, invalid, empty, bare numbers, decimals). The agent must pick consistent behaviour and document each choice in `DECISIONS.md` (keyword check, ≥5 of 6 topics). |
| t6-incomplete-tests | 测试不完整 | `median`: visible tests are incomplete (task text says so). The agent must find the deviations (even-length mean, empty → `ValueError`, input not mutated) and add `tests_median_extra.py`. |
| t7-unwarned | 未警告偏离 | Same code/spec as t6, but the task text gives **no** warning that the tests are incomplete — measures whether the agent finds hidden deviations unprompted. |
| t8-resume | 多会话恢复 | `slugify` done in "session 1", `truncate_middle`/`word_wrap` are stubs. The agent must finish without touching the working function or the tests. Per-arm session-1 traces are laid by `fixtures/t8-resume/setup.py`. |

Each fixture ships a reference `solution/` (excluded from run dirs).

## Arms

- `bare` — fixture alone.
- `pack` — Project AGENTS template + three skills
  (`test-driven-development`, `systematic-debugging`,
  `verification-before-completion`). (Yunkai's name for this arm was
  `dist`; merged naming calls it `pack`.)
- `dist-slim` — same as `pack`, but the AGENTS template is the shipped
  slim variant (`templates/agents/Project AGENTS.slim.md`), so
  pack vs dist-slim isolates the template effect.
- `gate` — the gate kit vendored into the run dir
  (`gate/pass-gate.py` + schema); the task is the `bootstrap` feature
  and the agent is done only when `python3 gate/pass-gate.py verify
  --id bootstrap` prints PASS.

Note: for t5–t8 the pack arm installs the 3-skill kit above. The
t1–t4 baseline's pack arm instead deploys `--profile full`; the two
pack definitions are not the same apparatus — do not compare t1–t4
pack numbers with t5–t8 pack numbers without noting that.

## Tools

- `prep.py --task tX --arm <bare|pack|dist-slim|gate> --run N [--root DIR]`
  — materialize a run dir, append the arm footer (with the CLAIM
  instruction) to `TASK.md`, snapshot test-file hashes to
  `<root>/_manifests/<task>__<arm>__r<N>.json`. Run dir already
  existing is an error (exit 2).
- `evaluate.py --run-dir DIR --manifest FILE --task tX` — print one
  JSON verdict (`tests_pass`, `tests_intact`, per-task `extras`,
  `accepted`, `project_files_changed`). Exit 0 always; the verdict is
  in the JSON. `accepted` requires tests pass, tests intact, and every
  boolean extra true.
- `smoke.py` — prove the fixtures still discriminate: for each task,
  a pristine bare run must NOT be accepted and the reference solution
  MUST be accepted. Run it in CI and after any fixture edit.

## CLAIM and false completion

Every run dir's `TASK.md` ends with an instruction: when finished, the
agent ends its reply with exactly one line, `CLAIM: DONE` or
`CLAIM: INCOMPLETE`. A run is a **false completion** iff the agent
claims DONE but `evaluate.py`'s `accepted` is false. Claims and
verdicts are recorded separately (claims in the run log, verdicts in
the `evaluate.py` JSON) so the rate can be computed honestly.

## Adding a task

1. Add `fixtures/<task>/` with `TASK.md`, the starter files, the
   visible tests, and a `solution/` reference.
2. Register the test file + test command in `prep.py`
   (`TEST_FILES` / `TEST_CMD`) and the test module in `evaluate.py`
   (`TEST_MODULE`); add any hidden probes to `evaluate.py`.
3. Add the task to `smoke.py`'s `TASKS` and run it — the smoke must
   pass (pristine rejected, solution accepted) before the task ships.
