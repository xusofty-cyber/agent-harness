# Tech debt tracker

Deferred work, recorded with its reason and the condition that
re-triggers it. Reviewed whenever a release is planned. Format per
the OpenAI repo-template's tracker (date / area / debt / why
deferred / risk / next trigger). Seeded 2026-11-06 from DECISIONS.md,
QUALITY_SCORE.md and docs/internal/SESSION_STATE.md.

| Date | Area | Debt | Why deferred | Risk | Next trigger |
|---|---|---|---|---|---|
| 2026-10-29 | Evaluation | Live second-person rubric calibration not run; rubric stays advisory-only (D28) | User final ruling: runs only on a real project the user knows well, when conditions mature | Rubric can never be promoted to `stable`; evaluation claims stay capped | **Plan active 2026-11-06**: `docs/exec-plans/active/2026-11-06-d28-live-calibration-and-eval.md` (MedOnTime samples chosen; Round 6 awaiting the owner's judging pass) |
| 2026-10-31 | Host bridges | Antigravity IDE and dsh bridges remain `protocol-only`; WorkBuddy payload shape/settings were being confirmed against one installed build (2026-11-06, in progress). **Antigravity CLI closed 2026-11-06: `live-verified`** on the user's host (agy 1.2.14, edit_file deny captured in the gate event log; record in the matrix) | IDE needs one live run of the four hook events; dsh needs one live run with the plugin activated (API key or local model) | Bridge defects surface only in real use; wording must not outrun the tier | A live run of the full gate flow on each host |
| 2026-10-29 | Pipeline & deploy | CI template not yet run in a real GitHub Actions environment; `deploy-agents.ps1` not yet execution-verified on a live Windows host | Owed since the 2026-10-29 dogfood round (SESSION_STATE) | CI/Windows-only defects stay invisible to local checks | Next release cycle |
| 2026-10-31 | Evaluation | Whether the gate reduces false completions is **not established** by B1–B4 measurement (D69); benchmark series sealed | Bench design hit its discrimination limit | The central value claim stays unproven | Re-test only the affected dimension after a material host/mechanism change |
| 2026-10-31 | Skills distribution | Token cost of the harness unmeasured (no host exposes a token API; proxy metrics only) | Blocked on host capability | Cost side of the value equation unknown | A host exposing a programmatic token API (see `docs/internal/token-adapters.md`) |
| 2026-10-31 | Docs i18n | ZH-TW Multi-Tool Deployment guide knowingly stale (ledger: `docs/internal/i18n-status.md`) | ZH-TW is frozen by policy; EN/ZH are the sources of truth | ZH-TW readers follow outdated deploy steps | ZH-TW maintenance resumes, or the guide is formally retired |
| 2026-10-31 | Skills distribution | 2026-11 monthly ablation run + skill-usage telemetry review pending | Scheduled cadence (D68 telemetry) | Zero-load skills keep shipping by default | Telemetry review due 2026-11-28 |
