#!/usr/bin/env python3
"""lint-rules — rule-entry linter for agent-harness (ported from v3-yunyi).

Checks the rule *entries* (root AGENTS.md, .claude/settings.json, gate/
entry points, templates/): presence, hook wiring, schema/template
parseability, placeholder residue, dead references, translation drift,
and a line-count / hard-constraint report.

Skeleton adaptations (review 2026-10-29, D62):
- ENTRY_FILES drops yunyi's gate/harness.py and
  templates/feature_list.template.json (neither exists in this branch)
  and keeps the skeleton's gate/pass-gate.py + DECISIONS template.
- HOOK_FILES is the skeleton's six hooks (guard, guard-write,
  guard-feature-list, post-tool-use, session-start, stop-gate).
- LINT-003 checks gate/feature_list.schema.json (version 1, `items`
  list — not yunyi's `features`) plus non-empty state templates.
- LINT-004 is NEW coverage: the skeleton's existing placeholder check
  covers only docs/internal/*.md with angle-bracket markers; this rule
  covers TODO/FIXME/XXX in entry files, gate, and templates.
- LINT-005 overlaps the repo_checks Phase 0 dead-ref check by design
  (defense in depth); LINT-006 overlaps the i18n-check drift warning
  by design (linter view vs translation-tracker view).

Every rule carries source, scope, and expiry annotations:
- source: where the rule comes from (repo doc, schema, or hook file).
- scope: which paths the rule applies to.
- expiry: when the rule should be re-examined (never, or a trigger).

Exit codes: 0 = no error rule failed (warnings allowed); 2 = at least
one error rule failed. Output is one line per rule plus an info report.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENTRY_FILES = [
    "AGENTS.md",
    ".claude/settings.json",
    "gate/pass-gate.py",
    "templates/DECISIONS.template.md",
    "templates/PROJECT_CONTEXT.template.md",
    "templates/SESSION_STATE.template.md",
]

HOOK_FILES = [
    ".claude/hooks/guard.mjs",
    ".claude/hooks/guard-write.mjs",
    ".claude/hooks/guard-feature-list.mjs",
    ".claude/hooks/post-tool-use.mjs",
    ".claude/hooks/session-start.mjs",
    ".claude/hooks/stop-gate.mjs",
]

# Patterns are assembled from parts so this file does not itself contain
# the literals it scans for (otherwise lint would fail on its own source).
PLACEHOLDER_RESIDUE_RE = re.compile("TO" + "DO|FIX" + "ME|" + "X" * 3)
DEAD_NAMES = ["comet-" + "archive"]  # removed component; live refs must not remain
LIVE_SCOPE = ["AGENTS.md", "gate", "templates", ".claude"]
# Historical records may mention removed names; they are not live refs.
HISTORY_OK = ["docs/internal", "eval/calibration"]


@dataclass
class RuleResult:
    rule_id: str
    level: str  # PASS, WARN, FAIL
    detail: str


@dataclass
class Rule:
    rule_id: str
    source: str
    scope: str
    expiry: str
    severity: str  # error or warning
    check: object = field(repr=False)


def _read(root: Path, rel: str) -> str | None:
    p = root / rel
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _lines(root: Path, rel: str) -> int:
    text = _read(root, rel)
    return 0 if text is None else len(text.splitlines())


def check_entry_files(root: Path) -> RuleResult:
    missing = [f for f in ENTRY_FILES if not (root / f).is_file()]
    if missing:
        return RuleResult("LINT-001", "FAIL", f"missing entry files: {', '.join(missing)}")
    return RuleResult("LINT-001", "PASS", f"all {len(ENTRY_FILES)} entry files present")


def check_hooks_configured(root: Path) -> RuleResult:
    text = _read(root, ".claude/settings.json")
    if text is None:
        return RuleResult("LINT-002", "FAIL", ".claude/settings.json unreadable")
    try:
        settings = json.loads(text)
    except json.JSONDecodeError as e:
        return RuleResult("LINT-002", "FAIL", f".claude/settings.json invalid JSON: {e}")
    referenced: set[str] = set()
    hooks = settings.get("hooks", {})
    for _event, entries in hooks.items():
        for entry in entries if isinstance(entries, list) else []:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                cmd = hook.get("command", "") if isinstance(hook, dict) else ""
                m = re.search(r"(\.claude/hooks/\S+?\.mjs)", cmd)
                if m:
                    referenced.add(m.group(1))
    missing = sorted(f for f in HOOK_FILES if f not in referenced or not (root / f).is_file())
    if missing:
        return RuleResult("LINT-002", "FAIL",
                          f"hooks not wired or files missing: {', '.join(missing)}")
    return RuleResult("LINT-002", "PASS", f"{len(HOOK_FILES)} hooks wired in settings.json")


def check_templates_parse(root: Path) -> RuleResult:
    text = _read(root, "gate/feature_list.schema.json")
    if text is None or not text.strip():
        return RuleResult("LINT-003", "FAIL", "gate/feature_list.schema.json is empty")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return RuleResult("LINT-003", "FAIL", f"feature_list schema invalid JSON: {e}")
    # This is a JSON Schema document, not a feature_list instance: the
    # version lives in properties.version.const and the items list in
    # properties.items (yunyi's check read a template instance instead).
    props = data.get("properties", {}) if isinstance(data, dict) else {}
    version_ok = props.get("version", {}).get("const") == 1
    items_ok = props.get("items", {}).get("type") == "array"
    if not version_ok or not items_ok:
        return RuleResult("LINT-003", "FAIL",
                          "feature_list schema must pin version const==1 "
                          "and declare items as an array")
    for name in ("templates/SESSION_STATE.template.md",
                 "templates/PROJECT_CONTEXT.template.md"):
        if not (_read(root, name) or "").strip():
            return RuleResult("LINT-003", "FAIL", f"{name} is empty")
    return RuleResult("LINT-003", "PASS",
                      "feature_list schema parses (version const 1, items array)")


def check_no_placeholder_residue(root: Path) -> RuleResult:
    hits = []
    for rel in ["AGENTS.md", ".claude/settings.json"] + \
            [str(p.relative_to(root)) for p in (root / "gate").glob("*.py")] + \
            [str(p.relative_to(root)) for p in (root / "templates").glob("*.md")] + \
            [str(p.relative_to(root)) for p in (root / "templates").glob("*.json")]:
        text = _read(root, rel)
        if text and PLACEHOLDER_RESIDUE_RE.search(text):
            hits.append(rel)
    if hits:
        return RuleResult("LINT-004", "FAIL", f"placeholder-marker residue in: {', '.join(hits)}")
    return RuleResult("LINT-004", "PASS", "no placeholder markers in entry files, gate, or templates")


def check_no_dead_refs(root: Path) -> RuleResult:
    hits = []
    for scope in LIVE_SCOPE:
        base = root / scope
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = [p for p in base.rglob("*") if p.is_file()
                     and not any(h in str(p.relative_to(root)) for h in HISTORY_OK)]
        else:
            continue
        for p in files:
            text = _read(root, str(p.relative_to(root)))
            if text and any(name in text for name in DEAD_NAMES):
                hits.append(str(p.relative_to(root)))
    if hits:
        return RuleResult("LINT-005", "FAIL", f"dead references in: {', '.join(hits)}")
    return RuleResult("LINT-005", "PASS", "no live references to removed names")


def check_translation_drift(root: Path) -> RuleResult:
    drifts = []
    for stem in ("SESSION_STATE", "PROJECT_CONTEXT"):
        base = _lines(root, f"templates/{stem}.template.md")
        for variant in sorted((root / "templates").glob(f"{stem}.template.*.md")):
            n = _lines(root, f"templates/{variant.name}")
            if abs(n - base) > 5:
                drifts.append(f"{variant.name} {n} lines vs base {base}")
    if drifts:
        return RuleResult("LINT-006", "WARN", "template translation drift: " + "; ".join(drifts))
    return RuleResult("LINT-006", "PASS", "template translations within 5 lines of base")


RULES = [
    Rule("LINT-001", "repo AGENTS.md: Checks (hook tests + repo_checks)",
         "repo root entry files", "never (structural)", "error", check_entry_files),
    Rule("LINT-002", ".claude/settings.json hook wiring",
         ".claude/settings.json + .claude/hooks/", "on any hook rename", "error",
         check_hooks_configured),
    Rule("LINT-003", "gate/feature_list.schema.json (version 1, items list)",
         "gate/feature_list.schema.json + state templates",
         "on schema change", "error", check_templates_parse),
    Rule("LINT-004", "v3 6.3: placeholder residue must not ship",
         "AGENTS.md, .claude/settings.json, gate/*.py, templates/*",
         "never", "error", check_no_placeholder_residue),
    Rule("LINT-005", "v3 Phase 2: removed components must not be referenced live",
         "AGENTS.md, gate/, templates/, .claude/ (history excluded)",
         "when a component is removed", "error", check_no_dead_refs),
    Rule("LINT-006", "v3 6.4: non-EN/ZH templates are generated + spot-checked",
         "templates/*.template.*.md", "until translations are regenerated",
         "warning", check_translation_drift),
]


def entry_report(root: Path) -> list[str]:
    """Line-count + hard-constraint report (plan 6.3, informational)."""
    lines = ["entry sizes (lines):"]
    for rel in ["AGENTS.md", ".claude/settings.json", "gate/pass-gate.py",
                "gate/graph.py", "tools/loop.py"]:
        lines.append(f"  {rel}: {_lines(root, rel)}")
    guard = _read(root, ".claude/hooks/guard.mjs") or ""
    lines.append(f"hard constraints: guard.mjs deny( calls: {guard.count('deny(')}")
    return lines


def run_checks(root: Path) -> tuple[list[RuleResult], list[str]]:
    results = [rule.check(root) for rule in RULES]
    # A warning-severity rule reports WARN, never FAIL.
    fixed = []
    for rule, res in zip(RULES, results):
        if rule.severity == "warning" and res.level == "FAIL":
            res = RuleResult(res.rule_id, "WARN", res.detail)
        fixed.append(res)
    return fixed, entry_report(root)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="lint rule entries (skeleton-adapted)")
    ap.add_argument("--root", default=".", help="repo root to lint (default: .)")
    args = ap.parse_args(argv)
    root = Path(args.root)
    results, report = run_checks(root)
    for rule in RULES:
        res = next(r for r in results if r.rule_id == rule.rule_id)
        print(f"{res.level} {rule.rule_id} [{rule.severity}] "
              f"source={rule.source} scope={rule.scope} expiry={rule.expiry} — {res.detail}")
    for line in report:
        print(f"INFO {line}")
    failed = [r for r in results if r.level == "FAIL"]
    if failed:
        print(f"lint-rules: {len(failed)} error rule(s) failed", file=sys.stderr)
        return 2
    warns = [r for r in results if r.level == "WARN"]
    print(f"lint-rules: pass ({len(warns)} warning(s))" if warns else "lint-rules: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
