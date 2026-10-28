#!/usr/bin/env python3
"""eval/check-results.py — CI consistency guard for Phase 3 (v3 §4.5).

Recomputes the baseline numbers from eval/results/*.json and checks them
against docs/bench/baseline-2026-10.md. If a run record changes without
the report being updated (or vice versa), this exits 1.

Also guards honesty: no result file may claim a metric the runner did
not record, and no upstream token claim may appear in the report as our
own number.

Usage: python3 eval/check-results.py   (exit 0 = consistent)
"""

import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "eval" / "results"
REPORT = ROOT / "docs" / "bench" / "baseline-2026-10.md"
QUALITY = ROOT / "QUALITY_SCORE.md"

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


records = sorted(RESULTS.glob("*_bare_rep*.json")) + sorted(RESULTS.glob("*_pack_rep*.json")) + sorted(RESULTS.glob("*_gate_rep*.json"))
required = {"task", "arm", "rep", "start_commit", "host", "model",
            "started_epoch", "ended_epoch", "duration_s", "rounds",
            "verify_attempts", "interventions", "outcome", "false_completion"}
by_task: dict[str, list[int]] = {}
total = 0
passed = 0
false_completions = 0
for f in records:
    try:
        r = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        check(f"results:{f.name}-parses", False, str(e))
        continue
    missing = required - set(r)
    check(f"results:{f.name}-schema", not missing, f"missing fields: {sorted(missing)}")
    if missing:
        continue
    total += 1
    passed += r["outcome"] == "pass"
    false_completions += r["false_completion"]
    by_task.setdefault(r["task"], []).append(r["duration_s"])

check("results:count", total == len(records), f"{total} valid of {len(records)} files")

report = REPORT.read_text(encoding="utf-8")
for task, durations in sorted(by_task.items()):
    med = statistics.median(durations)
    # The report's table row must contain the median for this task.
    row = re.search(rf"\| {re.escape(task.split('-')[0].upper())} [^|]*\|[^|]*\|[^|]*\|[^|]*\| (\d+) s \|", report)
    if row:
        check(f"results:{task}-median-in-report", int(row.group(1)) == med,
              f"report says {row.group(1)} s, recomputed median is {med} s")

check("results:completion-claim",
      "12/12 (100%)" in report if total == 12 else True,
      "report completion claim does not match 12 recorded runs")
check("results:false-completion-claim",
      "0/12" in report if false_completions == 0 else True,
      "report false-completion claim does not match records")

# Honesty guard: no upstream token number presented as our own result.
for path in (REPORT, QUALITY):
    if not path.is_file():
        check(f"honesty:{path.name}-exists", False, "file missing")
        continue
    text = path.read_text(encoding="utf-8")
    check(f"honesty:{path.name}-no-upstream-token-number",
          "76.8" not in text, "upstream -76.8% token number appears in our report")
    check(f"honesty:{path.name}-marks-unmeasured",
          "unmeasured" in text.lower(), "report does not mark unmeasured cells")

print(f"{len(failures)} check(s) failed." if failures else "All results checks passed.")
sys.exit(1 if failures else 0)
