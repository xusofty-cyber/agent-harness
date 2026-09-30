---
name: comet
description: Use Comet when this project has it configured or the user explicitly requests it. Check the installed version and project configuration before following version-specific steps.
license: Apache-2.0
---

# Comet workflow integration

Comet is an independently versioned workflow tool. This skill is an entry-point guide; it does not implement Comet's state machine, hooks, phase guards, or archive behavior by itself.

## How to use

1. Check whether the project has Comet configuration (`.comet/config.yaml`) and inspect the installed CLI version when available.
2. Follow the workflow and commands supported by that installed version. Comet versions may provide Native and Classic workflows with different artifact layouts and phase behavior.
3. Preserve Comet's project state and artifacts. Do not invent state files, phase names, commands, automatic approval gates, or guard behavior.
4. If Comet is not installed/configured, explain that this repository's Markdown skill alone does not provide CLI enforcement. Continue with the user's requested workflow or use the project's configured planning/spec process.
5. Do not run `comet init`, `comet update`, or archive/publish actions unless the user requested the corresponding project change.

Consult current upstream documentation for version-specific behavior: <https://github.com/rpamis/comet>.
