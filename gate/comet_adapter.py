#!/usr/bin/env python3
"""comet_adapter.py — bridge between the Comet runtime and the gate (merged from v3-yunkai).

Comet is an optional adapter for this repo's gate, not its core. This
tool imports verification artifacts produced by a Comet run into a
feature's record as *external evidence*:

    python3 gate/comet_adapter.py import --comet-dir docs/comet/<change> \
        --feature <id> [--file gate/feature_list.json]
    python3 gate/comet_adapter.py map [--root .]

Importing never changes a feature's status: `passing` still requires
pass-gate.py to execute the feature's own verification commands. The
import exists so Comet's work is visible in the gate's audit trail
(events.jsonl) instead of living in a parallel universe.

`map` lists candidate Comet change directories (docs/comet/*,
openspec/changes/*) and suggests feature ids for them.
Standard library only.

Porting changes vs yunkai (which used a root-level feature_list.json
with a `features` array): the default file is gate/feature_list.json,
the top-level key is `items` (skeleton schema), and the imported
records land in the item's `external_evidence` array, which the
skeleton schema declares as an optional property (see
gate/feature_list.schema.json) so the list stays schema-valid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def find_evidence(comet_dir: Path) -> list[Path]:
    hits = []
    for p in sorted(comet_dir.rglob("*")):
        if p.is_file() and ("verif" in p.name.lower() or p.name.lower() == "verify-result.json"):
            hits.append(p)
    return hits


def _next_seq(events_path: Path) -> int:
    """Next event seq for the gate log: max integer seq + 1.

    Events must carry the gate format (seq/ts/actor/event/item_id/
    detail) or pass-gate.py's §3k check flags them and its append
    logic cannot order them. A corrupt log line fails here, BEFORE
    the feature list is touched, so an import never half-applies.
    """
    seq = 1
    if not events_path.exists():
        return seq
    for lineno, line in enumerate(
            events_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(
                f"gate/events.jsonl line {lineno} is not valid JSON; "
                f"repair or remove that line first — no state was changed")
        if isinstance(rec, dict) and isinstance(rec.get("seq"), int):
            seq = max(seq, rec["seq"] + 1)
    return seq


def cmd_import(args) -> int:
    list_path = Path(args.file)
    comet_dir = Path(args.comet_dir)
    if not comet_dir.is_dir():
        print(f"error: comet dir not found: {comet_dir}", file=sys.stderr)
        return 2
    evidence_files = find_evidence(comet_dir)
    if not evidence_files:
        print(f"error: no verification artifacts (*verif*) found under {comet_dir}", file=sys.stderr)
        return 1
    data = json.loads(list_path.read_text(encoding="utf-8-sig"))
    item = next((f for f in data["items"] if f.get("id") == args.feature), None)
    if item is None:
        print(f"error: no feature '{args.feature}' in {list_path}", file=sys.stderr)
        return 2
    try:
        seq = _next_seq(list_path.parent / "events.jsonl")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    imported = []
    for p in evidence_files:
        digest = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        imported.append({"source": "comet", "path": str(p), "sha256_16": digest, "imported_at": now()})
    item.setdefault("external_evidence", []).extend(imported)
    tmp = list_path.with_suffix(list_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(list_path)
    with (list_path.parent / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"seq": seq, "ts": now(),
                            "actor": "comet_adapter",
                            "event": "external_evidence_imported",
                            "item_id": args.feature,
                            "detail": f"imported {len(imported)} comet "
                                      f"artifact(s) as external evidence: "
                                      f"{[i['path'] for i in imported]}"},
                           ensure_ascii=False) + "\n")
    print(f"imported {len(imported)} comet artifact(s) into feature '{args.feature}' as external evidence.")
    print("note: status unchanged — passing still requires `pass-gate.py verify`.")
    return 0


def cmd_map(args) -> int:
    root = Path(args.root)
    candidates = []
    for base in [root / "docs" / "comet", root / "openspec" / "changes", root / ".comet"]:
        if base.is_dir():
            candidates += [d for d in sorted(base.iterdir()) if d.is_dir()]
    if not candidates:
        print("no comet change directories found (docs/comet, openspec/changes, .comet)")
        return 0
    for d in candidates:
        slug = re.sub(r"[^a-z0-9]+", "-", d.name.lower()).strip("-")
        print(f"{d}  ->  suggested feature id: {slug}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="comet <-> gate adapter")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("import")
    i.add_argument("--comet-dir", required=True)
    i.add_argument("--feature", required=True)
    i.add_argument("--file", default="gate/feature_list.json")
    m = sub.add_parser("map")
    m.add_argument("--root", default=".")
    args = ap.parse_args()
    return {"import": cmd_import, "map": cmd_map}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
