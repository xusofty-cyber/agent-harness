# Release v0.7.0 — release notes

> Cut 2026-11-06 from main: CHANGELOG `[Unreleased]` renamed to
> `## [0.7.0] - 2026-11-06`, `VERSION` written as 0.7.0,
> `tools/check-release.py` re-run green, tag `v0.7.0` on the cut
> commit `0ea0c65`; GitHub Release published from this note
> (https://github.com/xusofty-cyber/agent-harness/releases/tag/v0.7.0,
> marked Latest).
>
> Numbers below were re-verified on 2026-11-06 (not copied from
> older records): repo_checks all pass (1 environment-gated skip:
> `eval:bench-smoke-passes`); Python unit suite 125/125; all eight
> `tests/*.test.mjs` hook suites pass; `sync-skills --check
> --strict` all in-sync; `check-release.py` exit 0 (VERSION 0.6.0,
> lock 41 entries); gate `check-clean` all configured dimensions
> pass; i18n spot-check 5 passed with 0 stale rows; deploy smoke
> covered by the integration-level gate item `e2e-deploy-smoke`
> (live evidence in the gate log) and by CI.

## What v0.7.0 is

The first release after the full Harness-Engineering course pass:
the bridge layer is live-verified on every host surface the owner
uses, the gate grows dependency modeling and a two-track state
model, CI has a real all-green record, and the ZH-TW documentation
is back in sync.

## Highlights

- **Bridges live-verified (2026-11-06)**: Claude Code, Antigravity
  CLI, Antigravity IDE, Antigravity desktop app (global-registration
  route, step B2) and dsh all stand `live-verified` in
  `docs/internal/host-verification-matrix.md`. WorkBuddy remains
  `protocol-only` by owner ruling (deferred, not chased).
- **D72 — feature dependencies, graded**: `depends_on` (existence,
  self-dependency and cycle checks) + `out_of_scope` in the gate
  schema; `start` hard-blocks on unmet dependencies by default and
  `--override-deps "<reason>"` overrides with a hash-chained
  `dependency_override` event. Criterion set by the owner
  ("flexible"), mechanism chosen by the maintainer.
- **D73 — two-track state**: `docs/internal/SESSION_NOTES.md`
  (non-authoritative working notes) alongside the Track-A
  `SESSION_STATE.md` breakpoint.
- **First real CI, all green**: run #299 (2026-11-06), both jobs,
  all steps — lint pinned to markdownlint-cli 0.32.2 with the
  rationale recorded; the Windows ps1 deployment smoke discharged
  its long-standing review-only debt.
- **QUALITY_SCORE re-issued**: bridges 4 → 7 on the live-verified
  evidence; evaluation stays 4 pending the Round 6 live
  adjudication (D28 calibration, evaluator scores sealed).
- **Verification-strength mix**: integration-level gate item
  `e2e-deploy-smoke` (real deploy → gate lifecycle in a scratch
  project); mix now assert 5 / unit 1 / integration 1.
- **ZH-TW regeneration**: all five stale rows discharged; the
  Multi-Tool guide gains §4.5 Per-Surface Hook Wiring & Isolation
  in EN, ZH and ZH-TW.
- **Adapter hardening**: Antigravity adapters accept the flat
  Claude-style payload shape (a flat payload previously degraded
  silently to allow); pinned by test.
- **F4(a) invariant**: adapters never synthesize gate lifecycle
  events — `started` is written by pass-gate alone; pinned by test.

## Honest gaps (not done / not claimed)

- Desktop-app PreToolUse deny: **captured end-to-end 2026-11-06**
  — a live desktop session's `edit_file` call against
  `gate/feature_list.json` was denied by the pre-tool hook (the
  denial text is recorded verbatim in the session transcript) and
  the file stayed unmodified; the mechanism had additionally been
  proven the same day through the globally installed adapter
  (deny + `direct_write_blocked` event #16 on the host).
- dsh Stop steering: **proven live 2026-11-06** in a dedicated
  provocation run (DeepSeek official API, `deepseek-flash`): the
  stop was blocked, the steering text reached the model, the
  model complied instead of ending, gate event #8
  (`stop_blocked`) landed, and the item stayed `in_progress`.
  Residual honesty note: after the steered turn, the run ends in
  a host-side dsh error (`Cannot read properties of undefined
  (reading 'kind')`, the known rc.5 waterfall fragility) — the
  steering mechanism is proven, the host's post-steering turn
  termination is not clean.
- D28 evaluator rubric remains advisory-only; Round 6 adjudication
  by the owner is pending. No claim that the gate reduces false
  completions (D69 stands).
- `deploy-agents.ps1` interactive/full paths are still not run on
  a real Windows host (CI covers analyzer + deployment smoke).
