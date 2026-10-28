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

## D18 — Skill tiers: minimal (10) is the default; the core list is provisional (Phase 4, 4-1)

- **Decision:** deploy profiles `minimal` (10 skills, default) /
  `standard` (18) / `full` (40) as defined in `skills-profiles.json`
  (single source of truth; CI §3r asserts it). Default deploys minimal.
  Bench pack/gate arms pin `--profile full` so the Phase 3 comparison
  keeps its meaning.
- **Rationale:** the old default (38 skills, 1,790,367 deployed-total
  bytes) shipped everything to everyone. Minimal carries 212,777
  skills-only bytes; the cut is a size cut, not a token claim — no token
  number is asserted anywhere.
- **Provisional:** the core-10 selection has no usage data behind it (U1).
  Each skill's basis is tagged [measured] / [dependency] / [provisional]
  in `docs/internal/skill-tiers.md`. Re-selection after the 36-run bench
  matrix completes; review date **2026-11-28**.
- **Rejected:** picking the core by author preference without tagging the
  evidence class; claiming token savings from byte counts.
- **Date:** 2026-10-28.

## D19 — EN/ZH are the sources of truth; FR/DE/ZH-TW are generated products (Phase 4, 4-2)

- **Decision:** EN/ZH `##` parity stays a hard CI check; the 16-pair
  symmetric H2 hard check is removed. FR/DE/ZH-TW status is tracked in
  `docs/internal/i18n-status.md` (source sha per target) and enforced by
  `tools/i18n-check.py`: an `in-sync` claim must match the current source
  sha; `stale`/`frozen` pass with a printed reminder. Regeneration from
  the EN source + spot-check (`--spot-check`) happen before a release.
- **Rationale:** a translation being behind is tracked debt, not a build
  failure; the old check made every EN edit fail CI in three languages
  the owner does not maintain by hand.
- **Rejected:** keeping the symmetric hard check; deleting the FR/DE/ZH-TW
  files outright (D3 freeze stands — they stay, marked stale where the
  source moved).
- **Date:** 2026-10-28.

## D20 — Monthly ablation: one component, dependency gate, owner sign-off (Phase 4, 4-4)

- **Decision:** one ablation per month (`tools/ablation.py` + process in
  `docs/ablation/README.md`): dependency gate first (template/hook
  references block removal), then 4 tasks × 3 reps with the component
  removed from pack-arm run dirs, then a report against the bare-arm
  thresholds. No-regression is necessary but not sufficient for removal;
  the owner fills in the Human decision line. The script never removes
  anything itself. First run (2026-10, `writing-skills`): 12/12 pass, 0
  false completions — candidate for removal on bench evidence only,
  decision pending.
- **Rationale:** without a repeatable removal process, subtraction is a
  one-off opinion. With it, each removal has a gate, a run, and a named
  decider.
- **Rejected:** removing on bench data alone; ablating single OpenSpec
  loop steps (the family is decided as a whole).
- **Date:** 2026-10-28.

## D21 — Loop is built and dogfooded; its need is still unproven (Phase 5)

- **Decision:** the Loop layer ships as `tools/loop.py` (stdlib-only
  runner: Goal Loop + Maker-Checker, enforced stop conditions,
  per-command timeout, wall-clock budget, human approval) with
  `templates/loop/` (goal / loop-state / graph, EN+ZH) and a worked
  example graph (`docs/internal/phase5-graph.md`). Loop templates are
  NOT wired into `deploy-agents.sh` / `.ps1` yet — they ship with the
  repo; deploy integration is deferred to Phase 6 (release), with the
  rationale that the runner is repo tooling and the templates are
  opt-in project files, not part of the default distribution.
- **L14 five criteria, item by item (honest, not padded):**
  - 可独立拆分 — met: Goal Loop and Maker-Checker ran as separate
    loops in separate worktrees.
  - 有分支或回退 — partially met: reopen/block exist in the gate and
    the loop returns to the maker on failure; no real rollback was ever
    exercised in the bench.
  - 中间状态值得保存 — partially met: loop-state.json + loop-events.jsonl
    exist and were the audit trail for both demo runs; but the demo
    tasks' intermediate state was trivial.
  - 结果可验收 — met: every round's verdict came from a re-run verify /
    checker command, never from the maker's word.
  - 协作收益大于协调成本 — NOT met: no multi-agent parallelism need
    was ever measured; the two worktrees ran sequentially in practice.
  - Total: 2 met, 2 partial, 1 not met — the "at least 3" bar is met
    only if partials count, and two of the met items are properties of
    the gate layer, not evidence that Loop is needed.
