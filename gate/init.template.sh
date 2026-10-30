#!/bin/sh
# =============================================================================
# gate/init.template.sh — scaffold a project for the gate layer (Phase 1).
#
# Usage (run from the project root):
#   sh gate/init.template.sh --name <project-name> \
#       --verify "<command that proves the project works>" \
#       --start "<standard start command>" \
#       [--build "<build command>"] [--force]
#
# Creates:
#   gate/feature_list.json   (via pass-gate.py init, from the template)
#   gate/clean-state.json    (build / test / start commands for check-clean)
#   SESSION_STATE.md         (breakpoint format, if missing)
#   DECISIONS.md             (decision log, if missing)
# Then runs --verify once as a smoke test; a non-zero exit fails init.
#
# --name, --verify and --start are REQUIRED. A value left as a placeholder
# (empty, or still containing <...>) fails init instead of silently
# scaffolding a broken project. --build is optional; without it the build
# dimension of check-clean reports SKIP.
#
# This script is self-contained: it only depends on gate/pass-gate.py
# sitting next to it, so it works after deploy copies gate/ to a target
# project (no templates/ directory needed at the target).
# =============================================================================
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_NAME=""
VERIFY_CMD=""
START_CMD=""
BUILD_CMD=""
FORCE=false

while [ $# -gt 0 ]; do
    case "$1" in
        --name)   PROJECT_NAME="$2"; shift 2 ;;
        --verify) VERIFY_CMD="$2"; shift 2 ;;
        --start)  START_CMD="$2"; shift 2 ;;
        --build)  BUILD_CMD="$2"; shift 2 ;;
        --force)  FORCE=true; shift ;;
        -h|--help)
            sed -n '2,30p' "$0"
            exit 0 ;;
        *)
            echo "init: unknown argument: $1" >&2
            echo "usage: sh gate/init.template.sh --name <project> --verify \"<cmd>\" --start \"<cmd>\" [--build \"<cmd>\"] [--force]" >&2
            exit 2 ;;
    esac
done

fail() { echo "init: $1" >&2; exit 1; }

# --- Required values must be real, not placeholders -------------------------
[ -n "$PROJECT_NAME" ] || fail "--name is required"
[ -n "$VERIFY_CMD" ] || fail "--verify is required (the command that proves the project works)"
[ -n "$START_CMD" ] || fail "--start is required (the standard start command)"
case "$PROJECT_NAME$VERIFY_CMD$START_CMD$BUILD_CMD" in
    *"<"*|*">"*) fail "a value still contains a <...> placeholder — fill in real commands first" ;;
esac

# --- feature_list.json (via pass-gate, so the file is always valid) ---------
if [ -f "gate/feature_list.json" ] && [ "$FORCE" = false ]; then
    echo "init: gate/feature_list.json already exists (use --force to overwrite)"
else
    python3 "$SCRIPT_DIR/pass-gate.py" --root . init --project "$PROJECT_NAME" ${FORCE:+--force} \
        || fail "pass-gate.py init failed"
    echo "init: gate/feature_list.json created"
fi

# --- clean-state.json ---------------------------------------------------------
# Build the JSON values first so an absent --build renders as null, not
# as an empty value (which would be invalid JSON).
BUILD_JSON="null"
if [ -n "$BUILD_CMD" ]; then
    BUILD_JSON=$(printf '%s' "$BUILD_CMD" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
fi
VERIFY_JSON=$(printf '%s' "$VERIFY_CMD" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
START_JSON=$(printf '%s' "$START_CMD" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
cat > gate/clean-state.json <<EOF
{
  "build": $BUILD_JSON,
  "test": $VERIFY_JSON,
  "start": $START_JSON
}
EOF
python3 -m json.tool gate/clean-state.json >/dev/null \
    || fail "gate/clean-state.json is not valid JSON"
echo "init: gate/clean-state.json written"

# --- SESSION_STATE.md (breakpoint format, only if missing) -------------------
if [ ! -f "SESSION_STATE.md" ]; then
    cat > SESSION_STATE.md <<EOF
# SESSION_STATE — session breakpoint

> **Updated**: $(date -u +%Y-%m-%d) | **Project**: $PROJECT_NAME
> **Feature list**: gate/feature_list.json (status via \`python3 gate/pass-gate.py status\`)

## Goal

- <What this session is trying to ship, in one line>

## In progress

- <feature_list id>: <one-line state> (or: none — run \`pass-gate.py start --id <id>\`)

## Next

- [ ] <Next concrete step>

## Blocked

- <Blocker, or "none">

## Last verification

- <Last command run and its result, or "none yet">
EOF
    echo "init: SESSION_STATE.md created"
else
    echo "init: SESSION_STATE.md already exists, kept"
fi

# --- DECISIONS.md (only if missing) ------------------------------------------
if [ ! -f "DECISIONS.md" ]; then
    cat > DECISIONS.md <<'EOF'
# Decisions

Written decision records. Each entry: decision, rationale, rejected
alternative, date. See templates/DECISIONS.template.md in agent-harness.

## (no decisions recorded yet)
EOF
    echo "init: DECISIONS.md created"
else
    echo "init: DECISIONS.md already exists, kept"
fi

# --- Smoke: run VERIFY once, fail loudly instead of silently -----------------
echo "init: smoke run: $VERIFY_CMD"
if sh -c "$VERIFY_CMD"; then
    echo "init: OK — $PROJECT_NAME is gated (verify passed)"
    echo "init: next, work through templates/initializer-playbook.md in"
    echo "      agent-harness (opening questions, feature-list discipline,"
    echo "      initialization acceptance checklist) before starting items."
else
    fail "smoke verification failed (exit $?) — fix the project, then re-run init"
fi
