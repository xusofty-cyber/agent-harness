---
name: codegraph
description: "Code knowledge graph and AST-level symbol exploration tool. Replaces blind full-repo grep with semantic symbol lookups, callers/callees tracing, and impact analysis via codegraph explore. Use whenever exploring unfamiliar code, finding definitions/references, or evaluating refactoring blast radius."
license: MIT
---

# CodeGraph: AST-Based Code Knowledge Graph

CodeGraph provides structural understanding of multi-file codebases, drastically reducing token consumption compared to blind full-repository text searches (saving 90%+ reading tokens).

## Core Capabilities

1. **Symbol Definition & Lookup**: Rapidly find where classes, structs, functions, or interfaces are defined without scanning irrelevant mock data.
2. **Call Hierarchy & Callers**: Identify who calls a given method across the entire repository.
3. **Impact Analysis (Blast Radius)**: Determine which modules will be affected before renaming or altering a signature.

## Commands & Usage

```bash
# Explore a concept or architecture flow
codegraph explore "order checkout pipeline"

# Trace symbol references and call hierarchy
codegraph explore "UserService::validateCredentials"

# Check indexing status
codegraph status
```

## Agent Integration Rules

- **Subagent / CLI Rule**: Subagents do not inherit MCP server instructions. Use CLI `codegraph explore "<query>"` for both main agent and subagents.
- **Fallback Rule**: If CodeGraph index is uninitialized, stale, or querying non-code assets (e.g. YAML, JSON, Markdown), fall back to targeted `grep` with strict path limits.
