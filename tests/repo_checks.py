#!/usr/bin/env python3
"""tests/repo_checks.py — static repository checks for agent-harness CI.

Run: `python3 tests/repo_checks.py` (exit 0 = all pass)

Checks:
  1. JSON files parse (.claude/settings.json, skills-lock.json)
  2. TOML example parses if present (.ai-memory.toml.example)
  3. Every .agents/skills/*/SKILL.md has YAML frontmatter with name+description
  4. deploy-agents.ps1 / deploy-agents.sh feature-parity markers
"""

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
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
toml_example = ROOT / "templates" / "ai-memory.toml.example"
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

# --- 3b2. Every skill must have a provenance identifier ---
# Local skills: semver `version` (enforced above). External skills: `computedHash`
# serves as the content identifier. No skill may exist without provenance.
# (META_ENTRIES are source-repo placeholders, not real skills.)
for name, meta in sorted(lock_data.get("skills", {}).items()):
    if meta.get("meta") is True:  # source-repo meta entry (Phase 2, 2-2c), not a real skill
        continue
    has_provenance = bool(meta.get("version")) or bool(meta.get("computedHash"))
    check(f"provenance:{name}", has_provenance,
          f"skill {name} has neither version nor computedHash in lock")

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
DOC_TIERS = ("specs", "architecture", "reference", "guides", "management", "tests", "adr")
DOC_TYPES = {"specs", "architecture", "reference", "guide", "management", "tests", "adr"}
DOC_STATUS = {"draft", "active", "deprecated"}
TIER_TYPES = {"specs": "specs", "architecture": "architecture",
              "reference": "reference", "guides": "guide",
              "management": "management", "tests": "tests", "adr": "adr"}

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
        # docs/guides/ are user-facing docs, not tiered docs — skip frontmatter check
        if "docs/guides/" in f.as_posix():
            continue
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
              fm.get("type") == TIER_TYPES[tier],
              f"type {fm.get('type')!r} != tier {tier!r} (expected exact {TIER_TYPES[tier]!r})")
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

# --- 3f. Engineering-docs templates frontmatter check ---
# All 15 templates under .agents/skills/engineering-docs/references/templates/
# must declare valid living-doc YAML frontmatter with canonical types and schemas.
tmpl_dir = ROOT / ".agents" / "skills" / "engineering-docs" / "references" / "templates"
tmpl_files = sorted(tmpl_dir.glob("*.md"))
check("tmpl:count-15", len(tmpl_files) == 15,
      f"expected 15 engineering-docs templates, got {len(tmpl_files)}")

for tf in tmpl_files:
    rel = tf.relative_to(ROOT).as_posix()
    tf_content = tf.read_text(encoding="utf-8-sig")
    fm = _parse_simple_frontmatter(tf_content)
    check(f"tmpl:{rel}:frontmatter", fm is not None, "missing YAML frontmatter block")
    if fm is None:
        continue
    for field in ("id", "type", "status", "modules"):
        check(f"tmpl:{rel}:{field}",
              bool(fm.get(field)),
              f"template frontmatter must define non-empty {field}:")
    check(f"tmpl:{rel}:type-canonical",
          fm.get("type") in DOC_TYPES,
          f"type {fm.get('type')!r} not in canonical {sorted(DOC_TYPES)}")
    check(f"tmpl:{rel}:status-valid",
          fm.get("status") in DOC_STATUS,
          f"status {fm.get('status')!r} not in {sorted(DOC_STATUS)}")
    check(f"tmpl:{rel}:modules-is-list",
          isinstance(fm.get("modules"), list),
          f"template frontmatter modules must be a list")
    check(f"tmpl:{rel}:depends_on-is-list",
          isinstance(fm.get("depends_on"), list),
          f"template frontmatter depends_on must be a list")
    # depends_on paths must point to valid doc tiers
    for _dep in (fm.get("depends_on") or []):
        _dep_tier = _dep.split("/")[1] if _dep.startswith("docs/") and "/" in _dep[5:] else None
        check(f"tmpl:{rel}:depends_on-tier",
              _dep_tier in DOC_TIERS,
              f"depends_on {_dep!r} must point to docs/<tier>/ with tier in {DOC_TIERS}")

# --- 3f2. Comet <-> engineering-docs path mapping cross-check ---
# The "recommended storage path" for each template must agree between
# engineering-docs/SKILL.md (template table) and comet/SKILL.md (phase table).
# Prevents silent divergence of the two manually-maintained mappings.
def _extract_template_paths(skill_md: Path, pattern: str) -> dict:
    """Extract {template_number: docs_path} from a SKILL.md mapping table."""
    import re
    mapping = {}
    for m in re.finditer(pattern, skill_md.read_text(encoding="utf-8"), re.M):
        mapping[m.group(1)] = m.group(2)
    return mapping

edoc_skill = ROOT / ".agents" / "skills" / "engineering-docs" / "SKILL.md"
comet_skill = ROOT / ".agents" / "skills" / "comet" / "SKILL.md"
# engineering-docs table: "| 01 | ... | `docs/xxx/` |"
edoc_paths = _extract_template_paths(
    edoc_skill, r"^\| (\d{2}) \| [^|]+ \| [^|]+ \| [^|]+ \| `docs/([^/]+)/`")
check("xcheck:edoc-parsed-15", len(edoc_paths) == 15,
      f"engineering-docs template table parsed {len(edoc_paths)} templates, expected 15")
# comet table: template numbers mentioned per phase row; extract all `docs/xxx/` per row
# then map template numbers listed in that row to those paths.
import re as _re
comet_text = comet_skill.read_text(encoding="utf-8")
comet_paths: dict[str, set[str]] = {}
for row in _re.findall(r"^\| \*\*[^|]+\*\* \| ([^|]+) \| ([^|]+) \|", comet_text, _re.M):
    dirs, tmpls = row
    dir_set = set(_re.findall(r"`docs/([^/]+)/`", dirs))
    for tnum in _re.findall(r"`(\d{2})-[^`]+`", tmpls):
        comet_paths.setdefault(tnum, set()).update(dir_set)

for tnum, edoc_dir in sorted(edoc_paths.items()):
    cdirs = comet_paths.get(tnum, set())
    if cdirs:
        check(f"xcheck:tmpl-{tnum}-path",
              edoc_dir in cdirs,
              f"template {tnum}: engineering-docs says docs/{edoc_dir}/, "
              f"comet says {sorted('docs/'+d+'/' for d in cdirs)}")


# --- 3g. comet.config.yaml validity ---
# templates/comet.config.yaml must be valid YAML and have required top-level keys.
try:
    import yaml
    _yaml_available = True
except ImportError:
    _yaml_available = False

if _yaml_available:
    comet_cfg_path = ROOT / "templates" / "comet.config.yaml"
    check("comet-cfg:file-exists", comet_cfg_path.is_file(), "templates/comet.config.yaml missing")
    if comet_cfg_path.is_file():
        cfg_data = yaml.safe_load(comet_cfg_path.read_text(encoding="utf-8"))
        check("comet-cfg:valid-yaml-dict", isinstance(cfg_data, dict), "comet.config.yaml root must be a dict")
        if isinstance(cfg_data, dict):
            for req_key in ("schema", "default_workflow", "workflows"):
                check(f"comet-cfg:key-{req_key}", req_key in cfg_data, f"missing {req_key} in comet.config.yaml")
else:
    # Never silently skip: CI installs pyyaml, but local runs may not have it.
    print("  [warn] comet-cfg: PyYAML not installed, validation skipped (pip install pyyaml)")

