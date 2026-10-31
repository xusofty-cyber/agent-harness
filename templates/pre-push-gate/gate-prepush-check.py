#!/usr/bin/env python3
"""gate-prepush-check.py — host-independent gate check for pre-push / CI.

This is the core of the agent-harness pre-push / CI template gate
(templates/pre-push-gate/). It does NOT depend on any agent host, hook
system, or editor: it only needs Python 3 (stdlib) and the project's
own gate/ directory.

What it checks, in order (mirroring the repository's own CI
re-verification, tests/repo_checks.py section 3k):

  1. gate/feature_list.json exists and validates. Validation uses
     gate/pass-gate.py's own validate() when that file is importable
     (so this check and the gate cannot drift apart); otherwise it
     falls back to basic structural checks.
  2. Every `passing` item's evidence matches its verification
     command (evidence.command == verification.command), and the
     verification command exits 0 when re-run now. Items whose
     evidence carries an `override` flag are skipped here, exactly
     as in section 3k: a human override is truthful by declaration
     and visible in the event log, not re-provable by re-running.
  3. Uncommitted working-tree edits to `gate/feature_list.json`,
     `gate/events.jsonl`, or `gate/events-head.json` emit a `[WARN]`
     reminder (or fail when `--strict` is passed), because `git push`
     sends committed state rather than unstaged working-tree edits.

What it deliberately does NOT check:

  - `pass-gate.py check-clean` as a whole (build/test/start
    dimensions, temp artefacts, SESSION_STATE narrative). That check
    is run separately by the pre-push hook (as a warning by default)
    and by the CI template (as a blocking step), because a working
    tree mid-task is legitimately not handoff-clean, while a CI run
    checks committed state. Conflating the two would make the
    pre-push hook block ordinary work-in-progress pushes.

Exit codes: 0 = gate passes (or no gate/ directory is in use, in
which case the script says so and passes — it must not block
projects that never adopted the gate); 1 = a passing item's
evidence is stale or its verification now fails, or the feature
list itself is invalid (or `--strict` with dirty gate files).

Usage:
    python3 gate-prepush-check.py [--root PROJECT_ROOT] [--strict]
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ALLOWED_STATUSES = {"not_started", "in_progress", "blocked", "passing"}


def _validate_with_pass_gate(root, data):
    """Validate via gate/pass-gate.py's own validate(), or None if
    that file cannot be imported (caller falls back to basic checks)."""
    script = root / "gate" / "pass-gate.py"
    if not script.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("pass_gate", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.validate(data)
    except Exception as exc:  # noqa: BLE001 - import failure must not crash the gate
        print(f"gate-prepush-check: pass-gate.py validate() unavailable ({exc}); using basic checks")
        return None


def _basic_validate(data):
    """Structural checks used only when pass-gate.py is unavailable."""
    errors = []
    if not isinstance(data, dict):
        return ["feature_list.json is not a JSON object"]
    items = data.get("items")
    if not isinstance(items, list):
        return ["feature_list.json has no items list"]
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            errors.append("an item is not an object")
            continue
        item_id = item.get("id", "?")
        if item_id in seen:
            errors.append(f"{item_id}: duplicate id")
        seen.add(item_id)
        status = item.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{item_id}: unknown status {status!r}")
        if status == "passing":
            evidence = item.get("evidence") or {}
            if not isinstance(evidence, dict) or not evidence.get("command"):
                errors.append(f"{item_id}: passing item has no evidence.command")
            verification = item.get("verification") or {}
            if not isinstance(verification, dict) or not verification.get("command"):
                errors.append(f"{item_id}: passing item has no verification.command")
    return errors


def _dirty_gate_files(root):
    """Return list of uncommitted gate files in working tree if inside a git repo."""
    try:
        proc = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "gate/feature_list.json",
                "gate/events.jsonl",
                "gate/events-head.json",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode != 0:
            return []
        dirty = []
        for line in proc.stdout.splitlines():
            if len(line) > 3 and line[:2].strip():
                dirty.append(line[3:].strip())
        return dirty
    except Exception:  # noqa: BLE001
        return []


def main(argv):
    root = Path(".")
    strict = False
    args = list(argv)
    while args:
        if args[0] == "--root" and len(args) >= 2:
            root = Path(args[1])
            args = args[2:]
        elif args[0] == "--strict":
            strict = True
            args = args[1:]
        else:
            print(f"gate-prepush-check: unknown argument {args[0]!r}", file=sys.stderr)
            return 2

    gate_dir = root / "gate"
    list_path = gate_dir / "feature_list.json"
    if not gate_dir.exists() or not list_path.exists():
        print("gate-prepush-check: no gate/feature_list.json in use — nothing to check (PASS)")
        return 0

    try:
        data = json.loads(list_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"gate-prepush-check: FAIL — feature_list.json is not valid JSON: {exc}")
        return 1

    errors = _validate_with_pass_gate(root, data)
    if errors is None:
        errors = _basic_validate(data)
    if errors:
        print("gate-prepush-check: FAIL — feature list invalid:")
        for error in errors[:10]:
            print(f"  - {error}")
        return 1

    dirty = _dirty_gate_files(root)
    if dirty:
        print(
            f"  [WARN] uncommitted changes in {', '.join(dirty)} — "
            "git push sends committed state, not working-tree edits"
        )
        if strict:
            print("gate-prepush-check: FAIL (--strict) — commit or stash gate changes before pushing")
            return 1

    failures = []
    checked = 0
    for item in data.get("items", []):
        if item.get("status") != "passing":
            continue
        item_id = item.get("id", "?")
        evidence = item.get("evidence") or {}
        if evidence.get("override"):
            print(f"  [SKIP] {item_id}: human override (visible, not re-provable)")
            continue
        verification = item.get("verification") or {}
        command = verification.get("command", "")
        if evidence.get("command") != command:
            failures.append(f"{item_id}: evidence.command != verification.command (stale evidence)")
            continue
        if not command:
            failures.append(f"{item_id}: passing item has no verification command")
            continue
        checked += 1
        timeout = verification.get("timeout_seconds", 120)
        try:
            proc = subprocess.run(
                command, shell=True, cwd=root, timeout=timeout,
                capture_output=True, text=True,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{item_id}: verification timed out after {timeout}s")
            continue
        if proc.returncode != 0:
            failures.append(
                f"{item_id}: verification now exits {proc.returncode} "
                f"(evidence claims a pass): {command}"
            )
        else:
            print(f"  [PASS] {item_id}: verification re-ran clean")

    if failures:
        print("gate-prepush-check: FAIL — passing items no longer verify:")
        for failure in failures:
            print(f"  - {failure}")
        print("Fix: run `python3 gate/pass-gate.py verify --id <id>` for the "
              "failing item, fix the code, or `block` / `reopen` the item "
              "with a reason — do not hand-edit feature_list.json evidence.")
        return 1

    print(f"gate-prepush-check: PASS — {checked} passing item(s) re-verified, "
          f"no stale evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