- **Four questions:**
  - Who owns the goal: the repo owner (user).
  - Who can veto / roll back: the user, via `loop.py approve` (veto by
    refusing approval) and git revert (rollback).
  - Which metrics may move: round counts, verify attempts, durations —
    all recorded per round; thresholds stay provisional.
  - Which must freeze: the stop conditions in the goal file (max rounds,
    timeout, budget) — the runner enforces them; changing them mid-loop
    requires a new loop, not an edit.
- **Measured verdict:** Goal Loop took ~1.5× the manual baseline
  (2052 ms vs 1364 ms) on a 1-line fix; Maker-Checker needed 5 rounds
  with a genuinely shrinking failure list. Demonstrated benefits are
  process assurance (enforced verification, consecutive-pass rule,
  audit trail) — not speed and not false-completion reduction. The
  entry assessment's warning stands: no measured loop need exists yet.
  Harder benchmark tasks remain the missing evidence.
- **Rejected:** claiming Loop is needed because it exists; wiring loop
  templates into deploy before Phase 6; auto-approving loops (approval
  is always human, recorded).
- **Date:** 2026-10-28.

## D22 — The lock is a true lock; ghost meta entries stay annotated, never deleted (Phase 6, 6-1)

- **Decision:** `skills-lock.json` is enforced as a real lock, in two layers.
  Offline (`tests/repo_checks.py` §5/§5b/§5c): every github-source entry
  must carry a 40-hex `pinnedCommit`; every meta entry must carry a
  `pinnedCommit` + a non-empty `note`; a hash-only lock edit with no
  corresponding file change fails. Online (CI step
  `python3 tools/sync-skills.py --check --strict`): every vendored skill's
  local content is verified against the content at its pinnedCommit
  upstream; drift, tampering, or an unresolvable pin fails the build
  (measured locally: 34 s, all in-sync).
- **Continuation of D10:** v2 §6-1 originally said "delete the ghost
  entries". D10 already ruled the opposite — annotate (`meta: true` +
  note), never delete — because the entries pin suite repos that are the
  provenance of the vendored skills. Phase 6 keeps D10: the true-lock
  checks apply to real entries, and meta entries are checked for
  pin+note, not deleted. Deleting one would destroy the provenance trail
  the lock exists to preserve.
- **Update process:** upstream updates go through a reviewed PR
  (`sync-skills.py --apply` on a branch, never on main; never hand-edit
  `computedHash`); re-pinning updates `pinnedCommit` + `pinnedAt` (+
  `pinnedFrom`). Documented in CONTRIBUTING.md "Updating vendored skills".
- **Date:** 2026-10-28.

## D23 — Supply-chain close-out: every install is pinned or a recorded gap (Phase 6, 6-2)

- **Decision:** no unpinned install vector may remain in the repo's own
  instructions or deploy scripts. Closed in Phase 6: OCR CLI pinned
  1.13.3 (lock `npmVersion`/`pinnedAt`/`pinnedFrom` + `OCR_NPM_VERSION` /
  `$script:OcrNpmVersion` in both deploy scripts + `ocr-pin` guards);
  EN+ZH Panorama Guide show pinned installs only — versioned npm
  (`comet@0.5.1`, `codegraph@1.6.2`, `open-code-review@1.13.3`) and
  download-then-SHA256-verify flows for the codegraph/rtk installers
  (hashes taken from `skills-lock.json`, the record) — guarded by
  `docs-pin` checks in `tests/repo_checks.py` §3m1b.
- **Known gaps, recorded not hidden:**
  - The vendored comet skill (`.agents/skills/comet/SKILL.md:84`) still
    shows an unversioned comet install in upstream text. Editing a
    vendored skill would break the lock (§5 hash check and pin check),
    so it is left as-is and recorded here. It is upstream's text, not
    this repo's instruction.
  - RTK winget (`winget install rtk-ai.rtk`) has no version pin (D13
    known gap, unchanged).
  - FR/DE/ZH-TW Panorama Guide rows are `stale` in
    `docs/internal/i18n-status.md` (they still show curl|sh and
    unversioned npm install); translation is tracked debt, not a CI
    failure (D19).
- **Date:** 2026-10-28.

## D24 — Version and deprecation policy (Phase 6, 6-3)

