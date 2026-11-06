#!/usr/bin/env python3
"""Tests for D72 dependency modelling + L07 out_of_scope (pass-gate.py).

Run: python3 tests/pass_gate_deps_test.py
Stdlib only. Covers: unknown dep rejected, self-dep rejected, cycle
rejected, start hard-blocks on unmet deps and passes once deps are
passing, status annotates blocked-by, out_of_scope round-trips via add.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS_GATE = ROOT / "gate" / "pass-gate.py"


def _run(root, *argv):
    return subprocess.run([sys.executable, str(PASS_GATE), "--root", str(root), *argv],
                          capture_output=True, text=True)


def _write(root, items):
    gate = Path(root) / "gate"
    gate.mkdir(parents=True, exist_ok=True)
    (gate / "feature_list.json").write_text(json.dumps(
        {"version": 1, "project": "deps-test", "items": items}))


def _item(iid, **kw):
    it = {"id": iid, "title": iid, "priority": "p1", "area": "gate",
          "user_visible_behavior": "x", "status": "not_started",
          "verification": {"command": "true", "timeout_seconds": 60},
          "evidence": None}
    it.update(kw)
    return it


class DepsTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def test_unknown_dep_rejected(self):
        _write(self.root, [_item("a", depends_on=["ghost"])])
        r = _run(self.root, "status")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown id", r.stdout)

    def test_self_dep_rejected(self):
        _write(self.root, [_item("a", depends_on=["a"])])
        r = _run(self.root, "status")
        self.assertIn("cannot depend on itself", r.stdout)

    def test_cycle_rejected(self):
        _write(self.root, [_item("a", depends_on=["b"]), _item("b", depends_on=["a"])])
        r = _run(self.root, "status")
        self.assertIn("cycle", r.stdout)

    def test_start_override_logged(self):
        _write(self.root, [_item("base"), _item("top", depends_on=["base"])])
        r = _run(self.root, "start", "--id", "top", "--override-deps", "base is docs-only")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dependency override (logged)", r.stdout)
        events = (Path(self.root) / "gate" / "events.jsonl").read_text()
        self.assertIn("dependency_override", events)
        self.assertIn("base is docs-only", events)
        r2 = _run(self.root, "status")
        self.assertIn("[dep-override: base]", r2.stdout)

    def test_start_hard_blocks_then_passes(self):
        _write(self.root, [_item("base"), _item("top", depends_on=["base"])])
        r = _run(self.root, "start", "--id", "top")
        self.assertEqual(r.returncode, 1)
        self.assertIn("dependencies not passing", r.stdout)
        self.assertEqual(_run(self.root, "start", "--id", "base").returncode, 0)
        self.assertEqual(_run(self.root, "verify", "--id", "base").returncode, 0)
        self.assertEqual(_run(self.root, "start", "--id", "top").returncode, 0)

    def test_status_blocked_by_annotation(self):
        _write(self.root, [_item("base"), _item("top", depends_on=["base"])])
        r = _run(self.root, "status")
        self.assertIn("[blocked-by: base]", r.stdout)

    def test_out_of_scope_round_trip(self):
        _write(self.root, [])
        r = _run(self.root, "add", "--id", "x1", "--priority", "p1", "--area", "gate",
                 "--title", "t", "--behavior", "b", "--command", "true",
                 "--out-of-scope", "do not touch gate/")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads((Path(self.root) / "gate" / "feature_list.json").read_text())
        self.assertEqual(data["items"][0]["out_of_scope"], "do not touch gate/")


if __name__ == "__main__":
    unittest.main()
