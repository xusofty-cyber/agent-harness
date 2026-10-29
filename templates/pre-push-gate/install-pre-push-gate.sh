#!/bin/bash
# install-pre-push-gate.sh — explicit opt-in installer for the
# agent-harness pre-push gate template.
#
# This script is the ONLY supported way to install the hook. It never
# runs as part of deploy-agents.sh / deploy-agents.ps1, and it never
# silently overwrites an existing hook.
#
# Usage (from anywhere):
#   bash templates/pre-push-gate/install-pre-push-gate.sh [TARGET_PROJECT_DIR] [--force]
#
#   TARGET_PROJECT_DIR defaults to the current directory. It must be a
#   git work tree. The hook is installed into that project's
#   .git/hooks/pre-push (worktrees resolve via `git rev-parse
#   --absolute-git-dir`, so linked worktrees get the right hooks dir).
#   gate-prepush-check.py is installed next to it, because the hook
#   resolves its checker relative to its own directory first.
#
#   Without --force, an existing .git/hooks/pre-push is left untouched
#   and installation refuses (exit 1) — merge the two hooks by hand
#   instead of losing one. With --force, the existing hook is backed
#   up to pre-push.bak-<timestamp> before being replaced.
#
# After installing, test the hook without pushing:
#   printf '' | .git/hooks/pre-push
set -u

TARGET="${1:-.}"
FORCE=0
if [ "${2:-}" = "--force" ]; then FORCE=1; fi
if [ "${1:-}" = "--force" ]; then TARGET="."; FORCE=1; fi

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SRC="$SOURCE_DIR/pre-push"
CHECK_SRC="$SOURCE_DIR/gate-prepush-check.py"

[ -f "$HOOK_SRC" ] || { echo "install-pre-push-gate: missing $HOOK_SRC" >&2; exit 1; }
[ -f "$CHECK_SRC" ] || { echo "install-pre-push-gate: missing $CHECK_SRC" >&2; exit 1; }

GIT_DIR="$(git -C "$TARGET" rev-parse --absolute-git-dir 2>/dev/null)" || {
    echo "install-pre-push-gate: '$TARGET' is not a git work tree" >&2
    exit 1
}
HOOKS_DIR="$GIT_DIR/hooks"
mkdir -p "$HOOKS_DIR"

DEST_HOOK="$HOOKS_DIR/pre-push"
if [ -e "$DEST_HOOK" ] && [ "$FORCE" -ne 1 ]; then
    echo "install-pre-push-gate: refusing to overwrite existing $DEST_HOOK" >&2
    echo "install-pre-push-gate: merge the hooks by hand, or re-run with --force to back the existing hook up to pre-push.bak-<timestamp> first." >&2
    exit 1
fi
if [ -e "$DEST_HOOK" ] && [ "$FORCE" -eq 1 ]; then
    BACKUP="$HOOKS_DIR/pre-push.bak-$(date +%Y%m%d-%H%M%S)"
    cp "$DEST_HOOK" "$BACKUP"
    echo "install-pre-push-gate: existing hook backed up to $BACKUP"
fi

cp "$HOOK_SRC" "$DEST_HOOK"
cp "$CHECK_SRC" "$HOOKS_DIR/gate-prepush-check.py"
chmod +x "$DEST_HOOK" "$HOOKS_DIR/gate-prepush-check.py"

echo "install-pre-push-gate: installed $DEST_HOOK"
echo "install-pre-push-gate: installed $HOOKS_DIR/gate-prepush-check.py"
echo "install-pre-push-gate: test without pushing: printf '' | $DEST_HOOK"
echo "install-pre-push-gate: note — 'git push --no-verify' bypasses this hook; pair it with the CI template (templates/ci-gate-check.yml) and server-side branch protection."
