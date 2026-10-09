#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s [claude-code|codex|antigravity|antigravity-ide|antigravity-cli]\n' "$0" >&2
  printf 'If run without arguments in an interactive terminal, a step-by-step selection wizard is displayed.\n' >&2
  exit 2
}

prompt_multiselect() {
  local title="$1"
  shift
  local -a labels=()
  local -a values=()
  local -a checked=()
  while [[ $# -gt 0 ]]; do
    labels+=("$1")
    values+=("$2")
    checked+=("$3")
    shift 3
  done

  local count=${#labels[@]}
  local cur=0

  if [ ! -t 0 ]; then
    echo "$title"
    for i in "${!labels[@]}"; do
      echo "$((i+1))) [${checked[$i]}] ${labels[$i]}"
    done
    read -r -p "Enter numbers separated by space (or press Enter for defaults): " resp
    SELECTED_VALUES=()
    if [ -z "$resp" ]; then
      for i in "${!values[@]}"; do
        if [ "${checked[$i]}" -eq 1 ]; then SELECTED_VALUES+=("${values[$i]}"); fi
      done
    else
      for num in $resp; do
        idx=$((num-1))
        if [ "$idx" -ge 0 ] && [ "$idx" -lt "$count" ]; then
          SELECTED_VALUES+=("${values[$idx]}")
        fi
      done
    fi
    return
  fi

  local old_stty
  old_stty="$(stty -g 2>/dev/null || true)"
  trap 'stty "$old_stty" 2>/dev/null; printf "\033[?25h\n"; exit 1' INT TERM

  stty -echo -icanon min 1 time 0 2>/dev/null || true
  printf "\033[?25l"

  echo -e "$title"
  echo -e "\033[2m↑↓ move, space select, enter confirm\033[0m"

  while true; do
    for i in "${!labels[@]}"; do
      local pointer="  "
      if [ "$i" -eq "$cur" ]; then
        pointer="\033[36m> \033[0m"
      fi
      local box="\033[90m◯\033[0m "
      if [ "${checked[$i]}" -eq 1 ]; then
        box="\033[32m◉\033[0m "
      fi
      echo -e "${pointer}${box}${labels[$i]}"
    done

    IFS= read -rsn1 key
    if [[ "$key" == $'\x1b' ]]; then
      read -rsn2 -t 0.1 rest || true
      key+="$rest"
    fi

    case "$key" in
      $'\x1b[A'|[kK])
        cur=$(( (cur - 1 + count) % count ))
        ;;
      $'\x1b[B'|[jJ])
        cur=$(( (cur + 1) % count ))
        ;;
      ' ')
        if [ "${checked[$cur]}" -eq 1 ]; then
          checked[$cur]=0
        else
          checked[$cur]=1
        fi
        ;;
      ''|$'\n')
        break
        ;;
      [qQ])
        stty "$old_stty" 2>/dev/null
        printf "\033[?25h\n"
        echo "Aborted."
        exit 1
        ;;
    esac

    printf "\033[%dA" "$count"
  done

  stty "$old_stty" 2>/dev/null
  printf "\033[?25h\n"
  trap - INT TERM

  SELECTED_VALUES=()
  for i in "${!values[@]}"; do
    if [ "${checked[$i]}" -eq 1 ]; then
      SELECTED_VALUES+=("${values[$i]}")
    fi
  done
}

SELECTED_AGENTS=()
if [[ $# -ge 1 ]]; then
  for arg in "$@"; do
    case "$arg" in
      claude-code|codex|antigravity|antigravity-ide|antigravity-cli)
        SELECTED_AGENTS+=("$arg")
        ;;
      -h|--help)
        usage
        ;;
      *)
        usage
        ;;
    esac
  done
else
  if [ -t 0 ]; then
    prompt_multiselect "\n=== Select Agent Tools for ai-memory Integration ===" \
      "Claude Code (hooks + MCP)" "claude-code" 1 \
      "OpenAI Codex (hooks + MCP)" "codex" 1 \
      "Google Antigravity IDE (MCP + project instructions)" "antigravity-ide" 1 \
      "Google Antigravity CLI (hooks + MCP)" "antigravity-cli" 0
    if [ ${#SELECTED_VALUES[@]} -eq 0 ]; then
      printf "No agents selected. Exiting.\n"
      exit 0
    fi
    SELECTED_AGENTS=("${SELECTED_VALUES[@]}")
  else
    usage
  fi
fi

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

AI_MEMORY_PINNED_VERSION="2.6.0"
ver_output="$(ai-memory --version 2>/dev/null || true)"
if ! printf '%s\n' "$ver_output" | grep -Eq "(^|[^0-9.])${AI_MEMORY_PINNED_VERSION}([^0-9.]|$)"; then
  printf 'ai-memory version mismatch: this repo pins %s (got: %s). ' "$AI_MEMORY_PINNED_VERSION" "${ver_output:-<unknown>}" >&2
  printf 'Set AI_MEMORY_ALLOW_OTHER_VERSION=1 to override.\n' >&2
  if [[ "${AI_MEMORY_ALLOW_OTHER_VERSION:-}" != "1" ]]; then exit 1; fi
fi

configure_single_agent() {
  local agent="$1"
  if [[ "$agent" == "claude-code" || "$agent" == "codex" || "$agent" == "antigravity-cli" ]]; then
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

  printf "\nConfiguring ai-memory for %s. The upstream installer will merge its managed entries into this user's tool configuration.\n" "$agent"
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
  ai-memory install-instructions --target "$instruction_target" --no-skills

  case "$agent" in
    claude-code|codex|antigravity-cli)
      printf 'Native executable and hook mode preflight passed. Confirm installer output reports capture-policy enforcement.\n'
      ;;
  esac
  printf 'Configured %s. No server, container, API key, or LLM provider was installed or started.\n' "$agent"
}

for agent in "${SELECTED_AGENTS[@]}"; do
  configure_single_agent "$agent"
done
