#!/usr/bin/env python3
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
    # Write the feature list directly: pass-gate init seeds 3 example
    # items from the template, so init+add can never produce exactly
    # 0/1/2 items. (Found by the verify script failing the first manual
    # baseline attempt — the verify caught the wrong assumption.)
    tmpdir = Path(tempfile.mkdtemp())
    gate = tmpdir / "gate"
    gate.mkdir(parents=True)
    items = [{"id": f"item-{i}", "title": f"item {i}", "priority": "p1",
              "area": "gate", "user_visible_behavior": "x",
              "status": "not_started",
              "verification": {"command": "true", "timeout_seconds": 60},
              "evidence": None} for i in range(n_items)]
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "plural-test", "items": items}))
    # NOTE: --root takes the PROJECT root; pass-gate appends gate/ itself.
    out = subprocess.run([sys.executable, str(PASS_GATE), "--root", str(tmpdir),
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
