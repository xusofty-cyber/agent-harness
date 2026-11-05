# Round 6 (first LIVE round) — evaluator scores — SEALED

Sealed: 2026-11-06 (Asia/Shanghai), before the judge's pass.
Evaluator: maintainer agent. Judge: repo owner (live second
person, per D28). Samples: MedOnTime completed work units, per
`docs/exec-plans/active/2026-11-06-d28-live-calibration-and-eval.md`.
Scoring per `eval/rubric.md` (6 dimensions × 0–2; Block = any 0;
Accept = total ≥ 9 and no 0; else Revise), from artifacts and
re-run acceptance wherever an acceptance command exists.

Authorship flags (independence caveat from the plan): A1 executed
by a delegate under the evaluator's supervision; A2, A3, A4
delivered by the evaluator. The independent side is the judge.

## Cross-sample note (evaluator's systemic observation)

Verification scored 1 on all four samples. In this body of work
no sample offered a single acceptance command the evaluator could
fully re-run end-to-end today: A1's acceptance was a report +
disposition table, A2's defining acceptance lives on the judge's
physical device, A3's was re-runnable only in part (unit suites),
A4's is production-bound. Open question for the calibration
discussion: is Verification-2 achievable for device/production
work under the current anchor wording, or is the anchor biased
toward bench-shaped tasks?

## A1 — Code-review fix batch F1 (backend, 42 findings)

Evidence: medontime-review/code-review-2026-10-24/R1-backend.md
(42 findings) and FIXLOG-backend.md (final: 39 FIXED / 2 BY-DESIGN
/ 1 DEFERRED, with a real statistics section; build + tsc both
Exit 0 recorded). Evaluator spot re-check 2026-11-06: the CAS fix
for finding 19 is present in
services/api/src/modules/authorization/authorization.service.ts
(updateMany with version check). Known history: mid-run, the
FIXLOG stood at 21/42 entries and a patrol pass misjudged the
batch complete; the error was caught by an independent
line-count rule and the batch was then finished (part-2 run).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Final disposition complete and honest: every finding fixed or ruled (BY-DESIGN / DEFERRED) with per-item evidence |
| Verification | 1 | Build + typecheck green and spot re-check passed, but acceptance was not one re-runnable command, and the mid-run completion signal was false — caught by an outside tripwire, not by the batch's own verification |
| Scope discipline | 2 | Changes confined to the findings; non-fixes dispositioned, not silently expanded |
| Reliability | 1 | The acceptance signal was time-dependent: the same "is it complete?" question returned different answers at 21/42 and at 42/42 |
| Maintainability | 2 | FIXLOG + reports structured and in the repo's review conventions |
| Handover readiness | 1 | The intermediate run record misled a fresh reader (the patrol) into a wrong completion judgment — S2-adjacent: the record did not reflect true progress |

Total 9, no zero → **Accept** (at threshold).

## A2 — Android 0.3.5 background-reminder fix

Evidence: med-on-time commit 6ab5cba (ReminderGuardService
foreground service, alarm-clock-grade next dose, battery-exemption
+ autostart guidance in Settings), CI Android job green, GitHub
Release published (manual-31). Defining acceptance — notification
fires after the app is swiped away, on the owner's device, with
exemptions granted — is still pending the owner's retest.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Targets the diagnosed root cause (OEM process freezing) with the three mechanisms the diagnosis implied; code present and scoped |
| Verification | 1 | Compiled in CI and released, but the item's defining acceptance has not been re-run (device-bound, pending) |
| Scope discipline | 2 | Single-purpose fix; remaining diff files are release bookkeeping |
| Reliability | 1 | Outcome is OEM-ROM-dependent by nature; unproven across devices |
| Maintainability | 2 | Follows the existing reminder architecture; guard lifecycle wired at app/login/boot |
| Handover readiness | 2 | SESSION_STATE + release notes carry the exact retest checklist; what remains is unambiguous |

Total 10, no zero → **Accept**.

## A3 — Phone-number registration channel (AUTH-CHANNEL ruling)

Evidence: auth.service.ts implements phone-as-root with
phoneVerifiedAt gating; WeChat getPhoneNumber verification path;
the three unverified-phone restrictions enforced in auth,
authorization and notification code (inspected 2026-11-06).
Evaluator re-run 2026-11-06: `npx jest src/modules/auth` —
7/7 suites PASS (incl. auth-email, auth-wechat-bind). Known
history: the delivery was initially reported complete after only
the email path had been verified; the gap was self-caught on a
later patrol, corrected in the records, and the phone path's
real-device check remained pending at delivery time.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Final implementation matches the ruling on every point inspected |
| Verification | 1 | Delivery-time verification covered one channel while the claim covered all; today's re-run passes, but that repairs the present, not the delivery record |
| Scope discipline | 2 | Changes stayed within the ruled auth scope and its restrictions |
| Reliability | 2 | Server-side enforcement in three modules; deterministic unit evidence now green |
| Maintainability | 2 | Module conventions followed; spec suites added alongside the code |
| Handover readiness | 1 | S2: the delivery record omitted a known deviation (unverified phone path) when first reported |

Total 10, no zero → **Accept**.

## A4 — Official-account trio (2026-10-24)

Scope: strong-alert mode per ruling N-1; ai_provider_config table
+ admin "LLM config" page with test-connection; photo-recognize
endpoint returning drug-name candidates for user selection only
(never fabricating data). Evidence: AiProviderConfig model +
migration 20261024100000_v14 (and v15/v16), admin page
apps/admin/src/pages/ai-providers/, POST /drugs/photo-recognize
in drug.controller.ts — all present (inspected 2026-11-06);
production application of migrations and deployment recorded at
delivery time. Evaluator could not re-run production acceptance
(standing rule: production services are not touched without an
instruction).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | All three delivered as ruled, including the never-fabricate constraint on photo-recognize |
| Verification | 1 | Strong recorded deployment evidence, but no end-to-end re-run available to the evaluator (production-bound; photo path depends on an external model API) |
| Scope discipline | 2 | Confined to the three ruled features |
| Reliability | 1 | Two legs are deterministic; the photo-recognition leg depends on an external model's availability and quality |
| Maintainability | 2 | DB-backed config + admin UI follows the repo's config patterns; migrations versioned |
| Handover readiness | 2 | State and follow-ups (menu configuration) recorded and later closed the same day |

Total 10, no zero → **Accept**.

## Evaluator totals

| Sample | C | V | S | R | M | H | Total | Verdict |
|---|---|---|---|---|---|---|---|---|
| A1 | 2 | 1 | 2 | 1 | 2 | 1 | 9 | Accept |
| A2 | 2 | 1 | 2 | 1 | 2 | 2 | 10 | Accept |
| A3 | 2 | 1 | 2 | 2 | 2 | 1 | 10 | Accept |
| A4 | 2 | 1 | 2 | 1 | 2 | 2 | 10 | Accept |

Seal note: this file is committed before the judge's pass is
requested; the commit timestamp is the seal. Judge results and
divergence handling are appended to `eval/calibration.md` as the
Round 6 record, per the plan.
