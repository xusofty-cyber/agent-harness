# Antigravity two-surface hardening (IDE + desktop app as primary surfaces)

Status: active — opened 2026-11-06 after the bridge live-verification round.
Context: the owner ruled (2026-11-06) that day-to-day work will run mainly in
**Antigravity IDE** and the **Antigravity desktop app**. IDE is `live-verified`
(all four hook events incl. a Stop block). The desktop app is not: a smoke run
the same day showed the agent driving the gate CLI correctly while
`.agents/hooks.json` produced no observable hook effects (matrix scope note).

Official position (antigravity.google/docs/hooks, re-checked 2026-11-06):
hooks are configured at workspace `.agents/hooks.json` or global
`~/.gemini/config/hooks.json`, are viewable/toggleable in the app under
Settings > Customizations > Hooks, and the five events (PreToolUse,
PostToolUse, PreInvocation, PostInvocation, Stop) are shared by app, IDE
and CLI. So the desktop gap is most likely *wiring*, not a missing feature.

## Fix list

- [x] **F1 — Surface detection (done 2026-11-06).** Desktop app DOES fire command hooks: a probe group (absolute-path command, log-only) fired 17+ times across two fresh desktop sessions. The gate group stayed silent for a different reason — see F2. Morning smoke explained too: that session predated any global registration and workspace loading did not occur for it. Deterministic probe chain:
  1. Global registration: gate hooks.json also installed at
     `~/.gemini/config/hooks.json` on the verification host, plus a
     `hook-probe` group whose PreToolUse handler only logs its invocation to
     `~/hook-probe.log` and returns `{"decision": "allow"}` (zero behavioral
     impact). Done 2026-11-06.
  2. Desktop app: one minimal tool call. Probe fires → the app loads global
     hooks; the gate chain was a workspace-loading issue and global
     registration is the fix. Probe silent → the app does not fire command
     hooks in this build; F3 becomes the plan.
  3. IDE with the same workspace: confirm the probe also fires there
     (workspace-vs-global double coverage check).
- [x] **F2 — Repo-side support for global registration (done 2026-11-06).** Root cause: under global registration, hook commands do not run with cwd=.agents, so the template's relative `node hooks/...` commands fail silently. Fix pattern proven on the host (scripts copied to ~/.gemini/config/hooks/, group commands rewritten to absolute paths): the desktop final check then produced a Stop block (event #14) and a verified pass (#15). Productized in deploy-agents.sh --global step B2: copies scripts, backs up, merges the group with absolute paths, preserves other groups. deploy-agents gains a
  documented global-install path for the Antigravity hooks (or a Multi-Tool
  Deployment section): merge the `agent-harness-gate` group into
  `~/.gemini/config/hooks.json` preserving other groups, back up first, never
  overwrite blindly. Ships only after F1 shows which surface needs it.
- [x] **F3 — Fallback if hooks never fire in the desktop app. CLOSED as unnecessary** — F1 proved hooks fire; the gap was command-path wiring, fixed by F2. The audit-tripwire idea stays a backlog note only. The gate CLI
  already works there as plain commands (observed). Remaining risk is silent
  non-compliance, so add a repo-side tripwire usable from any surface:
  `pass-gate.py audit` (read-only) that flags passing items whose evidence is
  stale or whose `feature_list.json` hash chain shows unlogged edits, plus a
  pre-push/CI re-check of the same invariants (CI half exists). Document the
  desktop app as "CLI-driven, hook-less; audit before trusting status".
- [ ] **F4 — IDE hardening (primary surface).** (Desktop half now closed by F1/F2; the IDE residuals below remain.) Two recorded residuals from
  the live run: (a) the IDE session's `start` produced no separate `started`
  event — **RESOLVED 2026-11-06: neither an adapter gap nor an agent-flow
  quirk.** No bridge adapter (Antigravity, dsh, Claude) ever synthesizes
  gate events — `started` is written by `pass-gate.py start` itself, which
  the IDE session never invoked as a discrete step (it entered via
  `reopen`, whose `reopened` event #6 anchored the cycle; the Stop pair
  #7/#10 bracketed it). Invariant pinned by
  `tests/pass_gate_deps_test.py`-adjacent coverage in
  `tests/antigravity-hooks.test.mjs` (no adapter emits gate events) plus
  the CLI/desktop live runs, where discrete `start` invocations DID
  produce `started` events through the same code path; (b) re-run the four-event check after any
  agy major upgrade (version-drift watch, same rule as other hosts).
- [x] **F5 — Records (done 2026-11-06 for the desktop outcome; guide section lands with F4).** Matrix scope note rewritten with the full arc; tracker row updated. Matrix rows for IDE/desktop updated with F1's outcome;
  Multi-Tool Deployment guide gains a per-surface section (IDE: workspace
  hooks verified; desktop app: per F1/F3 outcome).

## Non-goals

- WorkBuddy stays owner-deferred; dsh stop steering stays provisional
  (unrelated tracks).
- No changes to gate rules themselves: every fix above is wiring, detection
  or audit — the Claude hook scripts remain the single source of truth.
