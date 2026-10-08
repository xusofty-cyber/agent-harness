---
name: cross-tool-memory
description: Use when continuing prior work or making durable coding, research, documentation, or design decisions in a project with ai-memory configured.
version: 0.1.0
---

# Cross-Tool Project Memory

Use ai-memory as a project-scoped navigation aid. It supplements repository rules and canonical documents; it never overrides the current user request, source code, configuration, or reproducible evidence.

## Recall

- When the MCP server is configured and reachable, query the current project's memory before substantial coding, research, documentation, or design work. Ask for the relevant decision, rationale, unresolved issue, or handoff rather than loading broad history.
- Verify recalled claims against current files and authoritative sources before acting. Treat old plans and remembered preferences as stale until confirmed.
- If the service or MCP tools are unavailable, continue with repository files such as `PROJECT_CONTEXT.md`, `SESSION_STATE.md`, and the relevant `AGENTS.md`; do not block the task or try to install/start the service automatically.
- For ChatGPT web without an available MCP connection, use a concise, human-mediated Markdown handoff. Do not claim that a local service is connected to the web chat.

## Retain

At meaningful task boundaries, retain only facts that are verified and likely to help a later task: durable architecture or constraints, confirmed decisions and rationale, reproducible lessons, documentation/design decisions, and actionable handoffs. Keep entries concise, project-scoped, dated when time-sensitive, and linked to canonical files or sources where practical.

Do not retain credentials, private keys, raw personal data, full conversations, full tool logs, large source excerpts, unverified assumptions, or transient details. Do not duplicate maintained documentation. Correct or remove memories that are stale, contradicted, or no longer useful.

## Privacy and availability

Automatic capture is available only when an operator has installed the native ai-memory hooks in allowlist mode and explicitly opted the repository in with a local `.ai-memory.toml`. Path exclusions do not redact arbitrary prompt text. Never put secrets into prompts or memory. Normal work must remain possible without the binary, server, hooks, MCP connection, or API credentials; default ai-memory operation uses no LLM or embedding provider.
