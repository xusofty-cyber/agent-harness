#!/usr/bin/env python3
"""sync-skills.py — external skill self-update for agent-harness.

Checks vendored external skills (sourceType=github in skills-lock.json)
against their upstream repositories and reports or applies updates.

Usage:
    python3 tools/sync-skills.py [--check] [--apply] [--skill NAME] [--json]

- --check (default): report which skills differ from upstream (read-only,
  safe to run in CI).
- --apply: update outdated skill files in place and refresh computedHash
  in skills-lock.json. Never touches local-authored skills.
- --skill NAME: limit to a single skill directory name.
- --json: machine-readable output.

Upstream fetch uses the GitHub API (default branch auto-detected, cached
per repo) with raw.githubusercontent fallback. Unauthenticated requests
are rate-limited to 60/hour; the tool degrades gracefully.

Hash scheme: SHA256 of file bytes (LF-normalized). The legacy computedHash
values in skills-lock.json predate this scheme and are refreshed on --apply.

Exit codes: 0 always (advisory tool, never blocks). Parse output for gating.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "skills-lock.json"
SKILLS_DIR = ROOT / ".agents" / "skills"

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"

_branch_cache: dict[str, str] = {}


def _http_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-harness-sync-skills",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _http_bytes(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={
        "User-Agent": "agent-harness-sync-skills",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception:
        return None


def default_branch(repo: str) -> str:
    """owner/name -> default branch, cached. Falls back to 'main'."""
    if repo not in _branch_cache:
        info = _http_json(f"{API}/repos/{repo}")
        _branch_cache[repo] = (info or {}).get("default_branch", "main")
        time.sleep(0.3)  # be gentle with rate limits
    return _branch_cache[repo]


def fetch_upstream(repo: str, path: str) -> bytes | None:
    branch = default_branch(repo)
    for b in (branch, "main", "master"):
        data = _http_bytes(f"{RAW}/{repo}/{b}/{path}")
        if data is not None:
            return data
        time.sleep(0.3)
    return None


def sha256_norm(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def load_lock() -> dict:
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def external_skills(lock: dict, only: str | None = None) -> list[tuple[str, dict]]:
    """Return (name, meta) for upstream-syncable skills.

    Skippable: local-authored skills, CLI tool entries (have `package`),
    source-repo meta entries (no resolvable upstream file), and
    locally-authored wrappers (skillPath under .agents/).
    """
    out = []
    for name, meta in lock.get("skills", {}).items():
        if only and name != only:
            continue
        if meta.get("sourceType") != "github":
            continue
        if "package" in meta:
            continue  # CLI tool entry, not a skill file
        sp = meta.get("skillPath", "")
        if not sp.startswith("skills/"):
            continue  # locally-authored wrapper or meta entry
        local_file = SKILLS_DIR / name / "SKILL.md"
        if not local_file.is_file():
            continue
        out.append((name, meta))
    return out


def check_skill(name: str, meta: dict) -> dict:
    repo = meta["source"]
    rel = meta["skillPath"]  # upstream-relative path
    local_file = SKILLS_DIR / name / "SKILL.md"
    result: dict = {"skill": name, "source": repo, "path": rel}

    upstream = fetch_upstream(repo, rel)
    if upstream is None:
        result["status"] = "fetch-failed"
        return result

    local_hash = sha256_norm(local_file.read_bytes())
    upstream_hash = sha256_norm(upstream)
    result["local_sha256"] = local_hash[:12]
    result["upstream_sha256"] = upstream_hash[:12]
    if local_hash == upstream_hash:
        result["status"] = "in-sync"
    else:
        result["status"] = "outdated"
        result["upstream_bytes"] = upstream
    return result


def apply_update(name: str, meta: dict, upstream: bytes) -> None:
    local_file = SKILLS_DIR / name / "SKILL.md"
    local_file.write_bytes(upstream)
    lock = load_lock()
    lock["skills"][name]["computedHash"] = sha256_norm(upstream)
    LOCK_PATH.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")


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


def prompt_interactive_wizard(lock: dict) -> tuple[bool, str | None, bool]:
    """Returns (do_apply, target_skill, is_json)."""
    print("\n\033[36m==================================================")
    print(" 🔄 sync-skills: 外部技能同步向导 (Interactive Sync)")
    print("==================================================\033[0m")

    action = tui_select("[1/3] 选择执行操作 (Select Action):", [
        ("检查外部技能更新状态（只读汇报，安全）", "check"),
        ("应用并就地更新过时技能文件（刷新 skills-lock.json）", "apply"),
    ])
    do_apply = (action == "apply")

    all_ext = [name for name, _ in external_skills(lock, None)]
    scope_options = [("同步所有外部技能 (All external skills)", "all")]
    for name in sorted(all_ext):
        scope_options.append((f"仅针对单个技能: {name}", name))

    chosen_scope = tui_select("[2/3] 选择同步范围 (Select Scope):", scope_options)
    target_skill = None if chosen_scope == "all" else chosen_scope

    fmt = tui_select("[3/3] 选择输出格式 (Select Output Format):", [
        ("控制台友好摘要报告 (Human-readable text report)", "text"),
        ("JSON 格式 (Machine-readable JSON)", "json"),
    ])
    is_json = (fmt == "json")

    return do_apply, target_skill, is_json


def main() -> int:
    ap = argparse.ArgumentParser(description="sync external skills with upstream")
    ap.add_argument("--check", action="store_true", help="report only (default)")
    ap.add_argument("--apply", action="store_true", help="update files + lock")
    ap.add_argument("--skill", default=None, help="limit to one skill")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--interactive", "-i", action="store_true", help="launch interactive step wizard")
    args = ap.parse_args()

    lock = load_lock()
    if args.interactive or (len(sys.argv) == 1 and sys.stdin.isatty()):
        do_apply, target_skill, is_json = prompt_interactive_wizard(lock)
        args.skill = target_skill
        args.json = is_json
    else:
        do_apply = args.apply

    skills = external_skills(lock, args.skill)
    if args.skill and not skills:
        print(f"Unknown or non-external skill: {args.skill}", file=sys.stderr)
        return 0

    results = []
    for name, meta in skills:
        r = check_skill(name, meta)
        if do_apply and r.get("status") == "outdated":
            apply_update(name, meta, r.pop("upstream_bytes"))
            r["status"] = "updated"
        else:
            r.pop("upstream_bytes", None)
        results.append(r)

    summary = {}
    for r in results:
        summary[r["status"]] = summary.get(r["status"], 0) + 1

    if args.json:
        print(json.dumps({"results": results, "summary": summary},
                         indent=2, ensure_ascii=False))
    else:
        icons = {"in-sync": "🟢", "outdated": "🟡", "updated": "🔵",
                 "fetch-failed": "⚪", "missing-local": "🔴"}
        print(f"Checked {len(results)} external skills: " +
              ", ".join(f"{k}={v}" for k, v in sorted(summary.items())))
        print()
        for r in sorted(results, key=lambda x: x["skill"]):
            icon = icons.get(r["status"], "❓")
            extra = ""
            if r["status"] in ("outdated", "updated"):
                extra = f" ({r['local_sha256']} → {r['upstream_sha256']})"
            print(f"{icon} {r['skill']}: {r['status']}{extra}")
        if do_apply and summary.get("updated"):
            print(f"\nUpdated {summary['updated']} skill(s); "
                  f"skills-lock.json hashes refreshed. Review the diff "
                  f"before committing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
