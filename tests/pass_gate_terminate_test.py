#!/usr/bin/env python3
"""Tests for pass-gate.py terminate / handoff / run (merged from v3-yunyi).

Run: python3 tests/pass_gate_terminate_test.py
Stdlib only. Each test builds a scratch project (and, for run, a scratch
git repo) in a temp dir; nothing here touches the real repo or main.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS_GATE = ROOT / "gate" / "pass-gate.py"


def _project(tmpdir, verification="true", item_id="demo-item"):
    """A minimal gate project: one in_progress item + clean-state config
    + SESSION_STATE mentioning the item + a parseable init.template.sh."""
    gate = tmpdir / "gate"
    gate.mkdir(parents=True)
    items = [{"id": item_id, "title": "Demo item", "priority": "p1",
              "area": "gate", "user_visible_behavior": "x",
              "status": "in_progress",
              "verification": {"command": verification,
                               "timeout_seconds": 60},
              "evidence": None}]
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "terminate-test",
                    "items": items}))
    (gate / "clean-state.json").write_text(
        json.dumps({"build": "true", "test": "true", "start": "true"}))
    (gate / "init.template.sh").write_text("#!/bin/sh\ntrue\n")
    (tmpdir / "SESSION_STATE.md").write_text(
        f"# SESSION_STATE\n\n- In progress: {item_id}\n- Next step: verify\n")
    return tmpdir


def _gate(*args, cwd):
    proc = subprocess.run([sys.executable, str(PASS_GATE), "--root", str(cwd),
                           *args], capture_output=True, text=True)
    return proc


def _termination(tmpdir):
    p = tmpdir / "gate" / "termination.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _item(tmpdir, item_id="demo-item"):
    data = json.loads((tmpdir / "gate" / "feature_list.json").read_text())
    return next(i for i in data["items"] if i["id"] == item_id)


def _events(tmpdir):
    p = tmpdir / "gate" / "events.jsonl"
    return p.read_text() if p.exists() else ""


class TerminateTest(unittest.TestCase):
    def test_full_chain_static_runtime_system(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            for stage in ("static", "runtime", "system"):
                proc = _gate("terminate", "--id", "demo-item",
                             "--stage", stage, cwd=tmpdir)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(_item(tmpdir)["status"], "passing")
            ev = _item(tmpdir)["evidence"]
            self.assertEqual(ev["exit_code"], 0)
            self.assertIn("output_sha256", ev)
            done = _termination(tmpdir)["demo-item"]
            self.assertTrue(done["static"] and done["runtime"] and done["system"])
            self.assertIn("passing via three-layer termination", _events(tmpdir))

    def test_skip_refused_and_logged(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "runtime", cwd=tmpdir)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("termination_skip_refused", _events(tmpdir))
            _gate("terminate", "--id", "demo-item", "--stage", "static",
                  cwd=tmpdir)
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "system", cwd=tmpdir)
            self.assertEqual(proc.returncode, 2)

    def test_runtime_failure_blocks_and_keeps_status(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d), verification="false")
            _gate("terminate", "--id", "demo-item", "--stage", "static",
                  cwd=tmpdir)
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "runtime", cwd=tmpdir)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(_item(tmpdir)["status"], "in_progress")
            self.assertNotIn("runtime", _termination(tmpdir).get("demo-item", {}))

    def test_reopen_clears_termination(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            for stage in ("static", "runtime", "system"):
                _gate("terminate", "--id", "demo-item", "--stage", stage,
                      cwd=tmpdir)
            self.assertIn("demo-item", _termination(tmpdir))
            proc = _gate("reopen", "--id", "demo-item",
                         "--reason", "evidence was stale", cwd=tmpdir)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertNotIn("demo-item", _termination(tmpdir))
            # Terminate starts from static again, not from stale marks.
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "runtime", cwd=tmpdir)
            self.assertEqual(proc.returncode, 2)

    def test_corrupt_termination_is_fatal_not_silent(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            (tmpdir / "gate" / "termination.json").write_text("{not json")
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "static", cwd=tmpdir)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("not valid JSON", proc.stdout + proc.stderr)

    def test_terminate_requires_in_progress(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            _gate("block", "--id", "demo-item", "--reason", "waiting",
                  cwd=tmpdir)
            proc = _gate("terminate", "--id", "demo-item",
                         "--stage", "static", cwd=tmpdir)
            # Wrong status is a rule violation (exit 1, same as verify);
            # only a layer skip is the exit-2 REFUSED case.
            self.assertEqual(proc.returncode, 1)


class HandoffTest(unittest.TestCase):
    def test_handoff_stdout_and_file(self):
        with tempfile.TemporaryDirectory() as d:
            tmpdir = _project(Path(d))
            proc = _gate("handoff", cwd=tmpdir)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("0 passing; in progress: 1", proc.stdout)
            self.assertIn("demo-item", proc.stdout)
            self.assertIn("Session breakpoint", proc.stdout)
            self.assertIn("In progress: demo-item", proc.stdout)
            self.assertIn("Recent commits", proc.stdout)
            self.assertIn("Recent gate events", proc.stdout)
            out = tmpdir / "handoff.md"
            proc = _gate("handoff", "--out", str(out), cwd=tmpdir)
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out.exists())
            self.assertFalse((tmpdir / "handoff.md.tmp").exists())
            self.assertIn("Handoff draft", out.read_text())


def _git_repo(tmpdir):
    def sh(*a, cwd=None):
        return subprocess.run(a, cwd=cwd or tmpdir, capture_output=True,
                              text=True, check=True)

    sh("git", "init", "-q", "-b", "main")
    sh("git", "config", "user.email", "t@localhost")
    sh("git", "config", "user.name", "t")
    _project(tmpdir)
    sh("git", "add", "-A")
    sh("git", "commit", "-qm", "base")
    return tmpdir


class RunTest(unittest.TestCase):
    def test_run_with_branch_success_no_merge(self):
        with tempfile.TemporaryDirectory() as d:
            repo = _git_repo(Path(d))
            proc = _gate("run", "--worktree", "w1", "--branch", "run-branch",
                         "--", "true", cwd=repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("does NOT auto-merge", proc.stdout)
            out = subprocess.run(["git", "branch", "--list", "run-branch"],
                                 cwd=repo, capture_output=True, text=True)
            self.assertIn("run-branch", out.stdout)
            out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                 cwd=repo, capture_output=True, text=True)
            self.assertEqual(out.stdout.strip(), "main")
            self.assertTrue((repo / ".worktrees" / "w1").exists())
            # Same worktree name is refused.
            proc = _gate("run", "--worktree", "w1", "--", "true", cwd=repo)
            self.assertEqual(proc.returncode, 2)

    def test_run_detached_head_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            repo = _git_repo(Path(d))
            proc = _gate("run", "--worktree", "w2", "--", "true", cwd=repo)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("detached HEAD", proc.stdout)

    def test_run_host_failure_passthrough_and_left_in_place(self):
        with tempfile.TemporaryDirectory() as d:
            repo = _git_repo(Path(d))
            proc = _gate("run", "--worktree", "w3", "--", "false", cwd=repo)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("NOT merged", proc.stdout + proc.stderr)
            self.assertTrue((repo / ".worktrees" / "w3").exists())

    def test_run_requires_command(self):
        with tempfile.TemporaryDirectory() as d:
            repo = _git_repo(Path(d))
            proc = _gate("run", "--worktree", "w4", cwd=repo)
            self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
