#!/usr/bin/env python3
"""Skill-usage report (D68): aggregate Skill-invocation telemetry.

The PostToolUse hook (.claude/hooks/post-tool-use.mjs) appends one
line per Skill invocation to .claude/skill-usage.jsonl — {ts, skill,
session?}, the skill NAME only, never arguments or content. This
tool turns that raw log into the input the monthly ablation (D20)
has always lacked: which deployed skills are actually loaded, and
which have zero recorded loads.

Deployed skills are read from the skills directories on disk
(default: <root>/.agents/skills and <root>/.claude/skills — a skill
counts as deployed when a directory bearing its name contains a
SKILL.md; symlinks are followed).

Usage:
  skill-usage-report.py [--root DIR] [--usage-file PATH]
                        [--skills-dir DIR ...] [--json]

Exit codes: 0 ok, 2 usage file missing/unreadable (no telemetry
recorded yet is reported, not silently treated as all-zero).
Stdlib only.
"""

import argparse
import json
import sys
from pathlib import Path

USAGE_NAME = Path(".claude") / "skill-usage.jsonl"


def deployed_skills(skills_dirs):
    """Names of deployed skills: subdirectories containing SKILL.md."""
    names = set()
    for base in skills_dirs:
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.is_dir() and (child / "SKILL.md").is_file():
                names.add(child.name)
    return sorted(names)


def load_counts(usage_file):
    """Return (counts, total, skipped) from a skill-usage.jsonl file.

    Malformed lines and lines without a string `skill` are skipped
    and counted, never fatal — the hook is fail-open, so the log's
    reader must be at least as tolerant.
    """
    counts = {}
    total = 0
    skipped = 0
    with usage_file.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            skill = rec.get("skill") if isinstance(rec, dict) else None
            if not isinstance(skill, str) or not skill:
                skipped += 1
                continue
            counts[skill] = counts.get(skill, 0) + 1
            total += 1
    return counts, total, skipped


def build_report(root, usage_file, skills_dirs):
    deployed = deployed_skills(skills_dirs)
    counts, total, skipped = load_counts(usage_file)
    zero = [name for name in deployed if counts.get(name, 0) == 0]
    return {
        "usage_file": str(usage_file),
        "total_loads": total,
        "skipped_lines": skipped,
        "counts": dict(sorted(counts.items(),
                              key=lambda kv: (-kv[1], kv[0]))),
        "deployed_skills": deployed,
        "zero_loads": zero,
        "undeployed_loads": sorted(
            name for name in counts if name not in deployed),
    }


def print_text(report):
    print(f"Skill usage — {report['usage_file']}")
    print(f"Total recorded loads: {report['total_loads']}"
          + (f" ({report['skipped_lines']} malformed line(s) skipped)"
             if report["skipped_lines"] else ""))
    print()
    if report["counts"]:
        width = max(len(name) for name in report["counts"])
        for name, n in report["counts"].items():
            print(f"  {name:<{width}}  {n}")
    else:
        print("  (no loads recorded)")
    print()
    print(f"Deployed skills with zero recorded loads "
          f"({len(report['zero_loads'])} of "
          f"{len(report['deployed_skills'])} deployed):")
    for name in report["zero_loads"]:
        print(f"  {name}")
    if report["undeployed_loads"]:
        print()
        print("Recorded loads for skills not deployed here "
              "(renamed/removed since?):")
        for name in report["undeployed_loads"]:
            print(f"  {name}  {report['counts'][name]}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="aggregate .claude/skill-usage.jsonl into "
                    "per-skill load counts + zero-load deployed skills")
    parser.add_argument("--root", default=".",
                        help="project root (default: current directory)")
    parser.add_argument("--usage-file", default=None,
                        help="usage log (default: <root>/.claude/"
                             "skill-usage.jsonl)")
    parser.add_argument("--skills-dir", action="append", default=None,
                        help="deployed-skills directory (repeatable; "
                             "default: <root>/.agents/skills and "
                             "<root>/.claude/skills)")
    parser.add_argument("--json", action="store_true",
                        help="print the report as JSON")
    args = parser.parse_args(argv)
    root = Path(args.root)
    usage_file = Path(args.usage_file) if args.usage_file \
        else root / USAGE_NAME
    if not usage_file.is_file():
        print(f"error: no skill-usage log at {usage_file} — no Skill "
              "invocations have been recorded yet (the PostToolUse "
              "hook writes it on the first Skill call in a gated "
              "project; SKILL_LEDGER=0 disables it)", file=sys.stderr)
        return 2
    skills_dirs = [Path(d) for d in args.skills_dir] if args.skills_dir \
        else [root / ".agents" / "skills", root / ".claude" / "skills"]
    report = build_report(root, usage_file, skills_dirs)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