# --- 3h. templates/agents canonical templates completeness ---
# All 15 canonical templates (3 types x 5 languages) must exist under templates/agents/
for tmpl_prefix in ("Global AGENTS", "Project AGENTS", "Directory AGENTS"):
    for lang_suf in ("", ".en", ".zh-tw", ".fr", ".de"):
        expected_tmpl = ROOT / "templates" / "agents" / f"{tmpl_prefix}{lang_suf}.md"
        check(f"template-exists:{tmpl_prefix}{lang_suf}", expected_tmpl.is_file(),
              f"missing canonical template: {expected_tmpl}")

# --- 3i. Skill counts: single source of truth (Phase 0, 0-1) ---
# tools/count-skills.py owns the expected composition (40 dirs on disk,
# 42 lock entries incl. 2 meta entries) and scans live docs for stale
# counts (44/43/42 in a skill context, openspec suite != 12). The script
# is the single implementation; this check only asserts it passes.
_count = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "count-skills.py"), "--check"],
    capture_output=True, text=True, cwd=str(ROOT), timeout=60)
_count_detail = (_count.stdout.strip().splitlines() or [""])[-1]
check("skills:count-source-of-truth", _count.returncode == 0, _count_detail)

# --- 3j. Skill references in templates/guides must resolve (Phase 0, 0-6) ---
# Backticked skill-name-looking tokens (`lowercase-hyphenated`) in the
# distributable agent templates and the FAQ guides must be either a real
# skill directory under .agents/skills/ or a known non-skill identifier
# (allowlist below). This catches dead references like `comet-archive`
# (removed in 0-6; no such skill ever existed). Slash-command utterances
# in prose (e.g. "/comet ...") are not backticked and stay a manual-review
# item. Also: docs/internal/*.md must not contain unfilled <PLACEHOLDER>/
# <TODO>/<TBD>/<XXX> markers.
_SKILL_TOKEN_RE = re.compile(r"`([a-z][a-z0-9_-]*)`")
_SKILL_REF_ALLOWLIST = {
    # product / project names, not skills
    "agent-harness", "ai-memory",
    # lock meta entry (source repo), not a skill directory
    "openspec",
    # frontmatter keys / git identifiers / CLI tool names
    "depends_on", "modules", "develop", "main", "master", "staging",
    "rebase", "ocr", "rg",
}
_skill_dirs = {p.name for p in (ROOT / ".agents" / "skills").iterdir() if p.is_dir()}
_skill_ref_bad: list[str] = []
for _rel in sorted(str(p.relative_to(ROOT)) for p in (ROOT / "templates" / "agents").glob("*.md")) + \
        sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "guides").glob("Agent Triggering and FAQ Guide.*.md")):
    _text = (ROOT / _rel).read_text(encoding="utf-8-sig")
    for _lineno, _line in enumerate(_text.splitlines(), 1):
        for _tok in _SKILL_TOKEN_RE.findall(_line):
            if _tok not in _skill_dirs and _tok not in _SKILL_REF_ALLOWLIST:
                _skill_ref_bad.append(f"{_rel}:{_lineno}: `{_tok}`")
check("skills:references-resolve", not _skill_ref_bad,
      "; ".join(_skill_ref_bad[:5]))
_PLACEHOLDER_RE = re.compile(r"<\s*(PLACEHOLDER|TODO|TBD|XXX)\b", re.IGNORECASE)
_placeholder_bad: list[str] = []
for _p in sorted((ROOT / "docs" / "internal").rglob("*.md")):
    for _lineno, _line in enumerate(_p.read_text(encoding="utf-8-sig").splitlines(), 1):
        if _PLACEHOLDER_RE.search(_line):
            _placeholder_bad.append(f"{_p.relative_to(ROOT)}:{_lineno}")
check("docs:no-unfilled-placeholders", not _placeholder_bad,
      "; ".join(_placeholder_bad[:5]))

# --- 3k. Gate layer: schema, evidence, events (Phase 1, 1-5b) ---
# CI second check of the anti-tamper triple. The repo dogfoods the gate on
# itself: gate/feature_list.json is this repo's own list.
#   1. gate/ ships the required files (script, schema, init template).
#   2. feature_list.json validates — via pass-gate.py's own validate(), so
#      CI and the gate cannot drift apart.
#   3. every `passing` item's evidence matches a fresh verification run:
#      evidence.command == verification.command and the command exits 0
#      when re-run now. A hand-edited evidence block with stale or invented
#      output is caught here, not at review time.
#   4. gate/events.jsonl is well-formed JSONL with strictly increasing seq
#      numbers, and every passing item has a `verified` or `override` event.
# Recursion guard: a verification command may itself be repo_checks.py;
# re-runs set GATE_CI_RECURSION=1 and a nested run skips this section.
_GATE_REQUIRED = ["pass-gate.py", "feature_list.schema.json",
                  "init.template.sh"]
_gate_missing = [f for f in _GATE_REQUIRED if not (ROOT / "gate" / f).exists()]
check("gate:files-present", not _gate_missing,
      f"missing gate files: {', '.join(_gate_missing)}")
if os.environ.get("GATE_CI_RECURSION"):
    print("[SKIP] gate:evidence-recheck (nested run)")
else:
    import importlib.util as _ilu
    import subprocess as _sp
    _spec = _ilu.spec_from_file_location(
        "pass_gate", ROOT / "gate" / "pass-gate.py")
    _pg = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_pg)
    _fl_path = ROOT / "gate" / "feature_list.json"
    if _fl_path.exists():
        _fl = json.loads(_fl_path.read_text(encoding="utf-8"))
        _fl_errors = _pg.validate(_fl)
        check("gate:feature-list-valid", not _fl_errors,
              "; ".join(_fl_errors[:5]))
        # 3. re-run verification of passing items.
        _evidence_bad: list[str] = []
        for _item in _fl.get("items", []):
            if _item.get("status") != "passing":
                continue
            _ev = _item.get("evidence") or {}
            if _ev.get("override"):
                continue  # human override: truthful by declaration, visible
            _cmd = _item.get("verification", {}).get("command", "")
            if _ev.get("command") != _cmd:
                _evidence_bad.append(
                    f"{_item['id']}: evidence.command != verification.command")
                continue
            _env = dict(os.environ, GATE_CI_RECURSION="1")
            try:
                _proc = _sp.run(_cmd, shell=True, cwd=ROOT, timeout=120,
                                capture_output=True, text=True, env=_env)
                if _proc.returncode != 0:
                    _evidence_bad.append(
                        f"{_item['id']}: verification now exits "
                        f"{_proc.returncode} (evidence claims a pass)")
            except _sp.TimeoutExpired:
                _evidence_bad.append(f"{_item['id']}: verification timed out")
        check("gate:evidence-matches-rerun", not _evidence_bad,
              "; ".join(_evidence_bad[:5]))
        # 4. events log well-formed, monotonic, and covers passing items.
        _events_path = ROOT / "gate" / "events.jsonl"
        _events_bad: list[str] = []
        _seen_events: set[tuple[str, str]] = set()
        if _events_path.exists():
            _prev_seq = 0
            for _lineno, _line in enumerate(
                    _events_path.read_text(encoding="utf-8").splitlines(), 1):
                if not _line.strip():
                    continue
                try:
                    _rec = json.loads(_line)
                except json.JSONDecodeError:
                    _events_bad.append(f"events.jsonl:{_lineno}: not JSON")
                    continue
                for _key in ("seq", "ts", "actor", "event"):
                    if _key not in _rec:
                        _events_bad.append(
                            f"events.jsonl:{_lineno}: missing key {_key}")
                if isinstance(_rec.get("seq"), int):
                    if _rec["seq"] <= _prev_seq:
                        _events_bad.append(
                            f"events.jsonl:{_lineno}: seq not increasing")
                    _prev_seq = _rec["seq"]
                if _rec.get("event") in ("verified", "override"):
                    _seen_events.add((_rec["event"], _rec.get("item_id") or ""))
            for _item in _fl.get("items", []):
                if _item.get("status") == "passing" and \
                        not (_item.get("evidence") or {}).get("override"):
                    if ("verified", _item["id"]) not in _seen_events:
                        _events_bad.append(
                            f"{_item['id']}: passing without a verified event")
        else:
            _events_bad.append("gate/events.jsonl missing")
        check("gate:events-log", not _events_bad,
              "; ".join(_events_bad[:5]))
    else:
        print("[SKIP] gate:feature-list-valid (no gate/feature_list.json yet)")
        print("[SKIP] gate:evidence-matches-rerun (no gate/feature_list.json yet)")
        print("[SKIP] gate:events-log (no gate/feature_list.json yet)")
    # The template itself must validate (all items not_started, no evidence).
    _tpl_path = ROOT / "templates" / "feature_list.template.json"
    if _tpl_path.exists():
        _tpl = json.loads(_tpl_path.read_text(encoding="utf-8"))
        _tpl_errors = _pg.validate(_tpl)
        check("gate:template-valid", not _tpl_errors,
              "; ".join(_tpl_errors[:5]))

