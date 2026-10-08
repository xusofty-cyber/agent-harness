#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <claude-code|codex|antigravity|antigravity-ide|antigravity-cli>\n' "$0" >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
agent="$1"
case "$agent" in
  claude-code|codex|antigravity|antigravity-ide|antigravity-cli) ;;
  *) usage ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
marker="$repo_root/.ai-memory.toml"
if [[ ! -f "$marker" ]]; then
  printf 'Memory is not enabled for this repository. Review .ai-memory.toml.example, create a local .ai-memory.toml with your chosen workspace/project, then rerun.\n' >&2
  exit 1
fi
if grep -Eq 'replace-with-' "$marker"; then
  printf 'Replace the example workspace/project values before installing integrations.\n' >&2
  exit 1
fi
if ! command -v ai-memory >/dev/null 2>&1; then
  printf 'ai-memory is not installed in this environment. Install it separately using the upstream guide; this helper never downloads or starts it.\n' >&2
  exit 1
fi

if [[ "$agent" == "claude-code" || "$agent" == "codex" || "$agent" == "antigravity-cli" ]]; then
  # Allowlist is enforced inside the native hook binary. Reject wrappers and
  # compatibility script modes before any user-level tool configuration changes.
  hook_platform="${AI_MEMORY_HOOK_PLATFORM:-}"
  if [[ -n "$hook_platform" && "$hook_platform" != "posix-native" ]]; then
    printf "AI_MEMORY_HOOK_PLATFORM='%s' selects a non-native or unverified hook mode. Unset it (or use posix-native) before running setup. No integrations were changed.\n" "$hook_platform" >&2
    exit 1
  fi
  ai_memory_path="$(command -v ai-memory)"
  magic="$(od -An -tx1 -N4 "$ai_memory_path" 2>/dev/null | tr -d ' \n')"
  case "$magic" in
    7f454c46|feedface|cefaedfe|feedfacf|cffaedfe) ;;
    *)
      printf 'The resolved ai-memory command is not a recognized native executable (%s). Wrappers cannot enforce allowlist capture. No integrations were changed.\n' "$ai_memory_path" >&2
      exit 1
      ;;
  esac
fi

if [[ "$agent" == "claude-code" ]]; then
  instruction_target="$repo_root/CLAUDE.md"
else
  instruction_target="$repo_root/AGENTS.md"
fi

printf "Configuring ai-memory for %s. The upstream installer will merge its managed entries into this user's tool configuration.\n" "$agent"
mcp_client="$agent"
case "$agent" in
  antigravity|antigravity-ide) mcp_client="antigravity-cli" ;;
esac
ai-memory install-mcp --client "$mcp_client" --apply
case "$agent" in
  claude-code|codex|antigravity-cli)
    ai-memory install-hooks --agent "$agent" --capture-mode allowlist --apply
    ;;
  *)
    printf 'MCP-only setup: this Antigravity surface does not have a first-party ai-memory lifecycle hook target.\n'
    ;;
esac
ai-memory install-instructions --target "$instruction_target"

case "$agent" in
  claude-code|codex|antigravity-cli)
    printf 'Native executable and hook mode preflight passed. Confirm installer output reports capture-policy enforcement.\n'
    ;;
esac
printf 'Configured %s. No server, container, API key, or LLM provider was installed or started.\n' "$agent"
