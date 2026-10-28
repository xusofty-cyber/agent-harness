#!/usr/bin/env python3
"""evaluate.py — rubric scorecard validator and stable-gate (merged from v3-yunyi).

Usage:
    python3 eval/evaluate.py check <scorecard.json>
        Validate a scorecard: six dimensions, each 0–2, each with a
        non-empty evidence citation; verdict must match the computed
        verdict. Exit 0 = valid, 1 = invalid.
    python3 eval/evaluate.py --gate <scorecard.json>
        Auto-approval gate. While eval/rubric-status.json is not
        "stable", this ALWAYS refuses (exit 2) — there is no auto-approve
        path before calibration is complete. When stable, it approves
        only Accept verdicts.
    python3 eval/evaluate.py status
        Print the current rubric status.

A scorecard is JSON: {"task": "...", "verdict": "Accept|Revise|Block",
"scores": {"correctness": {"score": 2, "evidence": "..."}, ...}} with
exactly the six dimension keys: correctness, verification,
scope_discipline, reliability, maintainability, handoff_readiness.

Verdict rule (eval/rubric.md, NOT yunyi's all-2 rule):
    Block  — any dimension scores 0.
    Revise — no 0, but total < 9.
    Accept — total >= 9 and no dimension scores 0.
The yunyi original computed Accept as all-2 (12/12); that threshold is
deliberately NOT adopted — see DECISIONS.md D28 (merge ruling C3).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIMS = ("correctness", "verification", "scope_discipline",
        "reliability", "maintainability", "handoff_readiness")


def computed_verdict(scores: dict) -> str:
    values = [scores[d]["score"] for d in DIMS]
    if any(v == 0 for v in values):
        return "Block"
    if sum(values) >= 9:
        return "Accept"
    return "Revise"


def validate(card: dict) -> list[str]:
    problems: list[str] = []
    scores = card.get("scores", {})
    if set(scores) != set(DIMS):
        problems.append(f"scores must contain exactly {DIMS}, got {sorted(scores)}")
        return problems
    for dim in DIMS:
        entry = scores[dim]
        if entry.get("score") not in (0, 1, 2):
            problems.append(f"{dim}: score must be 0, 1 or 2")
        if not entry.get("evidence", "").strip():
            problems.append(f"{dim}: evidence citation required (score without evidence is 0)")
        elif entry.get("score") == 0 and entry.get("evidence", "").strip():
            pass  # 0 with an explanation of the failure is allowed
    if card.get("verdict") != computed_verdict(scores):
        problems.append(f"verdict {card.get('verdict')!r} does not match computed "
                        f"{computed_verdict(scores)!r} (verdict is computed, not chosen)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="rubric scorecard validator and gate")
    parser.add_argument("action", nargs="?", default="status", help="check | status (or a scorecard path when --gate is used first)")
    parser.add_argument("scorecard", nargs="?", help="scorecard JSON file")
    parser.add_argument("--gate", action="store_true", help="auto-approval gate (refuses unless stable)")
    args = parser.parse_args()
    if args.action and args.action.endswith(".json") and not args.scorecard:
        args.scorecard, args.action = args.action, "check"
    status_path = ROOT / "eval" / "rubric-status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    if args.action == "status":
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return 0
    if not args.scorecard:
        print("scorecard file required for check", file=sys.stderr)
        return 2
    card = json.loads(Path(args.scorecard).read_text(encoding="utf-8"))
    problems = validate(card)
    if problems:
        for problem in problems:
            print(f"INVALID: {problem}", file=sys.stderr)
        return 1
    print(f"scorecard valid: {card.get('task')} -> {card['verdict']} "
          f"(total {sum(card['scores'][d]['score'] for d in DIMS)}/12)")
    if args.gate:
        if status.get("status") != "stable" or not status.get("auto_approve_allowed"):
            print("GATE REFUSED: rubric status is not stable; auto-approval is not "
                  "available before calibration completes (v3 2.2).", file=sys.stderr)
            return 2
        if card["verdict"] != "Accept":
            print(f"GATE REFUSED: verdict is {card['verdict']}, only Accept auto-approves.", file=sys.stderr)
            return 1
        print("GATE APPROVED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
