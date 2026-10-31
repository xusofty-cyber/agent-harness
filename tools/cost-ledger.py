#!/usr/bin/env python3
"""Cost ledger (Phase 2, 2-5): deterministic proxy metrics for gate runs.

A unified TOKEN ledger is deliberately NOT built here: no host exposes a
programmatic per-session token API (see docs/internal/token-adapters.md),
so any token number would be invented. Instead the ledger records what is
actually measurable today:

  - tool calls (one line per call, written by the PostToolUse hook
    .claude/hooks/post-tool-use.mjs into gate/cost-ledger.jsonl),
  - pipeline stage runs (one line per stage, written by run-pipeline.sh/.ps1,
    only when the target project has a gate/ directory),
  - verify failures + human overrides (read from gate/events.jsonl,
    which pass-gate.py / stop-gate.mjs already maintain).

Ledger file: <gate-dir>/cost-ledger.jsonl (one JSON object per line).
Budget file: <gate-dir>/cost-budget.json (created by `init-budget`).

Subcommands:
  init-budget    create cost-budget.json with defaults (never overwrites)
  record         append one ledger line (kinds: stage, run, tool_call)
  summary        aggregate ledger + events.jsonl (human text, or --json)
  check-budget   exit 0 within budget; exit 1 over budget (stderr alert +
                 one budget_exceeded event in gate/events.jsonl, deduped
                 per day). NEVER auto-stops a run — budget semantics for
                 auto-stop are not defined yet (v3 Phase 2, graded).

Exit codes: 0 ok (check-budget: within budget), 1 over budget / bad usage,
2 unreadable ledger, budget or events file.
Stdlib only.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default budget: per-day caps on measurable proxy metrics, plus a per-stage
# duration cap. No token limits — there is no programmatic token source.
DEFAULT_BUDGET = {
    "version": 1,
    "max_runs_per_day": 20,
    "max_tool_calls_per_day": 2000,
    "max_verify_failures_per_day": 10,
    "max_overrides_per_day": 5,
    "max_stage_duration_ms": 600000,
    "note": (
        "Proxy-metric budget (Phase 2, 2-5). Over-budget only alerts and "
        "records a budget_exceeded event — it never auto-stops a run. "
        "No token limits: no host exposes a programmatic token API yet "
        "(see docs/internal/token-adapters.md)."
    ),
}

LEDGER_NAME = "cost-ledger.jsonl"
BUDGET_NAME = "cost-budget.json"
EVENTS_NAME = "events.jsonl"


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _read_lines(path):
    """Yield parsed JSON objects from a .jsonl file (missing file -> empty)."""
    if not path.exists():
        return
    try:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable {path}: {exc}") from exc


def _append_line(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _load_budget(gate_dir):
    path = gate_dir / BUDGET_NAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable budget {path}: {exc}") from exc


def _aggregate(gate_dir):
    """Aggregate today's ledger + events into one dict of proxy metrics."""
    today = _today()
    agg = {
        "date": today,
        "tool_calls_today": 0,
        "runs_today": 0,
        "stages_today": 0,
        "stage_failures_today": 0,
        "stage_warns_today": 0,
        "verify_failures_today": 0,
        "overrides_today": 0,
        "max_stage_duration_ms_today": 0,
        "verify_failures_total": 0,
        "overrides_total": 0,
    }
    run_ids = set()
    for rec in _read_lines(gate_dir / LEDGER_NAME):
        ts = str(rec.get("ts", ""))
        if not ts.startswith(today):
            continue
        kind = rec.get("kind") or ("tool_call" if rec.get("hook") == "post-tool-use" else None)
        if kind == "tool_call":
            agg["tool_calls_today"] += 1
        elif kind == "stage":
            agg["stages_today"] += 1
            if rec.get("run_id"):
                run_ids.add(rec["run_id"])
            if rec.get("status") == "fail":
                agg["stage_failures_today"] += 1
            elif rec.get("status") == "warn":
                agg["stage_warns_today"] += 1
            dur = rec.get("duration_ms") or 0
            if isinstance(dur, (int, float)) and dur > agg["max_stage_duration_ms_today"]:
                agg["max_stage_duration_ms_today"] = dur
        elif kind == "run":
            if rec.get("run_id"):
                run_ids.add(rec["run_id"])
    agg["runs_today"] = len(run_ids)
    for ev in _read_lines(gate_dir / EVENTS_NAME):
        name = ev.get("event")
        if name == "verify_failed":
            agg["verify_failures_total"] += 1
            if str(ev.get("ts", "")).startswith(today):
                agg["verify_failures_today"] += 1
        elif name in ("override", "stop_override"):
            agg["overrides_total"] += 1
            if str(ev.get("ts", "")).startswith(today):
                agg["overrides_today"] += 1
    return agg


def cmd_init_budget(args):
    gate_dir = Path(args.gate_dir)
    path = gate_dir / BUDGET_NAME
    if path.exists():
        print(f"budget already exists: {path} (not overwritten)")
        return 0
    gate_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DEFAULT_BUDGET, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"created {path}")
    print(f"  max_runs_per_day={DEFAULT_BUDGET['max_runs_per_day']}, "
          f"max_tool_calls_per_day={DEFAULT_BUDGET['max_tool_calls_per_day']}, "
          f"max_verify_failures_per_day={DEFAULT_BUDGET['max_verify_failures_per_day']}, "
          f"max_overrides_per_day={DEFAULT_BUDGET['max_overrides_per_day']}, "
          f"max_stage_duration_ms={DEFAULT_BUDGET['max_stage_duration_ms']}")
    return 0


