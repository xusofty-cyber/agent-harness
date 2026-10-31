#!/usr/bin/env python3
"""Tests for the pre-push / CI template gate (templates/pre-push-gate/).

Run: python3 tests/prepush_gate_test.py
Stdlib only (unittest + subprocess + tempfile). Covers, with real git
pushes to a local bare remote (no network):

  - gate-prepush-check.py: no-gate pass, passing-item pass, failing
    verification blocks, stale evidence blocks, human override skips,
    uncommitted gate-file warning and --strict block.
  - install-pre-push-gate.sh: refuses to overwrite an existing hook
    without --force, backs it up with --force.
  - pre-push hook end to end: a clean gate pushes, a broken gate
    blocks the push (the remote never receives the new commit).

The hook under test is the template copy in this repo, not an
installed hook in the test's own checkout.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates" / "pre-push-gate"
CHECK = TEMPLATES / "gate-prepush-check.py"
HOOK = TEMPLATES / "pre-push"
INSTALLER = TEMPLATES / "install-pre-push-gate.sh"

GIT_ENV = {
    **{k: v for k, v in os.environ.items() if k not in ("BASH_ENV", "ENV")},
    "GIT_AUTHOR_NAME": "prepush test",
    "GIT_AUTHOR_EMAIL": "test@agent-harness.local",
    "GIT_COMMITTER_NAME": "prepush test",
    "GIT_COMMITTER_EMAIL": "test@agent-harness.local",
}


def run(cmd, cwd, input_text=None, check=False):
    proc = subprocess.run(
        cmd, cwd=cwd, input=input_text, capture_output=True, text=True,
        env=GIT_ENV,
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"{cmd} failed ({proc.returncode}): {proc.stdout} {proc.stderr}")
    return proc


def passing_item(item_id, command, evidence_command=None, override=False):
    evidence = {
        "command": command if evidence_command is None else evidence_command,
        "exit_code": 0,
        "ran_at": "2026-10-29T00:00:00Z",
        "output_tail": "ok",
    }
    if override:
        evidence["override"] = {"by": "human", "reason": "test", "at": "2026-10-29T00:00:00Z"}
    return {
        "id": item_id,
        "priority": "p1",
        "area": "gate",
        "title": f"item {item_id}",
        "user_visible_behavior": "x",
        "status": "passing",
        "verification": {"command": command, "timeout_seconds": 60},
        "evidence": evidence,
    }


def write_gate(project, items):
    gate = project / "gate"
    gate.mkdir(parents=True, exist_ok=True)
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "test", "items": items}),
        encoding="utf-8",
    )
    return gate


def init_repo(path):
    run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    (path / "README.md").write_text("# test\n", encoding="utf-8")
    run(["git", "add", "-A"], cwd=path, check=True)
    run(["git", "commit", "-qm", "init"], cwd=path, check=True)


class CheckerTest(unittest.TestCase):
    def test_no_gate_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("nothing to check", proc.stdout)

    def test_passing_item_reverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_gate(project, [passing_item("ok-item", "true")])
            proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("re-verified", proc.stdout)

    def test_failing_verification_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_gate(project, [passing_item("bad-item", "false")])
            proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("bad-item", proc.stdout)

    def test_stale_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_gate(project, [passing_item("stale-item", "true", evidence_command="true-old")])
            proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("stale evidence", proc.stdout)

    def test_human_override_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_gate(project, [passing_item("ov-item", "false", override=True)])
            proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("SKIP", proc.stdout)

    def test_dirty_gate_file_warns_by_default_and_blocks_under_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_repo(project)
            write_gate(project, [passing_item("ok-item", "true")])
            run(["git", "add", "-A"], cwd=project, check=True)
            run(["git", "commit", "-qm", "commit gate"], cwd=project, check=True)
            write_gate(project, [passing_item("ok-item", "true"), passing_item("ok-2", "true")])
            warn_proc = run([sys.executable, str(CHECK), "--root", tmp], cwd=tmp)
            self.assertEqual(warn_proc.returncode, 0, warn_proc.stdout)
            self.assertIn("[WARN] uncommitted changes in gate/feature_list.json", warn_proc.stdout)
            strict_proc = run([sys.executable, str(CHECK), "--root", tmp, "--strict"], cwd=tmp)
            self.assertEqual(strict_proc.returncode, 1, strict_proc.stdout)
            self.assertIn("FAIL (--strict)", strict_proc.stdout)


class InstallerTest(unittest.TestCase):
    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_repo(project)
            hooks = project / ".git" / "hooks"
            (hooks / "pre-push").write_text("#!/bin/bash\necho existing\n", encoding="utf-8")
            proc = run(["bash", str(INSTALLER), tmp], cwd=tmp)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("existing", (hooks / "pre-push").read_text(encoding="utf-8"))

    def test_force_backs_up_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            init_repo(project)
            hooks = project / ".git" / "hooks"
            (hooks / "pre-push").write_text("#!/bin/bash\necho existing\n", encoding="utf-8")
            proc = run(["bash", str(INSTALLER), tmp, "--force"], cwd=tmp, check=True)
            backups = list(hooks.glob("pre-push.bak-*"))
            self.assertEqual(len(backups), 1)
            self.assertIn("existing", backups[0].read_text(encoding="utf-8"))
            self.assertTrue(
                os.access(hooks / "pre-push", os.X_OK)
                or bool((hooks / "pre-push").stat().st_mode & 0o111)
            )
            self.assertTrue((hooks / "gate-prepush-check.py").exists())


class HookEndToEndTest(unittest.TestCase):
    def _repo_with_remote(self, tmp):
        project = Path(tmp) / "work"
        remote = Path(tmp) / "remote.git"
        project.mkdir()
        run(["git", "init", "-q", "--bare", str(remote)], cwd=tmp, check=True)
        init_repo(project)
        run(["git", "remote", "add", "origin", str(remote)], cwd=project, check=True)
        return project, remote

    def test_clean_gate_pushes_broken_gate_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, remote = self._repo_with_remote(tmp)
            write_gate(project, [passing_item("ok-item", "true")])
            run(["git", "add", "-A"], cwd=project, check=True)
            run(["git", "commit", "-qm", "add gate"], cwd=project, check=True)
            run(["bash", str(INSTALLER), str(project)], cwd=project, check=True)
            hook_file = project / ".git" / "hooks" / "pre-push"
            if not os.access(hook_file, os.X_OK):
                clean_hook = run(["bash", str(hook_file)], cwd=project, input_text="")
                self.assertEqual(clean_hook.returncode, 0, clean_hook.stderr)
                write_gate(project, [passing_item("ok-item", "false")])
                run(["git", "add", "-A"], cwd=project, check=True)
                run(["git", "commit", "-qm", "break gate"], cwd=project, check=True)
                blocked = run(["bash", str(hook_file)], cwd=project, input_text="")
                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("BLOCKED", blocked.stderr)
                return
            pushed = run(["git", "push", "origin", "main"], cwd=project)
            self.assertEqual(pushed.returncode, 0, pushed.stderr)
            write_gate(project, [passing_item("ok-item", "false")])
            run(["git", "add", "-A"], cwd=project, check=True)
            run(["git", "commit", "-qm", "break gate"], cwd=project, check=True)
            blocked = run(["git", "push", "origin", "main"], cwd=project)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("BLOCKED", blocked.stderr)
            head = run(["git", "rev-parse", "main"], cwd=remote, check=True)
            local = run(["git", "rev-parse", "main"], cwd=project, check=True)
            self.assertNotEqual(head.stdout.strip(), local.stdout.strip())


if __name__ == "__main__":
    unittest.main()
