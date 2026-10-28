#!/usr/bin/env python3
"""tools/count-skills.py — single source of truth for skill counts (Phase 0, 0-1).

The skill-count numbers in README / AGENTS.md / SESSION_STATE.md /
PROJECT_CONTEXT.md drifted apart (44 vs 43 vs 42 vs 40 on disk) because
every document quoted the count from memory. From Phase 0 on, the count
is computed here from `.agents/skills/` + `skills-lock.json`, and the
expected composition is declared explicitly below. Adding or removing a
skill means updating EXPECTED here first, then the documents.

Usage:
  python3 tools/count-skills.py            # print counts
  python3 tools/count-skills.py --json     # print counts as JSON
  python3 tools/count-skills.py --check    # exit 1 on any mismatch

--check verifies:
  1. Disk composition matches EXPECTED (total dirs, per-source dirs).
  2. skills-lock.json has 42 entries: the 40 dirs + exactly the 2 known
     source-repo meta entries (openspec, superpowers).
  3. No live doc states a stale skill count (42/43/44 in a skill context)
     or an openspec suite size other than 12. CHANGELOG.md and the dated
     docs/internal/SESSION_RESUME*.md snapshots are history, not live
     claims, and are excluded from check 3 on purpose.

CI enforcement lives in tests/repo_checks.py section 3i, which runs this
script with --check. This script is the human-facing reporter.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Expected composition. Update deliberately when skills are added/removed.
# Values are counts of skill *directories on disk*, keyed by lock `source`.
EXPECTED_DIRS = {
    "obra/superpowers": 15,
    "Fission-AI/OpenSpec": 12,
    "./agent-harness (authored in-repo)": 6,
    "anthropics/skills": 2,
    "other": 5,  # caveman, codegraph, comet, ponytail, rtk (one dir each)
}
EXPECTED_TOTAL_DIRS = 40
EXPECTED_LOCK_ENTRIES = 42
META_ENTRIES = {"openspec", "superpowers"}

# Live docs whose skill-count claims must agree with disk. History files
# (CHANGELOG.md, docs/internal/SESSION_RESUME*.md) are excluded on purpose.
LIVE_DOCS = [
    "README.md",
    "README.zh.md",
    "README.zh-tw.md",
    "README.fr.md",
    "README.de.md",
    "AGENTS.md",
    "docs/glossary.md",
    "CONTRIBUTING.md",
    "docs/internal/SESSION_STATE.md",
    "docs/internal/PROJECT_CONTEXT.md",
] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "guides").glob("*.md"))

STALE_COUNT_RE = re.compile(r"\b(42|43|44)\b")
OPENSPEC_LINE_RE = re.compile(r"openspec", re.IGNORECASE)
OPENSPEC_STALE_RE = re.compile(r"\b16\b")


def compute_counts():
    lock_data = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8-sig"))
    lock_skills = lock_data["skills"]
    dir_skills = {p.name for p in (ROOT / ".agents" / "skills").iterdir() if p.is_dir()}
    by_source = Counter()
    for name in dir_skills:
        src = lock_skills.get(name, {}).get("source", "<no-lock-entry>")
        if src in EXPECTED_DIRS:
            by_source[src] += 1
        else:
            by_source["other"] += 1
    return {
        "total_dirs": len(dir_skills),
        "by_source": {k: by_source.get(k, 0) for k in EXPECTED_DIRS},
        "lock_entries": len(lock_skills),
        "lock_meta_entries": sorted(set(lock_skills) & META_ENTRIES),
        "dirs_without_lock": sorted(dir_skills - set(lock_skills)),
        "lock_without_dir": sorted(set(lock_skills) - dir_skills - META_ENTRIES),
    }


def scan_live_docs():
    """Return a list of stale-claim findings in live docs."""
    findings = []
    for rel in LIVE_DOCS:
        p = ROOT / rel
        if not p.is_file():
            continue
        for lineno, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1):
            # Lines stating the lock's own entry count (42 by design: 40 dirs
            # + 2 meta entries) are correct, not stale — skip them.
            if "skills-lock.json" in line:
                continue
            if "skill" in line.lower() or "技能" in line:
                for m in STALE_COUNT_RE.finditer(line):
                    findings.append(f"{rel}:{lineno}: stale skill count {m.group(1)}: {line.strip()[:100]}")
            if OPENSPEC_LINE_RE.search(line) and OPENSPEC_STALE_RE.search(line):
                findings.append(f"{rel}:{lineno}: openspec suite != 12: {line.strip()[:100]}")
    return findings


def check():
    counts = compute_counts()
    problems = []
    for src, expected in EXPECTED_DIRS.items():
        actual = counts["by_source"][src]
        if actual != expected:
            problems.append(f"source {src}: expected {expected} dirs, got {actual}")
    if counts["total_dirs"] != EXPECTED_TOTAL_DIRS:
        problems.append(f"total dirs: expected {EXPECTED_TOTAL_DIRS}, got {counts['total_dirs']}")
    if counts["lock_entries"] != EXPECTED_LOCK_ENTRIES:
        problems.append(f"lock entries: expected {EXPECTED_LOCK_ENTRIES}, got {counts['lock_entries']}")
    if counts["dirs_without_lock"]:
        problems.append(f"dirs without lock entry: {counts['dirs_without_lock']}")
    if counts["lock_without_dir"]:
        problems.append(f"lock entries without dir: {counts['lock_without_dir']}")
    problems.extend(scan_live_docs())
    return counts, problems


def main(argv=None):
    ap = argparse.ArgumentParser(description="Report / verify agent-harness skill counts.")
    ap.add_argument("--json", action="store_true", help="print counts as JSON")
    ap.add_argument("--check", action="store_true", help="exit 1 on any mismatch")
    args = ap.parse_args(argv)
    counts, problems = check()
    if args.json:
        print(json.dumps(counts, indent=2, sort_keys=True))
    else:
        print(f"skill dirs on disk: {counts['total_dirs']} (expected {EXPECTED_TOTAL_DIRS})")
        for src in EXPECTED_DIRS:
            print(f"  {src}: {counts['by_source'][src]} (expected {EXPECTED_DIRS[src]})")
        print(f"lock entries: {counts['lock_entries']} (expected {EXPECTED_LOCK_ENTRIES}, "
              f"meta: {', '.join(counts['lock_meta_entries'])})")
    if args.check:
        if problems:
            print("MISMATCH:")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("counts OK: docs agree with disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
