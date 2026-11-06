# SESSION_STATE — session breakpoint

> **Updated**: 2026-11-06 | **Project**: agent-harness
> **Feature list**: `gate/feature_list.json` (status via `python3 gate/pass-gate.py status`)
> **Rule**: one page max (≤60 lines), **Track-A content only**
> (breakpoint facts; working notes go to `SESSION_NOTES.md`).
> Finished work goes to `CHANGELOG.md`.

## Goal

- Keep the gate workflow on main honest by dogfooding it on this
  repo itself. Night-dogfood round closed: items
  `p1-dogfood-session-state` and `night-dogfood-session-state`
  passing; on 2026-11-06 all four bridges reached `live-verified`.

## In progress

- none. v0.7.0 released 2026-11-06; full record: CHANGELOG
  `[0.7.0]` and `docs/exec-plans/completed/release-v0.7.0.md`.

## Next

- [ ] Round 6 adjudication (owner): evaluator scores sealed in
  `eval/calibration-round6-evaluator-scores.md`; D28 stays
  advisory-only until the owner rules.
- [ ] Skill-usage telemetry review + monthly ablation
  (due 2026-11-28)
- [ ] Deferred by owner: WorkBuddy live run; ps1 full-path
  Windows run (tracked in `docs/exec-plans/tech-debt-tracker.md`)

## Blocked

- none

## Last verification

- 2026-11-06: **v0.7.0 released** — tag `v0.7.0` on main
  `0ea0c65`, GitHub Release published (Latest). Final residuals
  discharged the same day: desktop PreToolUse deny captured
  end-to-end (host transcript), dsh Stop steering proven live
  (gate event #8, DeepSeek `deepseek-flash` run). Pre-cut
  verification: repo_checks pass, unit suite 125/125, all hook
  suites pass, check-release exit 0, CI #299 all-green.
