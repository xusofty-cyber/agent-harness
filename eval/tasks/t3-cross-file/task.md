# T3 — Cross-file change

| Field | Value |
|---|---|
| id | `t3-cross-file` |
| kind | cross-file change |
| start_commit | `2e583970fb952158ad83617fe436534abd38295d` |
| acceptance | `python3 -m pytest tests/test_calc.py::test_times tests/test_cli.py -q` (exit 0) AND `grep -rn "multiply" --include="*.py" --include="*.md" .` finds nothing AND `python3 -c "from calc import times; assert times(2,3)==6"` (exit 0) |
| budget_time | 20 min |
| budget_rounds | 25 tool calls |
| host | Muse (this session) |
| model | Muse Spark (record the actual model per run) |
| fixture | `eval/fixture/` (tinycalc) |

## Goal

Rename the `multiply` operation to `times` everywhere it appears: `calc.py`,
`cli.py` (including the usage string and the `multiply` subcommand),
`tests/test_calc.py`, `tests/test_cli.py`, and `README.md`. After the rename,
`python3 cli.py times 2 3` must print `Result: 6.0`.

## Rules for the run

- Work only inside the isolated run directory prepared by `eval/run-bench.sh`.
- Do not read any other run directory, `solution.patch`, or another arm's files.
- Verify with the acceptance command. Do not claim success until it exits 0.
- The other failing tests at the start commit (`test_subtract`,
  `test_power`, `test_divide_rounding`) belong to other tasks — do not fix
  them, and do not count them against this task.
- Record the run with `eval/run-bench.sh record` (duration, rounds,
  verify attempts, outcome, false-completion flag).

## Reference solution

`solution.patch` (kept out of run directories) applies cleanly to the start
commit and makes the acceptance command pass. It is used by CI smoke tests,
never shown to the agent during a run.
