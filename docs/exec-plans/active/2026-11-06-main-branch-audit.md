# Main-branch audit — post-bridge-round review (2026-11-06)

Scope: full re-audit of `main` @ 2085fab after the one-day bridge
live-verification round (Antigravity CLI/IDE/desktop + dsh all reached
`live-verified`). Baseline re-measured this day: unit tests pass,
`tests/repo_checks.py` all pass (1 ENV-SKIP: eval bench smoke, no
pytest here), `check-clean` all configured dimensions pass, feature
list 6/6 passing. What follows is what still needs work, by severity.
Items marked OWNER are decisions only the owner can make; the rest are
executable work.

## P0 — claims that no longer match the evidence

1. **QUALITY_SCORE.md is stale by a full evidence generation.**
   The v0.6.0 edition (2026-10-31) scores Host bridges **4/10** on
   evidence that no longer exists ("no bridge has run a full gate flow
   on its live host"). As of today: four of five bridges are
   `live-verified` with full gate flows, real Stop blocks and captured
   denies; only WorkBuddy stays `protocol-only` (owner-deferred). The
   file's own rule says it is re-issued when evidence changes.
   **Action:** re-issue the scorecard; bridges re-scored on the matrix;
   gate/evaluation rows re-read for the same staleness.
2. **The tech-debt tracker has an unfiled row.** The bridges row lost
   its date/area cells in an earlier edit: it renders as a broken
   three-cell row inside the six-column table. Small, but it is the
   project's own ledger — fix the row structure while re-issuing.
3. **Release bookkeeping is behind the code.** Latest tagged edition
   is v0.6.0 (2026-10-31); main has since gained: the structure
   adoption batch, the D28 live-calibration plan + Round 6 sealed
   scores, the state-freshness check, three bridge live-verifications
   with two real bug-fix batches (dsh contract, Antigravity global
   hooks). **Action (OWNER-adjacent):** cut v0.7.0 via
   `docs/internal/release-checklist.md` — which itself requires a real
   CI run (see P1-2), so the two sequence together.

## P1 — decided or designed, not yet built

1. **Feature dependencies — proposal written, semantics unchosen
   (OWNER).** `docs/design-docs/proposal-feature-dependencies.md`:
   `depends_on` + existence/cycle checks are uncontroversial; the
   `start` semantics (record-only / warn+`--override-deps` / hard
   block) need the owner's ruling, then a DECISIONS entry, then
   implementation. Pairs naturally with (5).
2. **Item-level out-of-scope field (L07 residual).** Planning-level
   out-of-scope exists (initializer-playbook); the gate item schema
   and `pass-gate.py add` have no `out_of_scope` field. Same schema
   evolution batch as (4) — do them together, once.
3. **CI template — **DONE 2026-11-06**: first real runs #291/#296/#299; #299 fully green (both jobs, all steps). The unpinned-linter defect the first run exposed is fixed (0.32.2 pin). + `deploy-agents.ps1` still never ran for real**
   (owed since 2026-10-29). `ci.yml` + `eval-regression.yml` exist;
   QUALITY_SCORE's pipeline row is explicit that the Windows job is
   "committed, not yet observed". Blocks an honest v0.7.0 (checklist
   requires the real CI record incl. the ps-analyzer job).
   **Action:** one `workflow_dispatch` run on a release branch; read
   the result; fix what it finds.
4. **Two-track state layer — proposal written, unapproved (OWNER).**
   `docs/design-docs/proposal-state-two-track.md` (authoritative layer
   + SESSION_NOTES). The freshness check shipped 2026-11-06 covers the
   authoritative half's decay; the notes layer is the remaining half.
5. **Own feature list's verification strength.** This repo's 6 passing
   items are assert 5 + unit 1 — the exact mix the B3 design in the
   D28 plan criticizes (cross-component p0 items should carry at least
   integration-level verification). Dogfood gap: convert or add one
   integration-level item (e.g. an end-to-end deploy→gate→verify run
   in a temp project, like the Instabox clean-room run) and let it be
   the standing proof.
6. **Bridge residuals (small, scheduled).** (a) IDE `start` produced
   no separate `started` event in the live run (F4 of the two-surface
   plan) — determine agent-flow vs adapter gap, pin with a test.
   (b) dsh stop steering ran but was never provoked with an in_progress
   item. (c) Desktop PreToolUse deny has probe+Stop evidence but no
   captured deny of its own. Each is a half-hour instrumented run; do
   them in one session, ideally right after (6) so the versions match.

## P2 — cadence and hygiene

10. **2026-11 monthly skill ablation + telemetry review due
    2026-11-28** (D68). Zero-load skills still ship by default until
    this runs; the Distribution score (6) moves on its result.
11. **ZH-TW Multi-Tool guide knowingly stale** — either regenerate at
    the v0.7.0 release (its recorded trigger) or formally retire it;
    the middle state is the worst of the three.
12. **Token cost still unmeasured** (no host exposes a token API).
    Not actionable until a host changes; keep recorded, do not chase.
13. **WorkBuddy `protocol-only`** — owner-deferred 2026-11-06; resume
    is a sign-in + payload check on the installed 5.6.2 build. Listed
    for completeness, not as a recommendation to spend time now.

## Explicitly NOT recommended

+ Re-opening the B1–B4 benchmark series without a material change
  (D69 stands; bridge live-verification arguably IS a material change
  for the *enforcement* dimension only — if anything is re-run, it is
  B4's enforcement slice under the D28 plan's B2 mutation design, not
  the whole series).
+ Chasing the two phase1/dogfood historical files' migration: their
  paths are asserted by gate verification commands and the hash chain;
  retirement-by-new-item is a maintainer ruling (OWNER) with low value.

Sequencing suggestion: P0 (scorecard + tracker fix) → P1-6 CI run →
v0.7.0 release → owner rulings on (4)/(7) → schema batch (4)+(5) →
P1-8/P1-9 in one instrumented session → P2 on its dates.
