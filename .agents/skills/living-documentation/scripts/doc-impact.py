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


def tui_select(title: str, options: list[tuple[str, any]]) -> any:
    """Renders single-select interactive TUI or falls back to numbered prompt."""
    if not sys.stdin.isatty():
        print(title)
        for i, (label, _) in enumerate(options, 1):
            print(f"{i}) {label}")
        try:
            choice = input(f"Select [1-{len(options)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
        except Exception:
            pass
        return options[0][1]

    cur = 0
    count = len(options)
    print(f"\n\033[36m{title}\033[0m")
    print("\033[2m↑↓ move, enter confirm\033[0m")

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        if sys.platform != "win32":
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    for i, (label, _) in enumerate(options):
                        if i == cur:
                            sys.stdout.write(f"\033[36m> ● {label}\033[0m\n")
                        else:
                            sys.stdout.write(f"  \033[90m○\033[0m {label}\n")
                    sys.stdout.flush()

                    ch = sys.stdin.read(1)
                    if ch == "\x1b":
                        seq = sys.stdin.read(2)
                        if seq == "[A":
                            cur = (cur - 1 + count) % count
                        elif seq == "[B":
                            cur = (cur + 1) % count
                    elif ch in ("k", "K"):
                        cur = (cur - 1 + count) % count
                    elif ch in ("j", "J"):
                        cur = (cur + 1) % count
                    elif ch in ("\r", "\n"):
                        break
                    elif ch in ("q", "Q"):
                        sys.exit(0)

                    sys.stdout.write(f"\033[{count}A")
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        else:
            import msvcrt
            while True:
                for i, (label, _) in enumerate(options):
                    if i == cur:
                        sys.stdout.write(f"> ● {label}\n")
                    else:
                        sys.stdout.write(f"  ○ {label}\n")
                sys.stdout.flush()

                key = msvcrt.getch()
                if key in (b"\x00", b"\xe0"):
                    code = msvcrt.getch()
                    if code == b"H":
                        cur = (cur - 1 + count) % count
                    elif code == b"P":
                        cur = (cur + 1) % count
                elif key in (b"\r", b"\n"):
                    break
                elif key in (b"q", b"Q"):
                    sys.exit(0)

                sys.stdout.write(f"\033[{count}A")
                sys.stdout.flush()
    except Exception:
        pass
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()

    return options[cur][1]


def prompt_interactive_wizard() -> tuple[str | None, str | None, list[str] | None, bool]:
    """Returns (root, since, changed_files, is_json)."""
    print("\n\033[36m==================================================")
    print(" 📑 doc-impact: 活体文档影响分析向导 (Living Doc Impact)")
    print("==================================================\033[0m")

    mode = tui_select("[1/3] 选择影响分析检测范围 (Select Analysis Mode):", [
        ("工作区当前变更 (Working tree changes: HEAD + untracked)", "working-tree"),
        ("自特定 Commit / 分支对比 (Since commit or branch)", "since"),
        ("指定具体变更文件列表 (Explicit file list)", "files"),
    ])

    since = None
    changed_files_list = None
    if mode == "since":
        since = input("\n输入对比基线 Commit/分支 (例: HEAD~1, origin/main) [Default: HEAD~1]: ").strip() or "HEAD~1"
    elif mode == "files":
        raw = input("\n输入文件路径列表（空格分隔）: ").strip()
        if raw:
            changed_files_list = raw.split()

    print("\n[2/3] 目标项目根目录 (Target Project Root):")
    root_input = input("项目根目录路径 (默认自动识别当前项目 [.]) [Root DIR]: ").strip() or None

    fmt = tui_select("[3/3] 选择输出格式 (Select Output Format):", [
        ("人类可读控制台报告 (Human-readable text report)", "text"),
        ("JSON 格式 (Machine-readable JSON)", "json"),
    ])
    is_json = (fmt == "json")

    return root_input, since, changed_files_list, is_json


def main() -> int:
    ap = argparse.ArgumentParser(description="living-documentation impact analysis")
    ap.add_argument("--root", default=None, help="Root directory of target project")
    ap.add_argument("--changed-files", nargs="*", default=None, help="Explicit list of changed files")
    ap.add_argument("--since", default=None, help="Compare changes since commit/ref")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    ap.add_argument("--interactive", "-i", action="store_true", help="Launch interactive step wizard")
    args = ap.parse_args()

    if args.interactive or (len(sys.argv) == 1 and sys.stdin.isatty()):
        root_opt, since_opt, files_opt, json_opt = prompt_interactive_wizard()
        if root_opt:
            args.root = root_opt
        if since_opt:
            args.since = since_opt
        if files_opt:
            args.changed_files = files_opt
        args.json = json_opt

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
