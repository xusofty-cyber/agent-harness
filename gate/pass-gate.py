#!/usr/bin/env python3
"""pass-gate.py — the self-owned verification gate for agent-harness (Phase 1).

Reads ``gate/feature_list.json``, runs the verification command an item
declares, and only then moves the item to ``passing`` — with evidence.
The agent never edits the ``status`` field by hand: the PreToolUse hook
(``.claude/hooks/guard-feature-list.mjs``, Claude Code only) blocks direct
writes to ``feature_list.json``, and ``tests/repo_checks.py`` §3k re-checks
every ``passing`` item in CI. All three together are defence in depth:
they raise the cost of faking a pass and leave a trace, they do not
guarantee a pass cannot be faked. See ``gate/README.md``.

Stdlib only. No third-party dependencies, no network.

Usage (run from the project root, or pass --root):
  pass-gate.py init [--root DIR] [--project NAME]
  pass-gate.py start --id <id>
  pass-gate.py verify --id <id> | --all
  pass-gate.py block --id <id> --reason <text>
  pass-gate.py unblock --id <id>
  pass-gate.py reopen --id <id> --reason <text>
  pass-gate.py override --id <id> --reason <text> [--by NAME]
  pass-gate.py status [--json]
  pass-gate.py check-clean [--root DIR]
  pass-gate.py events [--last N]
  pass-gate.py terminate --id <id> --stage static|runtime|system
      (merged from v3-yunyi: three-layer termination, no skipping)
  pass-gate.py handoff [--out PATH]
      (merged from v3-yunyi: handoff draft from git + events + breakpoint)
  pass-gate.py run --worktree <name> [--branch <branch>] -- <command...>
      (merged from v3-yunyi: run a host command in an isolated git
      worktree, then check-clean there; never auto-merges)

Exit codes: 0 = the requested check passed / the command succeeded;
1 = verification failed, state unchanged, or a rule was violated
(WIP=1, bad transition, missing evidence, clean-state dimension failed).
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

SCHEMA_VERSION = 1
STATUSES = ("not_started", "in_progress", "blocked", "passing")
PRIORITIES = ("p0", "p1", "p2")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ITEM_REQUIRED = ("id", "priority", "area", "title",
                 "user_visible_behavior", "status", "verification")
# NOTE (panel P1-5): the old ALLOWED transition table was defined here
# but never referenced by any command — dead code that implied a
# guarantee nothing enforced. It is deleted, not wired in: transitions
# are enforced per-command by the status checks in cmd_start,
# cmd_block, cmd_reopen, cmd_verify, cmd_override and cmd_terminate
# (e.g. start only from not_started/blocked, override only from
# in_progress). A single-snapshot validator cannot check transitions.
ITEM_KEYS = set(ITEM_REQUIRED) | {"evidence", "notes", "external_evidence"}
TOP_KEYS = {"version", "project", "items"}
VERIFICATION_KEYS = {"command", "timeout_seconds", "level"}
# Verification strength, weakest to strongest (v0.4.1, D66). Optional:
# an item without a level is reported as "unspecified" by check-clean.
# The level is descriptive, never a gate: it makes evidence strength
# visible instead of letting a grep-assert passing look identical to
# an end-to-end passing (course L10).
LEVELS = ("assert", "unit", "integration", "e2e")
EVIDENCE_KEYS = {"command", "exit_code", "ran_at", "output_tail", "override",
                 "output_sha256"}
OVERRIDE_KEYS = {"by", "reason", "at"}
EXTERNAL_EVIDENCE_KEYS = {"source", "path", "sha256_16", "imported_at"}
MAX_OUTPUT_TAIL = 2048


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z")


def _actor():
    return os.environ.get("GATE_ACTOR", "agent")


def _feature_list_path(root):
    return os.path.join(root, "gate", "feature_list.json")


def _events_path(root):
    return os.path.join(root, "gate", "events.jsonl")


def _load(root):
    path = _feature_list_path(root)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None, f"feature list not found: {path} (run `pass-gate.py init`)"
    except json.JSONDecodeError as e:
        return None, f"feature list is not valid JSON: {path}: {e}"
    return data, None


def _save(root, data):
    path = _feature_list_path(root)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _extra_keys(where, obj, allowed, errors):
    extra = sorted(set(obj) - allowed)
    if extra:
        errors.append(f"{where} has unknown fields (schema "
                      f"additionalProperties:false): {', '.join(extra)}")


def validate(data):
    """Validate a feature list against gate/feature_list.schema.json.

    Returns a list of error strings (empty = valid).
    tests/repo_checks.py §3k imports this function so the CI check and
    the gate cannot drift apart. Panel P1-5 closed the drift: this now
    enforces the schema's additionalProperties:false at every level,
    verification.timeout_seconds 1..3600, and the evidence object's
    required fields (command/exit_code/ran_at/output_tail) — plus the
    type guards that used to crash on a non-dict verification.
    Deliberately NOT enforced (documented, not drift): nothing — every
    constraint in the schema file is covered except the prose
    descriptions. If a future schema constraint is added without a
    check here, update this docstring to name it.
    """
    errors = []
    if not isinstance(data, dict):
        return ["feature list must be a JSON object"]
    _extra_keys("feature list", data, TOP_KEYS, errors)
    if data.get("version") != SCHEMA_VERSION:
        errors.append(f"version must be {SCHEMA_VERSION}")
    if not isinstance(data.get("project"), str) or not data["project"]:
        errors.append("project must be a non-empty string")
    items = data.get("items")
    if not isinstance(items, list):
        return errors + ["items must be an array"]
    seen_ids = set()
    in_progress = []
    for i, item in enumerate(items):
        where = f"items[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        _extra_keys(where, item, ITEM_KEYS, errors)
        for field in ITEM_REQUIRED:
            if field not in item:
                errors.append(f"{where} missing required field: {field}")
        item_id = item.get("id", "")
        if not isinstance(item_id, str):
            errors.append(f"{where}.id must be a string")
        else:
            if not ID_RE.match(item_id):
                errors.append(f"{where}.id {item_id!r} must match "
                              "^[a-z0-9][a-z0-9-]*$")
            if item_id in seen_ids:
                errors.append(f"duplicate item id: {item_id}")
            seen_ids.add(item_id)
        if item.get("priority") not in PRIORITIES:
            errors.append(f"{where}.priority must be one of {PRIORITIES}")
        for field in ("area", "title", "user_visible_behavior"):
            if field in item and (not isinstance(item[field], str)
                                  or not item[field].strip()):
                errors.append(f"{where}.{field} must be a non-empty string")
        if "notes" in item and not isinstance(item["notes"], str):
            errors.append(f"{where}.notes must be a string")
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{where}.status must be one of {STATUSES}")
        elif status == "in_progress":
            in_progress.append(item_id)
        verification = item.get("verification")
        v_command = None
        if not isinstance(verification, dict):
            errors.append(f"{where}.verification must be an object")
        else:
            _extra_keys(f"{where}.verification", verification,
                        VERIFICATION_KEYS, errors)
            v_command = verification.get("command")
            if not isinstance(v_command, str) or not v_command.strip():
                errors.append(f"{where}.verification.command must be a "
                              "non-empty string")
            if "timeout_seconds" in verification:
                timeout = verification["timeout_seconds"]
                if not _is_int(timeout) or not 1 <= timeout <= 3600:
                    errors.append(f"{where}.verification.timeout_seconds "
                                  "must be an integer in 1..3600")
            if "level" in verification \
                    and verification["level"] not in LEVELS:
                errors.append(f"{where}.verification.level must be one "
                              f"of {LEVELS}")
        evidence = item.get("evidence")
        if evidence is not None and not isinstance(evidence, dict):
            errors.append(f"{where}.evidence must be an object or null")
        elif isinstance(evidence, dict):
            _extra_keys(f"{where}.evidence", evidence, EVIDENCE_KEYS, errors)
            if not isinstance(evidence.get("command"), str):
                errors.append(f"{where}.evidence.command must be a string")
            if not _is_int(evidence.get("exit_code")):
                errors.append(f"{where}.evidence.exit_code must be an integer")
            if not isinstance(evidence.get("ran_at"), str) \
                    or not evidence["ran_at"]:
                errors.append(f"{where}.evidence.ran_at must be a "
                              "non-empty string")
            if not isinstance(evidence.get("output_tail"), str):
                errors.append(f"{where}.evidence.output_tail must be a string")
            if "output_sha256" in evidence \
                    and not isinstance(evidence["output_sha256"], str):
                errors.append(f"{where}.evidence.output_sha256 must be a string")
            override = evidence.get("override")
            if override is not None:
                if not isinstance(override, dict):
                    errors.append(f"{where}: evidence.override must be "
                                  "an object with by/reason/at")
                else:
                    _extra_keys(f"{where}.evidence.override", override,
                                OVERRIDE_KEYS, errors)
                    for field in ("by", "reason", "at"):
                        if not isinstance(override.get(field), str) \
                                or not override[field]:
                            errors.append(f"{where}: evidence.override.{field} "
                                          "must be a non-empty string")
            if status == "passing":
                if override is None and evidence.get("exit_code") != 0:
                    errors.append(f"{where}: passing evidence must have "
                                  "exit_code 0 (or a logged override)")
                # Guarded by the verification-is-dict check above: a
                # non-dict verification used to crash here with
                # AttributeError (panel P1-5). The verification error
                # is already recorded, so skip the comparison then.
                if isinstance(verification, dict) and override is None \
                        and evidence.get("command") != v_command:
                    errors.append(f"{where}: evidence.command must equal "
                                  "verification.command (or be an override)")
        elif status == "passing":
            errors.append(f"{where}: status=passing requires "
                          "non-empty evidence (run pass-gate.py verify)")
        external = item.get("external_evidence")
        if external is not None:
            if not isinstance(external, list):
                errors.append(f"{where}.external_evidence must be an array")
            else:
                for j, entry in enumerate(external):
                    ewhere = f"{where}.external_evidence[{j}]"
                    if not isinstance(entry, dict):
                        errors.append(f"{ewhere} must be an object")
                        continue
                    _extra_keys(ewhere, entry, EXTERNAL_EVIDENCE_KEYS, errors)
                    for field in EXTERNAL_EVIDENCE_KEYS:
                        if not isinstance(entry.get(field), str) \
                                or not entry[field]:
                            errors.append(f"{ewhere}.{field} must be a "
                                          "non-empty string")
    if len(in_progress) > 1:
        errors.append(f"WIP=1 violated: more than one in_progress item: "
                      f"{', '.join(in_progress)}")
    return errors


class EventsLogError(ValueError):
    """The append-only event log is unreadable.

    Raised instead of letting a raw JSONDecodeError/KeyError traceback
    escape: callers fail with a clear message BEFORE mutating any state,
    so a corrupt log line can never silently drop a state change.
    """


def _read_events(root):
    path = _events_path(root)
    events = []
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    raise EventsLogError(
                        f"gate/events.jsonl line {lineno} is not valid "
                        f"JSON (starts: {line[:80]!r}); repair or remove "
                        f"that line first — no state was changed")
    return events


def _append_event(root, event, item_id, detail):
    """Append one event to gate/events.jsonl (append-only by convention).

    The log is committed to git, so rewriting history is visible in the
    diff; the file itself cannot stop a determined rewrite — it leaves a
    trace. Sequence numbers are monotonic; a gap or duplicate is a
    smell CI (§3k) flags. The sequence number is the maximum integer
    seq already in the log plus one, so an event written by another
    tool without a seq (or with a non-integer seq) can never crash
    the append with KeyError — the next append simply continues from
    the highest known seq.
    """
    path = _events_path(root)
    events = _read_events(root)
    seq = 1
    for rec in events:
        if isinstance(rec, dict) and isinstance(rec.get("seq"), int):
            seq = max(seq, rec["seq"] + 1)
    record = {
        "seq": seq,
        "ts": _utcnow(),
        "actor": _actor(),
        "event": event,
        "item_id": item_id,
        "detail": detail,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def _find(data, item_id):
    for item in data["items"]:
        if item["id"] == item_id:
            return item
    return None


def _run(cmd, root, timeout):
    """Run a verification command. Returns (exit_code, output_tail)."""
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=root, timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, errors="replace")
        out = proc.stdout or ""
        return proc.returncode, out[-MAX_OUTPUT_TAIL:]
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") \
            if isinstance(e.stdout, bytes) else (e.stdout or "")
        return 124, (out + "\n[TIMEOUT after %ss]" % timeout)[-MAX_OUTPUT_TAIL:]
    except FileNotFoundError:
        return 127, "[command not found by the shell]"


def _diagnose_layer(exit_code, output):
    """Attribute a failure to one of the five diagnostic layers (best effort).

    Layers: goal (wrong target), plan (wrong command/steps), execution
    (tooling/environment), verification (the check itself), handover
    (stale state). This is a heuristic label for the log, not a proof.
    """
    low = output.lower()
    if exit_code in (127, 126) or "command not found" in low \
            or "no such file" in low:
        return "execution: command or file missing in this environment"
    if "timeout" in low or exit_code == 124:
        return "execution: verification timed out"
    if "traceback" in low or "error:" in low:
        return "verification: the check ran and reported a failure"
    return "verification: verification command exited non-zero"


def cmd_add(args):
    """Append a new not_started item. This is the only sanctioned way to
    add items (the PreToolUse hook blocks hand-editing feature_list.json)."""
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    if _find(data, args.id) is not None:
        print(f"an item with id {args.id} already exists")
        return 1
    item = {
        "id": args.id,
        "priority": args.priority,
        "area": args.area,
        "title": args.title,
        "user_visible_behavior": args.behavior,
        "status": "not_started",
        "verification": {"command": args.command,
                         "timeout_seconds": args.timeout,
                         **({"level": args.level} if args.level else {})},
        "evidence": None,
        "notes": args.notes or "",
    }
    data["items"].append(item)
    errors = validate(data)
    if errors:
        print("new item is invalid:")
        for e in errors:
            print(f"  - {e}")
        return 1
    _save(args.root, data)
    _append_event(args.root, "added", args.id, args.title)
    print(f"added: {args.id} — {args.title}")
    return 0


def cmd_init(args):
    import shutil
    root = args.root
    gate_dir = os.path.join(root, "gate")
    os.makedirs(gate_dir, exist_ok=True)
    path = _feature_list_path(root)
    if os.path.exists(path) and not args.force:
        print(f"feature list already exists: {path} (use --force to overwrite)")
        return 1
    template = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "templates", "feature_list.template.json")
    if os.path.exists(template):
        shutil.copyfile(template, path)
        data, _ = _load(root)
        data["project"] = args.project
        _save(root, data)
    else:
        _save(root, {"version": 1, "project": args.project, "items": []})
    events = _events_path(root)
    if not os.path.exists(events):
        _append_event(root, "gate_init", None,
                      f"feature list created for project {args.project!r}")
    print(f"initialized gate in {gate_dir}")
    return 0


def cmd_start(args):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    errors = validate(data)
    if errors:
        print("feature list is invalid:")
        for e in errors:
            print(f"  - {e}")
        return 1
    item = _find(data, args.id)
    if item is None:
        print(f"no such item: {args.id}")
        return 1
    if item["status"] not in ("not_started", "blocked"):
        print(f"cannot start {args.id}: status is {item['status']} "
              "(start only from not_started or blocked)")
        return 1
    if any(i["status"] == "in_progress" for i in data["items"]):
        print("WIP=1: another item is already in_progress; "
              "finish or block it first")
        return 1
    item["status"] = "in_progress"
    _save(args.root, data)
    _append_event(args.root, "started", args.id, item["title"])
    print(f"started: {args.id} — {item['title']}")
    return 0


def _verify_one(root, item):
    """Run one item's verification. Returns (ok, exit_code, output_tail)."""
    cmd = item["verification"]["command"]
    timeout = item["verification"].get("timeout_seconds", 300)
    print(f"$ {cmd}")
    exit_code, tail = _run(cmd, root, timeout)
    if exit_code == 0:
        item["status"] = "passing"
        item["evidence"] = {
            "command": cmd,
            "exit_code": 0,
            "ran_at": _utcnow(),
            "output_tail": tail,
            "output_sha256": hashlib.sha256(
                tail.encode("utf-8")).hexdigest(),
        }
        return True, exit_code, tail
    return False, exit_code, tail


