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

- [ ] **F1 — Surface detection (in progress).** Deterministic probe chain:
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
- [ ] **F2 — Repo-side support for global registration.** deploy-agents gains a
  documented global-install path for the Antigravity hooks (or a Multi-Tool
  Deployment section): merge the `agent-harness-gate` group into
  `~/.gemini/config/hooks.json` preserving other groups, back up first, never
  overwrite blindly. Ships only after F1 shows which surface needs it.
- [ ] **F3 — Fallback if hooks never fire in the desktop app.** The gate CLI
  already works there as plain commands (observed). Remaining risk is silent
  non-compliance, so add a repo-side tripwire usable from any surface:
  `pass-gate.py audit` (read-only) that flags passing items whose evidence is
  stale or whose `feature_list.json` hash chain shows unlogged edits, plus a
  pre-push/CI re-check of the same invariants (CI half exists). Document the
  desktop app as "CLI-driven, hook-less; audit before trusting status".
- [ ] **F4 — IDE hardening (primary surface).** Two recorded residuals from
  the live run: (a) the IDE session's `start` produced no separate `started`
  event — confirm whether that is the agent's flow or an adapter gap, and
  pin it with a test either way; (b) re-run the four-event check after any
  agy major upgrade (version-drift watch, same rule as other hosts).
- [ ] **F5 — Records.** Matrix rows for IDE/desktop updated with F1's outcome;
  Multi-Tool Deployment guide gains a per-surface section (IDE: workspace
  hooks verified; desktop app: per F1/F3 outcome).

## Non-goals

- WorkBuddy stays owner-deferred; dsh stop steering stays provisional
  (unrelated tracks).
- No changes to gate rules themselves: every fix above is wiring, detection
  or audit — the Claude hook scripts remain the single source of truth.
