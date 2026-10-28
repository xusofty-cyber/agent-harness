#!/usr/bin/env python3
"""Tests for gate/comet_adapter.py (merged from v3-yunkai).

Import must never change a feature's status, must append external
evidence atomically, must log the import to gate/events.jsonl, and the
resulting feature list must still pass `pass-gate.py validate`.
Run: python3 tests/comet_adapter_test.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "gate" / "comet_adapter.py"
PASS_GATE = ROOT / "gate" / "pass-gate.py"


def make_list(tmp: Path) -> Path:
    gate = tmp / "gate"
    gate.mkdir()
    fl = {"version": 1, "project": "adapter-test",
          "items": [{"id": "demo", "priority": "p0", "area": "test",
                     "title": "demo feature",
                     "user_visible_behavior": "demo works.",
                     "status": "not_started",
                     "verification": {"command": "true", "timeout_seconds": 60},
                     "evidence": None, "notes": ""}]}
    p = gate / "feature_list.json"
    p.write_text(json.dumps(fl, indent=2), encoding="utf-8")
    return p


class TestCometAdapter(unittest.TestCase):
    def run_adapter(self, *argv, cwd=None):
        return subprocess.run(
            [sys.executable, str(ADAPTER), *argv],
            capture_output=True, text=True, cwd=cwd)

    def test_import_appends_evidence_status_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            fl = make_list(tmp)
            comet = tmp / "docs" / "comet" / "change-1"
            comet.mkdir(parents=True)
            (comet / "verify-result.json").write_text("{}", encoding="utf-8")
            r = self.run_adapter("import", "--comet-dir", str(comet),
                                 "--feature", "demo", "--file", str(fl))
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(fl.read_text(encoding="utf-8"))
            item = data["items"][0]
            self.assertEqual(item["status"], "not_started")
            self.assertEqual(len(item["external_evidence"]), 1)
            self.assertEqual(item["external_evidence"][0]["source"], "comet")
            self.assertEqual(len(item["external_evidence"][0]["sha256_16"]), 16)
            self.assertFalse((tmp / "gate" / "feature_list.json.tmp").exists())
            events = (tmp / "gate" / "events.jsonl").read_text(encoding="utf-8")
            ev = json.loads(events.strip().splitlines()[-1])
            self.assertEqual(ev["event"], "external_evidence_imported")
            self.assertEqual(ev["item"], "demo")
            # Still a valid feature list after the import (validate() is
            # a module-level function; there is no `validate` subcommand).
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pass_gate_mod", str(PASS_GATE))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            data = json.loads(fl.read_text(encoding="utf-8"))
            self.assertEqual(mod.validate(data), [])

    def test_import_no_artifacts_exits_1(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            fl = make_list(tmp)
            comet = tmp / "docs" / "comet" / "empty"
            comet.mkdir(parents=True)
            r = self.run_adapter("import", "--comet-dir", str(comet),
                                 "--feature", "demo", "--file", str(fl))
            self.assertEqual(r.returncode, 1)

    def test_import_missing_dir_and_unknown_feature_exit_2(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            fl = make_list(tmp)
            r = self.run_adapter("import", "--comet-dir", str(tmp / "nope"),
                                 "--feature", "demo", "--file", str(fl))
            self.assertEqual(r.returncode, 2)
            comet = tmp / "docs" / "comet" / "change-1"
            comet.mkdir(parents=True)
            (comet / "verify-result.json").write_text("{}", encoding="utf-8")
            r = self.run_adapter("import", "--comet-dir", str(comet),
                                 "--feature", "ghost", "--file", str(fl))
            self.assertEqual(r.returncode, 2)

    def test_map_no_candidates_exits_0(self):
        with tempfile.TemporaryDirectory() as td:
            r = self.run_adapter("map", "--root", td)
            self.assertEqual(r.returncode, 0)
            self.assertIn("no comet change directories", r.stdout)


if __name__ == "__main__":
    unittest.main()