# --- 3l. Pipeline gates are real (Phase 2, 2-1) ---
# The old pipeline swallowed stage failures (`cmd || true`) and recorded
# PASS unconditionally. Guard the fix structurally:
#   1. both pipeline scripts define a strict mode;
#   2. no stage tool invocation is followed by `|| true` (stty/trap/read and
#      the informational comet probe keep theirs — they record no PASS);
#   3. both tools are invoked with --strict by the pipeline, so findings are
#      machine-detectable in every mode (strict decides FAIL vs WARN);
#   4. both summaries can print WARN (advisory failure, never PASS);
#   5. both tools document real exit codes (no "0 always" left).
_p_sh = (ROOT / "run-pipeline.sh").read_text(encoding="utf-8")
_p_ps1 = (ROOT / "run-pipeline.ps1").read_text(encoding="utf-8-sig")
check("pipeline-strict:sh-flag",
      "--strict" in _p_sh and "STRICT_MODE" in _p_sh,
      "run-pipeline.sh lacks --strict / STRICT_MODE")
check("pipeline-strict:ps1-flag", "[switch]$Strict" in _p_ps1,
      "run-pipeline.ps1 lacks [switch]$Strict")
check("pipeline-strict:sh-no-swallow",
      '"${skills_cmd[@]}" || true' not in _p_sh
      and '"claude-code" "codex" "antigravity-ide" || true' not in _p_sh,
      "run-pipeline.sh still swallows a stage failure with || true")
check("pipeline-strict:tools-strict",
      '"--strict"' in _p_sh and '"--strict"' in _p_ps1,
      "pipeline does not invoke sync-skills/doc-impact with --strict")
check("pipeline-strict:warn-status",
      'SUMMARY_STATUS+=("WARN")' in _p_sh
      and 'summaryStatus += "WARN"' in _p_ps1,
      "pipeline summary cannot print WARN")
_sync_src = (ROOT / "tools" / "sync-skills.py").read_text(encoding="utf-8")
_doc_src = (ROOT / "tools" / "doc-impact.py").read_text(encoding="utf-8")
check("pipeline-strict:tools-exit-codes",
      "0 always" not in _sync_src and "0 always" not in _doc_src
      and "strict_exit_code" in _sync_src and "strict_exit_code" in _doc_src,
      "sync-skills.py / doc-impact.py still claim exit 0 always")

# --- 3m. Comet supply-chain pin (Phase 2, 2-2) ---
# The pinned version was measured at implementation time
# (`npm view @rpamis/comet version` -> 0.5.1 on 2026-10-28; git tag 0.5.1
# is the repo HEAD). The lock is the record; both deploy scripts must agree
# with it, and no bare (unversioned) `npm install -g @rpamis/comet` may
# remain. tools/check-comet.py is the runtime gate for the same pin.
import re as _re3
_comet_lock = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8-sig"))
_comet_meta = _comet_lock.get("skills", {}).get("comet", {})
_comet_pin = _comet_meta.get("npmVersion", "")
check("comet-pin:lock",
      bool(_comet_pin) and bool(_comet_meta.get("pinnedCommit"))
      and bool(_comet_meta.get("pinnedAt"))
      and bool(re.fullmatch(r"[0-9a-f]{40}", _comet_meta.get("pinnedCommit", ""))),
      f"comet lock entry lacks npmVersion/pinnedCommit(40-hex)/pinnedAt: {_comet_meta}")
_deploy_sh_txt = (ROOT / "deploy-agents.sh").read_text(encoding="utf-8")
_deploy_ps1_txt = (ROOT / "deploy-agents.ps1").read_text(encoding="utf-8-sig")
_sh_pin = _re3.search(r'COMET_NPM_VERSION="([^"]+)"', _deploy_sh_txt)
_ps1_pin = _re3.search(r'\$script:CometNpmVersion = "([^"]+)"', _deploy_ps1_txt)
check("comet-pin:scripts-agree-with-lock",
      bool(_sh_pin) and bool(_ps1_pin)
      and _sh_pin.group(1) == _comet_pin and _ps1_pin.group(1) == _comet_pin,
      f"deploy pin mismatch: sh={_sh_pin.group(1) if _sh_pin else None} "
      f"ps1={_ps1_pin.group(1) if _ps1_pin else None} lock={_comet_pin}")
check("comet-pin:no-bare-install",
      _re3.search(r"install -g @rpamis/comet(?!@)", _deploy_sh_txt) is None
      and _re3.search(r"install -g @rpamis/comet(?!@)", _deploy_ps1_txt) is None,
      "bare `npm install -g @rpamis/comet` (unversioned) still present")
check("comet-pin:check-tool-exists",
      (ROOT / "tools" / "check-comet.py").is_file(),
      "tools/check-comet.py missing")
import subprocess as _sp3
try:
    _cc = _sp3.run([sys.executable, str(ROOT / "tools" / "check-comet.py"), "--json"],
                   capture_output=True, text=True, timeout=60)
    _cc_ok = _cc.returncode == 0 and json.loads(_cc.stdout).get("ok") is True
except Exception as _cc_exc:  # noqa: BLE001
    _cc_ok = False
    _cc = None
check("comet-pin:check-tool-passes", _cc_ok,
      "tools/check-comet.py does not pass on this repo")

# --- 3m1. OCR CLI pin (Phase 6, 6-2) ---
# Mirrors comet-pin: the open-code-review *skill* is authored in-repo
# (local), but the optional OCR *CLI* it can delegate to is pinned by
# version in the lock entry (npmVersion + pinnedAt) and in both deploy
# scripts (OCR_NPM_VERSION / $script:OcrNpmVersion). No bare (unversioned)
# `npm install -g @alibaba-group/open-code-review` may remain.
_ocr_meta = _comet_lock.get("skills", {}).get("open-code-review", {})
_ocr_pin = _ocr_meta.get("npmVersion", "")
check("ocr-pin:lock",
      bool(_ocr_pin) and bool(_ocr_meta.get("pinnedAt"))
      and bool(_ocr_meta.get("pinnedFrom")),
      f"open-code-review lock entry lacks npmVersion/pinnedAt/pinnedFrom: {_ocr_meta}")
