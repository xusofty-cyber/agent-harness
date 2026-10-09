#!/usr/bin/env python3
"""doc-impact.py — living-documentation impact analysis.

Scans docs/{specs,architecture,reference,guides,adr}/**/*.md frontmatter,
matches changed files against each document's `modules` globs, walks
`depends_on` upward, and reports staleness via `last_verified_commit`.

Usage:
    python3 doc-impact.py [--root DIR] [--changed-files F ...] [--since COMMIT] [--json]

- Default changed set: `git diff --name-only HEAD` + untracked files.
- --since COMMIT: use `git diff --name-only COMMIT..HEAD` instead.
- --root DIR: root directory of target project (auto-detected by default).
- --json: machine-readable output.

Exit codes: 0 always (advisory tool, never blocks). Parse output for CI gating.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

DOC_TIERS = ("specs", "architecture", "reference", "guides", "adr")


def _sh(cmd: list[str], cwd: Path) -> str:
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:
        return ""


def resolve_root(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).resolve()
        if p.is_dir():
            return p
    # Try finding git toplevel from cwd
    try:
        git_root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True, timeout=5).stdout.strip()
        if git_root and Path(git_root).is_dir():
            return Path(git_root).resolve()
    except Exception:
        pass
    # Fallback to cwd if it contains docs/
    if (Path.cwd() / "docs").is_dir():
        return Path.cwd().resolve()
    # Fallback to repo root containing this script
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir.parent, script_dir.parent.parent.parent.parent]:
        if (candidate / "docs").is_dir() or (candidate / ".git").is_dir():
            return candidate.resolve()
    return Path.cwd().resolve()


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fields: dict = {}
    current_list_key = None
    for line in m.group(1).splitlines():
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and current_list_key:
            fields[current_list_key].append(item.group(1).strip().strip("\"'"))
            continue
        current_list_key = None
        km = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if km:
            key, val = km.group(1), km.group(2).strip()
            if val == "":
                fields[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                fields[key] = [v.strip().strip("\"'")
                               for v in val[1:-1].split(",") if v.strip()]
            else:
                fields[key] = val.strip("\"'")
    return fields


def load_docs(root: Path) -> list[dict]:
    docs = []
    for tier in DOC_TIERS:
        tier_dir = root / "docs" / tier
        if not tier_dir.is_dir():
            continue
        for f in sorted(tier_dir.rglob("*.md")):
            fm = parse_frontmatter(f.read_text(encoding="utf-8-sig"))
            if not fm:
                continue
            rel = f.relative_to(root).as_posix()
            docs.append({
                "path": rel,
                "id": fm.get("id", ""),
                "type": fm.get("type", ""),
                "status": fm.get("status", ""),
                "modules": fm.get("modules") or [],
                "depends_on": fm.get("depends_on") or [],
                "last_verified_commit": fm.get("last_verified_commit", ""),
            })
    return docs


def changed_files(root: Path, since: str | None,
                  explicit: list[str] | None) -> list[str]:
    if explicit:
        return [f.strip().lstrip("./") for f in explicit if f.strip()]
    if since:
        out = _sh(["git", "diff", "--name-only", f"{since}..HEAD"], root)
        return sorted({l.strip().lstrip("./") for l in out.splitlines() if l.strip()})
    else:
        out = _sh(["git", "diff", "--name-only", "HEAD"], root)
        staged = _sh(["git", "diff", "--name-only", "--cached"], root)
        untracked = _sh(["git", "ls-files", "--others", "--exclude-standard"], root)
        files = {l.strip().lstrip("./")
                 for l in (out + "\n" + staged + "\n" + untracked).splitlines() if l.strip()}
        return sorted(files)


def commits_behind(root: Path, commit: str) -> int | None:
    if not commit:
        return None
    if commit == "HEAD":
        return 0
    out = _sh(["git", "rev-list", "--count", f"{commit}..HEAD"], root)
    return int(out) if out.isdigit() else None


def match_glob(file_path: str, pattern: str) -> bool:
    f = file_path.strip().lstrip("./")
    p = pattern.strip().lstrip("./")
    if fnmatch.fnmatch(f, p):
        return True
    p_clean = p.rstrip("/")
    if f == p_clean or f.startswith(f"{p_clean}/"):
        return True
    return False


def analyze(root: Path, files: list[str]) -> dict:
    docs = load_docs(root)
    by_path = {d["path"]: d for d in docs}

    def norm(p: str) -> str:
        p = p.strip().strip("\"'")
        if p.startswith("docs/"):
            return p
        return f"docs/{p.lstrip('/')}"

    direct: dict[str, list[str]] = {}
    for d in docs:
        matched = [f for f in files
                   if any(match_glob(f, g) for g in d["modules"])]
        if matched:
            direct[d["path"]] = matched

    # Walk depends_on upward (dependents of impacted docs are indirectly affected)
    dependents: dict[str, list[str]] = {}
    for d in docs:
        for dep in d["depends_on"]:
            dependents.setdefault(norm(dep), []).append(d["path"])

    indirect: dict[str, int] = {}
    frontier = [(p, 1) for p in direct]
    seen = set(direct)
    while frontier:
        path, depth = frontier.pop(0)
        for dep_path in dependents.get(path, []):
            if dep_path not in seen:
                seen.add(dep_path)
                indirect[dep_path] = depth
                frontier.append((dep_path, depth + 1))

    results = []
    for path in sorted(set(direct) | set(indirect)):
        d = by_path[path]
        behind = commits_behind(root, d["last_verified_commit"])
        if path in direct:
            if behind is not None and behind > 0:
                level = "must-update"
            elif behind == 0:
                level = "in-sync"
            elif not d["last_verified_commit"]:
                level = "must-update"
            else:
                level = "review"
        else:
            level = "review"
        results.append({
            "path": path,
            "id": d["id"],
            "type": d["type"],
            "status": d["status"],
            "impact": "direct" if path in direct else f"indirect(depth={indirect[path]})",
            "matched_files": direct.get(path, []),
            "last_verified_commit": d["last_verified_commit"],
            "commits_behind": behind,
            "action": level,
        })
    order = {"must-update": 0, "review": 1, "in-sync": 2}
    results.sort(key=lambda r: (order[r["action"]], r["path"]))
    return {"changed_files": files, "documents": results,
            "summary": {k: sum(1 for r in results if r["action"] == k)
                        for k in order}}


def render_text(report: dict) -> str:
    lines = [f"Changed files: {len(report['changed_files'])}",
             f"Impacted documents: {len(report['documents'])} "
             f"(must-update={report['summary']['must-update']}, "
             f"review={report['summary']['review']}, "
             f"in-sync={report['summary']['in-sync']})", ""]
    icons = {"must-update": "🔴", "review": "🟡", "in-sync": "🟢"}
    for d in report["documents"]:
        behind = (f"{d['commits_behind']} commits behind"
                  if d["commits_behind"] is not None else "unknown staleness")
        lines.append(f"{icons[d['action']]} {d['path']} [{d['id']}] "
                     f"({d['impact']}, {behind})")
        for f in d["matched_files"]:
            lines.append(f"    ↳ {f}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="living-documentation impact analysis")
    ap.add_argument("--root", default=None, help="Root directory of target project")
    ap.add_argument("--changed-files", nargs="*", default=None, help="Explicit list of changed files")
    ap.add_argument("--since", default=None, help="Compare changes since commit/ref")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = ap.parse_args()

    root = resolve_root(args.root)
    files = changed_files(root, args.since, args.changed_files)
    report = analyze(root, files)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
