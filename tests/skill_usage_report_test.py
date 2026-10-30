#!/usr/bin/env python3
"""Unit tests for tools/skill-usage-report.py (D68).
Run: python3 tests/skill_usage_report_test.py
Stdlib only.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "skill-usage-report.py"

spec = importlib.util.spec_from_file_location("skill_usage_report", TOOL)
report_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report_mod)


def _make_project(tmp):
    root = Path(tmp)
    skills = root / ".agents" / "skills"
    for name in ("alpha", "beta", "gamma"):
        d = skills / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    # A directory without SKILL.md is not a deployed skill.
    (skills / "not-a-skill").mkdir()
    usage = root / ".claude" / "skill-usage.jsonl"
    usage.parent.mkdir(parents=True)
    return root, usage


def _write_usage(usage, lines):
    usage.write_text("".join(
        (json.dumps(rec) if isinstance(rec, dict) else rec) + "\n"
        for rec in lines), encoding="utf-8")


class SkillUsageReportTest(unittest.TestCase):
    def test_counts_and_zero_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, usage = _make_project(tmp)
            _write_usage(usage, [
                {"ts": "t", "skill": "alpha"},
                {"ts": "t", "skill": "alpha", "session": "s1"},
                {"ts": "t", "skill": "beta"},
            ])
            report = report_mod.build_report(
                root, usage, [root / ".agents" / "skills"])
            self.assertEqual(report["counts"], {"alpha": 2, "beta": 1})
            self.assertEqual(report["total_loads"], 3)
            self.assertEqual(report["zero_loads"], ["gamma"])
            self.assertEqual(report["deployed_skills"],
                             ["alpha", "beta", "gamma"])
            self.assertEqual(report["undeployed_loads"], [])

    def test_malformed_lines_are_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, usage = _make_project(tmp)
            _write_usage(usage, [
                {"ts": "t", "skill": "alpha"},
                "NOT-JSON",
                {"ts": "t"},  # no skill field
                {"ts": "t", "skill": "removed-skill"},
            ])
            report = report_mod.build_report(
                root, usage, [root / ".agents" / "skills"])
            self.assertEqual(report["total_loads"], 2)
            self.assertEqual(report["skipped_lines"], 2)
            self.assertEqual(report["undeployed_loads"], ["removed-skill"])
            self.assertEqual(report["zero_loads"], ["beta", "gamma"])

    def test_missing_usage_file_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(TOOL), "--root", tmp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertIn("no skill-usage log", r.stderr)

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, usage = _make_project(tmp)
            _write_usage(usage, [{"ts": "t", "skill": "beta"}])
            r = subprocess.run(
                [sys.executable, str(TOOL), "--root", tmp, "--json"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            report = json.loads(r.stdout)
            self.assertEqual(report["counts"], {"beta": 1})
            self.assertEqual(report["zero_loads"], ["alpha", "gamma"])


if __name__ == "__main__":
    unittest.main()
