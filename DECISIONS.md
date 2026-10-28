# Decisions — agent-harness

Written decision records for the Phase 0 consensus (v3, 2026-10-28).
Each entry states the decision, the rationale, and the rejected
alternative. Dates are the decision dates; the Phase 0 items were all
decided 2026-10-28 during the v3 consensus review. Unresolved items
(N1–N5) are recommendations, not decisions — they are settled at the
Phase 0 decision meeting.

## D1 — Core gate is self-owned and host-agnostic; Comet is an adapter

- **Decision:** the verification gate built from Phase 1 on is owned by
  this repo and works the same on every host (Claude Code, Codex,
  Antigravity, Copilot, …). Comet is demoted to an optional adapter /
  advanced runtime, not the harness itself.
- **Rationale:** the repo's value is portable rules + skills. Tying the
  gate to one vendor's CLI would make the gate unusable everywhere else
  and hand the project's core to an upstream the project does not control.
- **Rejected:** "Comet is the harness" (build the gate on the comet CLI
  and its state files) — rejected because it makes every non-Comet host a
  second-class citizen and couples the roadmap to comet releases.
- **Date:** 2026-10-28.

## D2 — Pilot on this repo's own small changes (dogfood)

- **Decision:** Phase 1 is piloted on this repository's own small,
  real changes (doc edits, skill additions, template fixes) before any
  external project is asked to use the gate.
- **Rationale:** the repo is the cheapest, most honest test subject — its
  changes are small, its history is the maintainer's own, and a broken
  gate hurts nobody else.
- **Rejected:** piloting on a large external project first (too much
  blast radius, too slow a feedback loop) and piloting on synthetic
  fixtures only (they never surprise you the way real edits do).
- **Date:** 2026-10-28.

## D3 — Freeze non-EN/ZH docs; do not delete FR/DE templates yet

- **Decision:** from Phase 0 on, user-facing text changes go to EN + ZH
  only. The ZH-TW / FR / DE READMEs, guides, and templates stay as-is
  (frozen, not deleted) until a decision is made about their future.
- **Rationale:** five-language maintenance is the main multiplier on
  every doc change (see `docs/internal/users-and-change-cost.md`); the
  project cannot afford it at the current pace, but deleting the
  translations outright would strand existing users.
- **Rejected:** deleting FR/DE now (too destructive without user input)
  and continuing five-language updates (unaffordable at Phase 0 pace).
- **Date:** 2026-10-28.

## D4 — `archive_confirmation` defaults to `required` (template only)

- **Decision:** `templates/comet.config.yaml` changes
  `archive_confirmation` from `automatic` to `required`. Only the
  template default changes; deployed projects' own `.comet/config.yaml`
  files are untouched.
- **Rationale:** automatic archiving after checks pass silently closes a
  phase; requiring explicit confirmation keeps the human in the loop at
  the one irreversible step (archiving). A template default is cheap to
  change back per project.
