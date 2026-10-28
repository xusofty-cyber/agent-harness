#!/usr/bin/env python3
"""Tests for the eval/cost.py hard-stop gate (yunyi D23; merge D57).

Run: python3 tests/cost_test.py
All cases use temporary ledger/budget files; the real ledger is untouched.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COST = ROOT / "eval" / "cost.py"

BASE_BUDGET = {
    "hard_stop_enabled": True,
    "hard_stop_task": {"max_verifications": 10, "max_duration_s": 3600, "max_retries": 5},
    "hard_stop_day": {"max_verifications": 100, "max_duration_s": 28800},
}


def run_check(tmp, ledger_records, budget, task="T1", day="2026-10-28"):
    ledger = tmp / "ledger.jsonl"
    ledger.write_text("".join(json.dumps(r) + "\n" for r in ledger_records), encoding="utf-8")
    bpath = tmp / "budget.json"
    bpath.write_text(json.dumps(budget), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(COST), "check", "--task", task, "--ledger", str(ledger), "--budget", str(bpath), "--day", day],
        capture_output=True, text=True, cwd=ROOT,
    )
    return proc


def test_under_ceiling_ok():
    with tempfile.TemporaryDirectory() as d:
        proc = run_check(Path(d), [{"task": "T1", "date": "2026-10-28", "duration_ms": 30000, "verifications": 2, "retries": 0}], BASE_BUDGET)
        assert proc.returncode == 0, proc.stdout
        assert "BUDGET OK" in proc.stdout


def test_task_verifications_stop():
    with tempfile.TemporaryDirectory() as d:
        proc = run_check(Path(d), [{"task": "T1", "date": "2026-10-28", "duration_ms": 1000, "verifications": 10, "retries": 0}], BASE_BUDGET)
        assert proc.returncode == 2, proc.stdout
        assert "BUDGET STOP" in proc.stdout
        assert "budget_stop" in (Path(d) / "ledger.jsonl").read_text()


def test_task_duration_stop():
    with tempfile.TemporaryDirectory() as d:
        proc = run_check(Path(d), [{"task": "T1", "date": "2026-10-28", "duration_ms": 3600000, "verifications": 1, "retries": 0}], BASE_BUDGET)
        assert proc.returncode == 2, proc.stdout


def test_day_ceiling_stop():
    with tempfile.TemporaryDirectory() as d:
        recs = [{"task": f"T{i}", "date": "2026-10-28", "duration_ms": 1000, "verifications": 50, "retries": 0} for i in range(2)]
        proc = run_check(Path(d), recs, BASE_BUDGET, task="T9")
        assert proc.returncode == 2, proc.stdout


def test_hard_stop_off_never_blocks():
    with tempfile.TemporaryDirectory() as d:
        off = dict(BASE_BUDGET, hard_stop_enabled=False)
        proc = run_check(Path(d), [{"task": "T1", "date": "2026-10-28", "duration_ms": 1000, "verifications": 999, "retries": 99}], off)
        assert proc.returncode == 0, proc.stdout
        assert "hard stop OFF" in proc.stdout


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
    print("all cost tests passed")


if __name__ == "__main__":
    main()
