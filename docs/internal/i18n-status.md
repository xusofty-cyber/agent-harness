# i18n status — FR/DE/ZH-TW translations (Phase 4, 4-2)

EN/ZH are the sources of truth. FR/DE/ZH-TW are **generated products**:
when an EN source changes, the translation is regenerated from it (by a
translator or an agent working from the EN source) and spot-checked — it is
never hand-synced sentence by sentence across five files. That is why the
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
| README.zh-tw.md | README.md | stale | 3ee95251d864 | EN changed in Phase 4-1d (profile notes); last synced at 7aadadf |
| README.fr.md | README.md | stale | 3ee95251d864 | EN changed in Phase 4-1d (profile notes); last synced at 7aadadf |
| README.de.md | README.md | stale | 3ee95251d864 | EN changed in Phase 4-1d (profile notes); last synced at 7aadadf |
| docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | in-sync | c702baf26aa3 | Target touched after source's last change (2026-10-20 vs 2026-10-14) |
| docs/guides/Multi-Tool Deployment and Configuration Guide.fr.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | in-sync | c702baf26aa3 | Target touched with source's last change (2026-10-14) |
| docs/guides/Multi-Tool Deployment and Configuration Guide.de.md | docs/guides/Multi-Tool Deployment and Configuration Guide.md | in-sync | c702baf26aa3 | Target touched after source's last change (2026-10-20 vs 2026-10-14) |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 160ef6246eff | Source and target last changed in the same commit (7aadadf) |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.fr.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 160ef6246eff | Source and target last changed in the same commit (7aadadf) |
| docs/guides/Tools Practical Usage and Skills Panorama Guide.de.md | docs/guides/Tools Practical Usage and Skills Panorama Guide.md | in-sync | 160ef6246eff | Source and target last changed in the same commit (7aadadf) |
| docs/guides/Skills Usage Guide.zh-tw.md | docs/guides/Skills Usage Guide.md | stale | 99a37475bf2e | EN changed in Phase 4-1d (tier section added, `##` 12→13); last synced at b2b73b4 (2026-10-16) |
| docs/guides/Skills Usage Guide.fr.md | docs/guides/Skills Usage Guide.md | stale | 99a37475bf2e | EN changed in Phase 4-1d (tier section added, `##` 12→13); last synced at 5b100f2 (2026-10-16) |
| docs/guides/Skills Usage Guide.de.md | docs/guides/Skills Usage Guide.md | stale | 99a37475bf2e | EN changed in Phase 4-1d (tier section added, `##` 12→13); last synced at 39de8b5 (2026-10-16) |
| templates/agents/Global AGENTS.zh-tw.md | templates/agents/Global AGENTS.md | stale | e670c1fb9a40 | EN changed in Phase 0-11 (terminology ruling line, EN+ZH only); last synced at f98adbb (2026-10-16) |
| templates/agents/Global AGENTS.fr.md | templates/agents/Global AGENTS.md | stale | e670c1fb9a40 | EN changed in Phase 0-11 (terminology ruling line, EN+ZH only); last synced at f98adbb (2026-10-16) |
| templates/agents/Global AGENTS.de.md | templates/agents/Global AGENTS.md | stale | e670c1fb9a40 | EN changed in Phase 0-11 (terminology ruling line, EN+ZH only); last synced at f98adbb (2026-10-16) |
| templates/agents/Project AGENTS.zh-tw.md | templates/agents/Project AGENTS.md | in-sync | fd6b35ddfd15 | Source and target last changed in the same commit (f3f3568, Phase 0-6) |
| templates/agents/Project AGENTS.fr.md | templates/agents/Project AGENTS.md | in-sync | fd6b35ddfd15 | Source and target last changed in the same commit (f3f3568, Phase 0-6) |
| templates/agents/Project AGENTS.de.md | templates/agents/Project AGENTS.md | in-sync | fd6b35ddfd15 | Source and target last changed in the same commit (f3f3568, Phase 0-6) |
| templates/agents/Directory AGENTS.zh-tw.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
| templates/agents/Directory AGENTS.fr.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
| templates/agents/Directory AGENTS.de.md | templates/agents/Directory AGENTS.md | in-sync | 911d13caaf6f | Source and target moved together (2026-10-13 templates move) |
