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
| README.zh-tw.md | README.md | in-sync | 2432c5e99ca3 | Regenerated from EN (base main e9b32ab) |
| docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | in-sync | b99ed7e36870 | Regenerated from EN (base main e9b32ab) |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 00305df7d61e | Regenerated from EN (base main e9b32ab); MD012 extra blank line fixed; §2.3 pinned versions match EN |
| docs/guides/Skills Usage Guide.zh-tw.md | docs/guides/Skills Usage Guide.md | in-sync | d1297c2d3797 | Regenerated from EN (base main e9b32ab) |
| templates/agents/Global AGENTS.zh-tw.md | templates/agents/Global AGENTS.md | in-sync | 0794aec75e66 | Checked against Global AGENTS.en.md (base main 5fd31c7); restored the dropped source-of-truth line, rest already faithful |
| templates/agents/Project AGENTS.zh-tw.md | templates/agents/Project AGENTS.md | in-sync | fd6b35ddfd15 | Source and target last changed in the same commit (f3f3568, Phase 0-6) |
| templates/agents/Directory AGENTS.zh-tw.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
