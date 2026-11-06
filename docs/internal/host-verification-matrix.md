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

## Matrix (as of 2026-11-06: Antigravity CLI + IDE + dsh live-verified; earlier rows 2026-10-30, v0.4.0 + v0.4.1 convergence round)

| Host | Tier | Evidence | Owed before moving up |
|---|---|---|---|
| Claude Code | `live-verified` | Five hook events wired in `.claude/settings.json`; 168 hook tests pass locally (hooks 90 + gate 11 + lifecycle 12 + antigravity 20 + workbuddy 16 + dsh 20, all protocol suites included); Phase 1 dogfood intercepted a planted fake pass live | — |
| Antigravity CLI (agy) | `live-verified` | Full gate flow run live on the user's host, 2026-11-06, **agy 1.2.14** (project deployed fresh from main @ 962d261): SessionStart injected; agy ran start → verify (PASS, real evidence written; events #3/#4) → check-clean (all dimensions pass). The owed instrumented re-run is now discharged: agy's `edit_file` attempt on `gate/feature_list.json` was denied by the PreToolUse hook with its own message, **and the deny itself was captured in the gate event log** (event #5 `guard-feature-list direct_write_blocked`: "Write to …/gate/feature_list.json denied"); the item stayed `passing` with evidence and zero forged content (sha256 recorded). Supersedes the 2026-10-30 partial-live record (agy 1.4.10 retest; `edit_file` bypass found live, fix landed on main since) | — |
| Antigravity IDE | `live-verified` | One full live run of all four hook events on the user's host, 2026-11-06 (**agy 1.2.14**, IDE running the same deployed project @ 962d261; gate event log is the record): SessionStart preceded the session; Stop **blocked** an in_progress finish (event #7 `antigravity-stop stop_blocked`, decision=continue returned) and allowed the finish after verification (event #10 `stop_allowed_hook_active`, the documented deadlock guard); verify wrote real evidence (#8); PreToolUse denied the `edit_file` forgery on `feature_list.json` (#9 `guard-feature-list direct_write_blocked`, zero forged content). Nuance resolved (F4a, 2026-11-06): no adapter synthesizes gate events — `started` is written by `pass-gate.py start` itself; the IDE session entered via `reopen` (event #6) and never invoked a discrete start, so no `started` event was owed; the cycle was anchored by the reopen (#6) and the Stop pair (#7/#10) | — |

> **Scope note — the Antigravity desktop app (resolved 2026-11-06).** The desktop app is **not** a separate
> agent: it loads the same hooks (official docs: workspace `.agents/hooks.json` or global
> `~/.gemini/config/hooks.json`, five shared events). But it needed its own verification, and the arc is
> recorded because each step corrected the last: (1) a morning smoke run showed the agent driving the gate CLI
> with zero hook effects → first read "ungated"; (2) an instrumented probe (log-only group, absolute-path
> command) fired 17+ times in fresh desktop sessions → the app DOES fire command hooks from the global file;
> (3) the gate group had stayed silent because its commands are relative (`node hooks/...`), valid only when
> the hook cwd is the workspace `.agents/` (CLI/IDE workspace mode) — under global registration they fail
> silently. With the group installed globally using absolute paths and the scripts copied to
> `~/.gemini/config/hooks/`, a desktop final check produced a **Stop block** (gate event #14
> `antigravity-stop stop_blocked`) and a verified pass (#15) — **the desktop app stands `live-verified` on
> the global-registration route**. One honest gap: the final check's edit-tool forgery produced no deny event
> (the first attempt did not go through as a write; no direct_write_blocked was logged), so PreToolUse deny
> on the desktop is supported by the probe + Stop evidence rather than a captured deny from a live
> model session. The mechanism itself was proven same-day: an edit_file payload aimed at
> `gate/feature_list.json`, run through the globally installed adapter on the host, returned `deny`
> and logged `direct_write_blocked` (gate event #16, global registration chain); the live re-run
> session used its shell for the status step and never issued the edit call, so the model-issued
> end-to-end capture is the one remaining gap — a session-behavior gap, not an adapter gap. `deploy-agents.sh
> --global` now performs this installation (step B2).
| WorkBuddy | `protocol-only` | `tests/workbuddy-hooks.test.mjs` 16 pass against *assumed* Claude-shaped payloads. **Owner ruling 2026-11-06: live verification deferred — do not chase.** The 5.6.2 Linux build is installed on the Instabox test box (official .deb, hash-verified), so resuming needs only an account sign-in + the payload/settings check | One live run after an account sign-in on an installed build, whenever the owner re-opens it |
| DeepSeek Harness (dsh) | `live-verified` | One full live run on the user's host, 2026-11-06 (**dsh 0.2.1-rc.5**, headless profile, model `IFM/K2-Horizon-375B-A23B` via a custom OpenAI-compatible provider; project deployed from main @ 1bf4c72 plus the contract fixes below): start/verify wrote real evidence (gate events #3/#4), the `feature_list.json` forgery was denied **twice** with both denies in the hash-chained log (#5/#6), `check-clean` passed, item ends `[passing]` with evidence, zero forged content. Three contract fixes the run forced are now in the plugin and pinned by its 20 unit tests: (1) waterfall handlers never propagate an `undefined` tail (dsh reads `.kind` on it and crashes); (2) `ctx.tools.guard` is absent in rc.5 — pre-execute is the only gate, as designed; (3) **creation-time resume injection is disabled on dsh**: a synchronous `agent.inject` inside the serial `agent/created` chain crashes the run inside dsh's admission path, so the resume is surfaced on stderr instead — a recorded limitation, not a silent gap. Stop enforcement remains provisional: the `agent/turn-stopping` handler ran in this session, but no in_progress stop was provoked, so the steering path is still unproven live | — |
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