def cmd_verify(args):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    errors = validate(data)
    if errors:
        print("feature list is invalid:")
        for e in errors:
            print(f"  - {e}")
        return 1
    if args.all:
        targets = [i for i in data["items"]
                   if i["status"] == "in_progress"]
        if not targets:
            print("nothing in_progress to verify")
            return 0
    else:
        item = _find(data, args.id)
        if item is None:
            print(f"no such item: {args.id}")
            return 1
        if item["status"] != "in_progress":
            print(f"cannot verify {args.id}: status is {item['status']} "
                  "(verify only from in_progress — run `start` first)")
            return 1
        targets = [item]
    failed = []
    for item in targets:
        ok, exit_code, tail = _verify_one(args.root, item)
        if ok:
            _append_event(args.root, "verified", item["id"],
                          f"verification passed (exit 0): "
                          f"{item['verification']['command']}")
            print(f"PASS {item['id']}: {item['title']}")
        else:
            layer = _diagnose_layer(exit_code, tail)
            _append_event(args.root, "verify_failed", item["id"],
                          f"exit {exit_code}; {layer}; "
                          f"command: {item['verification']['command']}")
            print(f"FAIL {item['id']}: verification exited {exit_code}")
            print(f"  where: {item['verification']['command']}")
            print(f"  why: {layer}")
            print(f"  fix: address the failure, then run "
                  f"`pass-gate.py verify --id {item['id']}` again; "
                  "status stays in_progress")
            if tail.strip():
                print("  output (tail):")
                for line in tail.strip().splitlines()[-10:]:
                    print(f"    {line}")
            failed.append(item["id"])
    _save(args.root, data)
    if failed:
        return 1
    return 0


