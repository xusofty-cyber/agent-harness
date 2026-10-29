#!/usr/bin/env python3
"""Gate bootstrap verification covers task extras (review 2026-10-29).

The gate arm's bootstrap item must verify the FULL acceptance, not just
the unit-test command: t5 needs DECISIONS.md topic coverage, t6 needs
tests_median_extra. t7/t8 have no extras. A bootstrap that passes while
evaluate.py still fails the run is a false completion by construction.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "eval" / "bench"))
import prep  # noqa: E402


class VerifyCmdTest(unittest.TestCase):
    def test_t5_t6_carry_extras(self):
        self.assertIn("DECISIONS.md", prep.VERIFY_CMD["t5-ambiguous"])
        self.assertIn("tests_median_extra",
                      prep.VERIFY_CMD["t6-incomplete-tests"])

    def test_t7_t8_unchanged(self):
        self.assertEqual(prep.VERIFY_CMD["t7-unwarned"],
                         prep.TEST_CMD["t7-unwarned"])
        self.assertEqual(prep.VERIFY_CMD["t8-resume"],
                         prep.TEST_CMD["t8-resume"])

    def _run_gate(self, task, with_extra):
        tmp = Path(tempfile.mkdtemp(prefix="bootstrap-verify-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        r = subprocess.run(
            [sys.executable, str(REPO / "eval" / "bench" / "prep.py"),
             "--task", task, "--arm", "gate", "--run", "1",
             "--root", str(tmp)],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        run_dir = tmp / task / "gate" / "r1"
        sol = REPO / "eval" / "bench" / "fixtures" / task / "solution"
        if task == "t5-ambiguous":
            shutil.copy(sol / "durations.py", run_dir / "durations.py")
            if with_extra:
                shutil.copy(sol / "DECISIONS.md", run_dir / "DECISIONS.md")
        else:
            shutil.copy(sol / "statsx.py", run_dir / "statsx.py")
            if with_extra:
                shutil.copy(sol / "tests_median_extra.py",
                            run_dir / "tests_median_extra.py")
        v = subprocess.run(
            [sys.executable, str(run_dir / "gate" / "pass-gate.py"),
             "--root", str(run_dir), "verify", "--id", "bootstrap"],
            capture_output=True, text=True, timeout=300)
        return v.returncode

    def test_t5_without_decisions_fails_then_passes(self):
        self.assertNotEqual(self._run_gate("t5-ambiguous", False), 0)
        self.assertEqual(self._run_gate("t5-ambiguous", True), 0)

    def test_t6_without_extra_tests_fails_then_passes(self):
        self.assertNotEqual(self._run_gate("t6-incomplete-tests", False), 0)
        self.assertEqual(self._run_gate("t6-incomplete-tests", True), 0)


if __name__ == "__main__":
    unittest.main()
