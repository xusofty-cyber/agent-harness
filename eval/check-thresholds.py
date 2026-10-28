#!/usr/bin/env python3
"""eval/check-thresholds.py — threshold regression check for bench runs
(merged from v3-yunyi bench/check-thresholds.py).

Reads the run records in eval/results/ (*_{bare,pack,gate,dist-slim}_rep*.json,
the format eval/run-bench.sh writes) and checks, per (task, arm) group:
  - pass 3/3 (every record's outcome == "pass");
  - median verify_attempts <= 4;
  - median duration_s <= 120;
  - false_completion == 0 for every record.
A group with fewer than 3 records is "no conclusion" (never a breach and
never a pass) — thresholds are not judged on insufficient samples.

The t5-t8 matrix records (eval/results/bench-t5-t8-merge-round1/,
{task}__{arm}__r{n}.json, written by evaluate.py) are acceptance-only:
they carry accepted / tests_pass / tests_intact / extras but no
outcome / verify_attempts / duration_s / false_completion. They are
normalized here (accepted -> outcome, task/arm from the filename), so
they join the pass-rate check; the median and false-completion checks
are skipped for those groups (no data), and with 1 record per group
they currently report "no conclusion". Do not read a t5-t8 "ok" as a
full threshold pass — it can only ever be a pass-rate signal.

Thresholds are PROVISIONAL: they are generous headroom (2-4x) over the
2026-10-28 baseline (pooled duration median 6.0s, verify_attempts 1,
false_completion 0/36) and must be re-derived from the merged baseline
after the t5-t8 / dist-slim runs land. Do not tighten them without that
re-derivation.

Exit codes: default is MEASUREMENT mode — a breach prints
"THRESHOLD BREACH: ..." but still exits 0 (a breach is a signal to
investigate, not an automatic failure; bench is a measurement, not a
gate). With --strict, any breach exits 2.

Usage:
    python3 eval/check-thresholds.py [--strict] [--dir DIR]
    EVAL_RESULTS_DIR overrides the records directory.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARMS = ("bare", "pack", "gate", "dist-slim")
PASS_PER_GROUP = 3
MAX_VERIFY_ATTEMPTS_MEDIAN = 4
MAX_DURATION_MEDIAN_S = 120


def _load_records(results_dir: Path) -> list[dict]:
    records = []
    for arm in ARMS:
        for path in sorted(results_dir.glob(f"*_{arm}_rep*.json")):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception as exc:  # noqa: BLE001 - a bad file is check-results.py's job
                print(f"WARN: skipping unreadable record {path.name}: {exc}")
    # t5-t8 matrix records (review 2026-10-29): evaluate.py writes
    # acceptance-only JSONs (accepted / tests_pass / tests_intact /
    # extras) under bench-t5-t8-merge-round1/, named
    # {task}__{arm}__r{n}.json — not the run-bench.sh record shape.
    # Normalize: accepted -> outcome, task/arm from the filename.
    # duration_s / verify_attempts / false_completion stay absent, so
    # the median and false-completion checks skip these groups.
    t5t8_dir = results_dir / "bench-t5-t8-merge-round1"
    if t5t8_dir.is_dir():
        for path in sorted(t5t8_dir.glob("*.json")):
            try:
                rec = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                print(f"WARN: skipping unreadable record {path.name}: {exc}")
                continue
            parts = path.stem.split("__")
            if len(parts) != 3 or not isinstance(rec, dict):
                print(f"WARN: skipping unparseable t5-t8 record {path.name}")
                continue
            rec["task"], rec["arm"] = parts[0], parts[1]
            rec["outcome"] = "pass" if rec.get("accepted") else "fail"
            records.append(rec)
    return records


def check(results_dir: Path) -> list[str]:
    """Return the list of breach descriptions (empty = no breach)."""
    records = _load_records(results_dir)
    by_group: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for rec in records:
        if not isinstance(rec, dict) or "task" not in rec or "arm" not in rec:
            continue
        by_group[(rec["task"], rec["arm"])].append(rec)
    breaches: list[str] = []
    for (task, arm), group in sorted(by_group.items()):
        label = f"{task}/{arm}"
        if len(group) < PASS_PER_GROUP:
            print(f"no conclusion: {label} has {len(group)} record(s) "
                  f"(need {PASS_PER_GROUP})")
            continue
        passed = sum(1 for r in group if r.get("outcome") == "pass")
        if passed < len(group):
            breaches.append(f"{label}: pass {passed}/{len(group)} (need 3/3)")
            continue
        attempts = [r["verify_attempts"] for r in group
                    if isinstance(r.get("verify_attempts"), int)]
        if attempts:
            med = statistics.median(attempts)
            if med > MAX_VERIFY_ATTEMPTS_MEDIAN:
                breaches.append(f"{label}: verify_attempts median {med} "
                                f"(max {MAX_VERIFY_ATTEMPTS_MEDIAN})")
        durations = [r["duration_s"] for r in group
                     if isinstance(r.get("duration_s"), (int, float))]
        if durations:
            med = statistics.median(durations)
            if med > MAX_DURATION_MEDIAN_S:
                breaches.append(f"{label}: duration_s median {med} "
                                f"(max {MAX_DURATION_MEDIAN_S}s)")
        false_done = [r for r in group if r.get("false_completion")]
        if false_done:
            breaches.append(f"{label}: {len(false_done)} false completion(s)")
        if not any(b.startswith(label) for b in breaches):
            print(f"ok: {label} ({len(group)} records, pass 3/3)")
    return breaches


def main() -> int:
    parser = argparse.ArgumentParser(description="bench threshold regression check")
    parser.add_argument("--strict", action="store_true",
                        help="exit 2 on any breach (default: report only, exit 0)")
    parser.add_argument("--dir", default=None,
                        help="records directory (default: eval/results, or $EVAL_RESULTS_DIR)")
    args = parser.parse_args()
    results_dir = Path(args.dir or os.environ.get("EVAL_RESULTS_DIR")
                       or (ROOT / "eval" / "results"))
    breaches = check(results_dir)
    if breaches:
        for breach in breaches:
            print(f"THRESHOLD BREACH: {breach}")
        if args.strict:
            return 2
        print("measurement mode: breach reported, exit 0 (see --strict)")
        return 0
    print("no threshold breach")
    return 0


if __name__ == "__main__":
    sys.exit(main())
