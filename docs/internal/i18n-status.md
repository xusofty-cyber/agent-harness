# i18n status — ZH-TW translations (Phase 4, 4-2)

EN/ZH are the sources of truth. ZH-TW is a **generated product**:
when an EN source changes, the translation is regenerated from it (by a
translator or an agent working from the EN source) and spot-checked — it is
never hand-synced sentence by sentence across three files. That is why the
old symmetric `##`-count hard check is gone (v2 4-2): a translation being
behind is tracked debt, not a CI failure.

## Statuses

| Status | Meaning | CI effect |
|---|---|---|
| `in-sync` | Translation matches the EN source at the recorded sha. | `tools/i18n-check.py` verifies the sha; mismatch FAILS. |
| `stale` | EN source moved after the recorded sha; regeneration owed before the next release. | Passes with a printed reminder. |
| `frozen` | Deliberately untouched this phase (D3 freeze); regenerate at release time. | Same as `stale`. |

## Workflow

1. EN source changes → the translator/agent regenerates the FR/DE/ZH-TW
   file from the new EN source.
2. Update this table: status `in-sync`, sha = first 12 hex of
   `sha256sum` of the EN source.
3. Before a release, run `python3 tools/i18n-check.py --spot-check 5` and
   have a human read the sampled sections against their sources.
4. `in-sync` basis for the rows below is `##`-count parity plus the target
   having been touched after (or with) its source's last change. Content
   was **not** line-verified — that is what the spot-check is for.

## Status table

| Target | Source | Status | Source SHA (last synced) | Note |
|---|---|---|---|---|
| README.zh-tw.md | README.md | in-sync | da63a5b0dc18 | Regenerated 2026-11-06 (v0.7.0 round): support-matrix Antigravity row + host-dependence and Windows bullets synced to the EN source (live-verified tier wording incl. desktop global registration; CI ps1 smoke discharged); 2026-11-06 index addition for the Project Deployment Walkthrough guide synced the same day (EN/ZH links only — the new guide has no ZH-TW edition) |
| docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | in-sync | 12a5878b8099 | Regenerated 2026-11-06: new §4.5 per-surface hook wiring & isolation section (from the 2026-11-06 live-verification round) added in EN/ZH/ZH-TW together; the rest of the guide was verified current against the EN source (title/Q3 counts already matched) |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 4f56582587b8 | EN TOC §2.4 aligned to body heading (Skill Loading and Optional CLI Setup); ZH-TW TOC already matched its body, no text change needed |
| docs/guides/Skills Usage Guide.zh-tw.md | docs/guides/Skills Usage Guide.md | in-sync | d1297c2d3797 | Regenerated from EN (base main e9b32ab) |
| templates/agents/Global AGENTS.zh-tw.md | templates/agents/Global AGENTS.md | in-sync | f9d8d538d800 | Regenerated 2026-11-06: the D71 expert-panel section replaced by the Multi-Angle Deterministic Review protocol, matching the EN source section-for-section |
| templates/agents/Project AGENTS.zh-tw.md | templates/agents/Project AGENTS.md | in-sync | d8a1d3f809b4 | Regenerated 2026-11-06: Definition-of-Done gained the pass-gate paragraph and gate steps (verify + check-clean), matching the EN source |
| templates/agents/Directory AGENTS.zh-tw.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
| templates/SESSION_STATE.template.zh-tw.md | templates/SESSION_STATE.template.md | in-sync | (v0.4.1 regeneration) | Regenerated from the EN base in the D61 31-line breakpoint format during the v0.4.1 convergence round (was a 46-line legacy format, flagged as drift by lint-rules LINT-006); content mirrors the base section-for-section |
