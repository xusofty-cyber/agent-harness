---
name: rtk
description: "Optional Rust Token Killer CLI integration that rewrites supported terminal commands to concise output. Use when RTK is installed and its hook is configured for the current agent."
license: MIT
---

# RTK (Rust Token Killer)

This repository ships guidance only. It does not install RTK or enable its command-rewrite hook. The unrelated Rust Type Kit project also uses the `rtk` command name; verify this tool with `rtk gain`.

## Check availability

- Use RTK rewriting only when the CLI and the current agent integration are configured. RTK setup is performed with `rtk init` for a project or `rtk init --global` for supported global integrations.
- If RTK is unavailable or not active for the current agent, use the normal CLI with quiet flags and bounded output. Do not assume an ordinary shell command is automatically rewritten.
- Never skip required validation merely to reduce output. Keep concise summaries and preserve detailed logs locally when useful.

## Safe output handling

- Prefer tool-native concise options such as `pytest -q` or `ctest --output-on-failure` where suitable.
- For verbose commands, redirect output to a local temporary log and report relevant errors; do not expose secrets from logs.
- Treat filtered output as a presentation aid, not proof that omitted checks passed.
