#!/usr/bin/env python3
"""Unit tests for tools/cost-ledger.py (Phase 2, 2-5).
Run: python3 tests/cost_ledger_test.py
Stdlib only.
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import importlib.util
spec = importlib.util.spec_from_file_location(
    "cost_ledger",
    Path(__file__).resolve().parent.parent / "tools" / "cost-ledger.py",
)
cost_ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cost_ledger)


def _ts_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CostLedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gate = Path(self.tmp.name) / "gate"
        self.gate.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _write_events(self, events):
        path = self.gate / "events.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for seq, ev in enumerate(events, 1):
                row = {"seq": seq, "ts": _ts_now(), "actor": "test",
                       "event": ev, "item_id": None, "detail": ""}
                fh.write(json.dumps(row) + "\n")

    def test_init_budget_creates_defaults_and_never_overwrites(self):
        rc = cost_ledger.main(["init-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 0)
        budget = json.loads((self.gate / "cost-budget.json").read_text())
        for key in ("max_runs_per_day", "max_tool_calls_per_day",
                    "max_verify_failures_per_day", "max_overrides_per_day",
                    "max_stage_duration_ms"):
            self.assertIn(key, budget)
        (self.gate / "cost-budget.json").write_text('{"custom": true}')
        rc = cost_ledger.main(["init-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 0)
        self.assertEqual(
            json.loads((self.gate / "cost-budget.json").read_text()),
            {"custom": True})

    def test_record_and_summary_counts_hook_style_tool_calls(self):
        # PostToolUse hook lines have no "kind", only hook:"post-tool-use".
        ledger = self.gate / "cost-ledger.jsonl"
        with ledger.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _ts_now(), "hook": "post-tool-use",
                                 "tool": "Bash"}) + "\n")
            fh.write(json.dumps({"ts": _ts_now(), "hook": "post-tool-use",
                                 "tool": "Read"}) + "\n")
        rc = cost_ledger.main(["record", "--gate-dir", str(self.gate),
                               "--kind", "stage", "--stage", "阶段 3",
                               "--status", "fail", "--duration-ms", "1234",
                               "--run-id", "run-1"])
        self.assertEqual(rc, 0)
        rc = cost_ledger.main(["summary", "--gate-dir", str(self.gate),
                               "--json"])
        self.assertEqual(rc, 0)

    def test_summary_aggregates_events(self):
        self._write_events(["verify_failed", "verify_failed", "override",
                            "stop_override", "init"])
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cost_ledger.main(["summary", "--gate-dir", str(self.gate),
                                   "--json"])
        self.assertEqual(rc, 0)
        agg = json.loads(buf.getvalue())
        self.assertEqual(agg["verify_failures_today"], 2)
        self.assertEqual(agg["verify_failures_total"], 2)
        self.assertEqual(agg["overrides_today"], 2)
        self.assertEqual(agg["overrides_total"], 2)

    def test_check_budget_within(self):
        cost_ledger.main(["init-budget", "--gate-dir", str(self.gate)])
        rc = cost_ledger.main(["check-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 0)

    def test_check_budget_over_records_event_once(self):
        cost_ledger.main(["init-budget", "--gate-dir", str(self.gate)])
        budget = json.loads((self.gate / "cost-budget.json").read_text())
        budget["max_tool_calls_per_day"] = 1
        (self.gate / "cost-budget.json").write_text(json.dumps(budget))
        ledger = self.gate / "cost-ledger.jsonl"
        with ledger.open("w", encoding="utf-8") as fh:
            for _ in range(3):
                fh.write(json.dumps({"ts": _ts_now(), "hook": "post-tool-use",
                                     "tool": "Bash"}) + "\n")
        rc = cost_ledger.main(["check-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 1)
        events = list(cost_ledger._read_lines(self.gate / "events.jsonl"))
        exceeded = [e for e in events if e["event"] == "budget_exceeded"]
        self.assertEqual(len(exceeded), 1)
        self.assertIn("max_tool_calls_per_day: 3 > 1", exceeded[0]["detail"])
        # Second check: same over-budget state must not duplicate the event.
        rc = cost_ledger.main(["check-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 1)
        events = list(cost_ledger._read_lines(self.gate / "events.jsonl"))
        exceeded = [e for e in events if e["event"] == "budget_exceeded"]
        self.assertEqual(len(exceeded), 1)

    def test_check_budget_missing_budget_file(self):
        rc = cost_ledger.main(["check-budget", "--gate-dir", str(self.gate)])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