def cmd_block(args):
    return _transition(args, "blocked", "blocked",
                       allowed_from=("in_progress",))


def cmd_unblock(args):
    return _transition(args, "in_progress", "unblocked",
                       allowed_from=("blocked",))


def _transition(args, new_status, event_name, allowed_from):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    item = _find(data, args.id)
    if item is None:
        print(f"no such item: {args.id}")
        return 1
    if item["status"] not in allowed_from:
        print(f"cannot move {args.id} from {item['status']} "
              f"to {new_status}")
        return 1
    if new_status == "in_progress" and any(
            i["status"] == "in_progress" for i in data["items"]):
        print("WIP=1: another item is already in_progress")
        return 1
    item["status"] = new_status
    _save(args.root, data)
    _append_event(args.root, event_name, args.id,
                  getattr(args, "reason", "") or item["title"])
    print(f"{args.id}: {item['status']}")
    return 0


def cmd_reopen(args):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    item = _find(data, args.id)
    if item is None:
        print(f"no such item: {args.id}")
        return 1
    if item["status"] != "passing":
        print(f"cannot reopen {args.id}: status is {item['status']} "
              "(only passing items can be reopened)")
        return 1
    item["status"] = "in_progress"
    item["evidence"] = None
    _save(args.root, data)
    # A rolled-back item must not reuse stale termination stages:
    # clear its record so terminate starts from static again.
    _clear_termination(args.root, args.id)
    _append_event(args.root, "reopened", args.id,
                  f"reason: {args.reason}")
    print(f"reopened: {args.id} (evidence cleared; verify again to pass)")
    return 0


