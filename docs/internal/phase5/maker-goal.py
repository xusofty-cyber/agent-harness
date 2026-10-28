#!/usr/bin/env python3
"""Round-based maker for the Phase 5 Goal Loop demo (docs/internal/phase5).

Goal: `gate/pass-gate.py status` prints "1 item" (not "1 items") and a
regression test covers 0/1/2 items. The maker applies one step per round,
reading the round number from LOOP_ROUND (set by tools/loop.py):
  round 1 — fix the pluralization in gate/pass-gate.py
  round 2 — add tests/pass_gate_test.py (regression test)
  round 3+ — no-op (the verify re-runs; consecutive passes stop the loop)

Deterministic and reviewable: every edit is an exact-string replacement
(asserted) or a fixed file write. Run by the loop runner, cwd is the
loop root; the repo root is derived from this file's own location.
"""

import os
import sys

_HERE = os.path.abspath(__file__)  # <root>/docs/internal/phase5/maker-goal.py
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
# dirname x4: phase5 -> internal -> docs -> repo root

OLD_STATUS = '''    print(f"project: {data.get('project')}  "
          f"({len(data.get('items', []))} items)")'''

NEW_STATUS = '''    n_items = len(data.get('items', []))
    print(f"project: {data.get('project')}  "
          f"({n_items} item{'s' if n_items != 1 else ''})")'''

TEST_FILE = '''#!/usr/bin/env python3
"""Regression tests for gate/pass-gate.py status pluralization (Phase 5).

Run: python3 tests/pass_gate_test.py
Stdlib only. The status line must read "0 items" / "1 item" / "2 items".
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS_GATE = ROOT / "gate" / "pass-gate.py"


def _status_with(n_items):
    tmp = tempfile.mkdtemp()
    gate = Path(tmp) / "gate"
    subprocess.run([sys.executable, str(PASS_GATE), "--root", str(gate),
                    "init", "--project", "plural-test"],
                   check=True, capture_output=True)
    for i in range(n_items):
        subprocess.run([sys.executable, str(PASS_GATE), "--root", str(gate),
                        "add", "--id", f"item-{i}", "--title", f"item {i}",
                        "--behavior", "x", "--command", "true"],
                       check=True, capture_output=True)
    out = subprocess.run([sys.executable, str(PASS_GATE), "--root", str(gate),
                          "status"], check=True, capture_output=True, text=True)
    return out.stdout


class StatusPluralTest(unittest.TestCase):
    def test_zero_items(self):
        self.assertIn("(0 items)", _status_with(0))

    def test_one_item(self):
        out = _status_with(1)
        self.assertIn("(1 item)", out)
        self.assertNotIn("(1 items)", out)

    def test_two_items(self):
        self.assertIn("(2 items)", _status_with(2))


if __name__ == "__main__":
    unittest.main()
'''


def main():
    rnd = int(os.environ.get("LOOP_ROUND", "1"))
    if rnd == 1:
        path = os.path.join(ROOT, "gate", "pass-gate.py")
        text = open(path, encoding="utf-8").read()
        assert OLD_STATUS in text, "pluralization site not found (already fixed?)"
        open(path, "w", encoding="utf-8").write(text.replace(OLD_STATUS, NEW_STATUS, 1))
        print("maker-goal: round 1 — pluralization fixed in gate/pass-gate.py")
    elif rnd == 2:
        path = os.path.join(ROOT, "tests", "pass_gate_test.py")
        assert not os.path.exists(path), "test file already exists"
        with open(path, "w", encoding="utf-8") as f:
            f.write(TEST_FILE)
        os.chmod(path, 0o755)
        print("maker-goal: round 2 — tests/pass_gate_test.py written")
    else:
        print(f"maker-goal: round {rnd} — no-op (nothing left to change)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
