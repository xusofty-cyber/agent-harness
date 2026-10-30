# Host verification matrix (v0.4.1)

One place that answers, per host: **how strongly is the gate actually
verified there?** The README support table links here. A host may only
move up a tier on recorded evidence, never on protocol tests alone.

## Tiers

| Tier | Meaning |
|---|---|
| `live-verified` | A full gate flow (add → start → verify → Stop block) has been run on the real host/client and the run is recorded. |
| `partial-live` | Some live evidence exists (e.g. one real CLI run that found and fixed a bug), but the full gate flow has not been run live, or a surface (IDE vs CLI) is untested. |
| `protocol-only` | Adapters pass protocol-level tests with mocked payloads; no live host run. Payload shapes are assumed, not confirmed. |
| `config-only` | No gate enforcement on this host: rules/files are deployed, the gate is manual discipline plus the host-independent CI/pre-push backstop. |

## Matrix (as of 2026-10-30, v0.4.0 + v0.4.1 convergence round)

| Host | Tier | Evidence | Owed before moving up |
|---|---|---|---|
| Claude Code | `live-verified` | Five hook events wired in `.claude/settings.json`; 168 hook tests pass locally (hooks 90 + gate 11 + lifecycle 12 + antigravity 20 + workbuddy 16 + dsh 19, all protocol suites included); Phase 1 dogfood intercepted a planted fake pass live | — |
| Antigravity CLI (agy) | `partial-live` | Full gate flow run live on agy 1.4.10, 2026-10-30 (retest record: `~/workspace/agy-gate-retest/RETEST-2026-10-30.md`): SessionStart resume injected verbatim; Stop blocked an in_progress stop once then allowed per deadlock guard (events seq 4 `stop_allowed_hook_active`); verify wrote real evidence; PreToolUse denied a `write_file` overwrite of `feature_list.json`. BUT the same run proved a live bypass: agy's `edit_file` tool was in neither the hooks.json matcher nor the adapter WRITE_TOOLS set, and a direct edit forged `passing` with empty evidence (tampered file preserved). The `edit_file` coverage fix (matcher + WRITE_TOOLS + 2 pinning tests) landed on feat/v0.5.1 the same day | Re-run the retest's session-1 direct-edit step against the fixed adapter and observe the deny; only then does this row move to `live-verified` |
| Antigravity IDE | `protocol-only` | Adapters shared with CLI; IDE cwd behaviour never observed live | One live IDE run of the four hook events |
| WorkBuddy | `protocol-only` | `tests/workbuddy-hooks.test.mjs` 16 pass against *assumed* Claude-shaped payloads | Verify payload shape and settings location against official docs **and** one installed WorkBuddy build |
| DeepSeek Harness (dsh) | `protocol-only` | `tests/dsh-gate.test.mjs` 19 pass against a mock Cordis context; the plugin API surface is unverified against official documentation; `tsc --noEmit` discharged 2026-10-30 in the v0.4.1 round (TypeScript 5.x, exit 0, no errors) | One live dsh run with the plugin activated; official-doc re-check of every event name and steering surface used |
| Codex / Copilot / Zed / others reading `AGENTS.md` | `config-only` | Native `AGENTS.md` loading; no hooks | Nothing owed — the tier is the honest ceiling unless a host gains a hook surface |
| Host-independent (any git project) | `live-verified` (as a checker) | `templates/pre-push-gate/` + `templates/ci-gate-check.yml` re-run every `passing` item's verification (mirrors repo_checks §3k, which runs in this repo's CI) | Server-side branch protection is the deployer's side, not this repo's |

## Rules

1. README's Enforcement column must not claim more than this matrix:
   anything below `live-verified` is worded "deployed, not
   live-verified" there.
2. When a live run happens, record it here with date, host version,
   and what flowed (link the session/dogfood note), then update the
   tier in the same change.
3. A tier never goes down silently: if a live run *fails*, record the
   failure here first, then decide.
