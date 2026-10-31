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
| README.zh-tw.md | README.md | stale | 59c9fba1f1e2 | EN changed in the v0.4.1 convergence round (host-verification-matrix wording in the support table and current-status section, synced to ZH in the same change); ZH-TW not regenerated per the frozen-translation policy — regenerate at release time |
| docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | stale | 849ec7008f74 | EN changed (Q3 title 40+ → 39+, dsh paragraph parenthetical now English); Q3 title synced to ZH-TW; ZH-TW not fully regenerated per frozen-translation policy, write_file live-name fix + live-run verification status still owed |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 4f56582587b8 | EN TOC §2.4 aligned to body heading (Skill Loading and Optional CLI Setup); ZH-TW TOC already matched its body, no text change needed |
| docs/guides/Skills Usage Guide.zh-tw.md | docs/guides/Skills Usage Guide.md | in-sync | d1297c2d3797 | Regenerated from EN (base main e9b32ab) |
| templates/agents/Global AGENTS.zh-tw.md | templates/agents/Global AGENTS.md | in-sync | 0794aec75e66 | Checked against Global AGENTS.en.md (base main 5fd31c7); restored the dropped source-of-truth line, rest already faithful |
| templates/agents/Project AGENTS.zh-tw.md | templates/agents/Project AGENTS.md | stale | fd6b35ddfd15 | Source updated in v0.5.2 audit fix to wire gate/pass-gate.py into DoD; regenerate ZH-TW before release |
| templates/agents/Directory AGENTS.zh-tw.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
| templates/SESSION_STATE.template.zh-tw.md | templates/SESSION_STATE.template.md | in-sync | (v0.4.1 regeneration) | Regenerated from the EN base in the D61 31-line breakpoint format during the v0.4.1 convergence round (was a 46-line legacy format, flagged as drift by lint-rules LINT-006); content mirrors the base section-for-section |
| docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | stale | 849ec7008f74 | Deliberately NOT regenerated in v0.4.1: full-guide regeneration is a release-time task on the ZH-TW regeneration branch. Until then this file is knowingly behind EN — v0.4.1's host-verification wording (README EN/ZH) does not depend on it. Do not cite the ZH-TW guide for v0.4.x enforcement status; use `docs/internal/host-verification-matrix.md` |