_sh_ocr = _re3.search(r'OCR_NPM_VERSION="([^"]+)"', _deploy_sh_txt)
_ps1_ocr = _re3.search(r'\$script:OcrNpmVersion = "([^"]+)"', _deploy_ps1_txt)
check("ocr-pin:scripts-agree-with-lock",
      bool(_sh_ocr) and bool(_ps1_ocr)
      and _sh_ocr.group(1) == _ocr_pin and _ps1_ocr.group(1) == _ocr_pin,
      f"deploy pin mismatch: sh={_sh_ocr.group(1) if _sh_ocr else None} "
      f"ps1={_ps1_ocr.group(1) if _ps1_ocr else None} lock={_ocr_pin}")
check("ocr-pin:no-bare-install",
      _re3.search(r"install -g @alibaba-group/open-code-review(?!@)", _deploy_sh_txt) is None
      and _re3.search(r"install -g @alibaba-group/open-code-review(?!@)", _deploy_ps1_txt) is None,
      "bare `npm install -g @alibaba-group/open-code-review` (unversioned) still present")

# --- 3m1b. Docs pin guard (Phase 6, 6-2) ---
# The EN+ZH Panorama Guides are repo-authored install instructions: they
# must show only pinned installs — versioned npm packages and
# download-then-verify installer flows. No bare `npm install -g <pkg>`
# (unversioned) and no piped `curl | sh` / `irm | iex` install may appear.
# FR/DE/ZH-TW are translations: tracked stale in docs/internal/i18n-status.md,
# not hard-failed here (Phase 4, 4-2). The vendored comet skill
# (.agents/skills/comet/SKILL.md) still shows an unversioned comet install
# in upstream text — editing it would break the lock (§5); recorded as a
# known gap in D22, not scanned here.
_GUIDE_EN = (ROOT / "docs" / "guides" / "Tools Practical Usage and Skills Panorama Guide.md").read_text(encoding="utf-8")
_GUIDE_ZH = (ROOT / "docs" / "guides" / "Tools Practical Usage and Skills Panorama Guide.zh.md").read_text(encoding="utf-8")
for _gname, _gtxt in (("EN", _GUIDE_EN), ("ZH", _GUIDE_ZH)):
    check(f"docs-pin:{_gname}-no-bare-npm",
          _re3.search(r"install -g @rpamis/comet(?!@)", _gtxt) is None
          and _re3.search(r"install -g @alibaba-group/open-code-review(?!@)", _gtxt) is None
          and _re3.search(r"i -g @colbymchenry/codegraph(?!@)", _gtxt) is None
          and _re3.search(r"install -g @colbymchenry/codegraph(?!@)", _gtxt) is None,
          f"{_gname} Panorama Guide still shows a bare (unversioned) npm install")
    check(f"docs-pin:{_gname}-no-piped-install",
          "install.sh | sh" not in _gtxt and "install.ps1 | iex" not in _gtxt,
          f"{_gname} Panorama Guide still shows a piped curl|sh / irm|iex install")

# --- 3m2. Pinned installer scripts (Phase 2, 2-2) ---
# codegraph/rtk installers are pinned by upstream commit + SHA256 of the
# installer at that commit (measured 2026-10-28). The lock is the record;
# both deploy scripts must carry the same URL + hash, and no piped
# `curl | sh` / `irm | iex` install may remain in either script.
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
for _name in ("codegraph", "rtk"):
    _m = _comet_lock.get("skills", {}).get(_name, {})
    check(f"installer-pin:{_name}-lock",
          bool(_HEX40.match(_m.get("pinnedCommit", "")))
          and bool(_HEX64.match(_m.get("installerSha256", "")))
          and _m.get("pinnedCommit", "") in _m.get("installerUrl", "")
          and bool(_m.get("pinnedAt")),
          f"{_name} lock entry lacks pinnedCommit/installerSha256/installerUrl/pinnedAt")
    check(f"installer-pin:{_name}-sh-agrees",
          _m.get("installerUrl", "") in _deploy_sh_txt
          and _m.get("installerSha256", "") in _deploy_sh_txt,
          f"deploy-agents.sh installer URL/SHA disagrees with lock for {_name}")
check("installer-pin:codegraph-ps1-agrees",
      _comet_lock["skills"]["codegraph"].get("installerUrlPs1", "") in _deploy_ps1_txt
      and _comet_lock["skills"]["codegraph"].get("installerSha256Ps1", "") in _deploy_ps1_txt,
      "deploy-agents.ps1 codegraph installer URL/SHA disagrees with lock")
check("installer-pin:no-piped-install",
      "codegraph/main/install.sh | sh" not in _deploy_sh_txt
      and "rtk/master/install.sh | sh" not in _deploy_sh_txt
      and "install.ps1 | iex" not in _deploy_ps1_txt
      and "Invoke-Expression (Invoke-RestMethod" not in _deploy_ps1_txt,
      "piped curl|sh / irm|iex install still present in a deploy script")

# --- 3n. Hook lifecycle coverage (Phase 2, 2-3) ---
# .claude/settings.json must wire all five Claude Code hook events, and the
# hook scripts they point at must exist. The Stop hook came in Phase 1;
# SessionStart and PostToolUse are Phase 2.
_settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
_hooks = _settings.get("hooks", {})
for _event in ("PreToolUse", "Stop", "SessionStart", "PostToolUse",
               "UserPromptSubmit"):
    check(f"hooks-lifecycle:{_event}-wired",
          isinstance(_hooks.get(_event), list) and len(_hooks[_event]) > 0,
          f".claude/settings.json lacks {_event} hooks")
_settings_text = json.dumps(_hooks)
for _script in ("guard.mjs", "guard-write.mjs", "guard-feature-list.mjs",
                "stop-gate.mjs", "session-start.mjs", "post-tool-use.mjs"):
    check(f"hooks-lifecycle:script-{_script}",
          (ROOT / ".claude" / "hooks" / _script).is_file(),
          f".claude/hooks/{_script} missing")
check("hooks-lifecycle:session-start-wired",
      "session-start.mjs" in _settings_text,
      "settings.json does not register session-start.mjs")
check("hooks-lifecycle:post-tool-use-wired",
      "post-tool-use.mjs" in _settings_text,
      "settings.json does not register post-tool-use.mjs")

# --- 3o. Guard graded hardening (Phase 2, 2-4) ---
# guard.mjs must expand command substitutions and eval/sh -c indirection
# (not a blanket fail-closed: parse failures stay fail-open but logged).
_guard = (ROOT / ".claude" / "hooks" / "guard.mjs").read_text(encoding="utf-8")
check("guard:expands-substitutions",
      "rewriteSubstitutions" in _guard and "GIT_TOKEN" in _guard,
      "guard.mjs lacks command-substitution expansion")
check("guard:expands-indirection",
      '"eval"' in _guard and '"-c"' in _guard and "MAX_EXPAND_DEPTH" in _guard,
      "guard.mjs lacks eval/sh -c indirection expansion")
check("guard:parse-failure-logged",
      "parse failed" in _guard,
      "guard.mjs parse failure is silent (must log to stderr)")
_hooks_test = (ROOT / "tests" / "hooks.test.mjs").read_text(encoding="utf-8")
check("guard:which-git-test",
      "$(which git)" in _hooks_test and "sh -c" in _hooks_test,
      "hooks.test.mjs lacks substitution/indirection bypass tests")