- **Rejected:** changing deployed configs too (out of scope for this repo
  — it does not own other projects' files) and leaving `automatic`
  (keeps the silent-archive footgun).
- **Date:** 2026-10-28. Implemented in Phase 0 commit `5a45ed6`.

## N1 — Gate state in git; Comet local state not in git (recommendation)

- **Recommendation:** the self-owned gate's state (feature lists, evidence)
  is committed to git; Comet's local runtime state stays out of git
  (already the case via `.gitignore`: `.comet/*` ignored except the config
  template, which no longer lives at the repo root after Phase 0-7).
- **Rationale:** gate evidence must be reviewable in a PR; local runtime
  state contains machine paths and per-machine noise.
- **Caveat:** whether Comet state files actually contain machine paths was
  never measured (see U2) — re-check during Phase 1 dogfooding.
- **Status:** unresolved; decide at the Phase 0 decision meeting.

## N3 — Gate directory is named `gate/` (recommendation)

- **Recommendation:** the Phase 1 gate code lives in `gate/`, not
  `kernel/`.
- **Rationale:** `gate/` says what it does (a verification gate);
  `kernel/` over-promises a runtime the project explicitly decided not to
  build (see D1 / K3).
- **Rejected alternative:** `kernel/` (implies an orchestration runtime).
- **Status:** unresolved; decide at the Phase 0 decision meeting.

## N4 — Schedule is 8 weeks (recommendation)

- **Recommendation:** the v3 route runs 8 weeks in 6 phases, not 6.
- **Rationale:** the 6-week variant compresses the gate + dogfood +
  benchmark work into a span with no slack for the maintainer's real
  schedule; 8 weeks keeps the same scope with a realistic buffer.
- **Status:** unresolved; decide at the Phase 0 decision meeting.

## N5 — Symlink vs duplicate for `engineering.md` (open)

- **Issue:** `.agents/rules/engineering.md` is a symlink to
  `engineering-spec.md`. It breaks under Windows / zip download; no check
  detects a broken link (see CONTRIBUTING.md, "Symlink risk").
- **Trade-off:** replacing the symlink with a real duplicate file fixes
  the breakage but reintroduces drift between the two copies; keeping the
  symlink keeps one source of truth but keeps the breakage risk.
- **Status:** open; no recommendation yet. Revisit when the rule files
  are next restructured.

## Open questions (from v3, not decisions)

- **U1 — No usage data.** The user portrait
  (`docs/internal/users-and-change-cost.md`) is provisional; the core
  ≤10 skill list cannot be set from data yet. Re-check after Phase 3
  bench data.
- **U2 — Comet state contents unmeasured.** See N1 caveat.
- **U3 — sh/ps1 dual-implementation endgame.** Settled by D17 (Phase 4):
  keep dual, sh-first, review 2027-04-28.

## D5 — Gate code lives in `gate/`, not `kernel/` (Phase 1; settles N3)

- **Decision:** the Phase 1 gate code lives in `gate/`:
  `gate/feature_list.schema.json`, `gate/pass-gate.py`,
  `gate/events.jsonl`, `gate/init.template.sh`.
- **Rationale:** `pass-gate.py` is a verification script, not a runtime
  kernel; the name must match the substance (v3 §3, N3).
- **Rejected:** `kernel/` — kept the "name is wrong, judgement follows
  the name" mistake the v3 consensus explicitly called out.
- **Date:** 2026-10-28.

## D6 — Human override is logged and visible, never silent (Phase 1)

- **Decision:** a human may mark an item passing without a passing run,
  but only through `pass-gate.py override --reason` (recorded in
  `evidence.override` with exit_code −1 and in `gate/events.jsonl`), or
  stop a session with in_progress items only through the Stop hook's
  `GATE_ALLOW_STOP=1` + non-empty `GATE_STOP_REASON` (recorded as a
  `stop_override` event). An override without a reason is not an
  override.
- **Rationale:** the gate must never deadlock a session, but an
  unlogged escape hatch is the same as no gate — a reviewer must be
  able to tell an override from a passing run at a glance.
- **Rejected:** silent override flags, and no override at all (the Stop
  hook would lock a session mid-item with no way out).
- **Date:** 2026-10-28.

## D7 — Clean-state is five dimensions; progress counts twice (Phase 1)

- **Decision:** `pass-gate.py check-clean` checks five dimensions:
  build, tests, progress, temp artefacts, standard start path. The
  progress dimension has two checks: (3a) narrative progress in
  `SESSION_STATE.md` names the in_progress item, and (3b) the feature
  list is truthful — every `passing` item's verification still exits 0
  on re-run. A dimension with no command configured reports SKIP, never
  PASS.
- **Rationale:** narrative alone can lie and the list alone can go
  stale; the pair catches both (v3 §4.1 clean-state ruling).
- **Rejected:** six separate dimensions (double-counts progress) and
  treating unconfigured dimensions as passing (fake green).
- **Date:** 2026-10-28.

## D8 — Gate state is committed to git; Comet local state is not (Phase 1; settles N1)

- **Decision:** the self-owned gate's state (`gate/feature_list.json`,
  `gate/events.jsonl`, `gate/clean-state.json`) is committed to git.
  Comet's local runtime state stays out of git (already the case via
  `.gitignore`).
