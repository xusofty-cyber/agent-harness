#!/usr/bin/env python3
"""End-to-end dogfood smoke: deploy -> gate init -> add -> start -> verify.

Runs the real deploy-agents.sh into a temp dir, then drives the deployed
project's own pass-gate through one full item lifecycle and asserts the
evidence is written. This is the integration-level counterpart to the
assert-heavy item mix on this repo's own feature list (audit 2026-11-06).
Exits 0 on success, 1 on any failed step. No network access needed.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(cmd, cwd, expect=0):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    if res.returncode != expect:
        print(f"FAIL: {' '.join(map(str, cmd))} exited {res.returncode}\n{res.stdout}\n{res.stderr}")
        sys.exit(1)
    return res


def main():
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "proj"
        run(["bash", str(REPO / "deploy-agents.sh"), str(proj), "--lang", "en"], cwd=td)
        gate = proj / "gate" / "pass-gate.py"
        if not gate.exists():
            print("FAIL: deployed project has no gate/pass-gate.py")
            sys.exit(1)
        py = sys.executable
        run([py, str(gate), "init"], cwd=proj)
        (proj / "hello.txt").write_text("hello\n", encoding="utf-8")
        run([py, str(gate), "add", "--id", "e2e-hello", "--priority", "p1",
             "--area", "core", "--title", "hello file exists",
             "--behavior", "hello.txt contains hello",
             "--command", "grep -q hello hello.txt",
             "--level", "integration"], cwd=proj)
        run([py, str(gate), "start", "--id", "e2e-hello"], cwd=proj)
        run([py, str(gate), "verify", "--id", "e2e-hello"], cwd=proj)
        data = json.loads((proj / "gate" / "feature_list.json").read_text(encoding="utf-8"))
        item = next(i for i in data["items"] if i["id"] == "e2e-hello")
        if item["status"] != "passing" or not item.get("evidence"):
            print(f"FAIL: item not passing with evidence: {item.get('status')}")
            sys.exit(1)
        run([py, str(gate), "check-clean"], cwd=proj)
    print("E2E deploy smoke PASS: deploy -> init -> add -> start -> verify -> evidence -> check-clean")


if __name__ == "__main__":
    main()