# --- 3p. Cost ledger (Phase 2, 2-5) ---
# tools/cost-ledger.py records deterministic proxy metrics (no token ledger:
# no host exposes a programmatic token API — see token-adapters.md).
# Over-budget alerts + records, never auto-stops.
_ledger = (ROOT / "tools" / "cost-ledger.py").read_text(encoding="utf-8")
check("cost-ledger:tool-exists",
      (ROOT / "tools" / "cost-ledger.py").is_file(),
      "tools/cost-ledger.py missing")
check("cost-ledger:subcommands",
      all(s in _ledger for s in ("init-budget", "check-budget", '"record"', '"summary"')),
      "cost-ledger.py lacks one of init-budget/record/summary/check-budget")
check("cost-ledger:budget-defaults",
      all(k in _ledger for k in ("max_runs_per_day", "max_tool_calls_per_day",
                                 "max_verify_failures_per_day",
                                 "max_overrides_per_day",
                                 "max_stage_duration_ms")),
      "cost-ledger.py lacks the five proxy-metric budget limits")
check("cost-ledger:no-auto-stop",
      "never auto-stops" in _ledger.lower() or "never auto-stop" in _ledger.lower(),
      "cost-ledger.py does not state the no-auto-stop rule")
check("cost-ledger:pipeline-records",
      "cost-ledger.py" in _p_sh and "cost-ledger.py" in _p_ps1,
      "run-pipeline.sh/.ps1 do not record ledger events per stage")
check("cost-ledger:token-adapters-doc",
      (ROOT / "docs" / "internal" / "token-adapters.md").is_file(),
      "docs/internal/token-adapters.md missing")
check("cost-ledger:own-budget",
      (ROOT / "gate" / "cost-budget.json").is_file(),
      "this repo's own gate/cost-budget.json missing (dogfood init-budget)")

# --- 3q. Benchmarks & evaluation (Phase 3, v3 §4.5) ---
# Framework first, then measured runs: 4 tasks (fixed start commit,
# acceptance, budget), rubric (six dimensions), calibration (3+ rounds),
# results that recompute to the baseline report. Unmeasured cells must be
# marked unmeasured, never filled with invented numbers.
_EVAL_START = "2e583970fb952158ad83617fe436534abd38295d"
_eval_tasks = sorted((ROOT / "eval" / "tasks").glob("*/task.md"))
check("eval:four-tasks", len(_eval_tasks) == 4, f"expected 4 task specs, found {len(_eval_tasks)}")
for _spec in _eval_tasks:
    _text = _spec.read_text(encoding="utf-8")
    _tid = _spec.parent.name
    check(f"eval:{_tid}-fields",
          all(f in _text for f in ("start_commit", "acceptance", "budget_time", "budget_rounds")),
          f"{_tid}/task.md lacks a required field")
    check(f"eval:{_tid}-start-commit", _EVAL_START in _text,
          f"{_tid}/task.md start_commit != {_EVAL_START}")
    check(f"eval:{_tid}-solution", (_spec.parent / "solution.patch").is_file(),
          f"{_tid}/solution.patch missing")
_rubric = (ROOT / "eval" / "rubric.md").read_text(encoding="utf-8")
check("eval:rubric-six-dimensions",
      all(d in _rubric for d in ("Correctness", "Verification", "Scope discipline",
                                 "Reliability", "Maintainability", "Handover readiness")),
      "eval/rubric.md lacks one of the six dimensions")
check("eval:rubric-rerun-rule", "re-running" in _rubric,
      "eval/rubric.md does not require re-running acceptance")
_calib = (ROOT / "eval" / "calibration.md").read_text(encoding="utf-8")
check("eval:calibration-rounds", _calib.count("## Round ") >= 3,
      "eval/calibration.md has fewer than 3 recorded rounds")
check("eval:calibration-not-stable",
      "NOT yet `stable`" in _calib or "not `stable`" in _calib,
      "calibration claims stable without a live second-judge round")
check("eval:workflow-exists",
      (ROOT / ".github" / "workflows" / "eval-regression.yml").is_file(),
      ".github/workflows/eval-regression.yml missing")
_wf = (ROOT / ".github" / "workflows" / "eval-regression.yml").read_text(encoding="utf-8")
check("eval:workflow-triggers",
      "workflow_dispatch" in _wf and "schedule" in _wf,
      "eval-regression.yml lacks manual + monthly triggers")
check("eval:quality-score-exists",
      (ROOT / "QUALITY_SCORE.md").is_file(), "QUALITY_SCORE.md missing")
_qs = (ROOT / "QUALITY_SCORE.md").read_text(encoding="utf-8")
check("eval:quality-marks-unmeasured", "unmeasured" in _qs.lower(),
      "QUALITY_SCORE.md does not mark unmeasured cells")
check("eval:quality-no-upstream-number", "76.8" not in _qs,
      "QUALITY_SCORE.md quotes the upstream -76.8% token number")
_eval_result_files = sorted((ROOT / "eval" / "results").glob("*.json"))
_required_result_fields = {"task", "arm", "rep", "start_commit", "host", "model",
                           "started_epoch", "ended_epoch", "duration_s", "rounds",
                           "verify_attempts", "interventions", "outcome", "false_completion"}
for _rf in _eval_result_files:
    try:
        _rec = json.loads(_rf.read_text(encoding="utf-8"))
        _missing = _required_result_fields - set(_rec)
    except Exception as e:  # noqa: BLE001
        _missing = {f"parse error: {e}"}
    check(f"eval:result-{_rf.name}", not _missing, f"missing fields: {sorted(_missing)}")
_check_results = subprocess.run(
    [sys.executable, str(ROOT / "eval" / "check-results.py")],
    capture_output=True, text=True, cwd=ROOT)
check("eval:check-results-passes", _check_results.returncode == 0,
      _check_results.stdout.strip().splitlines()[-1] if _check_results.stdout else "check-results.py failed")
_bench_smoke = subprocess.run(
    ["bash", str(ROOT / "eval" / "run-bench.sh"), "smoke"],
    capture_output=True, text=True, cwd=ROOT)
check("eval:bench-smoke-passes", _bench_smoke.returncode == 0,
      "eval/run-bench.sh smoke failed")

# --- 3r. Deploy profiles (Phase 4, 4-1) ---
# skills-profiles.json is the single source of truth for profile
# membership. Assertions: default is minimal; minimal <= 10; standard is a
# strict superset of minimal; full is exactly every skill directory on
# disk; heavy skills (docx, brainstorming) are in full only; every listed
# skill exists on disk; the EN+ZH Skills Usage Guides' tier sections
# (between <!-- profiles:begin --> / <!-- profiles:end -->) list exactly
# the profile members.
import json as _json3r
_profiles_path = ROOT / "skills-profiles.json"
try:
    _profiles_data = _json3r.loads(_profiles_path.read_text(encoding="utf-8"))
except Exception as e:  # noqa: BLE001
    _profiles_data = {}
    check("profiles:file-valid", False, f"skills-profiles.json unreadable: {e}")
_profiles = _profiles_data.get("profiles", {}) if isinstance(_profiles_data, dict) else {}
check("profiles:default-minimal", _profiles_data.get("default") == "minimal",
      f"default profile is {_profiles_data.get('default')!r}, expected 'minimal'")
_disk_skills = {p.name for p in (ROOT / ".agents" / "skills").iterdir() if p.is_dir()}
for _pname in ("minimal", "standard", "full"):
    _plist = _profiles.get(_pname, {}).get("skills", []) if isinstance(_profiles.get(_pname), dict) else []
    check(f"profiles:{_pname}-exists", bool(_plist), f"profile {_pname} missing or empty")
    check(f"profiles:{_pname}-no-duplicates", len(_plist) == len(set(_plist)),
          f"profile {_pname} has duplicate entries")
    _missing = [s for s in _plist if s not in _disk_skills]
    check(f"profiles:{_pname}-on-disk", not _missing,
          f"profile {_pname} lists skills not on disk: {_missing}")
