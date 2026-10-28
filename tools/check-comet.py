#!/usr/bin/env python3
"""check-comet.py — verify the pinned Comet CLI supply chain (Phase 2, 2-2).

Checks, stdlib only:
  1. skills-lock.json comet entry carries a pinned npm version + git commit.
     The pin was measured at implementation time with
     `npm view @rpamis/comet version` (see pinnedFrom / pinnedAt in the lock);
     the git commit is the tag for that version
     (`git ls-remote --tags https://github.com/rpamis/comet.git`).
  2. the installed `comet --version` (if comet is installed) reports exactly
     the pinned npm version. Comet not installed -> SKIP, not FAIL
     (comet is an optional adapter, D1).
  3. templates/comet.config.yaml declares `schema: comet.project.v1`,
     the schema this repo's templates target.

Exit codes: 0 = all checks pass (or comet absent); 1 = pin missing or
version/schema mismatch. 2 = lock/template file unreadable.

Usage:
    python3 tools/check-comet.py [--root DIR] [--json]
    --root DIR: repo root (default: parent of tools/)
    --json: machine-readable output.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "comet.project.v1"
SEMVER_RE = re.compile(r"(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)")


def load_pin(root: Path) -> dict:
    lock_path = root / "skills-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    return lock.get("skills", {}).get("comet", {})


def installed_version() -> str | None:
    exe = shutil.which("comet")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "--version"], capture_output=True,
                             text=True, timeout=30).stdout.strip()
    except Exception:
        return None
    m = SEMVER_RE.search(out)
    return m.group(1) if m else None


def template_schema(root: Path) -> str | None:
    tpl = root / "templates" / "comet.config.yaml"
    text = tpl.read_text(encoding="utf-8")
    m = re.search(r"^schema:\s*(\S+)\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def check(root: Path) -> dict:
    results: dict = {"checks": {}}
    try:
        pin = load_pin(root)
    except Exception as exc:  # noqa: BLE001 - report, don't crash
        results["error"] = f"cannot read skills-lock.json: {exc}"
        results["ok"] = False
        return results
    pinned_version = pin.get("npmVersion", "")
    pinned_commit = pin.get("pinnedCommit", "")
    results["checks"]["pin-present"] = bool(pinned_version) and bool(pinned_commit)
    results["pinned"] = {"npmVersion": pinned_version,
                         "pinnedCommit": pinned_commit,
                         "pinnedAt": pin.get("pinnedAt", ""),
                         "pinnedFrom": pin.get("pinnedFrom", "")}
    ver = installed_version()
    if ver is None:
        results["checks"]["installed-version"] = None  # SKIP: comet optional
        results["installed"] = None
    else:
        results["installed"] = ver
        results["checks"]["installed-version"] = (ver == pinned_version)
    try:
        schema = template_schema(root)
    except Exception as exc:  # noqa: BLE001
        results["error"] = f"cannot read templates/comet.config.yaml: {exc}"
        results["ok"] = False
        return results
    results["template_schema"] = schema
    results["checks"]["template-schema"] = (schema == SCHEMA)
    results["ok"] = all(v is not False for v in results["checks"].values())
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="verify the pinned Comet CLI supply chain")
    ap.add_argument("--root", default=None, help="repo root (default: parent of tools/)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else ROOT
    res = check(root)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        pin = res.get("pinned", {})
        print(f"pinned: @rpamis/comet@{pin.get('npmVersion') or '?'} "
              f"(commit {pin.get('pinnedCommit', '?')[:12]}, {pin.get('pinnedAt', '?')})")
        for name, ok in res.get("checks", {}).items():
            mark = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
            print(f"  [{mark}] {name}")
        if res.get("installed") is not None:
            print(f"installed comet: {res['installed']}")
        else:
            print("installed comet: not installed (optional, skipped)")
        print(f"template schema: {res.get('template_schema')}")
        if res.get("error"):
            print(f"error: {res['error']}", file=sys.stderr)
    if res.get("error"):
        return 2
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