- **Decision:** `tools/check-release.py` (stdlib-only) is the release
  gate, wired into `tests/repo_checks.py` §3c2: VERSION must be semver
  and equal the newest `## [x.y.z]` in CHANGELOG.md; every released
  heading must carry a `- YYYY-MM-DD` date; the lock must be
  release-ready (github entries: pin + hash; local entries: version +
  hash; meta entries: pin + note). A release can never be cut with an
  unpinned skill.
- **Deprecation:** a template breaking change must be recorded as a
  `**Breaking**` bullet (or under `### Deprecated`) in CHANGELOG
  `[Unreleased]` **with a `Migration:` note** — the tool fails the build
  if the note is missing (negative-tested). The old form stays available
  for **one full version cycle** (kept deprecated in the release that
  introduces the replacement, removable only in the release after that);
  removal is itself a `**Breaking**` entry with a `Migration:` note and
  needs owner sign-off.
- **Release notes:** v0.3.0 draft prepared in
  `docs/internal/release-v0.3.0.md` (what was done / not done / measured
  numbers); procedure in `docs/internal/release-checklist.md`. VERSION
  stays 0.2.1 and no tag is created in Phase 6 — tagging needs separate
  user approval.
- **Date:** 2026-10-28.

## D25 — Loop layer ships with deploy (Phase 6, 6-5; closes D21 leftover)

- **Decision:** the Loop layer is now part of the distribution, not just
  repo tooling. Both deploy scripts ship `templates/loop/` (all six
  templates: goal / loop-state / graph × EN+ZH) to
  `${TARGET}/templates/loop/` and the stdlib-only runner to
  `${TARGET}/tools/loop.py`, mirroring the gate precedent (ship code +
  templates; per-project state — `loop-state.json` /
  `loop-events.jsonl` — is created by runs, never copied). Skipped on
  self-deploy. PARITY row `LoopDeploy`/`loop-deploy` added; `tests/
  repo_checks.py` §3t deploys to an empty temp dir and verifies all six
  templates + the runner land and the deployed runner executes.
- **Unchanged from D21:** Loop's need is still unproven (2 met + 2
  partial + 1 not met on the L14 criteria); shipping it in deploy does
  not claim otherwise. Approval stays human, always.
- **Date:** 2026-10-28.

---

## Merge decisions (2026-10-28, branch `feat/merge-v3`)