_min = _profiles.get("minimal", {}).get("skills", [])
_std = _profiles.get("standard", {}).get("skills", [])
_full = _profiles.get("full", {}).get("skills", [])
check("profiles:minimal-le-10", len(_min) <= 10, f"minimal has {len(_min)} skills, must be <= 10")
check("profiles:standard-superset-minimal", set(_min) < set(_std),
      "standard must be a strict superset of minimal")
check("profiles:full-is-all", set(_full) == _disk_skills,
      f"full must be exactly the {len(_disk_skills)} skill dirs on disk")
check("profiles:heavy-in-full-only",
      set(_profiles.get("full", {}).get("heavy", [])) == {"brainstorming", "docx"}
      and not (set(_min) | set(_std)) & {"brainstorming", "docx"},
      "heavy skills (docx, brainstorming) must be listed in full.heavy and in no smaller profile")
_deploy_sh_txt = (ROOT / "deploy-agents.sh").read_text(encoding="utf-8")
_deploy_ps1_txt = (ROOT / "deploy-agents.ps1").read_text(encoding="utf-8-sig")
check("profiles:sh-default-minimal", 'PROFILE="minimal"' in _deploy_sh_txt,
      "deploy-agents.sh default PROFILE is not minimal")
check("profiles:ps1-default-minimal", '$SkillProfile = "minimal"' in _deploy_ps1_txt,
      "deploy-agents.ps1 default SkillProfile is not minimal")
for _guide in ("docs/guides/Skills Usage Guide.md", "docs/guides/Skills Usage Guide.zh.md"):
    _gtext = (ROOT / _guide).read_text(encoding="utf-8")
    _m = re.search(r"<!-- profiles:begin -->(.*?)<!-- profiles:end -->", _gtext, re.S)
    check(f"profiles:guide-section-{_guide}", _m is not None,
          f"{_guide} lacks the <!-- profiles:begin/end --> tier section")
    if _m:
        _sec = _m.group(1)
        _min_sec = re.search(r"### minimal.*?(?=###|\Z)", _sec, re.S | re.I)
        _std_sec = re.search(r"### standard.*?(?=###|\Z)", _sec, re.S | re.I)
        _min_listed = {s for s in re.findall(r"`([a-z][a-z0-9-]+)`", _min_sec.group(0))
                       if s in _disk_skills} if _min_sec else set()
        _std_listed = {s for s in re.findall(r"`([a-z][a-z0-9-]+)`", _std_sec.group(0))
                       if s in _disk_skills} if _std_sec else set()
        check(f"profiles:guide-minimal-{_guide}", _min_listed == set(_min),
              f"{_guide} minimal subsection lists {_min_listed}, want {set(_min)}")
        check(f"profiles:guide-standard-{_guide}",
              _std_listed == set(_std) - set(_min),
              f"{_guide} standard subsection lists {_std_listed}, want {sorted(set(_std) - set(_min))}")
        check(f"profiles:guide-full-{_guide}", "40" in _sec,
              f"{_guide} tier section does not state the full profile has 40 skills")

# --- 3s. Loop layer (Phase 5, v3 §4.6) ---
# tools/loop.py (stdlib only) + templates/loop/ (goal / loop-state / graph,
# EN+ZH) + worked example graph + run records. The graph template carries
# defaults (60 s timeout), so graph-validate must pass on it as well as on
# the worked example. The smoke runs a real goal loop and a real timeout.
_LOOP_TEMPLATES = {
    "goal.template.md": ("## Goal", "## Verification", "## Stop conditions"),
    "goal.template.zh.md": ("## 目标", "## 验证方式", "## 停止条件"),
    "loop-state.template.md": ("## Rounds", "## Approval"),
    "loop-state.template.zh.md": ("## 各轮", "## 批准"),
    "graph.template.md": ("## Nodes", "## Edges", "## Approval", "## Timeout",
                          "## Fan-out"),
    "graph.template.zh.md": ("## 节点", "## 边", "## 批准", "## 超时",
                             "## 并行展开"),
}
for _lt, _sections in _LOOP_TEMPLATES.items():
    _lp = ROOT / "templates" / "loop" / _lt
    check(f"loop:template-{_lt}-exists", _lp.is_file(), f"templates/loop/{_lt} missing")
    if _lp.is_file():
        _ltext = _lp.read_text(encoding="utf-8")
        check(f"loop:template-{_lt}-sections",
              all(s in _ltext for s in _sections),
              f"templates/loop/{_lt} lacks a required section")
_LOOP_ALLOWED_IMPORTS = {"argparse", "json", "os", "re", "shutil",
                         "subprocess", "sys", "time", "datetime"}
_loop_tree = ast.parse((ROOT / "tools" / "loop.py").read_text(encoding="utf-8"))
_loop_imports = set()
for _node in ast.walk(_loop_tree):
    if isinstance(_node, ast.Import):
        _loop_imports.update(a.name.split(".")[0] for a in _node.names)
    elif isinstance(_node, ast.ImportFrom):
        _loop_imports.add((_node.module or "").split(".")[0])
check("loop:stdlib-only", _loop_imports <= _LOOP_ALLOWED_IMPORTS,
      f"tools/loop.py imports non-stdlib: {sorted(_loop_imports - _LOOP_ALLOWED_IMPORTS)}")
_loop_help = subprocess.run([sys.executable, str(ROOT / "tools" / "loop.py"), "--help"],
                            capture_output=True, text=True)
check("loop:help-exits-0", _loop_help.returncode == 0, "loop.py --help failed")
for _g in ("templates/loop/graph.template.md", "docs/internal/phase5-graph.md"):
    _gv = subprocess.run([sys.executable, str(ROOT / "tools" / "loop.py"),
                          "graph-validate", "--graph", str(ROOT / _g)],
                         capture_output=True, text=True)
    check(f"loop:graph-validate-{Path(_g).name}", _gv.returncode == 0,
          f"graph-validate failed on {_g}")
_loop_tmp = tempfile.mkdtemp(prefix="loop-smoke-")
_loop_goal = os.path.join(_loop_tmp, "goal.md")
Path(_loop_goal).write_text("# Goal\n", encoding="utf-8")
_loop_init = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "loop.py"), "init",
     "--root", os.path.join(_loop_tmp, "run"), "--goal-file", _loop_goal,
     "--kind", "goal", "--max-rounds", "3", "--consecutive-passes", "2",
     "--timeout", "5"],
    capture_output=True, text=True)
_loop_run = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "loop.py"), "goal-loop",
     "--root", os.path.join(_loop_tmp, "run"), "--maker", "true", "--verify", "true"],
    capture_output=True, text=True)
check("loop:smoke-goal-loop",
      _loop_init.returncode == 0 and _loop_run.returncode == 0,
      "loop.py goal-loop smoke (true/true) failed")
_loop_to_init = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "loop.py"), "init",
     "--root", os.path.join(_loop_tmp, "run3"), "--goal-file", _loop_goal,
     "--kind", "goal", "--max-rounds", "1", "--consecutive-passes", "1",
     "--timeout", "1"],
    capture_output=True, text=True)
_loop_to_run = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "loop.py"), "goal-loop",
     "--root", os.path.join(_loop_tmp, "run3"), "--maker", "true", "--verify", "sleep 30"],
    capture_output=True, text=True, timeout=30)
