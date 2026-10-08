# Cross-Tool Local Memory Integration Design

**Status:** Approved by user
**Date:** 2026-10-07
**Scope:** One free, local memory backend for coding and documentation/design work across Codex, Claude Code, and Antigravity; preserve the earlier global/project/directory rule and deployment changes.

## 1. Purpose

Integrate one long-term memory backend into this repository so agents can carry verified project decisions, active work, and documentation/design context across supported tools. The solution must work without a paid memory service, LLM API key, or embedding API key in its default mode.

## 2. Decision

Select **ai-memory** as the only integrated backend.

Its documented default is local Markdown memory with zero LLM calls. Its support matrix lists Claude Code, Codex, and Antigravity CLI; its MCP server can be configured in Antigravity IDE. Current Windows guidance documents both WSL2 and native Windows modes and requires installing/configuring ai-memory in the same environment that launches the agent. [Project README](https://github.com/akitaonrails/ai-memory) [Windows guidance](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md)

Hindsight is not selected because the integrated route for ChatGPT uses Hindsight Cloud, while its local daemon requires additional local model/runtime setup. Memmy is not selected because its documented integrations do not list Antigravity CLI/IDE. Neither is installed or configured by this change.

## 3. Supported surfaces and honest limits

| Surface | Integration | Boundary |
|---|---|---|
| Claude Code | ai-memory lifecycle hooks, MCP, and skill/instruction bridge | Install through ai-memory's supported merge-aware CLI; preserve unrelated hooks and settings |
| Codex CLI | ai-memory hooks and MCP | Local user configuration; require the host's hook trust review where applicable |
| Codex desktop app | Codex hook configuration shared with the Codex runtime | Verify against current Codex docs and installed version; do not assume app and CLI have identical runtime environments |
| Antigravity CLI | ai-memory's documented native hooks/MCP integration | WSL2/Linux setup is the supported Windows route |
| Antigravity IDE | Manually configured MCP connection plus the repository's shared Skill and rule files | The IDE is an MCP client; do not claim ai-memory has a first-party IDE hook adapter |
| ChatGPT web | Manual handoff to/from the same human-readable project memory | A free, loopback-only local service cannot be called directly by ChatGPT web. Remote MCP and write support depend on ChatGPT account features; this project will not require a tunnel, paid plan, or hosted service |

The support basis is the [ai-memory integration and install documentation](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) and [Antigravity MCP documentation](https://www.antigravity.google/docs/mcp). OpenAI documents Codex hooks in local configuration and plugin hook support in Codex desktop; verify exact runtime availability before making an installed-host claim. [Codex hooks](https://developers.openai.com/codex) [Codex plugin hooks](https://developers.openai.com/plugins/build/plugins)

## 4. Memory scopes and content

| Scope | Source of truth | Memory behavior |
|---|---|---|
| Global | Shared `Global AGENTS.md`; user-controlled machine-local settings | Store reusable behavior rules in the template. Do not create a global cross-project personal memory bank or commit personal preferences |
| Project | Repository source, canonical docs, and one local ai-memory project namespace | Share verified architecture, decisions/rationale, coding conventions, document/design decisions, lessons, and actionable session handoffs across agents |
| Directory | Nearest `Directory AGENTS.md` and the files in that subtree | Keep normative local constraints in that file. Memory remains project-scoped unless an operator explicitly configures a narrower namespace; do not create nested memory stores by default |
| ChatGPT web | Same checked-in or user-visible project Markdown files | Copy a concise handoff or design summary manually; no automatic cloud connection is promised |

Memory is a navigation aid, not authority over current user instructions, source code, configuration, or maintained design documents. A remembered design decision must link to or be reconciled with its canonical project document where practical.

## 5. Capture, privacy, and operation

- Run a local ai-memory server/binary and its MCP endpoint on loopback. The default setup uses no LLM/embedding provider and no API key; optional LLM features remain off and out of scope.
- Use ai-memory's allowlist capture mode. A repository is not captured until the user explicitly opts it in with a local marker/config. Do not check in a marker that silently opts every clone into capture.
- Use the supported client-side sanitization and path exclusions. Never persist credentials, private keys, raw personal data, or unnecessary full transcripts. Keep capture bounded to opted-in project work; allow explicit no-prompt capture where supported by the host.
- Favor concise, durable project facts and handoffs across coding, research, UI/document design, and technical writing. Remove stale or contradicted memories when found.
- Keep `PreToolUse` security hooks separate from memory hooks. Install ai-memory through its own official installer so it merges its event handlers; never replace the repository's existing Claude security hook configuration.
- Memory service failure must not block normal agent use. Installation, opt-in, and uninstall must be explicit and reversible.

## 6. Repository integration

The implementation plan will:

1. Add one shared `.agents/skills/ai-memory/SKILL.md` describing when to recall, what to retain, how to cite/verify memory, and how to use the same project memory for code and document/design tasks.
2. Update Global/Project/Directory templates to describe the local backend, opt-in capture, memory scope, privacy, and current-evidence precedence without adding project-specific facts to the generic global template.
3. Add a sample local configuration/marker that is safe by default and is not an automatic opt-in. Provide a setup/teardown wrapper or documented commands that call ai-memory's own merge-aware installer; do not download/install a binary or alter user-global settings during normal rule deployment.
4. Update PowerShell/Bash deployment scripts with an explicit memory integration switch only if it can preserve existing config and call the supported ai-memory CLI without introducing a second installer implementation. Otherwise expose a separate setup helper and keep `deploy-agents` focused on templates.
5. Update Chinese and English guides, including Codex desktop/CLI distinctions, Antigravity IDE MCP setup, WSL2 as the supported Windows path, ChatGPT web manual handoff, local data location, capture controls, backup/export, and uninstall.
6. Update `PROJECT_CONTEXT.md` and `SESSION_STATE.md` with the selected backend, integration scope, verification actually performed, and known host limitations.

No backend binary, Docker image, model, credential, network endpoint, or ChatGPT connector is provisioned by the repository's default deploy command.

## 7. Non-Goals

- Integrating more than one of Hindsight, Memmy, or ai-memory.
- Requiring any API key, paid cloud memory account, hosted MCP server, or automatic tunnel.
- Claiming automatic ChatGPT web integration under a free ChatGPT account.
- Replacing Markdown rules or canonical documentation with opaque generated memory.
- Automatically creating directory-specific memory databases.
- Capturing all user data from every repository on the machine.

## 8. Compatibility and Failure Behavior

- The portable file-based workflow continues to work when ai-memory is not installed or its service is stopped.
- On Windows, document both upstream-supported WSL2 and native Windows modes; emphasize that installation/configuration must run in the same environment as the agent and that hook payload/capture-policy support can differ by client/platform.
- Installer commands must be idempotent and preserve unrelated user hooks/settings. Never commit tokens or local endpoints containing credentials.
- If a host lacks the required hook event, use its documented MCP + shared Skill route and label the limitation; do not emulate hooks by silently scanning transcripts.
- ChatGPT web remains a manual handoff unless the user later chooses an accessible remote MCP deployment and has account-level write support.

## 9. Verification

- Verify scripts and configuration templates by syntax/static checks and diff review; do not install the backend or mutate the user's global tool setup as part of repository verification.
- Confirm all opt-in defaults fail closed, existing hook handlers are preserved, and an absent local service does not stop agent use.
- Review English/Chinese docs for the same support matrix and no-key/local guarantees.
- Do not add or run automated tests under the existing user-approved verification constraint.

## 10. Self-Review

- One backend is selected and its no-key/default-local constraint is explicit.
- Codex CLI and desktop are both named; app behavior remains version-verified rather than inferred.
- Antigravity IDE is explicitly MCP-based, not described as a first-party ai-memory hook integration.
- ChatGPT web's free/local boundary is explicit and has a usable manual fallback.
- Capture is project-opt-in; global personal memory and automatic per-directory stores are excluded.
