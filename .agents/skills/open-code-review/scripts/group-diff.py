#!/usr/bin/env python3
"""group-diff.py — deterministic diff file grouping for open-code-review Tier B.

Groups changed files into review bundles (implementation+test, i18n pairs,
same-feature clusters) without any LLM calls.

Usage:
    python3 group-diff.py [--root DIR] [--changed-files F ...] [--since COMMIT] [--json]

Exit codes: 0 always (advisory tool, never blocks).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

NOISE_PATTERNS = (
    r"(^|/)package-lock\.json$", r"(^|/)yarn\.lock$", r"(^|/)pnpm-lock\.yaml$",
    r"(^|/)poetry\.lock$", r"(^|/)Cargo\.lock$", r"(^|/)go\.sum$",
    r"(^|/)(dist|build|out)/", r"\.min\.js$", r"\.bundle\.js$",
    r"\.(png|jpe?g|gif|ico|woff2?|ttf|pdf|zip|tar\.gz)$",
    r"(^|/)(vendor|node_modules)/", r"\.pb\.go$", r"_generated\.py$",
)


def _sh(cmd: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:
        return ""


def resolve_root(explicit: str | None) -> Path:
    if explicit and Path(explicit).is_dir():
        return Path(explicit).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True,
                             timeout=5).stdout.strip()
        if out and Path(out).is_dir():
            return Path(out).resolve()
    except Exception:
        pass
    return Path.cwd().resolve()


def changed_files(root: Path, since: str | None,
                  explicit: list[str] | None) -> list[str]:
    if explicit:
        return sorted({f.strip().lstrip("./") for f in explicit if f.strip()})
    if since:
        out = _sh(["git", "diff", "--name-only", f"{since}..HEAD"], root)
    else:
        out = _sh(["git", "diff", "--name-only", "HEAD"], root)
        staged = _sh(["git", "diff", "--name-only", "--cached"], root)
        untracked = _sh(["git", "ls-files", "--others", "--exclude-standard"], root)
        out = out + "\n" + staged + "\n" + untracked
    return sorted({l.strip().lstrip("./") for l in out.splitlines() if l.strip()})


def is_noise(path: str) -> str | None:
    for pat in NOISE_PATTERNS:
        if re.search(pat, path):
            return pat
    return None


def test_partner(path: str, files: set[str]) -> str | None:
    """Find the implementation<->test partner for a path."""
    p = Path(path)
    stem = p.stem
    parent = p.parent.as_posix()
    candidates = []
    if stem.startswith("test_"):
        base = stem[5:]
        candidates = [f"{parent}/{base}{p.suffix}".lstrip("./"),
                      f"{parent}/src/{base}{p.suffix}".lstrip("./")]
    elif stem.endswith("_test") or stem.endswith(".test") or stem.endswith(".spec"):
        base = re.sub(r"(_test|\.test|\.spec)$", "", stem)
        candidates = [f"{parent}/{base}{p.suffix}".lstrip("./")]
    else:
        candidates = [f"{parent}/test_{stem}{p.suffix}".lstrip("./"),
                      f"{parent}/{stem}_test{p.suffix}".lstrip("./"),
                      f"{parent}/{stem}.test{p.suffix}".lstrip("./"),
                      f"{parent}/{stem}.spec{p.suffix}".lstrip("./")]
    for c in candidates:
        if c in files and c != path:
            return c
    return None


def i18n_key(path: str) -> str | None:
    m = re.match(r"^(.*)_(en|zh|ja|ko|ru|es|fr|de)(\.[^.]+)$", path)
    return f"{m.group(1)}{m.group(3)}" if m else None


def group(files: list[str]) -> dict:
    reviewable, excluded = [], []
    for f in files:
        pat = is_noise(f)
        if pat:
            excluded.append({"path": f, "reason": f"noise pattern: {pat}"})
        else:
            reviewable.append(f)

    file_set = set(reviewable)
    assigned: set[str] = set()
    bundles: list[dict] = []

    # Pass 1: test <-> implementation pairs
    for f in reviewable:
        if f in assigned:
            continue
        partner = test_partner(f, file_set)
        if partner and partner not in assigned:
            bundles.append({"bundle": "test-pair", "files": sorted([f, partner])})
            assigned.update([f, partner])

    # Pass 2: i18n groups
    i18n: dict[str, list[str]] = {}
    for f in reviewable:
        if f in assigned:
            continue
        key = i18n_key(f)
        if key:
            i18n.setdefault(key, []).append(f)
    for key, group_files in i18n.items():
        if len(group_files) > 1:
            bundles.append({"bundle": "i18n", "files": sorted(group_files)})
            assigned.update(group_files)

    # Pass 3: same-directory clusters (same feature area)
    by_dir: dict[str, list[str]] = {}
    for f in reviewable:
        if f not in assigned:
            by_dir.setdefault(str(Path(f).parent), []).append(f)
    for d, group_files in sorted(by_dir.items()):
        if len(group_files) > 1:
            bundles.append({"bundle": f"dir:{d}", "files": sorted(group_files)})
            assigned.update(group_files)

    # Pass 4: singletons
    for f in reviewable:
        if f not in assigned:
            bundles.append({"bundle": "single", "files": [f]})

    return {"reviewable": reviewable, "excluded": excluded, "bundles": bundles,
            "coverage": {"total": len(reviewable), "bundled": len(assigned)}}


def main() -> int:
    ap = argparse.ArgumentParser(description="group changed files into review bundles")
    ap.add_argument("--root", default=None)
    ap.add_argument("--changed-files", nargs="*", default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = resolve_root(args.root)
    files = changed_files(root, args.since, args.changed_files)
    report = group(files)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Reviewable: {len(report['reviewable'])}  "
              f"Excluded: {len(report['excluded'])}  "
              f"Bundles: {len(report['bundles'])}")
        for b in report["bundles"]:
            print(f"\n[{b['bundle']}]")
            for f in b["files"]:
                print(f"  - {f}")
        if report["excluded"]:
            print("\nExcluded:")
            for e in report["excluded"]:
                print(f"  - {e['path']} ({e['reason']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
