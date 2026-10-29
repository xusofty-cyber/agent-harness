#!/usr/bin/env python3
"""i18n status check (Phase 4, 4-2).

EN/ZH are the sources of truth. ZH-TW is a generated product, not
hand-synced copies: the old symmetric H2 hard check (repo_checks section 6
before Phase 4) is gone. What this script enforces instead:

1. EN/ZH structural parity is still a HARD check: the four EN/ZH pairs
   (README + three guides) must have equal `##` counts.
2. Every ZH-TW target must have a row in
   docs/internal/i18n-status.md with a status and a source sha.
3. A row marked `in-sync` must match the current sha256 of its EN source
   (first 12 hex chars); if the source moved, the check FAILS and the row
   must be marked `stale`.
4. A row marked `stale` or `frozen` PASSES but prints a reminder: the
   translation needs regeneration from the EN source before the next
   release. Nothing here fails the build for a translation being behind —
   that is the point of the change (v2 4-2): a stale translation is a
   tracked debt, not a CI failure.
5. Template-variant line drift is a WARNING only, never a failure
   (D61, review 2026-10-29): a SESSION_STATE/PROJECT_CONTEXT template
   variant that differs from its base by more than 5 lines prints a
   [drift] reminder. The skeleton 31-line SESSION_STATE format is final;
   the ZH-TW variant still carries the old 46-line format and is flagged
   here until regenerated.

Usage:
    i18n-check.py [--spot-check [N]] [--seed N]

--spot-check prints N random translated sections next to their EN source
sections, for a human to review before a release. It never fails.
Exit codes: 0 all hard checks pass; 1 a hard check failed.
"""
import hashlib
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = ROOT / "docs" / "internal" / "i18n-status.md"

# (EN source, ZH-TW targets) — the generated set.
# FR/DE targets were removed by user final ruling 2026-10-29 (D27);
# only ZH-TW remains as a generated translation.
GENERATED = [
    ("README.md", ["README.zh-tw.md"]),
    ("docs/guides/Multi-Tool Deployment and Configuration Guide.md", [
        "docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md"]),
    ("docs/guides/Tools Practical Usage and Skills Panorama Guide.md", [
        "docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md"]),
    ("docs/guides/Skills Usage Guide.md", [
        "docs/guides/Skills Usage Guide.zh-tw.md"]),
    ("templates/agents/Global AGENTS.md", [
        "templates/agents/Global AGENTS.zh-tw.md"]),
    ("templates/agents/Project AGENTS.md", [
        "templates/agents/Project AGENTS.zh-tw.md"]),
    ("templates/agents/Directory AGENTS.md", [
        "templates/agents/Directory AGENTS.zh-tw.md"]),
]

# EN/ZH pairs that must stay in structural sync (hard check).
EN_ZH_PAIRS = [
    ("README.md", "README.zh.md"),
    ("docs/guides/Multi-Tool Deployment and Configuration Guide.md",
     "docs/guides/Multi-Tool Deployment and Configuration Guide.zh.md"),
    ("docs/guides/Tools Practical Usage and Skills Panorama Guide.md",
     "docs/guides/Tools Practical Usage and Skills Panorama Guide.zh.md"),
    ("docs/guides/Skills Usage Guide.md",
     "docs/guides/Skills Usage Guide.zh.md"),
]

ROW_RE = re.compile(
    r"^\|\s*(?P<target>[^|]+?)\s*\|\s*(?P<source>[^|]+?)\s*\|\s*"
    r"(?P<status>[^|]+?)\s*\|\s*(?P<sha>[0-9a-f]{12})\s*\|")


def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def h2_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines()
               if line.startswith("## "))


def parse_status():
    rows = {}
    for line in STATUS_FILE.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if m:
            rows[m.group("target").strip()] = (
                m.group("source").strip(), m.group("status").strip(),
                m.group("sha").strip())
    return rows


def sections(path: Path):
    """Split a markdown file into (heading, body) sections by ## heading."""
    out, cur_h, cur_b = [], None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if cur_h is not None:
                out.append((cur_h, "\n".join(cur_b)))
            cur_h, cur_b = line[3:].strip(), []
        elif cur_h is not None:
            cur_b.append(line)
    if cur_h is not None:
        out.append((cur_h, "\n".join(cur_b)))
    return out


