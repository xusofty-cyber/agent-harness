# Core beliefs — agent-harness

The beliefs the detailed rules, checks and templates implement.
Each belief names its source of record; if a belief and a source
ever disagree, the source wins until this file is updated.

1. **The gate is self-owned and host-agnostic.** Comet and every
   host are adapters; the harness itself belongs to this repo.
   (DECISIONS.md, D1)
2. **Evidence beats confidence.** An item is `passing` only when
   its verification command actually ran and the evidence is
   recorded; self-report is never sufficient.
   (`gate/feature_list.schema.json`; AGENTS.md)
3. **One active item at a time.** WIP=1: depth of completion beats
   breadth of starts. (`gate/feature_list.schema.json`)
4. **Repository files are the source of truth.** Chat and memory
   are recall aids; anything an agent cannot find in the repo is
   treated as not existing. (AGENTS.md, "Source of truth")
5. **Repeated human feedback becomes a mechanical rule.** A
   correction issued twice is promoted into `tests/repo_checks.py`,
   a hook, or a lint rule — not re-issued a third time as prose.
   (Practice of record: the repo_checks guard suite)
6. **Claims never outrun their verification tier.** Wording in
   docs and release notes matches the evidence tier in
   `docs/internal/host-verification-matrix.md`; nothing below
   `live-verified` is described as enforced.
   (QUALITY_SCORE.md, "Numbers & claims hygiene")
7. **Subtraction is progress.** Components and skills must keep
   earning their place; the ablation cadence removes what
   telemetry shows is unused. (QUALITY_SCORE.md posture; D65, D68)
