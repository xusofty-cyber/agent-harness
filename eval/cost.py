#!/usr/bin/env python3
"""cost.py — minimal cost ledger (v3 Phase 2.6, hard stop since yunyi D23;
ported to feat/merge-v3 by user final ruling 2026-10-29, see D57).

Usage:
    python3 eval/cost.py record --task <name> -- <command...>
        Run a command, measure its wall duration, verification runs
        (counted by the caller via --verifications, --failures, --retries,
        --interventions), and append one JSONL record to
        eval/cost-ledger.jsonl (local only, never committed — see
        .gitignore note in eval/cost-budget.json).
    python3 eval/cost.py report [--budget eval/cost-budget.json]
        Print totals and, if any threshold is exceeded, an ALERT line.
        Reporting never blocks.
    python3 eval/cost.py check --task <name> [--ledger PATH] [--budget PATH]
        Hard-stop gate, to be consulted BEFORE starting a new
        verification run. Exit 0 = budget remains, run may start.
        Exit 2 = BUDGET STOP: a hard-stop ceiling is exhausted, the
        run must NOT start; the stop is logged to the ledger and the
        task is to be recorded as blocked (not passing, not failed).
        A stopped task resumes only after a human raises the budget
        or a new day starts (DECISIONS.md). Checking never kills an
        in-flight run — it only refuses new ones.

Token counts are recorded only when the host reliably provides them;
otherwise token_count is null and proxy metrics (runs, duration,
failures) are used. No token number is ever invented.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "eval" / "cost-ledger.jsonl"
BUDGET = ROOT / "eval" / "cost-budget.json"


def cmd_record(args) -> int:
    start = time.time()
    proc = subprocess.run(args.host_command)
    duration_ms = int((time.time() - start) * 1000)
    record = {
        "task": args.task,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "duration_ms": duration_ms,
        "command_exit": proc.returncode,
        "verifications": args.verifications,
        "verification_failures": args.failures,
        "retries": args.retries,
        "human_interventions": args.interventions,
        "token_count": args.tokens,
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"cost recorded: {args.task} duration_ms={duration_ms} exit={proc.returncode}")
    return proc.returncode


def cmd_report(args) -> int:
    budget = json.loads(Path(args.budget).read_text(encoding="utf-8")) if Path(args.budget).exists() else {}
    records = []
    if LEDGER.exists():
        records = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").strip().splitlines() if line.strip()]
    total_duration = sum(r["duration_ms"] for r in records)
    total_verifications = sum(r["verifications"] for r in records)
    print(f"records={len(records)} total_duration_ms={total_duration} total_verifications={total_verifications}")
    alerted = False
    if "max_total_duration_ms" in budget and total_duration > budget["max_total_duration_ms"]:
        print(f"ALERT: total duration {total_duration}ms exceeds budget {budget['max_total_duration_ms']}ms (alert only, no stop)")
        alerted = True
    if "max_verifications" in budget and total_verifications > budget["max_verifications"]:
        print(f"ALERT: total verifications {total_verifications} exceeds budget {budget['max_verifications']} (alert only, no stop)")
        alerted = True
    if not alerted:
        print("no budget alert")
    return 0  # alert-only: never blocks


def cmd_check(args) -> int:
    budget = json.loads(Path(args.budget).read_text(encoding="utf-8")) if Path(args.budget).exists() else {}
    if not budget.get("hard_stop_enabled"):
        print("hard stop OFF (alert only): new verification run may start")
        return 0
    ledger_path = Path(args.ledger)
    records = []
    if ledger_path.exists():
        records = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().splitlines() if line.strip()]
    today = args.day or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    task_recs = [r for r in records if r.get("task") == args.task and r.get("event") != "budget_stop"]
    day_recs = [r for r in records if r.get("date") == today and r.get("event") != "budget_stop"]
    task_v = sum(r.get("verifications", 0) for r in task_recs)
    task_s = sum(r.get("duration_ms", 0) for r in task_recs) / 1000
    task_r = sum(r.get("retries", 0) for r in task_recs)
    day_v = sum(r.get("verifications", 0) for r in day_recs)
    day_s = sum(r.get("duration_ms", 0) for r in day_recs) / 1000
    task_cap = budget.get("hard_stop_task", {})
    day_cap = budget.get("hard_stop_day", {})
    breach = None
    if task_v >= task_cap.get("max_verifications", 10):
        breach = f"task {args.task} verifications {task_v} >= ceiling {task_cap.get('max_verifications', 10)}"
    elif task_s >= task_cap.get("max_duration_s", 3600):
        breach = f"task {args.task} duration {task_s:.0f}s >= ceiling {task_cap.get('max_duration_s', 3600)}s"
    elif task_r >= task_cap.get("max_retries", 5):
        breach = f"task {args.task} retries {task_r} >= ceiling {task_cap.get('max_retries', 5)}"
    elif day_v >= day_cap.get("max_verifications", 100):
        breach = f"day {today} verifications {day_v} >= ceiling {day_cap.get('max_verifications', 100)}"
    elif day_s >= day_cap.get("max_duration_s", 28800):
        breach = f"day {today} duration {day_s:.0f}s >= ceiling {day_cap.get('max_duration_s', 28800)}s"
    if breach is None:
        print(f"BUDGET OK: task {args.task} verifications={task_v} duration_s={task_s:.0f} retries={task_r}; day verifications={day_v} duration_s={day_s:.0f}")
        return 0
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "budget_stop", "task": args.task, "date": today, "reason": breach}, ensure_ascii=False) + "\n")
    print("问题：预算已耗尽，新的验证轮次不得开始。")
    print(f"原因：{breach}。")
    print("修法：不要再开新验证；把任务记为 blocked（不是 passing，也不是 failed）；等人工在 DECISIONS.md 里调高预算，或等新的一天开始后再恢复。")
    print(f"BUDGET STOP: {breach}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="minimal cost ledger (hard stop since D23)")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("record")
    p.add_argument("--task", required=True)
    p.add_argument("--verifications", type=int, default=0)
    p.add_argument("--failures", type=int, default=0)
    p.add_argument("--retries", type=int, default=0)
    p.add_argument("--interventions", type=int, default=0)
    p.add_argument("--tokens", type=int, default=None)
    p.add_argument("host_command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_record)
    p = sub.add_parser("report")
    p.add_argument("--budget", default=str(BUDGET))
    p.set_defaults(func=cmd_report)
    p = sub.add_parser("check")
    p.add_argument("--task", required=True)
    p.add_argument("--ledger", default=str(LEDGER))
    p.add_argument("--budget", default=str(BUDGET))
    p.add_argument("--day", default=None)
    p.set_defaults(func=cmd_check)
    args = parser.parse_args()
    if getattr(args, "host_command", None) and args.host_command and args.host_command[0] == "--":
        args.host_command = args.host_command[1:]
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
