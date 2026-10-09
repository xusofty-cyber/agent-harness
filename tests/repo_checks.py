#!/usr/bin/env python3
"""tests/repo_checks.py — static repository checks for agent-harness CI.

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

# --- 3b. Skill version (in-repo-authored skills only) ---
# Skills with sourceType "local" in skills-lock.json must declare a semver
# `version:` in SKILL.md frontmatter, matching the lock entry. Vendored skills
# are versioned upstream — a local version: there is ignored, not an error.
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
lock_data = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8-sig"))
local_skills = {k for k, v in lock_data["skills"].items()
                if v.get("sourceType") == "local"}
for name in sorted(local_skills):
    f = ROOT / ".agents" / "skills" / name / "SKILL.md"
    fm_m = re.match(r"^---\n(.*?)\n---\n", f.read_text(encoding="utf-8-sig"), re.DOTALL)
    ver_m = re.search(r"^version:\s*(\S+)", fm_m.group(1), re.MULTILINE) if fm_m else None
    ver = ver_m.group(1).strip("\"'") if ver_m else ""
    check(f"skill:{name}:version-present", bool(ver),
          "local skill must declare version: in SKILL.md frontmatter")
    check(f"skill:{name}:version-semver", bool(SEMVER.match(ver)),
          f"version {ver!r} is not semver x.y.z")
    check(f"skill:{name}:version-lock-match",
          lock_data["skills"][name].get("version") == ver,
          f"lock version {lock_data['skills'][name].get('version')!r} != frontmatter {ver!r}")

# --- 3c. VERSION file consistency ---
# VERSION must equal the newest ## [x.y.z] heading in CHANGELOG.md.
# (Tag consistency is verified manually at release time; CI checkouts
# don't fetch tags by default.)
version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
cl_headings = re.findall(r"^## \[(\d+\.\d+\.\d+)\]",
                         (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
                         re.MULTILINE)
check("version:file-exists", bool(version_file), "VERSION is empty")
check("version:matches-changelog",
      bool(cl_headings) and version_file == cl_headings[0],
      f"VERSION={version_file!r} vs CHANGELOG newest={cl_headings[0] if cl_headings else None!r}")

# --- 3d. Living-doc frontmatter ---
# docs/{specs,architecture,reference,guides,adr}/ .md files must declare
# valid traceability frontmatter: id / type / status / modules (non-empty).
# type must match the containing tier directory. Missing tier dirs are skipped
# (scaffold is created by deploy scripts in target projects, not in this repo).
DOC_TIERS = ("specs", "architecture", "reference", "guides", "adr")
DOC_TYPES = {"specs", "architecture", "reference", "guide", "adr"}
DOC_STATUS = {"draft", "active", "deprecated"}
TIER_TYPE = {"specs": "specs", "architecture": "architecture",
             "reference": "reference", "guides": "guide", "adr": "adr"}

def _parse_simple_frontmatter(text):
    """Minimal YAML-subset parser for flat key: value, key: [a, b],
    and multi-line list fields."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fields = {}
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
                fields[key] = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
            else:
                fields[key] = val.strip("\"'")
    return fields

for tier in DOC_TIERS:
    tier_dir = ROOT / "docs" / tier
    if not tier_dir.is_dir():
        continue
    for f in sorted(tier_dir.rglob("*.md")):
        rel = f.relative_to(ROOT).as_posix()
        fm = _parse_simple_frontmatter(f.read_text(encoding="utf-8-sig"))
        check(f"doc:{rel}:frontmatter", fm is not None,
              "missing YAML frontmatter block")
        if fm is None:
            continue
        for field in ("id", "type", "status", "modules"):
            check(f"doc:{rel}:{field}",
                  bool(fm.get(field)),
                  f"frontmatter must define non-empty {field}:")
        check(f"doc:{rel}:type-valid",
              fm.get("type") in DOC_TYPES,
              f"type {fm.get('type')!r} not in {sorted(DOC_TYPES)}")
        check(f"doc:{rel}:type-tier-match",
              fm.get("type") == TIER_TYPE[tier],
              f"type {fm.get('type')!r} != tier {tier!r} (expected {TIER_TYPE[tier]!r})")
        check(f"doc:{rel}:status-valid",
              fm.get("status") in DOC_STATUS,
              f"status {fm.get('status')!r} not in {sorted(DOC_STATUS)}")

