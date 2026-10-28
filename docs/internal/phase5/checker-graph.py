#!/usr/bin/env python3
"""Checker for the Phase 5 Maker-Checker demo (docs/internal/phase5).

Runs in the checker's isolated directory (cwd — the loop runner sets it
to <loop-root>/checker). It sees only the artifact copied fresh each
round (graph.template.md), never the maker's notes. Checks, each printed:
  1. tools/loop.py graph-validate passes on the artifact
  2. nodes table has at least 6 rows (maker, verify, timeout-enforcer,
     event-log, approval, merge)
  3. timeout value is present and <= 300 seconds
  4. merge rule is exactly "all must pass"
Exits 0 only when every item passes.
"""

import os
import re
import subprocess
import sys

_HERE = os.path.abspath(__file__)  # <root>/docs/internal/phase5/checker-graph.py
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
# dirname x4: phase5 -> internal -> docs -> repo root

ARTIFACT = "graph.template.md"


def main():
    failures = []
    path = os.path.join(os.getcwd(), ARTIFACT)
    if not os.path.isfile(path):
        print("checker: FAIL — artifact graph.template.md not in checker dir")
        return 1
    text = open(path, encoding="utf-8").read()

    rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "loop.py"),
                         "graph-validate", "--graph", path],
                        capture_output=True, text=True).returncode
    print(f"checker: graph-validate {'PASS' if rc == 0 else 'FAIL'}")
    if rc != 0:
        failures.append("graph-validate")

    nodes_section = text.split("## Nodes", 1)[1].split("## ", 1)[0] if "## Nodes" in text else ""
    rows = [ln for ln in nodes_section.splitlines() if ln.strip().startswith("|")
            and "---" not in ln and "Node" not in ln]
    print(f"checker: nodes rows = {len(rows)} (need >= 6) "
          f"{'PASS' if len(rows) >= 6 else 'FAIL'}")
    if len(rows) < 6:
        failures.append("nodes-rows")

    m = re.search(r"timeout:\s*(\d+)\s*seconds", text, re.IGNORECASE)
    timeout_ok = bool(m) and int(m.group(1)) <= 300
    print(f"checker: timeout value = {m.group(1) if m else 'none'}s "
          f"(need <= 300) {'PASS' if timeout_ok else 'FAIL'}")
    if not timeout_ok:
        failures.append("timeout-value")

    merge_ok = "all must pass" in text.lower()
    print(f"checker: merge rule 'all must pass' {'PASS' if merge_ok else 'FAIL'}")
    if not merge_ok:
        failures.append("merge-rule")

    if failures:
        print(f"checker: FAIL — {', '.join(failures)}")
        return 1
    print("checker: PASS — all items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
