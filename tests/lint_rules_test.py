#!/usr/bin/env python3
"""lint-rules port tests (D62, review 2026-10-29).

Yunyi's tests/lint_rules_test.py contains zero test functions, so these
are written fresh: the tool passes on the real tree (exit 0, warnings
allowed) and fails (exit 2) on a tmp tree with a broken entry.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "lint-rules.py"


def _run(root):
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root)],
                          capture_output=True, text=True, timeout=60)


def _mini_tree():
    tmp = Path(tempfile.mkdtemp(prefix="lint-rules-"))
    (tmp / ".claude" / "hooks").mkdir(parents=True)
    (tmp / "gate").mkdir()
    (tmp / "templates").mkdir()
    shutil.copy(REPO / "AGENTS.md", tmp / "AGENTS.md")
    shutil.copy(REPO / ".claude" / "settings.json",
                tmp / ".claude" / "settings.json")
    for hook in ("guard.mjs", "guard-write.mjs", "guard-feature-list.mjs",
                 "post-tool-use.mjs", "session-start.mjs", "stop-gate.mjs"):
        shutil.copy(REPO / ".claude" / "hooks" / hook,
                    tmp / ".claude" / "hooks" / hook)
    shutil.copy(REPO / "gate" / "pass-gate.py", tmp / "gate" / "pass-gate.py")
    shutil.copy(REPO / "gate" / "feature_list.schema.json",
                tmp / "gate" / "feature_list.schema.json")
    for name in ("DECISIONS.template.md", "PROJECT_CONTEXT.template.md",
                 "SESSION_STATE.template.md"):
        shutil.copy(REPO / "templates" / name, tmp / "templates" / name)
    return tmp


class LintRulesTest(unittest.TestCase):
    def test_passes_on_real_tree(self):
        r = _run(REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS LINT-001", r.stdout)
        self.assertIn("PASS LINT-002", r.stdout)
        self.assertIn("PASS LINT-003", r.stdout)
        self.assertIn("PASS LINT-004", r.stdout)
        self.assertIn("PASS LINT-005", r.stdout)

    def test_missing_entry_fails(self):
        tmp = _mini_tree()
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "gate" / "pass-gate.py").unlink()
        r = _run(tmp)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("FAIL LINT-001", r.stdout)

    def test_placeholder_residue_fails(self):
        tmp = _mini_tree()
        self.addCleanup(shutil.rmtree, tmp, True)
        with open(tmp / "AGENTS.md", "a", encoding="utf-8") as f:
            f.write("\nTODO: fix this later\n")
        r = _run(tmp)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("FAIL LINT-004", r.stdout)


if __name__ == "__main__":
    unittest.main()
