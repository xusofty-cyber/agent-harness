# Monthly ablation (Phase 4, 4-4)

One component a month, disabled for a bench run, kept or removed on
evidence — not on opinion. The bar for removal is deliberately high: a
no-regression result is necessary but not sufficient, and the owner signs
off every removal in writing.

## Cadence

- **Monthly, one component per run.** Pick the next component from the
  queue below; run it; file the report under `docs/ablation/`; the owner
  fills in the Human decision line. A report without a decision is an open
  item, not a removal.
- **12 months, ≥6 recorded ablations** is the v2 target. Missing a month
  is recorded as missed, not silently skipped.

## Selection queue (largest guide-only skills first)

Order by size among skills with no template/hook references (the
dependency gate in `tools/ablation.py` re-checks this at run time; the
queue is a starting point, not a verdict):

| # | Component | Bytes | Gate (2026-10-28) |
|---|---|---|---|
| 1 | `writing-skills` | 107,640 | CLEAR — first run, 2026-10; skill REMOVED 2026-10-29 by owner decision (D65), no longer a candidate |
| 2 | `diagnosing-superpowers` | 40,841 | CLEAR (guide-listed only) |
| 3 | `executing-plans` | 23,060 | CLEAR (guide-listed only) |
| 4 | `using-superpowers` | 20,630 | CLEAR (guide-listed only) |
| 5 | `receiving-code-review` | 6,203 | CLEAR (guide-listed only) |
| 6 | `git-advanced` | 5,580 | CLEAR (guide-listed only) |

(`cross-tool-memory` was first listed here and removed on verification:
the gate finds it referenced by `templates/agents/Project AGENTS.md` as a
path, so it is BLOCKED, not CLEAR. The queue above was re-verified skill
by skill with `ablation.py check`.)

Skills referenced by a distributable template or hook (16 of 39, e.g.
`systematic-debugging`, `ponytail`, `codegraph`) are NOT ablatable until
their references are removed first — the gate blocks them, and the report
says so. OpenSpec family skills are ablated as a family decision, not one
by one: removing a single loop step breaks the loop.

## How a run works

```sh
# 1. Dependency gate
python3 tools/ablation.py check --component diagnosing-superpowers
# 2. For each task (t1..t4) and rep (1..3): prepare a pack-arm run dir
#    with the component removed, perform the task, record it.
python3 tools/ablation.py prepare --component diagnosing-superpowers --task t1 --rep 1
#    ... perform the task in the printed directory ...
bash eval/run-bench.sh record --task t1-bugfix --arm pack --rep 1 \
  --dir /tmp/ablation/diagnosing-superpowers/t1-bugfix/rep1 \
  --started <epoch> --ended <epoch> --rounds <n> --verify-attempts <n> \
  --outcome <pass|fail> --false-completion <0|1> --ablation diagnosing-superpowers
# 3. Report against the bare-arm thresholds
python3 tools/ablation.py report --component diagnosing-superpowers
```

Records land in `eval/results/ablation/` with an `"ablation"` field; they
never enter the three-arm matrix (`check-results.py` only globs the top
level of `eval/results/`).

## Reading a report

- **NO REGRESSION on these four tasks** → candidate for removal. The
  owner still decides: the four bench tasks do not exercise every skill,
  and a skill can be load-bearing for real work while invisible to the
  bench. Removal also means updating the guides, `skills-profiles.json`,
  and `skills-lock.json` in the same change.
- **REGRESSION** → keep. The report names the breached threshold.
- **BLOCKED at the gate** → pick another component or remove the
  template references first (a separate change, with its own review).
