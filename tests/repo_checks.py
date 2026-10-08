#!/usr/bin/env python3
"""tests/repo_checks.py — static repository checks for agents-living CI.

Run: `python3 tests/repo_checks.py` (exit 0 = all pass)

Checks:
  1. JSON files parse (.claude/settings.json, skills-lock.json)
  2. TOML example parses if present (.ai-memory.toml.example)
  3. Every .agents/skills/*/SKILL.md has YAML frontmatter with name+description
  4. deploy-agents.ps1 / deploy-agents.sh feature-parity markers
"""

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


# --- 1. JSON validity ---
for rel in [".claude/settings.json", "skills-lock.json"]:
    p = ROOT / rel
    try:
        json.loads(p.read_text(encoding="utf-8-sig"))
        check(f"json:{rel}", True)
    except Exception as e:  # noqa: BLE001
        check(f"json:{rel}", False, str(e))

# --- 2. TOML example validity (branch-aware: only on branches that have it) ---
toml_example = ROOT / ".ai-memory.toml.example"
if toml_example.exists():
    try:
        tomllib.loads(toml_example.read_text(encoding="utf-8-sig"))
        check("toml:.ai-memory.toml.example", True)
    except Exception as e:  # noqa: BLE001
        check("toml:.ai-memory.toml.example", False, str(e))
else:
    print("[SKIP] toml:.ai-memory.toml.example (not present on this branch)")

# --- 3. SKILL.md frontmatter ---
skill_files = sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
check("skills:found", len(skill_files) > 0, "no skills found")
for f in skill_files:
    text = f.read_text(encoding="utf-8-sig")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    name = f.parent.name
    if not m:
        check(f"skill:{name}:frontmatter", False, "missing YAML frontmatter block")
        continue
    fm = m.group(1)
    has_name = re.search(r"^name:\s*\S", fm, re.MULTILINE) is not None
    has_desc = re.search(r"^description:\s*\S", fm, re.MULTILINE) is not None
    check(f"skill:{name}:frontmatter", has_name and has_desc,
          "frontmatter must define non-empty name: and description:")

# --- 4. deploy script parity ---
# Parity = no unilateral features: if a feature marker exists in one script,
# its counterpart marker must exist in the other. Markers that exist in
# neither script are skipped (branch-aware: LTMG-only features don't fail main).
# Table: (ps1 marker, sh marker, feature description)
PARITY = [
    ("Sync-GlobalRule", "deploy_global_rule", "safe global-rule sync"),
    ("Backup-ManagedPath", "backup_path", "timestamped backup before overwrite"),
    ("Backup-GlobalRule", "deploy_global_rule", "safe global-rule backup (LTMG+)"),
    ("AGENTS.override.md", "AGENTS.override.md", "Codex override-file detection"),
    ("CODEX_HOME", "CODEX_HOME", "Codex home directory support"),
    ("Antigravity", "Antigravity", "Antigravity deployment"),
    ("GEMINI.md", "GEMINI.md", "Antigravity legacy GEMINI.md pointer"),
    ("skills-lock.json", "skills-lock.json", "skills lock metadata"),
    (".claude", ".claude", "Claude Code hooks deployment"),
    ("CometInit", "comet-init", "optional Comet init flag"),
]
ps1 = (ROOT / "deploy-agents.ps1").read_text(encoding="utf-8-sig")
sh = (ROOT / "deploy-agents.sh").read_text(encoding="utf-8")
for ps1_marker, sh_marker, feature in PARITY:
    in_ps1 = ps1_marker in ps1
    in_sh = sh_marker in sh
    if not in_ps1 and not in_sh:
        print(f"[SKIP] parity:{feature} (not present on this branch)")
        continue
    detail = ""
    if in_ps1 and not in_sh:
        detail = f"'{sh_marker}' missing in deploy-agents.sh"
    elif in_sh and not in_ps1:
        detail = f"'{ps1_marker}' missing in deploy-agents.ps1"
    check(f"parity:{feature}", in_ps1 == in_sh, detail)

# --- 5. skills-lock.json consistency ---
# Every skill directory must have a lock entry (provenance metadata).
# Lock entries without a directory are allowed only for known meta-entries
# (suites, not single skills).
META_ENTRIES = {"openspec", "superpowers"}
lock_skills = set(json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8-sig"))["skills"])
dir_skills = {p.name for p in (ROOT / ".agents" / "skills").iterdir() if p.is_dir()}
missing_lock = sorted(dir_skills - lock_skills)
check("lock:covers-all-dirs", not missing_lock,
      f"skill dirs without lock entry: {missing_lock}")
orphan_lock = sorted(lock_skills - dir_skills - META_ENTRIES)
check("lock:no-orphans", not orphan_lock,
      f"lock entries without skill dir: {orphan_lock}")

# --- 6. Bilingual doc pairs: structural parity ---
# Each EN/ZH guide pair must keep the same ## section count, so the
# translated structure cannot silently drift from the source.
BILINGUAL_PAIRS = [
    ("README.md", "README_zh.md"),
    ("Multi-Tool Deployment and Configuration Guide.md",
     "Multi-Tool Deployment and Configuration Guide.zh.md"),
    ("Tools Practical Usage and Skills Panorama Guide.md",
     "Tools Practical Usage and Skills Panorama Guide.zh.md"),
]

def h2_count(path):
    return sum(1 for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
               if line.startswith("## "))

for en, zh in BILINGUAL_PAIRS:
    en_n, zh_n = h2_count(en), h2_count(zh)
    check(f"bilingual:{en}=={zh}", en_n == zh_n,
          f"## section count drift: {en_n} vs {zh_n}")

# --- 7. Executable bit on entry-point scripts ---
# The GitHub contents API resets the exec bit to 100644 on every content push,
# so this guard catches the regression in CI. If it fails, run locally:
#   git update-index --chmod=+x deploy-agents.sh setup-ai-memory.sh
import subprocess
EXEC_SCRIPTS = ["deploy-agents.sh", "setup-ai-memory.sh"]
try:
    ls = subprocess.run(["git", "ls-files", "-s", "--", *EXEC_SCRIPTS],
                        capture_output=True, text=True, cwd=ROOT, check=True).stdout
    modes = {line.split("\t", 1)[1]: line.split()[0]
             for line in ls.splitlines() if line.strip()}
except Exception as e:  # not a git checkout (e.g. sdist)
    modes = {}
    check("exec-bit:git-available", False, f"cannot query git index: {e}")
for script in EXEC_SCRIPTS:
    check(f"exec-bit:{script}", modes.get(script) == "100755",
          f"mode is {modes.get(script)}, expected 100755 — run: "
          f"git update-index --chmod=+x {script}")

print()
if failures:
    print(f"{len(failures)} check(s) failed.")
    sys.exit(1)
print("All repo checks passed.")
