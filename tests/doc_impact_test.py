#!/usr/bin/env python3
"""Unit tests for tools/doc-impact.py pure functions."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
# doc-impact.py has a hyphen, use importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "doc_impact", 
    str(Path(__file__).resolve().parent.parent / "tools" / "doc-impact.py")
)
doc_impact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doc_impact)
parse_frontmatter = doc_impact.parse_frontmatter
match_glob = doc_impact.match_glob


class TestParseFrontmatter(unittest.TestCase):
    def test_valid_frontmatter(self):
        text = """---
title: Test Doc
modules: [src/auth, src/api]
---
# Content
"""
        result = parse_frontmatter(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Test Doc")

    def test_no_frontmatter(self):
        text = "# Just a heading\nNo frontmatter here."
        result = parse_frontmatter(text)
        self.assertIsNone(result)

    def test_empty(self):
        self.assertIsNone(parse_frontmatter(""))


class TestMatchGlob(unittest.TestCase):
    def test_exact_match(self):
        self.assertTrue(match_glob("src/auth/login.py", "src/auth/login.py"))

    def test_wildcard(self):
        self.assertTrue(match_glob("src/auth/login.py", "src/auth/*.py"))

    def test_recursive_wildcard(self):
        self.assertTrue(match_glob("src/auth/deep/login.py", "src/**/*.py"))

    def test_no_match(self):
        self.assertFalse(match_glob("src/other/file.py", "src/auth/*.py"))


class TestStrictExitCode(unittest.TestCase):
    """Phase 2, 2-1: --strict fails only on must-update, never on review."""

    def test_clean_is_zero(self):
        report = {"summary": {"must-update": 0, "review": 0, "in-sync": 3}}
        self.assertEqual(doc_impact.strict_exit_code(report), 0)

    def test_review_only_is_zero(self):
        report = {"summary": {"must-update": 0, "review": 2, "in-sync": 1}}
        self.assertEqual(doc_impact.strict_exit_code(report), 0)

    def test_must_update_is_one(self):
        report = {"summary": {"must-update": 1, "review": 0, "in-sync": 0}}
        self.assertEqual(doc_impact.strict_exit_code(report), 1)

    def test_missing_summary_is_zero(self):
        self.assertEqual(doc_impact.strict_exit_code({}), 0)


if __name__ == "__main__":
    unittest.main()
