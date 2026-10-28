#!/usr/bin/env python3
"""Tests for eval/check-thresholds.py (merged from v3-yunyi, adapted to
the skeleton's run-record format: outcome / verify_attempts / duration_s /
false_completion in eval/results/*_{arm}_rep*.json).

Run: python3 tests/threshold_test.py
Uses --dir to point the checker at synthetic temp records; the real
results are untouched.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "eval" / "check-thresholds.py"


def run(records_dir, strict=False):
    args = [sys.executable, str(CHECK), "--dir", str(records_dir)]
    if strict:
        args.append("--strict")
    return subprocess.run(args, capture_output=True, text=True, cwd=ROOT)


def write_records(tmp, records):
    for rec in records:
        name = f"{rec['task']}_{rec['arm']}_rep{rec['rep']}.json"
        (tmp / name).write_text(json.dumps(rec), encoding="utf-8")
    return tmp


def group_ok(task="t1-bugfix", arm="bare"):
    return [{"task": task, "arm": arm, "rep": i, "outcome": "pass",
             "verify_attempts": 1, "duration_s": 6, "false_completion": 0}
            for i in (1, 2, 3)]


def test_all_pass_no_breach():
    with tempfile.TemporaryDirectory() as d:
        tmp = write_records(Path(d), group_ok() + group_ok(arm="gate"))
        proc = run(tmp)
        assert proc.returncode == 0, proc.stdout
        assert "no threshold breach" in proc.stdout


def test_fail_breaches_strict():
    with tempfile.TemporaryDirectory() as d:
        bad = group_ok()
        bad[0]["outcome"] = "fail"
        proc = run(write_records(Path(d), bad), strict=True)
        assert proc.returncode == 2, proc.stdout
        assert "THRESHOLD BREACH" in proc.stdout


def test_verify_attempts_median_breaches():
    with tempfile.TemporaryDirectory() as d:
        bad = [{**r, "verify_attempts": 6} for r in group_ok()]
        proc = run(write_records(Path(d), bad), strict=True)
        assert proc.returncode == 2, proc.stdout
        assert "verify_attempts median" in proc.stdout


def test_duration_median_breaches():
    with tempfile.TemporaryDirectory() as d:
        bad = [{**r, "duration_s": 200} for r in group_ok()]
        proc = run(write_records(Path(d), bad), strict=True)
        assert proc.returncode == 2, proc.stdout
        assert "duration_s median" in proc.stdout


def test_false_completion_breaches():
    with tempfile.TemporaryDirectory() as d:
        bad = group_ok()
        bad[2]["false_completion"] = 1
        proc = run(write_records(Path(d), bad), strict=True)
        assert proc.returncode == 2, proc.stdout
        assert "false completion" in proc.stdout


def test_insufficient_runs_no_breach():
    with tempfile.TemporaryDirectory() as d:
        proc = run(write_records(Path(d), group_ok()[:2]), strict=True)
        assert proc.returncode == 0, proc.stdout
        assert "no conclusion" in proc.stdout
        assert "THRESHOLD BREACH" not in proc.stdout


def test_default_mode_never_fails_on_breach():
    with tempfile.TemporaryDirectory() as d:
        bad = group_ok()
        bad[0]["outcome"] = "fail"
        proc = run(write_records(Path(d), bad), strict=False)
        assert proc.returncode == 0, proc.stdout
        assert "THRESHOLD BREACH" in proc.stdout


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
    print("all threshold tests passed")


if __name__ == "__main__":
    main()