# --- 3e. doc-impact.py dual-copy sync ---
# tools/doc-impact.py and the skill-bundled copy must stay identical.
# (The skill copy deploys to target projects; tools/ is this repo's own copy.)
_impact_a = ROOT / "tools" / "doc-impact.py"
_impact_b = (ROOT / ".agents" / "skills" / "living-documentation"
             / "scripts" / "doc-impact.py")
check("doc-impact:sync",
      _impact_a.is_file() and _impact_b.is_file()
      and _impact_a.read_bytes() == _impact_b.read_bytes(),
      "tools/doc-impact.py and living-documentation/scripts/doc-impact.py diverged")

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
    ("AiMemoryInit", "ai-memory-init", "optional ai-memory init flag"),
    (".ai-memory.toml.example", ".ai-memory.toml.example", "ai-memory config template sync"),
    ("LivingDocScaffold", "living-doc-scaffold", "living documentation directory scaffold"),
    ("Open Code Review CLI", "Open Code Review CLI", "optional OCR CLI detection"),
    ("review-sensitive-paths.json", "review-sensitive-paths.json", "sensitive paths config sync"),
    ("sync-skills.py", "sync-skills.py", "external skill sync in update flow"),
    ("Comet CLI", "Comet CLI", "optional Comet CLI detection"),
    ("Resolve-TemplateFile", "resolve_template", "multilingual template resolution"),
    ("Prompt-InteractiveWizard", "prompt_interactive_wizard", "interactive terminal wizard"),
    ("GEMINI.md -> AGENTS.md", "GEMINI.md -> AGENTS.md", "Gemini CLI bridge"),
    ("QWEN.md -> AGENTS.md", "QWEN.md -> AGENTS.md", "Qwen Code bridge"),
    ("CODEBUDDY.md -> AGENTS.md", "CODEBUDDY.md -> AGENTS.md", "CodeBuddy bridge"),
    ("New-RuleDirBridge", "bridge_rule_dir", "rule-directory bridge helper"),
    (".windsurf/rules", ".windsurf/rules", "Windsurf bridge"),
    (".clinerules", ".clinerules", "Cline bridge"),
    (".roo/rules", ".roo/rules", "Roo Code bridge"),
    (".kiro/steering", ".kiro/steering", "Kiro bridge"),
    (".continue/rules", ".continue/rules", "Continue.dev bridge"),
    (".trae/rules", ".trae/rules", "Trae bridge"),
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

# --- 6. Multilingual doc pairs: structural parity ---
# Each translated guide must keep the same ## section count as its source,
# so the translated structure cannot silently drift from the source.
MULTILINGUAL_DOC_PAIRS = [
    ("README.md", "README_zh.md"),
    ("README.md", "README.zh-tw.md"),
    ("README.md", "README.fr.md"),
    ("README.md", "README.de.md"),
    ("Multi-Tool Deployment and Configuration Guide.md",
     "Multi-Tool Deployment and Configuration Guide.zh.md"),
    ("Multi-Tool Deployment and Configuration Guide.md",
     "Multi-Tool Deployment and Configuration Guide.zh-tw.md"),
    ("Multi-Tool Deployment and Configuration Guide.md",
     "Multi-Tool Deployment and Configuration Guide.fr.md"),
    ("Multi-Tool Deployment and Configuration Guide.md",
     "Multi-Tool Deployment and Configuration Guide.de.md"),
    ("Tools Practical Usage and Skills Panorama Guide.md",
     "Tools Practical Usage and Skills Panorama Guide.zh.md"),
    ("Tools Practical Usage and Skills Panorama Guide.md",
     "Tools Practical Usage and Skills Panorama Guide.zh-tw.md"),
    ("Tools Practical Usage and Skills Panorama Guide.md",
     "Tools Practical Usage and Skills Panorama Guide.fr.md"),
    ("Tools Practical Usage and Skills Panorama Guide.md",
     "Tools Practical Usage and Skills Panorama Guide.de.md"),
]

def h2_count(path):
    return sum(1 for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
               if line.startswith("## "))

for src, target in MULTILINGUAL_DOC_PAIRS:
    src_n, target_n = h2_count(src), h2_count(target)
    check(f"doc-parity:{src}=={target}", src_n == target_n,
          f"## section count drift: {src_n} vs {target_n}")

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
