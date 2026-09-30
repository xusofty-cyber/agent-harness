---
name: codegraph
description: "Optional CodeGraph integration for semantic code exploration through its agent MCP tools. Use when CodeGraph tools are available and the task needs cross-file definitions, callers, or impact analysis."
license: MIT
---

# CodeGraph

This repository ships this guidance file. It does not install the CodeGraph CLI, configure an agent MCP connection, or create a project index.

## Check availability

- If CodeGraph MCP tools are available in the current agent, use them for semantic exploration.
- Otherwise check whether `codegraph` is installed and configured. The CLI installs the agent connection with `codegraph install`; initialize a project from its root with `codegraph init`.
- The CLI manages installation, agent configuration, and indexing. Semantic queries are made through the configured agent MCP tools; do not assume a `codegraph explore` CLI command exists.
- If unavailable or not initialized, use targeted file search (`rg`) and state that CodeGraph was unavailable. Do not block routine work on an optional tool.

## Use appropriately

- Use CodeGraph for cross-file symbol relationships, callers, and change impact when its MCP tools are connected.
- Use ordinary targeted search for exact text, configuration, documentation, and non-code assets.
- Treat graph results as navigation evidence; read the relevant source before editing.