- **Rationale:** gate evidence must be reviewable in a PR; the event
  log's tamper visibility depends on git history. Comet state contains
  machine paths and per-machine noise.
- **Caveat:** whether Comet state files actually contain machine paths
  was never measured (U2) — the Phase 1 dogfood did not run Comet, so
  this stays open for Phase 1 dogfooding on a Comet-using project.
- **Update (Phase 2, measured 2026-10-28):** U2 is now settled — see
  `docs/internal/phase2-verification.md` (comet interrupt-recovery
  test). The Native change state
  (`docs/comet/changes/<name>/comet-state.yaml`) uses relative refs
  only; `.comet/current-change.json` carries no machine paths; the
  `~/.comet/workspaces/<hash>/...` runtime directory named in comet's
  JSON envelope is not materialised on disk (lazy). No machine-path
  contamination was observed in any file a project would commit, which
  confirms the "comet state stays out of git" half of this decision.
  The decision itself is unchanged.
- **Date:** 2026-10-28.

## D9 — Comet is pinned to the version measured at implementation time (Phase 2, 2-2a)

- **Decision:** the pinned Comet version is the one measured at
  implementation time: `npm view @rpamis/comet version` → **0.5.1** on
  2026-10-28 (git tag 0.5.1 = the repo HEAD commit). The pin lives only
  in machine-read files: `skills-lock.json` (`npmVersion` /
  `pinnedCommit` / `pinnedAt` / `pinnedFrom`), `deploy-agents.sh`
  (`COMET_NPM_VERSION`), `deploy-agents.ps1`
  (`$script:CometNpmVersion`). `tools/check-comet.py` is the runtime
  gate: installed `comet --version` must equal the pin and the template
  must declare `schema: comet.project.v1`. Guide prose keeps the
  unversioned `npm install -g @rpamis/comet` command intentionally —
  human instructions, not machine-executed paths.
- **Rationale:** a version in prose rots; a version in machine-read
  files is checkable (`tests/repo_checks.py` §3m). No version number
  appears in any plan document.
- **Rejected:** hardcoding a version in the plan docs, and leaving the
  install unpinned.
- **Date:** 2026-10-28.

## D10 — Ghost lock entries are annotated, not deleted (Phase 2, 2-2c)

- **Decision:** the lock entries `openspec` and `superpowers` (suite
  level, no directory) get `"meta": true` + a note, and stay in
  `skills-lock.json`. Consumers derive the meta set from the marker,
  not from hardcoded names (`tools/count-skills.py`,
  `tests/repo_checks.py` §3b2/§5, `tools/sync-skills.py`
  `external_skills()` skips `meta` entries).
- **Rationale:** deleting would lose `pinnedCommit` provenance for
  suite-level pins; annotation keeps the pin while making the
  non-deployable nature explicit. The lock-hash refresh was a verified
  no-op: every `computedHash` already matched the current SHA256 of the
  vendored files (STALE: []).
- **Rejected:** deleting the two entries (provenance loss).
- **Date:** 2026-10-28.

## D11 — Guard hardening is graded, never blanket fail-closed (Phase 2, 2-4)

- **Decision:** `guard.mjs` expands command substitution
  (`$(...)` / backticks) that resolves to git (`which` /
  `command -v` / `type [-p]` git, paths ending in `/git`) and
  `eval` / `sh -c` indirection, recursively with a depth limit of 3 —
  beyond the limit it warns and stops expanding. Stdin parse failures
  stay fail-open (exit 0) but are now logged to stderr; the same
  one-line pattern was applied to `guard-write.mjs`,
  `guard-feature-list.mjs` and `stop-gate.mjs`. Known remaining gap:
  `xargs` / `find -exec` indirection is not expanded.