def main(argv):
    failures, reminders = [], []
    spot_n, seed = 0, 42
    i = 0
    while i < len(argv):
        if argv[i] == "--spot-check":
            spot_n = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 3
            i += 2 if i + 1 < len(argv) and argv[i + 1].isdigit() else 1
        elif argv[i] == "--seed":
            seed = int(argv[i + 1])
            i += 2
        else:
            print(f"i18n-check: unknown option {argv[i]}", file=sys.stderr)
            return 2

    # 1. EN/ZH hard parity.
    for src, tgt in EN_ZH_PAIRS:
        s, t = h2_count(ROOT / src), h2_count(ROOT / tgt)
        if s != t:
            failures.append(f"EN/ZH parity: {src} has {s} ## sections, {tgt} has {t}")

    # 2-4. Status-file rows.
    if not STATUS_FILE.is_file():
        print(f"i18n-check: missing {STATUS_FILE}", file=sys.stderr)
        return 1
    rows = parse_status()
    for src, tgts in GENERATED:
        for tgt in tgts:
            row = rows.get(tgt)
            if row is None:
                failures.append(f"missing i18n-status row for {tgt}")
                continue
            row_src, status, sha = row
            if row_src != src:
                failures.append(f"{tgt}: status row lists source {row_src}, expected {src}")
                continue
            if status == "in-sync":
                current = sha12(ROOT / src)
                if sha != current:
                    failures.append(
                        f"{tgt} claims in-sync at {sha} but {src} is now {current} "
                        f"— mark it stale")
            elif status in ("stale", "frozen"):
                reminders.append(
                    f"[reminder] {tgt} is {status} vs {src} "
                    f"(last synced {sha}) — regenerate before release")
            else:
                failures.append(f"{tgt}: unknown status {status!r}")

    # 5. Template-variant line drift (warning only, D61).
    for base in ("templates/SESSION_STATE.template.md",
                 "templates/PROJECT_CONTEXT.template.md"):
        base_path = ROOT / base
        if not base_path.is_file():
            continue
        base_lines = len(base_path.read_text(encoding="utf-8").splitlines())
        stem = base[:-len(".md")]
        for suffix in (".zh.md", ".zh-tw.md"):
            var = ROOT / (stem + suffix)
            if not var.is_file():
                continue
            var_lines = len(var.read_text(encoding="utf-8").splitlines())
            if abs(var_lines - base_lines) > 5:
                reminders.append(
                    f"[drift] {stem + suffix} is {var_lines} lines vs "
                    f"base {base} {base_lines} lines — regenerate from "
                    f"the base format (D61)")

    for r in reminders:
        print(r)
    if failures:
        for f in failures:
            print(f"[FAIL] {f}")
        print(f"{len(failures)} i18n check(s) failed.")
        return 1

    if spot_n:
        rng = random.Random(seed)
        all_targets = [t for _, ts in GENERATED for t in ts]
        print(f"--- spot-check (seed {seed}): {spot_n} sampled sections ---")
        for tgt in rng.sample(all_targets, min(spot_n, len(all_targets))):
            src = next(s for s, ts in GENERATED if tgt in ts)
            t_secs, s_secs = sections(ROOT / tgt), sections(ROOT / src)
            if not t_secs or not s_secs:
                print(f"{tgt}: no ## sections to sample")
                continue
            idx = rng.randrange(min(len(t_secs), len(s_secs)))
            print(f"\n[{tgt} §{idx + 1}] target heading: {t_secs[idx][0]}")
            print(f"  target (first 3 lines): "
                  f"{' / '.join(t_secs[idx][1].splitlines()[:3])}")
            print(f"[{src} §{idx + 1}] source heading: {s_secs[idx][0]}")
            print(f"  source (first 3 lines): "
                  f"{' / '.join(s_secs[idx][1].splitlines()[:3])}")
    print(f"i18n check passed ({len(reminders)} reminder(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