_to_events = Path(_loop_tmp, "run3", "loop-events.jsonl").read_text(encoding="utf-8") \
    if Path(_loop_tmp, "run3", "loop-events.jsonl").is_file() else ""
check("loop:smoke-timeout-enforced",
      _loop_to_init.returncode == 0 and _loop_to_run.returncode != 0
      and '"timeout"' in _to_events,
      "loop.py did not record a timeout for a verify past its timeout")
_decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
check("loop:d21-present", "## D21" in _decisions,
      "DECISIONS.md lacks D21 (Phase 5 L14 + four questions)")
_record = (ROOT / "docs" / "internal" / "phase5-loops.md").read_text(encoding="utf-8")
check("loop:record-sections",
      all(s in _record for s in ("## Goal Loop", "## Maker-Checker Loop",
                                 "## Timeout rule", "## Verdict")),
      "docs/internal/phase5-loops.md lacks a required section")
_pass_gate_test = subprocess.run(
    [sys.executable, str(ROOT / "tests" / "pass_gate_test.py")],
    capture_output=True, text=True)
check("loop:pass-gate-test-passes", _pass_gate_test.returncode == 0,
      "tests/pass_gate_test.py failed")

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
    ("comet.config.yaml", "comet.config.yaml", "Comet config template sync"),
    ("AiMemoryInit", "ai-memory-init", "optional ai-memory init flag"),
    ("templates/ai-memory.toml.example", ".ai-memory.toml.example", "ai-memory config template sync"),
    ("LivingDocScaffold", "living-doc-scaffold", "living documentation directory scaffold"),
    ("Open Code Review CLI", "Open Code Review CLI", "optional OCR CLI detection"),
    ("review-sensitive-paths.json", "review-sensitive-paths.json", "sensitive paths config sync"),
    ("sync-skills.py", "sync-skills.py", "external skill sync in update flow"),
    ("Comet CLI", "Comet CLI", "optional Comet CLI detection"),
    ("Resolve-TemplateFile", "resolve_template", "multilingual template resolution"),
    ("Prompt-InteractiveWizard", "prompt_interactive_wizard", "interactive terminal wizard"),
    ("--check-only", "--check-only", "pipeline read-only check mode"),
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
    ("PROJECT_CONTEXT.md", "PROJECT_CONTEXT.md", "project memory scaffold (PROJECT_CONTEXT/SESSION_STATE)"),
    ("Pipeline", "run-pipeline", "pipeline runner integration"),
    ("Agent Harness local runtime & machine-specific ignores", "Agent Harness local runtime & machine-specific ignores", "target project gitignore scaffold"),
    ("target-auto-create", "target-auto-create", "auto-create missing target directory"),
    ("IncludeHeavySkills", "include-heavy-skills", "opt-in heavy skills (docx, brainstorming)"),
    ("GateDeploy", "gate-deploy", "gate layer deployment (pass-gate.py + schema + init template)"),
    ("SkillProfile", "--profile", "deployment profiles minimal/standard/full"),
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

# --- 4a2. Deploy scaffold covers all doc tiers ---
# deploy-agents.sh/.ps1 must create every DOC_TIERS directory in target projects.
# Catches six-tier migration gaps (e.g. missing management/tests) without ci.yml changes.
import re as _re2
_deploy_sh = (ROOT / "deploy-agents.sh").read_text(encoding="utf-8")
_deploy_ps1 = (ROOT / "deploy-agents.ps1").read_text(encoding="utf-8-sig")
_sh_tiers = set(_re2.search(
    r"for doc_subdir in ([a-z ]+); do", _deploy_sh).group(1).split())
_ps1_tiers = set(_re2.findall(
    r'\$docSubdirs = @\(([^)]+)\)', _deploy_ps1)[0].replace('"', "").replace(",", " ").split())
for _tier in DOC_TIERS:
    check(f"deploy-scaffold:sh-{_tier}", _tier in _sh_tiers,
          f"deploy-agents.sh doc scaffold missing tier: {_tier}")
    check(f"deploy-scaffold:ps1-{_tier}", _tier in _ps1_tiers,
          f"deploy-agents.ps1 doc scaffold missing tier: {_tier}")

# --- 4b. run-pipeline script parity ---
# Ensures run-pipeline.ps1 and run-pipeline.sh maintain feature parity across stages.
PIPELINE_PARITY = [
    ("deploy-agents", "deploy-agents", "pipeline stage 1: deploy-agents"),
    ("setup-ai-memory", "setup-ai-memory", "pipeline stage 2: setup-ai-memory"),
    ("sync-skills.py", "sync-skills.py", "pipeline stage 3: sync-skills.py"),
    ("doc-impact.py", "doc-impact.py", "pipeline stage 4: doc-impact.py"),
    ("comet doctor", "comet doctor", "pipeline comet doctor health check"),
    ("comet status", "comet status", "pipeline comet status probe"),
    ("comet.config.yaml", "comet.config.yaml", "pipeline comet config scaffold"),
    ("PROJECT_CONTEXT.md", "PROJECT_CONTEXT.md", "pipeline project context scaffold"),
    ("SESSION_STATE.md", "SESSION_STATE.md", "pipeline session state scaffold"),
    ("BriefProbe", "brief-probe", "pipeline brief probe mode"),
    ("CheckOnly", "check-only", "pipeline check-only read-only mode"),
    ("ApplySkills", "apply-skills", "pipeline apply-skills flag"),
    ("Strict", "strict", "pipeline strict mode (fail vs warn)"),
    ("WARN", "WARN", "pipeline advisory WARN status"),
    ("cost-ledger.py", "cost-ledger.py", "pipeline cost ledger stage recording"),
    ("gitignore.snippet", "gitignore.snippet", "pipeline gitignore snippet scaffold"),
    ("Resolve-GlobalTemplate", "resolve_global_template", "pipeline global template resolution"),
]
p_ps1 = (ROOT / "run-pipeline.ps1").read_text(encoding="utf-8-sig")
p_sh = (ROOT / "run-pipeline.sh").read_text(encoding="utf-8")
for ps1_marker, sh_marker, feature in PIPELINE_PARITY:
    in_ps1 = ps1_marker in p_ps1
    in_sh = sh_marker in p_sh
    if not in_ps1 and not in_sh:
        print(f"[SKIP] pipeline-parity:{feature} (not present on this branch)")
        continue
    detail = ""
    if in_ps1 and not in_sh:
        detail = f"'{sh_marker}' missing in run-pipeline.sh"
    elif in_sh and not in_ps1:
        detail = f"'{ps1_marker}' missing in run-pipeline.ps1"
    check(f"pipeline-parity:{feature}", in_ps1 == in_sh, detail)

# --- 5. skills-lock.json consistency ---
# Every skill directory must have a lock entry (provenance metadata).
# Lock entries without a directory are allowed only for meta-entries
# (suites, not single skills), marked explicitly with "meta": true in the
# lock (Phase 2, 2-2c) — the marker, not a hardcoded name list, is the rule.
lock_data = json.loads((ROOT / "skills-lock.json").read_text(encoding="utf-8-sig"))
META_ENTRIES = {n for n, m in lock_data.get("skills", {}).items()
                if m.get("meta") is True}
check("lock:meta-entries-exact", META_ENTRIES == {"openspec", "superpowers"},
      f"meta entries must be exactly openspec + superpowers, got: {sorted(META_ENTRIES)}")
lock_skills = set(lock_data["skills"])
dir_skills = {p.name for p in (ROOT / ".agents" / "skills").iterdir() if p.is_dir()}
missing_lock = sorted(dir_skills - lock_skills)
check("lock:covers-all-dirs", not missing_lock,
      f"skill dirs without lock entry: {missing_lock}")