def cmd_record(args):
    gate_dir = Path(args.gate_dir)
    rec = {"ts": _utcnow(), "kind": args.kind}
    if args.run_id:
        rec["run_id"] = args.run_id
    if args.stage:
        rec["stage"] = args.stage
    if args.status:
        rec["status"] = args.status
    if args.duration_ms is not None:
        rec["duration_ms"] = args.duration_ms
    if args.tool:
        rec["tool"] = args.tool
    _append_line(gate_dir / LEDGER_NAME, rec)
    return 0


def cmd_summary(args):
    gate_dir = Path(args.gate_dir)
    try:
        agg = _aggregate(gate_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(agg, indent=2, ensure_ascii=False))
        return 0
    print(f"cost ledger summary — {agg['date']} (gate: {gate_dir})")
    print(f"  runs today:            {agg['runs_today']}")
    print(f"  tool calls today:      {agg['tool_calls_today']}")
    print(f"  stages today:          {agg['stages_today']} "
          f"(fail {agg['stage_failures_today']}, warn {agg['stage_warns_today']})")
    print(f"  max stage duration:    {agg['max_stage_duration_ms_today']} ms")
    print(f"  verify failures:       {agg['verify_failures_today']} today / "
          f"{agg['verify_failures_total']} total")
    print(f"  overrides:             {agg['overrides_today']} today / "
          f"{agg['overrides_total']} total")
    return 0


def cmd_check_budget(args):
    gate_dir = Path(args.gate_dir)
    try:
        budget = _load_budget(gate_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if budget is None:
        print(f"no budget file: {gate_dir / BUDGET_NAME} "
              "(run `cost-ledger.py init-budget` first)", file=sys.stderr)
        return 1
    try:
        agg = _aggregate(gate_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    exceeded = []
    checks = [
        ("max_runs_per_day", agg["runs_today"]),
        ("max_tool_calls_per_day", agg["tool_calls_today"]),
        ("max_verify_failures_per_day", agg["verify_failures_today"]),
        ("max_overrides_per_day", agg["overrides_today"]),
    ]
    for key, actual in checks:
        limit = budget.get(key)
        if isinstance(limit, (int, float)) and actual > limit:
            exceeded.append(f"{key}: {actual} > {limit}")
    limit = budget.get("max_stage_duration_ms")
    if isinstance(limit, (int, float)) and agg["max_stage_duration_ms_today"] > limit:
        exceeded.append(
            f"max_stage_duration_ms: {agg['max_stage_duration_ms_today']} > {limit}")
    if not exceeded:
        print(f"within budget ({agg['date']}): runs {agg['runs_today']}, "
              f"tool calls {agg['tool_calls_today']}, "
              f"verify failures {agg['verify_failures_today']}, "
              f"overrides {agg['overrides_today']}")
        return 0
    detail = "; ".join(exceeded)
    print(f"COST BUDGET EXCEEDED ({agg['date']}): {detail}", file=sys.stderr)
    print("Alert only — the run is NOT auto-stopped "
          "(budget semantics for auto-stop are not defined yet).",
          file=sys.stderr)
    # Record one budget_exceeded event in gate/events.jsonl, deduped per day
    # per limit-set (a repeated check must not spam the evidence log).
    events_path = gate_dir / EVENTS_NAME
    try:
        existing = list(_read_lines(events_path))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    already = any(
        ev.get("event") == "budget_exceeded"
        and str(ev.get("ts", "")).startswith(agg["date"])
        and ev.get("detail") == detail
        for ev in existing
    )
    if not already:
        pg_script = gate_dir / "pass-gate.py"
        if not pg_script.is_file():
            pg_script = Path(__file__).resolve().parent.parent / "gate" / "pass-gate.py"
        if pg_script.is_file() and gate_dir.name == "gate":
            import importlib.util
            spec = importlib.util.spec_from_file_location("pass_gate", pg_script)
            pg_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pg_mod)
            rec = pg_mod._append_event(str(gate_dir.parent),
                                       "budget_exceeded", None, detail,
                                       actor="cost-ledger")
            seq = rec["seq"]
        else:
            seq = max((ev.get("seq", 0) for ev in existing), default=0) + 1
            _append_line(events_path, {
                "seq": seq,
                "ts": _utcnow(),
                "actor": "cost-ledger",
                "event": "budget_exceeded",
                "item_id": None,
                "detail": detail,
            })
        print(f"recorded budget_exceeded event (seq {seq}) in {events_path}")
    else:
        print("budget_exceeded event already recorded today; not duplicated")
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cost ledger: deterministic proxy metrics for gate runs.")
    parser.add_argument("--gate-dir", default="gate",
                        help="gate directory (default: ./gate)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init-budget",
                            help="create cost-budget.json with defaults (never overwrites)")
    p_init.add_argument("--gate-dir", default="gate")
    p_record = sub.add_parser("record", help="append one ledger line")
    p_record.add_argument("--gate-dir", default="gate")
    p_record.add_argument("--kind", required=True,
                          choices=["stage", "run", "tool_call"])
    p_record.add_argument("--run-id")
    p_record.add_argument("--stage")
    p_record.add_argument("--status", choices=["pass", "fail", "warn"])
    p_record.add_argument("--duration-ms", type=int)
    p_record.add_argument("--tool")
    p_summary = sub.add_parser("summary", help="aggregate ledger + events")
    p_summary.add_argument("--gate-dir", default="gate")
    p_summary.add_argument("--json", action="store_true")
    p_check = sub.add_parser("check-budget",
                             help="exit 0 within budget, 1 over budget (alert + event, no auto-stop)")
    p_check.add_argument("--gate-dir", default="gate")
    args = parser.parse_args(argv)
    if args.command == "init-budget":
        return cmd_init_budget(args)
    if args.command == "record":
        return cmd_record(args)
    if args.command == "summary":
        return cmd_summary(args)
    if args.command == "check-budget":
        return cmd_check_budget(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
