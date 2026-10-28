#!/usr/bin/env python3
"""check-release.py — release consistency gate (Phase 6, 6-3).

Verifies the three release records agree before a version is cut:
  1. VERSION is semver and equals the newest ## [x.y.z] heading in
     CHANGELOG.md (mirrors tests/repo_checks.py §3c, as a standalone tool
     a maintainer can run before tagging).
  2. Every released ## [x.y.z] heading carries a "- YYYY-MM-DD" date.
  3. skills-lock.json is release-ready: every non-meta github entry has a
     pinnedCommit + computedHash, every local entry has a version +
     computedHash, every meta entry has a pinnedCommit + note (D10).
     A release must never ship an unpinned or unhashed skill.
  4. Deprecation policy (Phase 6, 6-3): any bullet under "### Deprecated"
     or marked **Breaking** in CHANGELOG [Unreleased] must carry a
     "Migration:" pointer, and the old behaviour/template must stay
     available for one version cycle (checked by convention — the tool
     enforces the note; the retention is a review duty, see
     CONTRIBUTING.md "Deprecation policy").

Stdlib only. Exit 0 = all checks pass, 1 = at least one failed.
Usage: python3 tools/check-release.py [--root PATH]
"""
import argparse
import json
import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\](?:\s+-\s+(\d{4}-\d{2}-\d{2}))?\s*$", re.MULTILINE)


def main() -> int:
    ap = argparse.ArgumentParser(description="Release consistency gate (VERSION/CHANGELOG/skills-lock).")
    ap.add_argument("--root", default=".", help="Repository root (default: .)")
    args = ap.parse_args()
    root = Path(args.root)
    failures = []

    def fail(msg):
        failures.append(msg)
        print(f"[FAIL] {msg}")

    # 1. VERSION is semver and matches the newest CHANGELOG heading.
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.match(version):
        fail(f"VERSION {version!r} is not semver x.y.z")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    headings = VERSION_HEADING.findall(changelog)
    if not headings:
        fail("CHANGELOG.md has no ## [x.y.z] heading")
    elif version != headings[0][0]:
        fail(f"VERSION={version!r} != CHANGELOG newest={headings[0][0]!r}")

    # 2. Every released heading carries a date.
    for ver, date in headings:
        if not date or not DATE.match(date):
            fail(f"CHANGELOG ## [{ver}] lacks a '- YYYY-MM-DD' date")

    # 3. skills-lock.json is release-ready.
    lock = json.loads((root / "skills-lock.json").read_text(encoding="utf-8-sig"))
    if not isinstance(lock.get("version"), int):
        fail(f"skills-lock.json top-level 'version' (format version) is not an int: {lock.get('version')!r}")
    for name, meta in sorted(lock.get("skills", {}).items()):
        if meta.get("meta") is True:
            if not meta.get("pinnedCommit") or not (meta.get("note") or "").strip():
                fail(f"meta entry {name} lacks pinnedCommit and/or note")
            continue
        if meta.get("sourceType") == "github":
            if not meta.get("pinnedCommit") or not meta.get("computedHash"):
                fail(f"github skill {name} lacks pinnedCommit and/or computedHash")
        elif meta.get("sourceType") == "local":
            if not meta.get("version") or not meta.get("computedHash"):
                fail(f"local skill {name} lacks version and/or computedHash")
        else:
            fail(f"skill {name} has unknown sourceType {meta.get('sourceType')!r}")

    # 4. Deprecation policy: breaking/deprecated entries need a Migration note.
    unreleased = changelog.split("## [Unreleased]", 1)[1] if "## [Unreleased]" in changelog else ""
    # Only up to the next ## [x.y.z] heading.
    unreleased = re.split(r"^## \[\d+\.\d+\.\d+\]", unreleased, flags=re.MULTILINE)[0]
    in_deprecated = False
    for line in unreleased.splitlines():
        if line.startswith("### "):
            in_deprecated = line.strip().lower() == "### deprecated"
            continue
        if line.startswith("- ") and (in_deprecated or "**breaking**" in line.lower()):
            if "migration:" not in line.lower():
                fail(f"breaking/deprecated entry lacks a 'Migration:' note: {line.strip()[:100]}")

    if failures:
        print(f"check-release: {len(failures)} failure(s)")
        return 1
    print("check-release: OK "
          f"(VERSION {version}, CHANGELOG newest {headings[0][0]}, "
          f"lock {len(lock.get('skills', {}))} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
