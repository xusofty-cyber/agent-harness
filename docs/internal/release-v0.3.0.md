# Release v0.3.0 — draft notes (Phase 6, 6-4)

> **DRAFT — do not publish.** Prepared 2026-10-28 on branch `feat/phase0-v3`.
> Cutting this release needs the user's explicit approval (tag `v0.3.0` is
> NOT created here; `VERSION` stays `0.2.1` until release day). See
> `docs/internal/release-checklist.md` for the procedure.
>
> This draft covers the whole v3 revamp (Phases 0–6). Final numbers must be
> re-verified on release day (`python3 tests/repo_checks.py`,
> `python3 tools/check-release.py`, deploy smoke).

## What v0.3.0 is

A ground-up rebuild of agent-harness from a "skill distribution pack" into a
gated harness: a pass-gate layer, a true skills lock, a pinned supply chain,
a self-built benchmark, a slimming pass, and an optional Goal Loop — all
verified with measured numbers, not claims.

## What was done (Phases 0–6)

- **Phase 0 — foundations**: skill count single source of truth
  (`tools/count-skills.py`, 40 skills on disk); `DECISIONS.md` D1–D4;
  `AGENTS.md` 156 → 61 lines; positioning + support matrix;
  `archive_confirmation` → `required` (superseded 2026-10-29 by user final
  ruling D26: the template default is `automatic`); dead `comet-archive` refs removed;
  `.comet/config.yaml` deduped; deploy auto-mkdir; docx/brainstorming opt-in.
- **Phase 1 — gate layer**: `gate/` (feature_list schema, stdlib-only
  `pass-gate.py`, init template, append-only events) + session templates +
  anti-tamper triple + Stop-hook override. Dogfood: fake pass blocked twice
  (CI §3k, hook denial).
- **Phase 2 — gate becomes real**: `--strict` on pipeline/tools; comet
  pinned 0.5.1; codegraph/rtk installers hash-verified (curl|sh / irm|iex
  zeroed); ghost meta entries annotated `meta: true`, never deleted (D10);
  all five hook events wired; Guard expands indirect execution; cost ledger
  - budget alerts (never auto-stop).
- **Phase 3 — self-built benchmark**: 4 tasks (fixed start commit),
  `eval/run-bench.sh`, six-dimension rubric (5 calibration rounds), eval
  regression CI, first `QUALITY_SCORE.md`.
- **Phase 4 — slimming**: deploy profiles minimal (default, 10 skills,
  212,777 bytes) / standard (18) / full (38 gated, 40 with heavy;
  1,790,382 bytes); EN/ZH as source of truth (i18n-check + status file);
  D17 sh/ps1 convergence (sh-first, re-review 2027-04-28); monthly ablation
  tooling, first run on writing-skills (12/12 pass, CANDIDATE FOR REMOVAL).
- **Bench matrix (full)**: 36/36 runs pass, 0 false completions (4 tasks ×
  3 repeats × 3 arms). Ceiling effect: tasks too easy to distinguish arms;
  gate arm costs ~+1 s / +1 round vs pack (verify overhead itself).
  Thresholds re-derived from pooled runs (T1 11 s / T2 25 s / T3 56 s /
  T4 59 s; rounds 6/6/6/8) — still provisional.
- **Phase 5 — Loop**: `tools/loop.py` (stdlib-only Goal Loop +
  Maker-Checker, enforced stop conditions, timeout, budget, human
  approval) + 6 loop templates. Real demos: fixed `pass-gate.py status`
  "1 items" plural bug; timeout killed at 2.005 s; over-budget fails even
  when verify passes. D21: L14 criteria 2 met + 2 partial + 1 not met.
- **Phase 6 — true lock + release readiness**: `sync-skills.py --check
  --strict` runs in CI (online pin verification); every github pin must be
  40-hex (repo_checks §5c); OCR CLI pinned 1.13.3 (lock + both deploy
  scripts); docs show pinned installs only (EN+ZH Panorama Guide);
  `tools/check-release.py` release gate (VERSION/CHANGELOG/lock +
  deprecation policy); Loop templates + runner wired into deploy.

## Measured numbers (re-verify on release day)

- `tests/repo_checks.py`: 599 checks passing at Phase 5 (count grows with
  Phase 6 additions — see the run log).
- Hook tests: 56 + 10 + 12 passing.
- Deploy smoke: `deploy-agents.sh` to an empty directory exits 0.
- `sync-skills.py --check --strict`: all skills in-sync vs pins (~34 s).
- Bench: 36/36 pass, 0 false completions; thresholds provisional.

## What was NOT done (known gaps, honest list)

- **Rubric not marked stable**: 5 calibration rounds, 0 disagreements, but
  still needs one real second human reviewer (Phase 3/4/5 carry-over).
- **Core-10 list provisional**: no usage data; re-review 2026-11-28.
- **Bench ceiling effect**: tasks too easy; the matrix does not prove the
  gate reduces false completions (the proof remains Phase 1 dogfood's
  planted interceptions).
- **Vendored comet skill** (`.agents/skills/comet/SKILL.md:84`) still shows
  an unversioned comet install in upstream text — editing it would break
  the lock; recorded in D22, not fixed.
- **RTK winget has no version pin** (D13 known gap).
- **FR/DE/ZH-TW Panorama Guide rows are `stale`** (EN §2.3 pinned
  instructions not yet translated); 9 older stale rows remain.
- **Ablation candidate `writing-skills`** awaits owner sign-off (not
  removed in this release).
- **Loop templates were not wired into deploy until Phase 6** (D21
  leftover, closed by this phase).

## Upgrade notes

- No breaking changes to deployed templates in this release. The deploy
  profiles are additive: existing `full` deployments keep working;
  `minimal` is the new default for fresh deploys.
- **Tier change (D58, user final ruling 2026-10-29): minimal no longer
  ships graph/loop.** `minimal` = the gate itself; `standard` = gate +
  orchestration (graph executor + loop runner/templates); `full` =
  everything. Previously minimal-deployed projects that already have
  graph/loop files will have those files **removed** on re-deploy with
  `minimal` (each file is backed up with a timestamped `.bak.` copy
  first); to keep them, re-deploy with `--profile standard`.
- `skills-lock.json` format version stays `2`; entries are unchanged in
  meaning, only hardened (pins now enforced in CI).