orphan_lock = sorted(lock_skills - dir_skills - META_ENTRIES)
check("lock:no-orphans", not orphan_lock,
      f"lock entries without skill dir: {orphan_lock}")

# Every skill must declare a domain (namespace grouping for scoped loading).
# Valid domains: openspec | superpowers | local | document | integration | utility
SKILL_DOMAINS = {"openspec", "superpowers", "local", "document", "integration", "utility"}
for name, meta in sorted(lock_data.get("skills", {}).items()):
    domain = meta.get("domain")
    check(f"lock-domain:{name}", domain in SKILL_DOMAINS,
          f"skill {name} has invalid/missing domain: {domain!r}")

# Verify computedHash matches actual local file content for all locked skills
for name, meta in sorted(lock_data.get("skills", {}).items()):
    expected_hash = meta.get("computedHash")
    if not expected_hash:
        continue
    skill_file = ROOT / ".agents" / "skills" / name / "SKILL.md"
    if not skill_file.is_file():
        continue
    actual_hash = hashlib.sha256(skill_file.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    check(f"lock-hash:{name}", actual_hash == expected_hash,
          f"computedHash mismatch for {name}: lock={expected_hash[:8]}, disk={actual_hash[:8]}")

# --- 5b. skills-lock history consistency ---
# Guards against silent lock edits: if a skill's computedHash changed vs the
# base ref, the corresponding SKILL.md must also have changed in the same diff.
# A hash-only change means someone edited the lock to cover a file state that
# was never reviewed — the git history is the audit trail, so force them together.
import subprocess as _sp
import os as _os

def _git_out(args):
    try:
        r = _sp.run(["git"] + args, capture_output=True, text=True,
                    cwd=str(ROOT), timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

_lock_base = _os.environ.get("LOCK_CHECK_BASE")
if not _lock_base:
    # Prefer origin/main, fall back to previous commit; skip if neither exists.
    for _cand in ("origin/main", "HEAD~1"):
        if _git_out(["rev-parse", "--verify", "--quiet", _cand]):
            _lock_base = _cand
            break

if _lock_base:
    _prev_lock_raw = _git_out(["show", f"{_lock_base}:skills-lock.json"])
    _changed_raw = _git_out(["diff", "--name-only", f"{_lock_base}...HEAD"]) or ""
    _uncommitted = _git_out(["diff", "--name-only"]) or ""
    _staged = _git_out(["diff", "--cached", "--name-only"]) or ""
    _changed_files = set(_changed_raw.split()) | set(_uncommitted.split()) | set(_staged.split())
    _changed_files.discard("")
    if _prev_lock_raw:
        try:
            _prev_skills = json.loads(_prev_lock_raw).get("skills", {})
        except Exception:
            _prev_skills = None
        if _prev_skills is not None:
            _cur_skills = lock_data.get("skills", {})
            for _name in sorted(set(_cur_skills) | set(_prev_skills)):
                _cur_h = (_cur_skills.get(_name) or {}).get("computedHash")
                _prev_h = (_prev_skills.get(_name) or {}).get("computedHash")
                if _cur_h and _prev_h and _cur_h != _prev_h:
                    _skill_path = f".agents/skills/{_name}/SKILL.md"
                    check(f"lock-history:{_name}",
                          _skill_path in _changed_files,
                          f"computedHash for {_name} changed vs {_lock_base} but "
                          f"{_skill_path} did not — silent lock edit?")
else:
    print("  [warn] lock-history: no base ref found, check skipped")

# --- 5c. True lock: every pin must resolve (Phase 6, 6-1) ---
# A lock is only a lock if every pinned entry is actually pinned. Offline
# part (no network): every github-source entry carries a 40-hex
# pinnedCommit, and every meta entry carries a pinnedCommit + a note
# explaining what it pins (D10: ghost meta entries are annotated, never
# deleted). The online part — local content == content at pinnedCommit —
# is enforced by the `sync-skills.py --check --strict` CI step (see
# .github/workflows/ci.yml), which fetches each pin from upstream.
for _name, _meta in sorted(lock_data.get("skills", {}).items()):
    if _meta.get("sourceType") == "github":
        check(f"lock-pin:{_name}",
              bool(_HEX40.match(_meta.get("pinnedCommit", ""))),
              f"github skill {_name} lacks a 40-hex pinnedCommit: "
              f"{_meta.get('pinnedCommit')!r}")
    if _meta.get("meta") is True:
        check(f"lock-pin:meta-{_name}",
              bool(_HEX40.match(_meta.get("pinnedCommit", "")))
              and bool((_meta.get("note") or "").strip()),
              f"meta entry {_name} lacks pinnedCommit and/or note")

# --- 6. Multilingual docs: EN/ZH parity + i18n status (Phase 4, 4-2) ---
# EN/ZH are the sources of truth: their ## counts must match (hard check).
# FR/DE/ZH-TW are generated products: tools/i18n-check.py enforces the
# status file (docs/internal/i18n-status.md) — an "in-sync" row must match
# its source sha, a "stale"/"frozen" row passes with a printed reminder.
# The old 16-pair symmetric H2 hard check was removed here: a translation
# being behind is tracked debt, not a CI failure (v2 4-2).
_i18n = subprocess.run(
    [sys.executable, str(ROOT / "tools" / "i18n-check.py")],
    capture_output=True, text=True, cwd=str(ROOT), timeout=60)
_i18n_tail = (_i18n.stdout.strip().splitlines() or [""])[-1]
check("i18n:status-check", _i18n.returncode == 0, _i18n_tail)
print(_i18n.stdout, end="")

# --- 7. Executable bit on entry-point scripts ---
# The GitHub contents API resets the exec bit to 100644 on every content push,
# so this guard catches the regression in CI. If it fails, run locally:
#   git update-index --chmod=+x deploy-agents.sh setup-ai-memory.sh
import subprocess
EXEC_SCRIPTS = ["deploy-agents.sh", "setup-ai-memory.sh", "run-pipeline.sh"]
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

# --- 8. Markdown internal link check ---
# Verify relative links in docs resolve to existing files.
import urllib.parse
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
# Only check these user-facing docs (not .agents/skills which are vendored)
LINK_CHECK_ROOTS = ["README.md", "README.zh.md", "README.zh-tw.md", "README.de.md",
                    "README.fr.md", "CONTRIBUTING.md", "docs/guides"]
checked_links = 0
broken_links = []
for root in LINK_CHECK_ROOTS:
    rp = ROOT / root
    files = [rp] if rp.is_file() else sorted(rp.rglob("*.md")) if rp.is_dir() else []
    for f in files:
        content = f.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(content):
            url = m.group(2).strip()
            # Skip external URLs, anchors, mailto
            if url.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Strip anchor fragment
            url_path = url.split("#")[0]
            if not url_path:
                continue
            # URL-decode (%20 etc.)
            url_path = urllib.parse.unquote(url_path)
            target = (f.parent / url_path).resolve()
            # Must be within repo
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                continue  # outside repo, skip
            checked_links += 1
            if not target.exists():
                broken_links.append(f"{f.relative_to(ROOT)} -> {url}")
for bl in broken_links[:10]:  # show first 10
    check(f"link:{bl}", False, "broken internal link")
check("link:total-checked", True, f"{checked_links} links checked, {len(broken_links)} broken")
if broken_links:
    check("link:no-broken", False, f"{len(broken_links)} broken internal links")

print()
if failures:
    print(f"{len(failures)} check(s) failed.")
    sys.exit(1)
print("All repo checks passed.")
