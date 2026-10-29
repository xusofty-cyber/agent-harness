# Phase 1 dogfood record

Date: 2026-10-28. Branch: `feat/phase0-v3`. Gate version: `gate/` as of
commit `56d3bb5` (dogfood 1) plus docs. Both runs used the gate as
shipped; no code was changed mid-run to make a run pass.

## Dogfood 1 — this repo (agent-harness itself)

Real change, not a fixture: migrate `docs/internal/SESSION_STATE.md`
from a long achievement log to the new ≤1-page breakpoint format
(item `p1-dogfood-session-state`).

| Step | Time (CST) | Result |
|---|---|---|
| Work starts; `pass-gate.py add` is missing, added first | 09:19:18 | `add` subcommand added (commit `41124f8`) — the gate could not have taken new items without it |
| Item started (`start`) | 09:19:40 | `in_progress`, event seq 1 |
| Fake pass planted by hand-editing `feature_list.json` (status `passing`, invented evidence, exit 0) | 09:19:44 | — |
| `python3 tests/repo_checks.py` (CI second check) | 09:19:44 | **Intercepted.** `gate:feature-list-valid` passed (the fake was well-formed), but `gate:evidence-matches-rerun` **FAIL** ("verification now exits 1") and `gate:events-log` **FAIL** ("passing without a verified event"). Repo checks overall FAIL |
| PreToolUse hook live: `Write` to `gate/feature_list.json` fed to `guard-feature-list.mjs` | 09:19:45 | **Denied**, exit 2, deny decision, logged as `direct_write_blocked` (event seq 2) |
| Tampered item manually restored to `in_progress`, evidence cleared | 09:19:49 | Manual repair — the tamper itself left no event (it went through the shell, not the Write tool). The CI failure above is the only record of it. Known limit, see gate/README.md |
| Real migration written (28 lines), `verify` | 09:20:05 | **PASS**, exit 0, evidence + event seq 3. Failing → passing chain complete |
| Handover test: fresh read of `SESSION_STATE.md` only, restate goal / in-progress / next / blocked, start next item, `check-clean` | 09:20:13–09:20:14 (~1 s) | Restated correctly; `check-clean` all 6 checks PASS (3a passed because the breakpoint file already named the next item in its Next section) |
| Rework found: the "In progress" line still named the just-verified item after it passed | 09:20:20 | Fixed with a session-boundary edit of `SESSION_STATE.md` (prose file, not gate state) |
| Committed | 09:20:25 | `56d3bb5` |

Rework total: ~1 min (tamper + restore) + one stale-line fix. No
rework on the gate code itself during the run.

## Dogfood 2 — second project (`/tmp/tinycalc`)

A real minimal project built for this run (not a fixture of the repo):
`calc.py`, a CLI calculator, plus `test_calc.py` (stdlib unittest).
Task: implement `subtract` (item `calc-subtract`, verification
`python3 -m unittest test_calc -v`).

| Step | Time (CST) | Result |
|---|---|---|
| `gate/init.template.sh --name tinycalc --verify "python3 -m unittest test_calc -v" --start "python3 calc.py add 2 3"` | 09:20:33 | **Smoke failed honestly, exit 1** — `subtract` raised `NotImplementedError`, so init refused to bless a broken project. Gate files were still created; the project was not marked good |
| `add` + `start` `calc-subtract` | 09:20:40 | `in_progress` |
| `verify` | 09:20:40 | **FAIL**, exit 1, status stayed `in_progress`, `verify_failed` event seq 4 |
| Fake pass planted by hand-edit; `check-clean` | 09:20:40 | **Intercepted.** Dimension 2 FAIL (tests genuinely fail) and **3b FAIL** ("`calc-subtract` (verification now exits 1)"). `check-clean` exit 1: "do not hand off yet" |
| `reopen --reason ...` | 09:20:40 | Back to `in_progress`, evidence cleared, event seq 5 |
| `subtract` implemented (`return a - b`), `verify` | 09:20:43 | **PASS**, exit 0, event seq 6. `python3 calc.py subtract 5 3` → `2.0` |
| Handover test: fresh read of `SESSION_STATE.md` only, `status`, `check-clean` | 09:20:46–09:20:47 (~1 s) | All configured dimensions PASS (build SKIP — no build command configured); 3b re-verified the passing item |

Rework total: none on the project code beyond the planned implement step;
the intercept + reopen cost ~1 min.

## What the two runs prove (and what they do not)

Proven:

- A real feature goes failing → passing through the gate in both projects.
- A fake pass is caught twice, by two different legs: CI §3k
  (dogfood 1) and `check-clean` 3b (dogfood 2). The PreToolUse hook
  denies a direct Write and logs it.
- A breakpoint file lets a fresh read restate goal / in-progress / next /
  blocked and continue in ~1 s (both runs; 5-minute budget, not close).
- `init.template.sh` refuses a broken project at smoke time instead of
  scaffolding success around it.

Not proven (honest limits):

- Both handovers were simulated by the same operator doing a fresh read,
  not by an independent second person or a new session. The 5-minute
  test passed, but with n=1 and a friendly reader.
- A tamper through the shell leaves no event; only CI catches it, and
  only at CI time. If a project never runs CI, leg 2 never fires.
- `check-clean` 3b re-runs verification commands; a slow/flaky command
  makes the handover check slow/flaky too.
- `pass-gate.py init` falls back to an empty list when
  `templates/feature_list.template.json` is absent (as in a deployed
  target); `add` is then the only way to create items. Intended, but
  worth knowing.
- Cosmetic nit: `status` prints "1 items" instead of "1 item".

## Timings summary

- Dogfood 1 (repo migration): 09:19:18 → 09:20:25, ~7 min including the
  intercept experiment and one rework fix.
- Dogfood 2 (tinycalc): 09:20:33 → 09:20:47, ~1 min for the full
  failing → passing chain once the project existed.
- Handover (both): ~1 s of reading each, vs the 5-minute budget.