def cmd_override(args):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    item = _find(data, args.id)
    if item is None:
        print(f"no such item: {args.id}")
        return 1
    if item["status"] != "in_progress":
        print(f"cannot override {args.id}: status is {item['status']} "
              "(override only from in_progress)")
        return 1
    item["status"] = "passing"
    item["evidence"] = {
        "command": item["verification"]["command"],
        "exit_code": -1,  # -1 = no passing run; human override, see below
        "ran_at": _utcnow(),
        "output_tail": "[HUMAN OVERRIDE — verification did not pass; "
                       "see override.reason]",
        "override": {"by": args.by, "reason": args.reason,
                     "at": _utcnow()},
    }
    _save(args.root, data)
    _append_event(args.root, "override", args.id,
                  f"by {args.by}: {args.reason}")
    print(f"OVERRIDE {args.id}: marked passing by {args.by} — "
          f"{args.reason}")
    print("  (recorded in evidence.override and gate/events.jsonl; "
          "a reviewer can see this was not a passing run)")
    return 0


def cmd_status(args):
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    errors = validate(data)
    if args.json:
        print(json.dumps({"project": data.get("project"),
                          "errors": errors,
                          "items": data.get("items", [])},
                         indent=2, ensure_ascii=False))
        return 1 if errors else 0
    n_items = len(data.get('items', []))
    print(f"project: {data.get('project')}  "
          f"({n_items} item{'s' if n_items != 1 else ''})")
    for item in data.get("items", []):
        ev = item.get("evidence") or {}
        mark = "override" if ev.get("override") else (
            "evidence" if ev else "no evidence")
        _lvl = (item.get("verification") or {}).get("level")
        _lvl_s = f" <{_lvl}>" if _lvl else ""
        print(f"  [{item['status']:12}] {item['id']} ({item['priority']}) "
              f"— {item['title']} [{mark}]{_lvl_s}")
    if errors:
        print("validation errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    return 0


def cmd_events(args):
    events = _read_events(args.root)
    for ev in events[-args.last:]:
        print(f"#{ev['seq']} {ev['ts']} {ev['actor']} "
              f"{ev['event']} {ev.get('item_id') or '-'} :: "
              f"{ev.get('detail', '')}")
    return 0


# --- three-layer termination, handoff, worktree run (merged from v3-yunyi) ---
# These three commands are ports of gate/harness.py (yunyi) onto the
# skeleton's own state shape: items (not features), verification objects
# {command, timeout_seconds}, evidence with output_sha256, events with a
# monotonic seq, and atomic writes everywhere. Differences vs. the
# original are called out where they matter; see gate/README.md.

TERMINATION_STAGES = ("static", "runtime", "system")


def _termination_path(root):
    return os.path.join(root, "gate", "termination.json")


def _load_termination(root):
    """Return (state, error). A corrupt termination.json is fatal, never
    silently discarded (yunyi's version returned {} on corrupt JSON)."""
    path = _termination_path(root)
    if not os.path.exists(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        return {}, f"termination state is not valid JSON: {path}: {e}"
    if not isinstance(state, dict):
        return {}, f"termination state must be a JSON object: {path}"
    return state, None


def _save_termination(root, state):
    """Atomic write (tmp + replace), unlike yunyi's direct write_text."""
    path = _termination_path(root)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _clear_termination(root, item_id):
    """Drop one item's termination record (reopen path). Best effort:
    a corrupt file is left alone and warned about — the next terminate
    will fail loudly on it instead of silently losing state."""
    state, err = _load_termination(root)
    if err:
        print(f"warning: {err} (leaving it for a human to inspect)",
              file=sys.stderr)
        return
    if item_id in state:
        del state[item_id]
        _save_termination(root, state)


def cmd_terminate(args):
    """Three-layer termination: static -> runtime -> system, no skipping.

    - static: the feature list validates and gate/init.template.sh (if
      present) parses. No verification runs yet.
    - runtime: the item's verification command runs and exits 0;
      evidence is written in the skeleton's format, but the status does
      NOT become passing yet.
    - system: check-clean passes AND the runtime evidence is present,
      passing (exit_code 0), and for the item's CURRENT verification
      command; only then does the item become passing. The evidence
      check is what stops a hand-written termination.json from
      skipping straight to passing: stage marks alone never suffice.
    Each successful stage appends its own event (static/runtime), so
    a forged termination record is distinguishable from a real run in
    the event log — previously only the final status_transition was
    logged.
    Stages are recorded in gate/termination.json ({id: {stage: true}});
    a stage is idempotent and re-runnable. Terminate only works from
    in_progress (same rule as verify). Reopening an item clears its
    termination record, so a rolled-back item cannot skip layers by
    reusing stale stage marks (a gap in the yunyi original, where
    rollback left termination.json untouched).
    """
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    item = _find(data, args.id)
    if item is None:
        print(f"no such item: {args.id}")
        return 1
    if item["status"] != "in_progress":
        print(f"cannot terminate {args.id}: status is {item['status']} "
              "(terminate only from in_progress — run `start` first)")
        return 1
    state, err = _load_termination(args.root)
    if err:
        print(err)
        return 1
    done = state.get(args.id, {})
    stage = args.stage
    prerequisites = {"static": [], "runtime": ["static"],
                     "system": ["static", "runtime"]}
    missing = [p for p in prerequisites[stage] if not done.get(p)]
    if missing:
        _append_event(args.root, "termination_skip_refused", args.id,
                      f"requested {stage} without {missing}")
        print(f"REFUSED: cannot run {stage} before {missing} for "
              f"{args.id} (three-layer order is static -> runtime -> "
              "system)", file=sys.stderr)
        return 2
    if stage == "static":
        errors = validate(data)
        init_sh = os.path.join(args.root, "gate", "init.template.sh")
        if os.path.exists(init_sh):
            proc = subprocess.run(["bash", "-n", init_sh],
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                errors.append(f"init.template.sh syntax failed: "
                              f"{proc.stderr[:200]}")
        if errors:
            _append_event(args.root, "termination_failed", args.id,
                          f"static failed: {errors[:3]}")
            print(f"FAIL static: {errors}", file=sys.stderr)
            return 1
        done["static"] = True
        _append_event(args.root, "termination_stage", args.id,
                      "static passed")
    elif stage == "runtime":
        cmd = item["verification"]["command"]
        timeout = args.timeout or item["verification"].get(
            "timeout_seconds", 300)
        exit_code, tail = _run(cmd, args.root, timeout)
        if exit_code != 0:
            _append_event(args.root, "verification_failed", args.id,
                          f"termination runtime failed (exit {exit_code})")
            print(f"FAIL runtime: {args.id} verification exit {exit_code}",
                  file=sys.stderr)
            return 1
        item["evidence"] = {
            "command": cmd,
            "exit_code": 0,
            "ran_at": _utcnow(),
            "output_tail": tail,
            "output_sha256": hashlib.sha256(
                tail.encode("utf-8")).hexdigest(),
        }
        _save(args.root, data)
        done["runtime"] = True
        _append_event(args.root, "termination_stage", args.id,
                      "runtime passed (verification exit 0)")
    else:  # system
        # P1-1: stage marks alone must never suffice. The runtime
        # evidence must exist, must have passed, and must be for the
        # item's CURRENT verification command — otherwise a
        # hand-written termination.json (or evidence from before the
        # command changed) would skip straight to passing.
        ev = item.get("evidence")
        current_cmd = item["verification"]["command"]
        if not isinstance(ev, dict) or ev.get("exit_code") != 0 \
                or ev.get("command") != current_cmd:
            _append_event(args.root, "termination_failed", args.id,
                          "system refused: no runtime evidence matching "
                          "the current verification command")
            print(f"FAIL system: {args.id} has no runtime evidence for "
                  f"the current verification command "
                  f"(evidence command: "
                  f"{None if not isinstance(ev, dict) else ev.get('command')!r} "
                  f"vs verification: {current_cmd!r}); run the runtime "
                  f"stage first", file=sys.stderr)
            return 1
        clean = cmd_check_clean(argparse.Namespace(root=args.root))
        if clean != 0:
            _append_event(args.root, "termination_failed", args.id,
                          "system failed: check-clean did not pass")
            print(f"FAIL system: check-clean did not pass for {args.id}",
                  file=sys.stderr)
            return 1
        item["status"] = "passing"
        _save(args.root, data)
        done["system"] = True
        _append_event(args.root, "status_transition", args.id,
                      "passing via three-layer termination "
                      "(static+runtime+system)")
    state[args.id] = done
    _save_termination(args.root, state)
    print(f"TERMINATE {stage}: {args.id} OK (stages done: "
          f"{[s for s in TERMINATION_STAGES if done.get(s)]})")
    return 0


def cmd_handoff(args):
    """Generate a handoff draft from git log, the event log and the
    session breakpoint. Always exits 0: a handoff is a draft for a human
    to review, never a verdict.

    Unlike the yunyi original, this also reads SESSION_STATE.md (the
    breakpoint file the original's docstring promised but its code never
    read) and writes --out atomically.
    """
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    items = data.get("items", [])
    in_progress = [i for i in items if i["status"] == "in_progress"]
    blocked = [i for i in items if i["status"] == "blocked"]
    passing = [i for i in items if i["status"] == "passing"]
    next_item = in_progress[0] if in_progress else next(
        (i for i in items if i["status"] == "not_started"), None)
    try:
        proc = subprocess.run(["git", "log", "--oneline", "-10"],
                              cwd=args.root, capture_output=True, text=True,
                              timeout=60)
        git_log = proc.stdout.strip() if proc.returncode == 0 else ""
    except Exception:  # noqa: BLE001 - git absent is not a failure
        git_log = ""
    events = _read_events(args.root)[-10:]
    events_text = "\n".join(
        f"#{ev['seq']} {ev['ts']} {ev['actor']} {ev['event']} "
        f"{ev.get('item_id') or '-'} :: {ev.get('detail', '')}"
        for ev in events)
    state_path = _session_state_path(args.root)
    if state_path is None:
        breakpoint_text = "(no SESSION_STATE.md found)"
    else:
        with open(state_path, encoding="utf-8") as f:
            lines = [l.rstrip() for l in f if l.strip()][:20]
        breakpoint_text = "\n".join(lines) or "(SESSION_STATE.md is empty)"
    lines = [
        "# Handoff draft (generated by pass-gate handoff — review before use)",
        "",
        f"- Verified: {len(passing)} passing; in progress: "
        f"{len(in_progress)}; blocked: {len(blocked)}",
        f"- In progress: {', '.join(i['id'] for i in in_progress) or 'none'}",
        f"- Blocked: {', '.join(i['id'] for i in blocked) or 'none'}",
        f"- Next: {next_item['id'] + ' — ' + next_item['title'] if next_item else 'none'}",
        "- Do not touch (until verified): gate/feature_list.json status / "
        "evidence fields — only pass-gate may write them.",
        "",
        "## Session breakpoint",
        breakpoint_text,
        "",
        "## Recent commits",
        git_log or "(not a git repository or no commits)",
        "",
        "## Recent gate events",
        events_text or "(no events yet)",
    ]
    text = "\n".join(lines) + "\n"
    if args.out:
        tmp = args.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, args.out)
        print(f"handoff written to {args.out}")
    else:
        print(text)
    return 0


def cmd_run(args):
    """Run a host command in an isolated git worktree, then check-clean
    there. Never auto-merges (Phase 1 safety rule).

    Differences vs. the yunyi original: an optional --branch creates a
    real branch for the worktree (the original used a detached HEAD and
    printed a merge hint for a branch that did not exist); without
    --branch the worktree is detached and the message says so plainly.
    The check-clean target is gate/feature_list.json (the skeleton's
    layout, not the original's root-level feature_list.json); a
    worktree without a gate is reported, not merged blindly.
    """
    root = args.root
    host_command = list(args.host_command or [])
    if host_command and host_command[0] == "--":
        host_command = host_command[1:]
    if not host_command:
        print("REFUSED: pass-gate run requires a host command after --",
              file=sys.stderr)
        return 2
    worktree_dir = os.path.join(root, ".worktrees", args.worktree)
    if os.path.exists(worktree_dir):
        print(f"REFUSED: worktree already exists: {worktree_dir} "
              "(remove it or pick another name)", file=sys.stderr)
        return 2
    cmd = ["git", "worktree", "add", worktree_dir]
    if args.branch:
        cmd += ["-b", args.branch]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"worktree creation failed: {proc.stdout} {proc.stderr}",
              file=sys.stderr)
        return 1
    print(f"worktree created: {worktree_dir}")
    try:
        run = subprocess.run(host_command, cwd=worktree_dir)
        if run.returncode != 0:
            print(f"host command failed (exit {run.returncode}); "
                  "worktree left in place for inspection; NOT merged.",
                  file=sys.stderr)
            return run.returncode
        # Check-clean inside the worktree (only if it is a gate project).
        if os.path.exists(os.path.join(
                worktree_dir, "gate", "feature_list.json")):
            clean = subprocess.run(
                [sys.executable, os.path.abspath(__file__),
                 "--root", worktree_dir, "check-clean"])
            if clean.returncode != 0:
                print("check-clean failed in worktree; NOT merged. Fix, "
                      "re-verify, then merge manually.", file=sys.stderr)
                return 1
        else:
            print("(worktree has no gate/feature_list.json; "
                  "skipping check-clean)")
        print(f"OK in worktree {worktree_dir}. pass-gate does NOT "
              "auto-merge.")
        if args.branch:
            print(f"To merge manually after review: git merge --no-ff "
                  f"{args.branch}")
        else:
            print("No branch was created (detached HEAD). To merge: "
                  "create a branch in the worktree first "
                  f"(git -C {worktree_dir} switch -c <branch>), then "
                  "merge it.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"pass-gate run failed: {exc}", file=sys.stderr)
        return 1


def _load_clean_config(root):
    path = os.path.join(root, "gate", "clean-state.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _session_state_path(root):
    for candidate in (os.path.join(root, "docs", "internal", "SESSION_STATE.md"),
                      os.path.join(root, "SESSION_STATE.md")):
        if os.path.exists(candidate):
            return candidate
    return None


def cmd_check_clean(args):
    """Clean-state check: the five course dimensions.

    1. build passes, 2. tests pass, 3. progress recorded — (a) narrative
    progress in SESSION_STATE mentions the in_progress item, (b) the
    feature list is truthful: every passing item's verification still
    exits 0 when re-run, (c) no unfilled SESSION_STATE placeholders
    (D47), 4. temp artefacts cleaned, 5. standard start
    path works. Commands come from gate/clean-state.json; a dimension
    with no command configured is SKIP, not PASS.
    """
    data, err = _load(args.root)
    if err:
        print(err)
        return 1
    config = _load_clean_config(args.root) or {}
    results = []  # (dimension, outcome, detail)

    def _run_dim(name, cmd):
        if not cmd:
            results.append((name, "SKIP", "no command configured in "
                            "gate/clean-state.json"))
            return
        code, tail = _run(cmd, args.root, 600)
        if code == 0:
            results.append((name, "PASS", cmd))
        else:
            results.append((name, "FAIL",
                            f"{cmd} (exit {code}): "
                            f"{tail.strip().splitlines()[-1] if tail.strip() else ''}"))

    _run_dim("1 build", config.get("build"))
    _run_dim("2 tests", config.get("test"))

    # 3a. narrative progress recorded
    in_progress = [i for i in data["items"]
                   if i["status"] == "in_progress"]
    state_path = _session_state_path(args.root)
    if not in_progress:
        results.append(("3a progress/narrative", "PASS",
                        "no item in_progress"))
    elif state_path is None:
        results.append(("3a progress/narrative", "FAIL",
                        "no SESSION_STATE.md found"))
    else:
        text = open(state_path, encoding="utf-8").read()
        missing = [i["id"] for i in in_progress if i["id"] not in text]
        if missing:
            results.append(("3a progress/narrative", "FAIL",
                            f"SESSION_STATE does not mention in_progress "
                            f"item(s): {', '.join(missing)}"))
        else:
            results.append(("3a progress/narrative", "PASS",
                            f"mentions {', '.join(i['id'] for i in in_progress)}"))

    # 3b. feature list truthful: re-run verification of passing items
    passing = [i for i in data["items"] if i["status"] == "passing"]
    bad = []
    for item in passing:
        ev = item.get("evidence") or {}
        if ev.get("override"):
            continue  # human override is truthful by declaration, and visible
        cmd = item["verification"]["command"]
        code, _ = _run(cmd, args.root,
                       item["verification"].get("timeout_seconds", 300))
        if code != 0:
            bad.append(f"{item['id']} (verification now exits {code})")
    if bad:
        results.append(("3b progress/feature-list truthful", "FAIL",
                        "; ".join(bad)))
    else:
        results.append(("3b progress/feature-list truthful", "PASS",
                        f"{len(passing)} passing item(s) re-verified"))

    # 3c. no unfilled SESSION_STATE placeholders (D47, adopted from
    # yunyi D15). A SESSION_STATE that still carries template markers
    # is not a handoff-ready state, even if every other dimension
    # passes. Skeleton-adapted markers: the skeleton template's own
    # unfilled markers (<YYYY-MM-DD>, <PROJECT_NAME>, "What this session
    # is trying to ship") plus generic angle-bracket task markers.
    # The pattern is assembled from parts so this file does not itself
    # contain the literals LINT-004 scans for (same trick as
    # tools/lint-rules.py). No SESSION_STATE file at all is SKIP here
    # (3a already FAILs when an item is in_progress without one; a
    # project with no in_progress items and no state file has nothing
    # to hand off).
    if state_path is None:
        results.append(("3c progress/no placeholders", "SKIP",
                        "no SESSION_STATE.md found"))
    else:
        state_text = open(state_path, encoding="utf-8").read()
        hits = [m for m in ("<YYYY-MM-DD>", "<PROJECT_NAME>",
                            "What this session is trying to ship")
                if m in state_text]
        hits += [m.group(0) for m in
                 re.finditer(r"<(TO" + "DO|TBD|XX" + "X|PLACEHOLDER)>",
                             state_text)]
        if hits:
            results.append(("3c progress/no placeholders", "FAIL",
                            f"unfilled placeholder(s): "
                            f"{', '.join(sorted(set(hits)))}"))
        else:
            results.append(("3c progress/no placeholders", "PASS",
                            "no unfilled placeholders"))

    # 3d. verification-strength summary (v0.4.1, D66; course L10).
    # Informational only — never a FAIL: a passing proved by a text
    # assertion and a passing proved end-to-end must not *look*
    # identical in the handover report, but the gate does not prescribe
    # the right level for a given item; the human does, at review time.
    if passing:
        _counts = {}
        for _item in passing:
            _lvl = (_item.get("verification") or {}).get("level") \
                or "unspecified"
            _counts[_lvl] = _counts.get(_lvl, 0) + 1
        _order = list(LEVELS) + ["unspecified"]
        _summary = ", ".join(f"{lvl} {_counts[lvl]}"
                             for lvl in _order if lvl in _counts)
        results.append(("3d verification levels (info)", "PASS",
                        f"passing by level: {_summary}"))

    # 4. temp artefacts cleaned
    temp_hits = []
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=args.root, capture_output=True, text=True, timeout=60)
        for line in proc.stdout.splitlines():
            path = line[3:].strip()
            if path.endswith((".tmp", ".bak")) or ".bak-" in path \
                    or "__pycache__" in path or path.endswith(".log"):
                temp_hits.append(path)
    except Exception as e:  # noqa: BLE001 - git absent is not a failure
        temp_hits = [f"(git status unavailable: {e})"]
    if temp_hits:
        results.append(("4 temp artefacts cleaned", "FAIL",
                        "; ".join(temp_hits[:5])))
    else:
        results.append(("4 temp artefacts cleaned", "PASS",
                        "no temp artefacts in git status"))

    _run_dim("5 standard start path", config.get("start"))

    failed = [r for r in results if r[1] == "FAIL"]
    for name, outcome, detail in results:
        print(f"[{outcome:4}] {name}: {detail}")
    if failed:
        print(f"clean-state: {len(failed)} dimension(s) failing — "
              "do not hand off yet")
        return 1
    print("clean-state: all configured dimensions pass")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="pass-gate: the self-owned verification gate")
    parser.add_argument("--root", default=os.getcwd(),
                        help="project root (default: current directory)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create gate/feature_list.json")
    p.add_argument("--project", default="my-project")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add", help="add a new not_started item")
    p.add_argument("--id", required=True)
    p.add_argument("--priority", choices=PRIORITIES, default="p1")
    p.add_argument("--area", default="gate")
    p.add_argument("--title", required=True)
    p.add_argument("--behavior", required=True,
                   help="user-visible behaviour when done")
    p.add_argument("--command", required=True,
                   help="verification command (exit 0 = pass)")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--level", choices=LEVELS, default=None,
                   help="verification strength: assert < unit < "
                        "integration < e2e (descriptive, see D66)")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("start", help="move an item to in_progress (WIP=1)")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("verify", help="run verification for an item")
    p.add_argument("--id")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("block", help="mark an in_progress item blocked")
    p.add_argument("--id", required=True)
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_block)

    p = sub.add_parser("unblock", help="move a blocked item back to in_progress")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_unblock)

    p = sub.add_parser("reopen", help="reopen a passing item (reason required)")
    p.add_argument("--id", required=True)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_reopen)

    p = sub.add_parser("override",
                       help="human override: mark passing with a logged reason")
    p.add_argument("--id", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--by", default=os.environ.get("USER", "human"))
    p.set_defaults(func=cmd_override)

    p = sub.add_parser("status", help="list items and validation errors")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("check-clean", help="five-dimension clean-state check")
    p.set_defaults(func=cmd_check_clean)

    p = sub.add_parser("events", help="show the append-only event log")
    p.add_argument("--last", type=int, default=20)
    p.set_defaults(func=cmd_events)

    p = sub.add_parser("terminate",
                       help="three-layer termination: static -> runtime "
                            "-> system, no skipping")
    p.add_argument("--id", required=True)
    p.add_argument("--stage", required=True, choices=TERMINATION_STAGES)
    p.add_argument("--timeout", type=int, default=None,
                   help="verification timeout in seconds for the runtime "
                        "stage (default: the item's timeout_seconds)")
    p.set_defaults(func=cmd_terminate)

    p = sub.add_parser("handoff", help="generate a handoff draft")
    p.add_argument("--out", default=None,
                   help="write handoff to file instead of stdout")
    p.set_defaults(func=cmd_handoff)

    p = sub.add_parser("run", help="run a host command in an isolated "
                       "git worktree (never auto-merges)")
    p.add_argument("--worktree", required=True,
                   help="worktree name under .worktrees/")
    p.add_argument("--branch", default=None,
                   help="create this branch for the worktree "
                        "(default: detached HEAD, no branch)")
    p.add_argument("host_command", nargs=argparse.REMAINDER,
                   help="host command after --")
    p.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    # Fail fast on a corrupt event log BEFORE any mutation: every
    # mutating command appends an event, so a bad log line would
    # otherwise surface mid-command — after some commands already
    # saved their state change (partial application) or as a raw
    # traceback. Read-only commands (status/events/check-clean/run/
    # handoff) keep working so the operator can still inspect state
    # while repairing the log.
    if args.cmd in ("init", "add", "start", "verify", "block",
                    "unblock", "reopen", "override", "terminate"):
        try:
            _read_events(args.root)
        except EventsLogError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0
    except EventsLogError as e:
        # Explicit failure, not a traceback: the command did not run and
        # no state was changed. The operator repairs the log line first.
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
