#!/usr/bin/env python3
"""check-clean placeholder dimension 3c (D47, review 2026-10-29).

A SESSION_STATE that still carries unfilled template markers must FAIL
check-clean, even when every other dimension passes. A clean state file
must PASS. The fixture is a minimal project dir: a valid
gate/feature_list.json with no in_progress items and an empty
gate/clean-state.json (all command dimensions SKIP).
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PASS_GATE = REPO / "gate" / "pass-gate.py"


def _project(state_text):
    tmp = Path(tempfile.mkdtemp(prefix="check-clean-"))
    gate = tmp / "gate"
    gate.mkdir()
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "check-clean-test",
                    "items": []}), encoding="utf-8")
    (gate / "clean-state.json").write_text("{}", encoding="utf-8")
    if state_text is not None:
        (tmp / "SESSION_STATE.md").write_text(state_text, encoding="utf-8")
    return tmp


def _check_clean(root):
    return subprocess.run(
        [sys.executable, str(PASS_GATE), "--root", str(root), "check-clean"],
        capture_output=True, text=True, timeout=120)


class CheckCleanPlaceholderTest(unittest.TestCase):
    def test_placeholder_state_fails(self):
        root = _project(
            "# SESSION_STATE\n\n"
            "- **Current goal**: ship <PROJECT_NAME>.\n"
            "- **Date**: <YYYY-MM-DD>\n")
        self.addCleanup(shutil.rmtree, root, True)
        r = _check_clean(root)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("3c progress/no placeholders", r.stdout)
        self.assertIn("FAIL", r.stdout)

    def test_generic_todo_marker_fails(self):
        root = _project("# SESSION_STATE\n\n- **Next step**: <TODO>\n")
        self.addCleanup(shutil.rmtree, root, True)
        r = _check_clean(root)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("<TODO>", r.stdout)

    def test_clean_state_passes(self):
        root = _project(
            "# SESSION_STATE\n\n"
            "- **Current goal**: ship the thing.\n"
            "- **In progress**: nothing.\n")
        self.addCleanup(shutil.rmtree, root, True)
        r = _check_clean(root)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("3c progress/no placeholders", r.stdout)
        self.assertIn("PASS", r.stdout)

    def test_missing_state_skips_3c(self):
        root = _project(None)
        self.addCleanup(shutil.rmtree, root, True)
        r = _check_clean(root)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("3c progress/no placeholders", r.stdout)
        self.assertIn("SKIP", r.stdout)


if __name__ == "__main__":
    unittest.main()