- **Rationale:** a blanket fail-closed would wedge sessions on
  malformed input; graded handling raises the bypass cost while
  keeping the hook usable. Fourteen new tests pin both the blocked
  cases and the must-stay-allowed cases (e.g. `echo $(git rev-parse
  HEAD)`, `x=$(which git) push --force`).
- **Rejected:** blanket fail-closed, and leaving the `$(which git)`
  bypass open.
- **Date:** 2026-10-28.

## D12 — Cost ledger is graded proxy metrics; no auto-stop, no unified token ledger (Phase 2, 2-3/2-5)

- **Decision:** the ledger records deterministic proxy metrics only:
  tool calls (PostToolUse hook → `gate/cost-ledger.jsonl`) and one
  stage event per pipeline run (only when the target has a `gate/`).
  Budget caps live in `gate/cost-budget.json` (per-day: runs, tool
  calls, verify failures, overrides; per-stage duration cap).
  `check-budget` exits 1 over budget, prints the exceeded limits to
  stderr, and records one deduped `budget_exceeded` event in
  `gate/events.jsonl` — it **never auto-stops a run**. The unified
  token ledger stays deferred: no host exposes a programmatic token
  API (inventory in `docs/internal/token-adapters.md`).
  `gate/cost-ledger.jsonl` is local telemetry (gitignored); the budget
  file is policy (committed).
- **Rationale:** proxy metrics are measurable today; a token number
  without a source would be invented. Auto-stop waits until budget
  semantics are explicit.
- **Rejected:** auto-stop before budget semantics are explicit, and a
  token ledger built on dashboard scraping.
- **Date:** 2026-10-28.

## D13 — PowerShell installer caveats, recorded honestly (Phase 2, 2-2b)

