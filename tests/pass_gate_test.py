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


def _load_pass_gate():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pass_gate_mod", str(PASS_GATE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class EventsLogToleranceTest(unittest.TestCase):
    """P0-1: the event log must never crash the gate with a traceback.

    A legacy seq-less event (as comet_adapter used to write) must not
    break the next append, and a corrupt line must fail a mutating
    command cleanly (exit 2) without changing any state.
    """

    def test_append_tolerates_seq_less_last_event(self):
        mod = _load_pass_gate()
        with tempfile.TemporaryDirectory() as td:
            gate = Path(td) / "gate"
            gate.mkdir()
            (gate / "events.jsonl").write_text(
                '{"ts": "2026-10-29T00:00:00Z", "event": "legacy", '
                '"item": "x", "via": "old-writer", "files": []}\n',
                encoding="utf-8")
            rec = mod._append_event(td, "test_event", "x", "d")
            self.assertEqual(rec["seq"], 1)
            (gate / "events.jsonl").write_text(
                '{"seq": 3, "ts": "t", "actor": "a", "event": "e", '
                '"item_id": null, "detail": ""}\n'
                '{"ts": "t", "event": "legacy2"}\n',
                encoding="utf-8")
            rec = mod._append_event(td, "test_event2", "x", "d")
            self.assertEqual(rec["seq"], 4)

    def test_read_events_raises_clear_error_on_bad_line(self):
        mod = _load_pass_gate()
        with tempfile.TemporaryDirectory() as td:
            gate = Path(td) / "gate"
            gate.mkdir()
            (gate / "events.jsonl").write_text(
                '{"seq": 1, "ts": "t", "actor": "a", "event": "e", '
                '"item_id": null, "detail": ""}\nNOT-JSON\n',
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                mod._read_events(td)
            self.assertIn("line 2", str(ctx.exception))
            self.assertIn("no state was changed", str(ctx.exception))

    def test_mutating_command_fails_clean_without_state_change(self):
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            gate = tmpdir / "gate"
            gate.mkdir()
            items = [{"id": "item-0", "title": "item 0", "priority": "p1",
                      "area": "gate", "user_visible_behavior": "x",
                      "status": "in_progress",
                      "verification": {"command": "true",
                                       "timeout_seconds": 60},
                      "evidence": None}]
            fl = gate / "feature_list.json"
            fl.write_text(json.dumps(
                {"version": 1, "project": "p", "items": items}))
            (gate / "events.jsonl").write_text(
                '{"seq": 1, "ts": "t", "actor": "a", "event": "e", '
                '"item_id": null, "detail": ""}\nNOT-JSON\n',
                encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(PASS_GATE), "--root", str(tmpdir),
                 "block", "--id", "item-0", "--reason", "r"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertNotIn("Traceback", r.stderr)
            self.assertIn("not valid JSON", r.stderr)
            data = json.loads(fl.read_text())
            self.assertEqual(data["items"][0]["status"], "in_progress")


class ValidateSchemaDriftTest(unittest.TestCase):
    """P1-5: validate() must not crash and must not drift from the schema.

    A non-dict verification used to crash the evidence comparison with
    AttributeError; timeout_seconds 99999 and evidence missing
    ran_at/output_tail used to validate clean; additionalProperties
    was never enforced; and the schema itself omitted output_sha256
    which verify/terminate actually write.
    """

    def _item(self, **over):
        item = {"id": "x", "priority": "p0", "area": "g", "title": "t",
                "user_visible_behavior": "b", "status": "not_started",
                "verification": {"command": "true", "timeout_seconds": 60},
                "evidence": None}
        item.update(over)
        return item

    def test_non_dict_verification_does_not_crash(self):
        mod = _load_pass_gate()
        data = {"version": 1, "project": "p",
                "items": [self._item(status="passing",
                                     verification="not-a-dict",
                                     evidence={"command": "true", "exit_code": 0,
                                               "ran_at": "2026-10-29T00:00:00Z",
                                               "output_tail": "ok"})]}
        errors = mod.validate(data)
        self.assertIn("items[0].verification must be an object", errors)

    def test_timeout_range_and_evidence_required_fields(self):
        mod = _load_pass_gate()
        data = {"version": 1, "project": "p",
                "items": [self._item(status="passing",
                                     verification={"command": "true",
                                                   "timeout_seconds": 99999},
                                     evidence={"command": "true",
                                               "exit_code": 0})]}
        errors = mod.validate(data)
        self.assertTrue(any("timeout_seconds" in e for e in errors), errors)
        self.assertTrue(any("ran_at" in e for e in errors), errors)
        self.assertTrue(any("output_tail" in e for e in errors), errors)

    def test_additional_properties_enforced(self):
        mod = _load_pass_gate()
        data = {"version": 1, "project": "p",
                "items": [self._item(surprise=1)]}
        errors = mod.validate(data)
        self.assertTrue(any("unknown fields" in e for e in errors), errors)

    def test_tool_written_evidence_shape_validates(self):
        mod = _load_pass_gate()
        data = {"version": 1, "project": "p",
                "items": [self._item(status="passing",
                                     evidence={"command": "true", "exit_code": 0,
                                               "ran_at": "2026-10-29T00:00:00Z",
                                               "output_tail": "ok",
                                               "output_sha256": "ab" * 32})]}
        self.assertEqual(mod.validate(data), [])


class StatusPluralTest(unittest.TestCase):
    def test_zero_items(self):
        self.assertIn("(0 items)", _status_with(0))

    def test_one_item(self):
        out = _status_with(1)
        self.assertIn("(1 item)", out)
        self.assertNotIn("(1 items)", out)

    def test_two_items(self):
        self.assertIn("(2 items)", _status_with(2))


class VerificationLevelTest(unittest.TestCase):
    """D66: verification.level is optional, enum-checked, and only
    descriptive — an unknown level is a validation error, a missing
    level is not, and check-clean summarises the passing mix."""

    def _data(self, level_marker):
        item = {"id": "a", "title": "a", "priority": "p1", "area": "gate",
                "user_visible_behavior": "x", "status": "not_started",
                "verification": {"command": "true", "timeout_seconds": 60},
                "evidence": None}
        if level_marker is not None:
            item["verification"]["level"] = level_marker
        return {"version": 1, "project": "t", "items": [item]}

    def test_valid_levels_and_absence_validate(self):
        mod = _load_pass_gate()
        for lvl in ("assert", "unit", "integration", "e2e", None):
            self.assertEqual(mod.validate(self._data(lvl)), [],
                             f"level={lvl!r} should validate")

    def test_unknown_level_rejected(self):
        mod = _load_pass_gate()
        errors = mod.validate(self._data("smoke"))
        self.assertTrue(any("verification.level" in e for e in errors),
                        errors)


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

