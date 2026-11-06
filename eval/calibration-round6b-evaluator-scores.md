# Round 6b (first LIVE round, replacement samples) — evaluator scores — SEALED

> Sealed 2026-11-06 by the evaluator BEFORE the judge's independent
> verdicts. Do not edit after sealing; reconciliation happens in
> `eval/calibration.md` once the judge rules.
>
> **Why 6b exists.** Round 6's original samples (A1–A4) were
> MedOnTime iterations. The judge (repo owner) reported on
> 2026-11-06 that they had not participated in that work — it was
> run end-to-end by agents — so no independent first-hand judgment
> exists to calibrate against; a verdict read off the evaluator's
> own materials would be circular. The A1–A4 evaluator scores stay
> sealed in `calibration-round6-evaluator-scores.md` as the record
> of that attempt (not counted toward live N). **Protocol lesson,
> now a sample-admission criterion: a calibration sample is only
> admissible if the judge can rule on it from first-hand
> participation, without re-studying the evaluator's materials.**
>
> Round 6b samples are the 2026-11-06 agent-harness batch itself:
> the judge directed it all day (rulings at 11:06, 11:15, 11:21,
> 12:12), ran the desktop test personally, and supplied every
> model credential tried. Independence note: the deliverer and the
> evaluator are the same agent; the independent side is the judge,
> per the Round 6 protocol. Rubric unchanged (6 dimensions × 0–2;
> Block = any 0; Accept = total ≥ 9 and no 0).

## B1 — CI first real run to green (#291 → #296 → #299)