- **Decision:** codegraph's PowerShell installer is hash-verified
  (`Get-FileHash` against the lock's `installerSha256Ps1`); rtk's
  PowerShell install stays `winget install rtk-ai.rtk` — winget offers
  no git-commit pin, so the asymmetry is recorded, not hidden. The
  `ocr` skill's `npm install -g @alibaba-group/open-code-review`
  remains unpinned (out of scope for Phase 2, known gap).
- **Rationale:** record the platform asymmetry honestly rather than
  claiming full parity where the platform offers none.
- **Date:** 2026-10-28.

## D14 — Benchmarks measure our own runs only; thresholds come from variance (Phase 3)

- **Decision:** the benchmark (`eval/`) runs 4 fixed tasks (T1 bugfix, T2
  single feature, T3 cross-file rename, T4 docs+code sync) on the tinycalc
  fixture at fixed start commit
  `2e583970fb952158ad83617fe436534abd38295d`, in three arms (bare / pack /
  gate) with P01 English independent-directory isolation, ≥3 reps per task,
  reporting median + distribution. Thresholds are derived from the measured
  baseline variance with a stated formula (duration red-line = median +
  2×(max − median); rounds red-line = max + 2; completion floor 11/12 per
  12-run window; any false completion is a red-line breach). Unmeasured
  cells are marked **unmeasured**; upstream token claims are not quoted in
  our reports at all (not even as disclaimers — `eval/check-results.py`
  enforces this).
- **Rationale:** D2's correction stands — a threshold without a measured
  baseline is invented. With n=3 the thresholds are provisional lower
  bounds and must be re-derived after the full 36-run matrix.
- **Rejected:** inventing a "completion −10%" red line; quoting upstream
  numbers as our results; single-run conclusions.
- **Date:** 2026-10-28.

## D15 — Rubric is six-dimensional and calibrated, not yet stable (Phase 3)

- **Decision:** one evaluator rubric (`eval/rubric.md`), six dimensions
  (correctness, verification, scope discipline, reliability,
  maintainability, handover readiness), each 0–2, verdict Accept / Revise /
  Block (any 0 → Block; total < 9 → Revise; else Accept). Verification
  requires re-running the acceptance command, never trusting the agent's
  claim. Calibrated in 4 rounds against recorded outcomes (0 verdict
  divergences, 1 wording change: the re-run rule) — see
  `eval/calibration.md`. The rubric stays **provisional, not `stable`**:
  all four rounds used recorded outcomes as the "human" side; a live
  second-person calibration round is still owed.
- **Rationale:** a rubric nobody calibrated is an opinion with a table.
  The negative control (retrospective Block of the pre-Phase-0 pack)
  shows the rubric can say no.
- **Rejected:** the four-dimension variant (kept only as a simplified view
  with an explicit mapping, if ever used); marking the rubric stable
  without a live second judge.
- **Date:** 2026-10-28.

## D16 — Eval tooling is shell-only; eval regression is manual + monthly (Phase 3)

- **Decision:** `eval/run-bench.sh` is Bash-only by design (CI runs on
  ubuntu; the runner is repo tooling, not a deployed feature, so the
  sh/ps1 PARITY rule does not apply). `.github/workflows/eval-regression.yml`
  runs on manual trigger + monthly cron: benchmark smoke, results
  recomputation (`eval/check-results.py`), pack/gate setup paths. It does
  NOT red-line on a single run's duration — thresholds apply to 12-run
  windows only.
- **Rationale:** a monthly eval that cries wolf on one slow run would be
  ignored within two months; the guard must match the statistics it
  enforces.
- **Date:** 2026-10-28.

## D17 — sh/ps1 dual implementation: keep both, sh-first, review 2027-04-28 (Phase 4, 4-3; settles U3)

- **Decision:** keep the dual implementation. `deploy-agents.sh` is the
  reference implementation; `deploy-agents.ps1` is a maintained port.
  Every new deploy/pipeline feature lands in sh first and is ported to ps1
  in the same PR — the PARITY test (`tests/repo_checks.py` §4/§4b) fails
  CI otherwise. No ps1-only features; no new shell entry points. This is a
  decision to keep the status quo deliberately, not a deferral: the
  alternatives were costed and rejected below.
- **Cost data (measured 2026-10-28):** deploy scripts 1,592 (sh) + 1,483
  (ps1) lines; pipeline scripts 1,136 (sh) + 1,058 (ps1) lines; 5,269
  lines total across the four files; 54 PARITY markers (37 deploy + 17
  pipeline) binding them. Phase 0-10 measured the same multiplier class
  for languages: one rule change touches ~20 files. The shell split is the
  same kind of cost, in the same order of magnitude.
- **Rationale:** there is no usage data on which shell users deploy with
  (U1 — no telemetry), so converging to one shell now would strand an
  unknown share of users on no evidence. The PARITY test is the mechanism
  that makes dual maintenance bounded: drift fails CI instead of
  accumulating silently.
- **Rejected:** (a) freezing ps1 to bug-fixes only — strands Windows users
  on no evidence; (b) a generator from a single source — unproven, and the
  generator itself would need parity tests against its output; (c) a
  Python `harness` CLI as the sole implementation — a 5,269-line rewrite
  with full regression risk and no forcing need.
- **Review date: 2027-04-28.** Revisit on any one trigger: (1) usage data
  shows one shell's deploy share below 10% over a quarter; (2) a third
  parity-drift incident (a feature landing in one script without the
  other — count starts at Phase 4; prior drift: `codegraph.cmd`, fixed in
  Phase 0); (3) a Python CLI lands for another reason, at which point
  convergence is re-decided rather than assumed. If none triggers by the
  review date, the review records a new date in writing — the decision
  does not silently lapse.
- **Date:** 2026-10-28.
