# Rubric calibration log — Phase 3

Status: **calibrated (5 rounds, 0 verdict divergences)**. NOT yet `stable`:
the "human" side in all five rounds below is the recorded outcome from
phase reports and acceptance commands, not a live second judge. A live
second-person calibration round is still owed before the rubric is marked
`stable`.

Method per round: the evaluator (this session) scores the item per
dimension with reasoning, gives a verdict, and compares it with the known
outcome. A divergence is a verdict mismatch; any divergence must change
the rubric wording or the scoring, and the change is recorded here.

## Round 1 — Phase 1 dogfood-1 (SESSION_STATE migration)

Source: `docs/internal/phase1-dogfood.md` (real run, 2026-10-28).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Migration done; 28-line breakpoint format; verify PASS |
| Verification | 2 | Acceptance re-run by CI §3k; planted fake caught only by re-run |
| Scope discipline | 1 | One extra change: a stale breakpoint line fixed along the way |
| Reliability | 2 | Deterministic re-runs, no flakiness observed |
| Maintainability | 2 | Follows the new SESSION_STATE template |
| Handover readiness | 2 | Handover test ~1 s; check-clean 6/6 |

Total 11 → **Accept**. Known outcome: Phase 1 Go-gate passed.
**Agreement: yes.**

Rubric change from this round: the header now states explicitly that
verification requires **re-running** the acceptance command, never trusting
the agent's claim — the fake pass was well-formed JSON and only the re-run
caught it.

## Round 2 — Phase 2 comet interruption recovery

Source: `docs/internal/phase2-verification.md` (real run, 2026-10-28).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | stateVersion preserved (2); auto_resume high confidence; doctor passed |
| Verification | 2 | `native status` / `next` / `doctor` all re-run and observed |
| Scope discipline | 2 | Only the recovery probe; nothing else touched |
| Reliability | 1 | One `next` call failed (exit 64, missing input) and confirmation went stale; guard worked as designed, but the run itself needed a revise loop |
| Maintainability | 2 | Steps recorded reproducibly in phase2-verification.md |
| Handover readiness | 2 | A new session can repeat the probe from the record alone |

Total 11 → **Accept**. Known outcome: Phase 2 Go-gate item 2 passed.
**Agreement: yes.** No rubric change.

## Round 3 — Bare-arm run T3 rep1 (cross-file rename)

Source: `eval/results/t3-cross-file_bare_rep1.json` (real run, 2026-10-28).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Rename complete; `cli.py times 2 3` prints `Result: 6.0` |
| Verification | 2 | Acceptance re-run by the evaluator exits 0 |
| Scope discipline | 1 | The mechanical `sed` rename also rewrote the fixture docstring ("T3 renames multiply to times" → "T3 renames times to times") — one unrelated change inside a touched file |
| Reliability | 2 | Deterministic; same acceptance passes on re-run |
| Maintainability | 2 | Follows existing code style |
| Handover readiness | 2 | Task spec + run record are sufficient to continue |

Total 11 → **Accept**. Known outcome: acceptance pass.
**Agreement: yes.** No rubric change. (The scope-1 anchor "one unrelated
change inside a touched file" was exercised here and fits.)

## Round 4 — Pre-Phase-0 distribution pack, retrospective

Source: v1 diagnosis + v3 K1 (repo at `97b01a2`, before Phase 0).

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 1 | Distributes rules/skills and deploys; but what it claims to be (a harness) it is not |
| Verification | 0 | Fake-green: `|| true` + unconditional PASS; doc-impact/sync-skills exit 0 always — checks passed while verification was hollow |
| Scope discipline | 1 | 40 skills, no tiering; undisciplined but not the failing dimension |
| Reliability | 1 | Works in the author's environment; hooks fail on non-Claude hosts |
| Maintainability | 1 | 156-line AGENTS.md; duplicated `.comet/config.yaml` |
| Handover readiness | 0 | No SESSION_STATE discipline, no clean-state check; a new session cannot tell what was done or next |

Total 5, contains 0s → **Block**. Known outcome: v1 diagnosis "not a
harness" + v3 consensus K1.
**Agreement: yes.** No rubric change. (The rubric correctly Blocks the
pre-Phase-0 state — the negative control works.)

## Round 5 — Full-matrix run T3 gate rep1 (cross-file rename, gate arm)

Source: `eval/results/t3-cross-file_gate_rep1.json` (real run, 2026-10-28,
fresh executor session). Scores the gate-arm run of the same task as
round 3, to check the scope dimension now that the executor rewrote the
fixture docstrings sensibly instead of mechanically.

| Dimension | Score | Reasoning |
|---|---|---|
| Correctness | 2 | Rename complete; `cli.py times 2 3` prints `Result: 6.0`; acceptance passes |
| Verification | 2 | Acceptance re-run by `pass-gate.py verify`; `status` confirms `passing` with evidence |
| Scope discipline | 2 | Exactly the 5 task files changed (14 insertions / 14 deletions, pure rename); both docstrings rewritten sensibly ("renames the old operation to times") — no "times to times" nonsense, unlike the bare rep1 scope-1 case |
| Reliability | 2 | Deterministic; same acceptance passes on re-run (and in rep2/rep3) |
| Maintainability | 2 | Follows existing code style |
| Handover readiness | 2 | Task spec + run record are sufficient to continue |

Total 12 → **Accept**. Known outcome: acceptance pass.
**Agreement: yes.** No rubric change. (The scope-2 anchor "only files
the task touches are changed" holds here; the contrast with round 3's
scope 1 shows the dimension discriminates the docstring handling.)

## Summary

| Round | Item | Rubric verdict | Known outcome | Agreement |
|---|---|---|---|---|
| 1 | Phase 1 dogfood-1 | Accept (11) | Go-gate passed | yes |
| 2 | Phase 2 comet recovery | Accept (11) | Go-gate passed | yes |
| 3 | T3 bare rep1 | Accept (11) | acceptance pass | yes |
| 4 | Pre-Phase-0 pack (retrospective) | Block (5) | "not a harness" | yes |
| 5 | T3 gate rep1 | Accept (12) | acceptance pass | yes |

5 rounds, 0 divergences, 1 wording change (re-run rule). Next step for
`stable`: one live second-person calibration round.