Evidence: GitHub Actions runs #291/#296/#299 on branch
`ci/first-real-run`; fixes on main (CI pins markdownlint-cli
0.32.2 with recorded rationale; `.markdownlint.json` exemptions
aligned; CHANGELOG `[Unreleased]` merged to single sections;
QUALITY_SCORE headings disambiguated); run #299 both jobs, all
steps green. Known history: the first browser-worker report on
#296 contained fabricated details (a non-existent file, an
invented linter version) — detected, not trusted, and re-verified
against the raw job log by a second pass; one earlier local
"lint exit 0" had been measured on a stashed clean tree and was
void as evidence for the dirty tree.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | End state is what was asked: CI genuinely green, with the lint failure root-caused to version drift + true MD024 violations, not suppressed wholesale |
| Verification | 1 | The decisive green is a real CI record (#299), but the round's own evidence chain contained a fabricated worker report and one void local measurement — verification of the verification was needed twice |
| Scope discipline | 2 | Changes confined to CI config, lint config and the two documents whose headings violated MD024 |
| Reliability | 2 | #299 is a full clean run on the same tree family; pinning removes the drift class that caused the red |
| Maintainability | 2 | Pin rationale recorded in the workflow file; exemptions follow the file's existing author-style philosophy |
| Handover readiness | 1 | S2-adjacent: intermediate reports (fabricated #296 details, the void local green) would have misled a fresh reader about the state mid-round; final records are accurate |

Total 11, no zero → **Accept**.

## B2 — Bridge residuals: F4(a) + desktop deny + dsh stop steering

Evidence: F4(a) invariant test in `tests/antigravity-hooks.test.mjs`
(adapters never synthesize gate lifecycle events); desktop deny in
host brain transcript `eb097d43…` steps 5–7 (2026-11-06T03:50Z,
denial text verbatim, file unmodified) plus adapter-level probe
event #16 on the host project; dsh stop steering in host run17
(DeepSeek official `deepseek-flash`): trace `turn-stopping:enter`,
steering text delivered and echoed by the model, gate event #8
`stop_blocked`, item still `in_progress`. Known history: the
original dsh probe script was triple-broken (agy-style `-p` flag,
missing brief file, missing key) and never ran — misreported
mid-day as "running, will fail on auth" before the log was read
properly; the desktop deny was twice misjudged "not captured"
because the check looked at `events.jsonl` while session-path
denies are evidenced in the host transcript; four model routes
failed on account-side grounds first (Spark 403 not provisioned,
GLM 429 rate limit, SiliconFlow 402 balance, IFM key unreachable)
before DeepSeek official worked.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | All three residuals closed with primary evidence (test, transcript, hash-chained event), including the honest rc.5 post-steering error tail recorded rather than hidden |
| Verification | 1 | Final evidence is strong and re-checkable, but the path contained two evaluator-side evidence errors (wrong log watched; script status misread) — the round's verification discipline failed before it succeeded |
| Scope discipline | 2 | Work stayed on the three residuals plus the one real adapter bug they surfaced (flat-payload silent allow, fixed + pinned) |
| Reliability | 1 | Results are host- and account-dependent by nature; the dsh proof is a single live run on one provider, and desktop capture rests on one session transcript |
| Maintainability | 2 | Matrix scope note rewritten with the full arc; the transcript-vs-event-log evidence lesson is written down where the next session will find it |
| Handover readiness | 1 | S2: the mid-day record stated the probe was "running" when it had never run — a known deviation omitted until the completion handoff forced a re-read |

Total 10, no zero → **Accept**.

## B3 — D72 graded dependencies + D73 two-track state

Evidence: `gate/pass-gate.py` schema + CLI (`depends_on` existence/
self/cycle validation, `out_of_scope`, `start` hard-block default
with `--override-deps "<reason>"` writing a hash-chained
`dependency_override` event, status annotations); unit tests
including the override-trail case; `docs/internal/SESSION_NOTES.md`
created with a non-authoritative header; DECISIONS D72/D73.
Known history: the judge's instruction was a criterion, not a
mechanism ("要灵活点" — "make it flexible"); the evaluator first
implemented the pure hard-block reading, shipped it, then
re-decided to the graded form after a one-tap clarification, and
D72's wording was corrected to record that the criterion is the
judge's and the mechanism the maintainer's choice.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Final behaviour matches the judge's criterion (flexible, graded) and the schema validations are the ones the audit asked for |
| Verification | 2 | Behaviour pinned by unit tests incl. cycle detection and the override audit trail; full suite green at merge |
| Scope discipline | 2 | Confined to the gate, its schema/tests and the two decision records; the repo's own 7 items were checked and honestly reported as having no real dependencies to backfill |
| Reliability | 2 | Deterministic CLI behaviour, hash-chained audit events; S3 noted (test-suite evidence, no live incident yet) |
| Maintainability | 2 | Follows the gate's existing patterns (additive optional fields, schema version unchanged with justification) |
| Handover readiness | 2 | D72/D73 texts record the criterion-vs-mechanism history accurately, including the first wrong reading — a fresh reader gets the true story |

Total 12, no zero → **Accept**.

## B4 — ZH-TW regeneration (5 stale rows) + v0.7.0 release

Evidence: regenerated files on main (Global/Project AGENTS zh-tw,
README.zh-tw, Multi-Tool guide incl. new §4.5 in EN/ZH/ZH-TW);
`docs/internal/i18n-status.md` at zero stale rows with per-file
regeneration notes; release checklist executed (repo_checks pass,
unit 125/125, all hook suites pass, sync-skills strict in-sync,
check-release exit 0, CI #299 record); tag `v0.7.0` = main
`0ea0c65`; GitHub Release published (Latest); post-release
wrap-up (fresh `[Unreleased]`, SESSION_STATE at 43 lines
re-verified through the gate). Known history: the first
SESSION_STATE refresh attempt produced a 63-line file and was
**rejected by this repo's own verify** during the release
wrap-up — compressed and re-verified before handoff; the release
cut waited for the dsh residual per the judge's 12:12 ruling
rather than shipping early.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | All five rows regenerated against their EN sources with the real content gaps closed (D71 protocol, DoD gate paragraph, live-tier wording), and the release shipped exactly what the checklist defines |
| Verification | 2 | Checklist numbers re-measured on release day, not copied; the gate's own verify caught the one defect (63-line state file) before it could ship |
| Scope discipline | 2 | Regeneration limited to the five ledger rows + the §4.5 addition the D03 gap required; cut contents match the [Unreleased] record |
| Reliability | 2 | Tag, Release and VERSION agree; CI record is on the same tree family |
| Maintainability | 2 | Ledger notes state the regeneration basis per file (parity + spot checks), so the next regeneration can repeat the method |
| Handover readiness | 2 | Release note carries the honest gaps (WorkBuddy deferred, ps1 full-path, D28 advisory) and the breakpoint was re-verified, not just edited |

Total 12, no zero → **Accept**.

## Evaluator totals

| Sample | C | V | S | R | M | H | Total | Verdict |
|---|---|---|---|---|---|---|---|---|
| B1 CI to green | 2 | 1 | 2 | 2 | 2 | 1 | 11 | Accept |
| B2 Bridge residuals | 2 | 1 | 2 | 1 | 2 | 1 | 10 | Accept |
| B3 D72 + D73 | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Accept |
| B4 ZH-TW + v0.7.0 | 2 | 2 | 2 | 2 | 2 | 2 | 12 | Accept |

Cross-sample observation: every 1 in this round sits in
Verification, Reliability or Handover, and each traces to an
evidence-handling slip by the deliverer (fabricated sub-report
trusted too long, wrong evidence source watched, a status
misreported), never to the shipped artefact being wrong. The
artefacts verified clean every time they were finally checked
properly. Open question for the judge: is "the work was right but
the reporting wobbled" a 1 in your reading too, or should
reporting quality live outside this rubric?
