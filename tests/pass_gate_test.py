#!/usr/bin/env python3
"""Regression tests for gate/pass-gate.py status pluralization (Phase 5).

Run: python3 tests/pass_gate_test.py
Stdlib only. The status line must read "0 items" / "1 item" / "2 items".
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PASS_GATE = ROOT / "gate" / "pass-gate.py"


def _status_with(n_items):
    # Write the feature list directly: pass-gate init seeds 3 example
    # items from the template, so init+add can never produce exactly
    # 0/1/2 items. (Found by the verify script failing the first manual
    # baseline attempt — the verify caught the wrong assumption.)
    tmpdir = Path(tempfile.mkdtemp())
    gate = tmpdir / "gate"
    gate.mkdir(parents=True)
    items = [{"id": f"item-{i}", "title": f"item {i}", "priority": "p1",
              "area": "gate", "user_visible_behavior": "x",
              "status": "not_started",
              "verification": {"command": "true", "timeout_seconds": 60},
              "evidence": None} for i in range(n_items)]
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "plural-test", "items": items}))
    # NOTE: --root takes the PROJECT root; pass-gate appends gate/ itself.
    out = subprocess.run([sys.executable, str(PASS_GATE), "--root", str(tmpdir),
                          "status"], check=True, capture_output=True, text=True)
    return out.stdout


class StatusPluralTest(unittest.TestCase):
    def test_zero_items(self):
        self.assertIn("(0 items)", _status_with(0))

    def test_one_item(self):
        out = _status_with(1)
        self.assertIn("(1 item)", out)
        self.assertNotIn("(1 items)", out)

    def test_two_items(self):
        self.assertIn("(2 items)", _status_with(2))


if __name__ == "__main__":
    unittest.main()


# --- Behavior suite (ported from v3-yunkai, skeleton-adapted, review 2026-10-29) ---
# Yunkai's suite targeted a different gate shape (array verification,
# --file flag, by/commands/history/failures fields, --layer flag,
# revert command, WIP enforced at verify, validate subcommand). The
# mapping to this branch's skeleton semantics:
# - verify-success: status passing, evidence {exit_code 0, output_sha256},
#   event "verified" (not "verify_pass"; no by/commands fields).
# - verify-failure: start first, then verify BAD -> exit 1, status stays
#   in_progress, evidence None, event "verify_failed" containing the
#   exit code (no --layer flag, no failures[] field).
# - passing-irreversible: verify on a passing item exits 1 ("cannot
#   verify ... status is passing"); there is no revert command — the
#   skeleton equivalent is reopen.
# - revert -> reopen --reason (required): status in_progress, evidence
#   None, event "reopened" containing the reason, and the prior
#   "verified" event still present in the append-only log (history is
#   preserved via events, not a history[] field).
# - WIP: enforced at start ("WIP=1: another item is already
#   in_progress"), not at verify — so this tests start/start refusal.
# - validate-claimed-completion / validate-empty-verification: the
#   skeleton has no validate subcommand; status runs validate() and
#   exits 1 (passing-without-evidence / empty-command errors).
# No new gate features are invented for this port.
OK_CMD = f'{sys.executable} -c "pass"'
BAD_CMD = f'{sys.executable} -c "import sys; sys.exit(3)"'


def _project_with(items):
    tmpdir = Path(tempfile.mkdtemp())
    gate = tmpdir / "gate"
    gate.mkdir(parents=True)
    (gate / "feature_list.json").write_text(
        json.dumps({"version": 1, "project": "behavior-test",
                    "items": items}), encoding="utf-8")
    return tmpdir


def _behavior_item(fid, command, status="not_started"):
    return {"id": fid, "priority": "p1", "area": "test", "title": fid,
            "user_visible_behavior": "observable", "status": status,
            "verification": {"command": command, "timeout_seconds": 60},
            "evidence": None, "notes": ""}


def _run_gate(root, *argv):
    return subprocess.run([sys.executable, str(PASS_GATE), "--root",
                           str(root), *argv],
                          capture_output=True, text=True, timeout=120)


def _load_items(root):
    return json.loads((root / "gate" / "feature_list.json")
                      .read_text(encoding="utf-8"))["items"]


def _events(root):
    p = root / "gate" / "events.jsonl"
    return p.read_text(encoding="utf-8") if p.exists() else ""


class PassGateBehaviorTest(unittest.TestCase):
    def test_verify_success_writes_evidence_and_event(self):
        root = _project_with([_behavior_item("a", OK_CMD)])
        self.assertEqual(_run_gate(root, "start", "--id", "a").returncode, 0)
        r = _run_gate(root, "verify", "--id", "a")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        item = _load_items(root)[0]
        self.assertEqual(item["status"], "passing")
        self.assertEqual(item["evidence"]["exit_code"], 0)
        self.assertIn("output_sha256", item["evidence"])
        self.assertIn('"verified"', _events(root))

    def test_verify_failure_keeps_in_progress_and_records_failure(self):
        root = _project_with([_behavior_item("a", BAD_CMD)])
        self.assertEqual(_run_gate(root, "start", "--id", "a").returncode, 0)
        r = _run_gate(root, "verify", "--id", "a")
        self.assertEqual(r.returncode, 1)
        item = _load_items(root)[0]
        self.assertEqual(item["status"], "in_progress")
        self.assertIsNone(item["evidence"])
        events = _events(root)
        self.assertIn('"verify_failed"', events)
        self.assertIn("exit 3", events)

    def test_passing_is_irreversible_without_reopen(self):
        root = _project_with([_behavior_item("a", OK_CMD)])
        self.assertEqual(_run_gate(root, "start", "--id", "a").returncode, 0)
        self.assertEqual(_run_gate(root, "verify", "--id", "a").returncode, 0)
        r = _run_gate(root, "verify", "--id", "a")
        self.assertEqual(r.returncode, 1)
        self.assertIn("cannot verify", r.stdout + r.stderr)
        self.assertEqual(_load_items(root)[0]["status"], "passing")

    def test_reopen_requires_reason_and_preserves_history(self):
        root = _project_with([_behavior_item("a", OK_CMD)])
        self.assertEqual(_run_gate(root, "start", "--id", "a").returncode, 0)
        self.assertEqual(_run_gate(root, "verify", "--id", "a").returncode, 0)
        r = _run_gate(root, "reopen", "--id", "a",
                      "--reason", "upstream API changed")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        item = _load_items(root)[0]
        self.assertEqual(item["status"], "in_progress")
        self.assertIsNone(item["evidence"])
        events = _events(root)
        self.assertIn('"verified"', events)
        self.assertIn('"reopened"', events)
        self.assertIn("upstream API changed", events)

    def test_wip_limit_blocks_second_start(self):
        root = _project_with([_behavior_item("a", BAD_CMD),
                              _behavior_item("b", OK_CMD)])
        self.assertEqual(_run_gate(root, "start", "--id", "a").returncode, 0)
        r = _run_gate(root, "start", "--id", "b")
        self.assertEqual(r.returncode, 1)
        self.assertIn("WIP=1", r.stdout + r.stderr)

    def test_status_rejects_claimed_completion(self):
        root = _project_with(
            [_behavior_item("a", OK_CMD, status="passing")])
        r = _run_gate(root, "status")
        self.assertEqual(r.returncode, 1)
        self.assertIn("requires non-empty evidence", r.stdout + r.stderr)

    def test_status_rejects_empty_verification(self):
        root = _project_with([_behavior_item("a", "")])
        r = _run_gate(root, "status")
        self.assertEqual(r.returncode, 1)
        self.assertIn("non-empty string", r.stdout + r.stderr)
