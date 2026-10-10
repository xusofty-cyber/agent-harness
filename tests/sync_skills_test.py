#!/usr/bin/env python3
"""Unit tests for tools/sync-skills.py — pure logic, no network.

Run: python3 tests/sync_skills_test.py
"""
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "sync_skills",
    Path(__file__).resolve().parent.parent / "tools" / "sync-skills.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestSha256Norm(unittest.TestCase):
    def test_crlf_normalized(self):
        a = mod.sha256_norm(b"hello\r\nworld\r\n")
        b = mod.sha256_norm(b"hello\nworld\n")
        self.assertEqual(a, b)

    def test_is_sha256(self):
        h = mod.sha256_norm(b"test")
        self.assertEqual(h, hashlib.sha256(b"test").hexdigest())


class TestExternalSkillsFilter(unittest.TestCase):
    def _lock(self):
        return {"skills": {
            "ext-ok": {"sourceType": "github", "source": "o/r",
                       "skillPath": "skills/x/SKILL.md"},
            "local": {"sourceType": "local", "source": "agent-harness",
                      "skillPath": ".agents/skills/local/SKILL.md"},
            "cli": {"sourceType": "github", "source": "o/c",
                    "package": "@o/c"},
            "wrapper": {"sourceType": "github", "source": "o/w",
                        "skillPath": ".agents/skills/wrapper/SKILL.md"},
            "meta": {"sourceType": "github", "source": "o/m",
                     "repository": "https://github.com/o/m"},
        }}

    def test_filters_correctly(self):
        with patch.object(mod, "SKILLS_DIR") as mock_dir:
            # Only ext-ok has a local file
            mock_dir.__truediv__.return_value.is_file.side_effect = (
                lambda: True
            )
            # Simpler: patch is_file per path
            real_truediv = Path.__truediv__

            def fake_is_file(self):
                return self.name == "ext-ok"

            with patch.object(Path, "is_file", fake_is_file):
                result = mod.external_skills(self._lock())
        names = [n for n, _ in result]
        self.assertEqual(names, ["ext-ok"])

    def test_only_flag(self):
        with patch.object(Path, "is_file", lambda self: True):
            result = mod.external_skills(self._lock(), only="local")
        self.assertEqual(result, [])


class TestCheckSkill(unittest.TestCase):
    def test_in_sync(self):
        content = b"# Skill\n"
        meta = {"source": "o/r", "skillPath": "skills/x/SKILL.md"}
        with patch.object(mod, "fetch_upstream", return_value=content):
            with patch.object(mod, "SKILLS_DIR"):
                fake_file = Path("/fake/x/SKILL.md")
                with patch.object(Path, "read_bytes", lambda self: content):
                    # Patch SKILLS_DIR / name / SKILL.md chain
                    with patch.object(mod, "SKILLS_DIR") as sd:
                        sd.__truediv__.return_value.__truediv__.return_value = fake_file
                        r = mod.check_skill("x", meta)
        self.assertEqual(r["status"], "in-sync")

    def test_outdated(self):
        meta = {"source": "o/r", "skillPath": "skills/x/SKILL.md"}
        with patch.object(mod, "fetch_upstream", return_value=b"new"):
            with patch.object(mod, "SKILLS_DIR") as sd:
                fake_file = Path("/fake/x/SKILL.md")
                sd.__truediv__.return_value.__truediv__.return_value = fake_file
                with patch.object(Path, "read_bytes", lambda self: b"old"):
                    r = mod.check_skill("x", meta)
        self.assertEqual(r["status"], "outdated")
        self.assertIn("upstream_bytes", r)

    def test_fetch_failed(self):
        meta = {"source": "o/r", "skillPath": "skills/x/SKILL.md"}
        with patch.object(mod, "fetch_upstream", return_value=None):
            r = mod.check_skill("x", meta)
        self.assertEqual(r["status"], "fetch-failed")

    def test_tampered(self):
        # When upstream matches locked computedHash, but local file was modified: tampered
        meta = {
            "source": "o/r",
            "skillPath": "skills/x/SKILL.md",
            "computedHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # sha of empty
        }
        with patch.object(mod, "fetch_upstream", return_value=b""):
            with patch.object(mod, "SKILLS_DIR") as sd:
                fake_file = Path("/fake/x/SKILL.md")
                sd.__truediv__.return_value.__truediv__.return_value = fake_file
                with patch.object(Path, "read_bytes", lambda self: b"locally modified"):
                    r = mod.check_skill("x", meta)
        self.assertEqual(r["status"], "tampered")
        self.assertIn("upstream_bytes", r)


if __name__ == "__main__":
    unittest.main(verbosity=1)
