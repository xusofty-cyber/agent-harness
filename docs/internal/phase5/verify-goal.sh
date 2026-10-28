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
# Write the feature list directly with exactly 1 item: pass-gate init
# seeds 3 example items from the template, so init+add can never yield
# a 1-item gate. (Found by this verify failing the first manual baseline
# attempt — the verify caught the wrong assumption.)
python3 - "$TMP" <<'PYEOF' || { echo "verify: fixture setup failed"; exit 1; }
import json
import sys
from pathlib import Path
gate = Path(sys.argv[1]) / "gate"
gate.mkdir(parents=True)
(gate / "feature_list.json").write_text(json.dumps({
    "version": 1, "project": "verify-goal",
    "items": [{"id": "item-1", "title": "one item", "priority": "p1",
               "area": "gate", "user_visible_behavior": "x",
               "status": "not_started",
               "verification": {"command": "true", "timeout_seconds": 60},
               "evidence": None}]}))
PYEOF
out="$(python3 "$ROOT/gate/pass-gate.py" --root "$TMP/gate" status)"
echo "$out" | grep -q "(1 item)" || { echo "verify: status does not say '(1 item)'"; exit 1; }
echo "$out" | grep -q "(1 items)" && { echo "verify: status still says '(1 items)'"; exit 1; }
[ -f "$ROOT/tests/pass_gate_test.py" ] || { echo "verify: tests/pass_gate_test.py missing"; exit 1; }
python3 "$ROOT/tests/pass_gate_test.py" >/dev/null 2>&1 || { echo "verify: tests/pass_gate_test.py failed"; exit 1; }
echo "verify: OK — status pluralization correct, regression test passes"