Three branches were merged per
`agent-harness-三分支对比与合并优化方案-2026-10-28.md`: the skeleton
`feat/phase0-v3` (this file's D1–D25) plus `v3-yunyi` and `v3-yunkai`.
The user was asleep during the merge and could not rule on the ten
open items (C1–C10); each ruling below was marked **合并执行时暂定，
用户复核时可改** (provisional at merge time, user may change on
review). D26, D27, and D28 have since been replaced by user final
rulings on 2026-10-29 (see those entries); D29–D35 remain provisional.

## Numbering note (deviation from the plan's §6.5 suggestion)

The plan suggested donor-branch decisions continue from D26. They do
not: D26–D35 are reserved for the ten C1–C10 rulings below, and donor
decisions continue from **D36**. The numbering is explicit here so no
one has to guess which D-number came from where.

## Correction: D27 belongs to yunyi, not yunkai

The merge plan's §6.3 attributed "D27 Guard conjunction + 13 tests"
to `v3-yunkai`. That attribution is wrong, verified against the
branches: D27 (Guard `$(which git)` indirection) lives at
`origin/v3-yunyi:DECISIONS.md:53` and its 13 tests at
`origin/v3-yunyi:tests/hooks.test.mjs:185-235`. Yunkai's actual Guard
work is recursive substitution parsing plus 5 hardening tests (see
D36–D56 table). The merge took D27 from yunyi (correct source); the
plan's attribution is corrected here, not silently repeated.

## D26 — C1: `archive_confirmation` defaults to `automatic` (user final ruling, 2026-10-29)

- **Decision:** the template default is `automatic` (yunkai D-004 adopted).
  Skeleton D4 / v3 D4 (`required`) is superseded for the template going
  forward; D4 remains as Phase 0 history. Deployed projects' own
  `.comet/config.yaml` files are untouched (deploy only copies the template
  when the target lacks one). This repo carries no `.comet/config.yaml` of
  its own (removed in Phase 0 dedup), so no in-tree own-config change
  applies; a project that wants the stricter behavior sets `required` in
  its own config.
- **Reason:** user final ruling 2026-10-29, adopting yunkai D-004's
  downstream-convenience default. Per-project override stays cheap.

## D27 — C2: FR/DE templates deleted (user final ruling, 2026-10-29)

- **Decision:** the 18 FR/DE files are deleted (yunkai D-006 adopted):
  README.fr/de, three guides × fr/de, PROJECT_CONTEXT/SESSION_STATE
  templates × fr/de, Global/Project/Directory AGENTS × fr/de. References
  cleaned in the same change: repo_checks §3h (3 types × 3 languages),
  link-check roots, i18n-check GENERATED set (ZH-TW only), i18n-status
  rows, README/guide language switchers, deploy language menus + mappings
  (fr/de inputs now fall back to EN), CONTRIBUTING language table.
  Skeleton D3/D19's freeze is superseded for FR/DE; ZH-TW stays frozen.
- **Reason:** user final ruling 2026-10-29, adopting yunkai D-006. FR/DE
  were stale, unmaintained translations; deleting them removes a standing
  regeneration debt and the false impression of five-language support.
  EN/ZH/ZH-TW remain.

## D28 — C3: rubric is standing advisory-only, never auto-approves (user final ruling, 2026-10-29)

- **Decision:** the rubric (yunyi's `eval/evaluate.py` + gate) is
  standing advisory-only: `eval/rubric-status.json` status
  `advisory-only`, `auto_approve_allowed: false`; `--gate` always
  refuses (exit 2) and there is no auto-approve path. A human always
  decides. Yunyi's all-2 (12/12) Accept rule is NOT adopted — the
  verdict rule follows the skeleton's `eval/rubric.md` (Accept =
  total ≥ 9 and no 0; Block = any 0). This ruling aligns with yunkai
  D-011 and supersedes the merge's provisional wording (which held
  the rubric "provisional until a live second-reviewer round marks it
  stable").
- **Reason:** yunyi's own D16 refused a stable claim until a
  confirmation round ran with fixed wording; the skeleton's D15
  likewise keeps the rubric un-stable for lack of a live second-judge
  round. Auto-approval on an un-stable rubric would let a gate pass
  work no human reviewed. The user ruling settles the direction:
  advisory is the standing state, not a waiting room.
- **Future trigger (deferred, NOT owed):** a live second review is
  not cancelled, but it is not outstanding homework either. It runs
  only when conditions mature, and it must run on a real project the
  user knows well — bench toy tasks do not count, because a second
  review on toy tasks cannot measure discrimination. Only if such a
  round actually runs and consistency meets the bar may `stable` and
  auto-approval be reconsidered. Until then, nothing is owed on this
  item.
- **Guard:** repo_checks `eval:rubric-advisory-only` pins status
  `advisory-only` with auto-approve off.

## D29 — C4: the skeleton's schema is the standard (merge ruling, provisional)

- **Decision:** `gate/feature_list.schema.json` keeps the skeleton's
  shape (top-level `items`, verification as an object
  `{command, timeout_seconds}`, `additionalProperties: false`). The
  yunkai shape (`features`, verification as a command array) is NOT
  adopted; yunkai's bench/comet_adapter/hooks were rewritten to the
  skeleton shape on port. A cross-branch migration/conversion script
  is a post-merge todo, not done in this merge.
- **Reason:** the skeleton's schema is the one `pass-gate.py`
  `validate()` and repo_checks §3k enforce, and it is the stricter of
  the two (closed object, required evidence rules). Adopting the
  looser yunkai schema would have weakened the gate for every existing
  deployment.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D30 — C5: standard profile is 18 skills (merge ruling, provisional)

- **Decision:** the standard profile stays 18 skills (skeleton D18,
  `skills-profiles.json`). Yunyi's D29 (standard = 22) is NOT
  adopted.
- **Reason:** the skeleton's profile membership is the single source
  of truth already guarded by CI; yunyi's 22 counts a different
  membership (openspec added wholesale) that was never bench-attributed
  to any outcome. Changing the count would move the default
  distribution without evidence.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D31 — C6: default profile is minimal (merge ruling, provisional)

- **Decision:** the default deploy profile stays `minimal` (10
  skills, skeleton D18). Yunkai's `--tier` default (`full`) is NOT
  adopted.
- **Reason:** v3 Phase 4 settled minimal as the default on the
  subtraction principle (ship the smallest proven set); yunkai's
  full-by-default would ship 40 skills — including the unproven bulk
  the quality scorecard scores 5/10 — to every new project.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D32 — C7: gate state files live inside `gate/` (merge ruling, provisional)

- **Decision:** `feature_list.json` / `events.jsonl` live in `gate/`
  (skeleton layout). Yunkai's root-level state files are NOT adopted;
  every ported yunkai path (bench gate arm, comet_adapter, t8 setup)
  was rewritten to `gate/`.
- **Reason:** the skeleton's layout keeps per-project state next to
  the engine that owns it, and the deploy scripts ship `gate/` as one
  unit. Root-level state files would collide with the repo's own
  root-level files in deployed projects and split state from engine.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D33 — C8: DECISIONS.md lives at the root, skeleton numbering is the base (merge ruling, provisional)

- **Decision:** this file stays at the repo root with the skeleton's
  numbering (D1–D25) as the base. Yunkai's `docs/internal/
  DECISIONS.md` (D-001–D-011) is folded in from D36 below, not kept
  as a second file.
- **Reason:** one decision log, one numbering, one place to look.
  Two files with overlapping numbers (D1 vs D-001) would make every
  future "per D7" reference ambiguous.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D34 — C9: Loop/Graph enter v0.3.0; release notes state the L14 gap honestly (merge ruling, provisional)

- **Decision:** Loop (skeleton Phase 5) and Graph (yunyi) ship in
  v0.3.0. The release notes must state honestly that the L14 criteria
  are not fully met (2 met + 2 partial + 1 not met, D21) — no claim
  that Loop/Graph are proven efficiency wins. Yunkai's D-008 (defer
  Loop/Graph) is recorded below, not adopted.
- **Reason:** the user explicitly chose to continue Loop (2026-10-28
  19:48) and the Graph executor is built and tested; withholding both
  from the release would discard finished work. But the entry gates
  were never fully met, so the release must not over-claim.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## D35 — C10: version is v0.3.0, but VERSION stays 0.2.1 in this branch (merge ruling, provisional)

- **Decision:** the release version is v0.3.0, but `VERSION` stays
  `0.2.1` in the merge branch — no bump, no tag here. The bump + tag
  happen in the release flow after merging to main (which needs
  separate user approval; main is frozen).
- **Reason:** the merge branch is not a release; tagging from it
  would publish a version whose contents were never approved for
  main. `tools/check-release.py` enforces VERSION/CHANGELOG/lock
  consistency, and a premature bump would break that gate.
- **Provisional:** 合并执行时暂定，用户复核时可改。

## Donor decisions (from D36)

Each donor decision is recorded once, with its source number and
what the merge did with it. "Adopted" means the substance landed in
this branch; "record" means it is preserved here for the history but
changed nothing in the merge; "not adopted" means the merge
deliberately did not take it (reason given).

| # | Source | Decision (one line) | Merge status |
|---|---|---|---|
| D36 | yunyi D27 | Guard `$(which git)` indirection: deny iff one segment has both a git-resolver substitution and an already-hard-blocked pattern; 13 tests | Adopted (merged, with the resolver-must-be-argv[0] refinement) |
| D37 | yunyi D32 | Brainstorming server loopback probe: HTTP+WS gap closed by live probe; server stays opt-in | Adopted (safety doc + 5 server tests) |
| D38 | yunyi D18 | brainstorming/server.cjs kept as opt-in skill asset, tests + safety note; not deleted, not promoted | Adopted (D37 is its evidence) |
| D39 | yunyi D8/D19 | Guard parse failure graded: log to guard-alerts.jsonl + stderr alert, allow (exit 0); raw stdin never logged | Adopted |
| D40 | yunyi D12 | Harness run never auto-merges; reports check-clean, leaves the worktree for manual merge | Adopted (`pass-gate run --branch`, no merge) |
| D41 | yunyi D26 | Phase 5 Graph entry met: parallel need concrete (T1–T4 ran 3 parallel subagents); merge rule ALL, fallback by layer, approval node | Adopted (gate/graph.py) |
| D42 | yunyi D2 | Second pilot SET: muse-ai-Desktop (draft releases, pilot branch cannot reach users); webhookBox NOT chosen (live relay) | Record (pilot not run in this merge) |
| D43 | yunkai D-009 | Slim Project template for minimal/standard tiers (ablation #2: outcome-neutral, −31% apparatus context) | Adopted |
| D44 | yunkai D-005 | Second pilot executed on webhookBox: gate ran on a real project, 2 features passed with evidence; kit not adopted there by owner decision | Record (experience only, no code; pilot branch discarded) |
| D45 | yunkai D-010 | v3-yunkai is not merged to main; main stays as the owner directs | Record (honoured: this merge touches no main) |
| D46 | yunyi D11 | Gate logic in `gate/harness.py`, `gate/pass-gate.py` a thin shim | Not adopted — skeleton has no harness.py; pass-gate.py is the implementation |
| D47 | yunyi D15 | check-clean FAILs when SESSION_STATE still has template placeholders | Not adopted in this merge (candidate follow-up) |
| D48 | yunyi D24 | repo_checks no longer fails fresh clones for gitignored local-only files | Not adopted in this merge (candidate follow-up) |
| D49 | yunkai D-008 | Loop/Graph engineering deferred, with triggers (manual re-mention ≥5×, workflow inexpressible in feature list, host missing a primitive) | Not adopted — merge ships Loop + Graph per C9/D34; triggers kept as the revisit signal |
| D50 | yunyi D14 | SESSION_STATE history archived to `docs/internal/SESSION_STATE.archive-2026-10-28.md` | Record (yunyi-internal housekeeping) |
| D51 | yunyi D25 | Phase 4 proceeds despite unmet gates 4–5, by explicit user instruction, deviation recorded | Record (yunyi-internal process) |
| D52 | yunyi D33 | Phase 6 leftovers closeout (SESSION_STATE de/fr/zh-tw rewritten, core review keeps minimal 10) | Record (yunyi-internal) |
| D53 | yunyi D20 | Support-matrix tiers: 真强制 / 仅配置 / 仅文件; tier upgrades need a repo test | Record (framing only) |
| D54 | yunyi D30 | Multilingual + lint: EN↔ZH pairs hard, others warn-only; harness lint-rules in CI | Partially adopted — EN/ZH hard covered by D19; harness lint-rules not ported |
| D55 | yunyi D13 | Comet template archive `required`; repo's own `.comet/config.yaml` stays `automatic` | Covered by D4 in substance; record |
| D56 | yunyi D6 | `docx` and `brainstorming/server.cjs` default OPTIONAL, not deleted; confirm usage first | Covered in substance by the skeleton's heavy-skill gating; record |

Covered by skeleton decisions and not listed above: yunyi D1 (≈D1),
D3 (≈D3), D4 (≈D4), D5/D17/D22 (hard stop OFF — see pending ruling),
D7 (skill counts, disk is truth), D9 (≈D8), D10 (branch isolation);
yunkai D-001 (≈D1), D-002 (≈D3/D19), D-003 (repo files are the source
of truth), D-007 (≈D12 + D15).

## Pending ruling (conflicts the merge did not settle)

These donor decisions conflict with the skeleton or with the merge
rulings above. They are recorded here, not silently absorbed, and
need a user ruling. Until then, the merge ruling (or skeleton
decision) stands. Settled since: yunkai D-004, yunkai D-006, yunkai
D-011, yunyi D23, and yunyi D16/D21 were decided by user final rulings
on 2026-10-29 (see D26, D27, D28, D57); the remaining items below are
still pending.

- **yunkai D-004 — `archive_confirmation` stays `automatic`.**
  SETTLED by user final ruling 2026-10-29 (see D26): the template default
  is `automatic`; D4's `required` is superseded for the template.
- **yunkai D-006 — delete the FR/DE rule templates (18 files).**
  SETTLED by user final ruling 2026-10-29 (see D27): the 18 files are
  deleted and references cleaned; D3/D19's freeze is superseded for FR/DE.
- **yunkai D-011 — human rubric calibration not run; rubric stays
  advisory-only.** SETTLED by user final ruling 2026-10-29 (see
  D28): the rubric is standing advisory-only, aligned with D-011.
  The live second review is deferred, not owed — it runs only when
  conditions mature, on a real project the user knows well.
- **yunyi D23 — cost hard stop ENABLED (user chose the ceilings).**
  SETTLED by user final ruling 2026-10-29 (see D57): hard stop is ON in
  this branch. `eval/cost.py` + `eval/cost-budget.json` are ported from
  yunyi with the D23 ceilings (task 10 verifications / 3600 s / 5 retries;
  day 100 verifications / 28800 s); `cost.py check` refuses new verification
  runs past a ceiling (exit 2) and never kills an in-flight run. The
  skeleton D12 proxy ledger (`tools/cost-ledger.py`) keeps its own
  warn-only property — two ledgers, two roles — so D12 is narrowed, not
  contradicted, and yunkai D-007's warn-only stance is superseded for
  verification runs by the same ruling.
- **yunyi D31 — lock pins with PIN_EXEMPT = {codegraph, comet, rtk}.**
  Conflicts with skeleton D22 (true lock, no exemptions). Merge kept
  the true lock — all three are pinned in `skills-lock.json` — and
  did not take the exemption.
  - **Pin-surface precision (review 2026-10-29):** the sentence above is
    literally true — codegraph, comet, and rtk each carry a pin in the
    42-entry lock (codegraph `pinnedCommit` + `installerSha256`, comet
    `npmVersion` 0.5.1 + `pinnedCommit`, rtk `pinnedCommit` +
    `installerSha256`) — but the lock entry is not the only pin surface.
    The deploy scripts enforce the same pins at install time (installer
    SHA checks agree with the lock), and the guides document the pinned
    installs. What the lock does NOT cover: rtk's PowerShell winget
    channel remains unpinned (skeleton D13, known gap). A lock pin that
    differs from the upstream tip is by design (pins are dated
    2026-10-28), not drift; re-pinning is a supply-chain decision, not a
    bug fix. Do not rewrite this bullet to claim the pins live only in
    scripts/guides — that would be false.
- **yunyi D29 — skill tiers standard = 22.** Conflicts with D30/C5
  (standard = 18). Merge kept 18.
- **yunyi D16/D21 — rubric `stable` claimed after confirmation round
  4.** Conflicts with skeleton D15 and D28/C3 (not stable, no live
  second-judge round). Merge did NOT carry the stable claim over;
  `eval/rubric-status.json` was provisional with auto-approve off.
  Settled by user final ruling 2026-10-29 (see D28): the rubric is
  standing advisory-only; a live second-person round is deferred, not
  owed, and must run on a real project the user knows well.

## D57 — Cost hard stop ON (user final ruling, 2026-10-29)

- **Decision:** the cost hard-stop gate is ON in this branch. `eval/cost.py`
  (ported from yunyi, D23) + `eval/cost-budget.json` carry the D23 ceilings:
  per task max 10 verifications / 3600 s / 5 retries; per day max 100
  verifications / 28800 s. `cost.py check` must be consulted before starting
  a new verification run; past a ceiling it exits 2 (BUDGET STOP), logs the
  stop to `eval/cost-ledger.jsonl` (local-only, gitignored), and the task is
  recorded as blocked (not passing, not failed). A stopped task resumes only
  after a human raises the budget or a new day starts. Checking never kills
  an in-flight run.
- **Supersedes:** the merge's provisional OFF (the pending-ruling entry for
  yunyi D23) and the merge's do-not-take list entry for the hard-stop gate.
- **Conflict resolved:** skeleton D12 (proxy ledger warns, never auto-stops)
  and yunkai D-007 (budgets warn, rubrics advise) described the skeleton's
  proxy ledger and yunkai's line, respectively. This ruling does not change
  `tools/cost-ledger.py` (it stays warn-only; repo_checks
  `cost-ledger:no-auto-stop` still holds for that tool). The hard stop lives
  in a separate gate over a separate task/day ledger, so D12/D-007 stand for
  their own tools while the branch-wide policy for verification runs is ON.
- **Guard:** repo_checks `cost-gate:*` pins the tool, the enabled flag, and
  the ceilings; `tests/cost_test.py` covers OK / task-verification stop /
  task-duration stop / day stop / OFF-never-blocks.

## D58 — Graph/Loop ship only on standard/full profiles (user final ruling, 2026-10-29)

- **Decision:** minimal deployments no longer ship `gate/graph.py`,
  `tools/loop.py`, or `templates/loop/` (6 templates). Standard and full
  keep them. Tier narrative: minimal = the gate itself (`pass-gate.py`,
  `comet_adapter.py`, schema, init template); standard = gate +
  orchestration (graph executor + loop runner/templates); full =
  everything.
- **Migration:** a project previously deployed with minimal that already
  has graph/loop files will have those files REMOVED on re-deploy with
  minimal (each file is backed up with a timestamped `.bak.` copy by the
  deploy scripts first). To keep them, re-deploy with `--profile standard`
  (`-SkillProfile standard`). This sentence is also in
  `docs/internal/skill-tiers.md`, the README profile paragraph (EN+ZH),
  and `docs/internal/release-v0.3.0.md` upgrade notes.
- **Scope:** distribution only. The loop/graph implementations are
  untouched; only the deploy scripts' tier gating changed.
- **Guard:** repo_checks §3t asserts the per-tier file sets (minimal
  absent, standard present + runners execute); PARITY row
  `TierGateGraphLoop` keeps the sh/ps1 gating in sync.

## D59 — D47: check-clean FAILs on unfilled SESSION_STATE placeholders (review ruling, 2026-10-29)

- **Decision:** ADOPT yunyi D15. `gate/pass-gate.py` `check-clean` gains
  dimension 3c "progress/no placeholders": FAIL if SESSION_STATE
  contains `<YYYY-MM-DD>`, `<PROJECT_NAME>`, the phrase "What this
  session is trying to ship", or `<TODO|TBD|XXX|PLACEHOLDER>` markers.
  Any FAIL dimension keeps the overall exit 1; other dimensions SKIP
  when unconfigured, as before. No SESSION_STATE file at all is SKIP
  for 3c (3a already FAILs when an item is in_progress without one).
- **Skeleton adaptation:** yunyi's check lived in `gate/harness.py`
  (which the skeleton does not have) and detected `<` plus "what this
  session" / "本会话要完成". The ported markers are the skeleton
  template's own unfilled markers, not yunyi's strings.
- **Guard:** `tests/check_clean_test.py` (placeholder → FAIL, generic
  `<TODO>` → FAIL, clean → PASS, missing file → SKIP).

## D60 — D48: fresh-clone check relaxation ADOPTED IN EFFECT, no code change (review ruling, 2026-10-29)

- **Decision:** yunyi D24 (fresh-clone checks must not require
  gitignored local-only files) is ADOPTED IN EFFECT. No code change:
  the merge branch's repo_checks contains no check requiring a
  gitignored file — the only gitignore-related checks assert the
  scaffold itself (patterns present), never the presence of an ignored
  artifact. To be confirmed by the fresh-clone run in the review
  verification round (docs/internal/merge-review-optimization-2026-10-29.md).

## D61 — SESSION_STATE template format: skeleton 31-line format is final (review ruling, 2026-10-29)

- **Decision:** the skeleton's 31-line EN SESSION_STATE template is the
  final format (consistent with D29 skeleton schema). Yunyi's 11-line
  breakpoint format is NOT adopted — switching formats would churn
  every downstream SESSION_STATE without a measured benefit.
- **Drift:** ZH is 27 lines (within the >5-line tolerance, no warning);
  ZH-TW is 46 lines (old format, flagged by the i18n-check [drift]
  warning until regenerated). FR/DE variants were deleted per D27.
- **Guard:** `tools/i18n-check.py` template-drift check (warning only,
  never fails the build; same >5-line tolerance as yunyi's lint LINT-006).

## D62 — Lint-rules ported (yunyi 6 rules, skeleton-adapted) (review ruling, 2026-10-29)

- **Decision:** yunyi's 6 lint rules are ported to `tools/lint-rules.py`
  + repo_checks `lint-rules:exit-0` (CI runs repo_checks, so CI is
  covered). Rule-by-rule reconciliation (full table in
  docs/internal/merge-review-optimization-2026-10-29.md):
  LINT-001 entry presence — NEW coverage, ENTRY_FILES adapted to
  skeleton reality (yunyi's `gate/harness.py` and
  `templates/feature_list.template.json` do not exist here and are
  dropped); LINT-002 hook wiring — overlaps the skeleton's five-event
  settings check, extended to the six hook files; LINT-003 schema
  parse — adapted to `gate/feature_list.schema.json` (a JSON Schema
  document: version const 1, items array) plus non-empty state
  templates, NEW coverage; LINT-004 placeholder residue — NEW scope
  (the skeleton's placeholder check covers only docs/internal/*.md
  with angle-bracket markers); LINT-005 dead refs — equivalent coverage
  already exists in repo_checks Phase 0, port kept for defense in
  depth; LINT-006 translation drift — NEW alert, overlaps the
  i18n-check drift warning by design (linter view vs
  translation-tracker view).
- **Porting notes:** the first LINT-003 draft wrongly required a
  feature_list instance shape (top-level version + items list) and
  failed on the real schema; fixed to read properties.version.const
  and properties.items.type. The first run also caught LINT-004
  residue in the new 3c code itself (D59 literals); the 3c pattern is
  now assembled from parts, the same trick lint-rules uses.
