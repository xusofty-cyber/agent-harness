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
- **U3 — sh/ps1 dual-implementation endgame.** No timetable exists for
  ending the dual-script maintenance; v3 requires a decision + review
  date in Phase 4-3, no indefinite deferral.
