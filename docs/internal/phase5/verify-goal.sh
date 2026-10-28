#!/bin/bash
# verify-goal.sh — Goal Loop verify for the status-pluralization goal.
# Passes only when: (a) `pass-gate status` on a 1-item gate prints
# "(1 item)" and never "(1 items)"; (b) tests/pass_gate_test.py exists
# and passes. Exits non-zero otherwise.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 "$ROOT/gate/pass-gate.py" --root "$TMP/gate" init --project verify-goal >/dev/null 2>&1 || { echo "verify: pass-gate init failed"; exit 1; }
python3 "$ROOT/gate/pass-gate.py" --root "$TMP/gate" add --id item-1 --title "one item" --behavior "x" --command "true" >/dev/null 2>&1 || { echo "verify: pass-gate add failed"; exit 1; }
out="$(python3 "$ROOT/gate/pass-gate.py" --root "$TMP/gate" status)"
echo "$out" | grep -q "(1 item)" || { echo "verify: status does not say '(1 item)'"; exit 1; }
echo "$out" | grep -q "(1 items)" && { echo "verify: status still says '(1 items)'"; exit 1; }
[ -f "$ROOT/tests/pass_gate_test.py" ] || { echo "verify: tests/pass_gate_test.py missing"; exit 1; }
python3 "$ROOT/tests/pass_gate_test.py" >/dev/null 2>&1 || { echo "verify: tests/pass_gate_test.py failed"; exit 1; }
echo "verify: OK — status pluralization correct, regression test passes"
