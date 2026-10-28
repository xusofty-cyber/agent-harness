#!/usr/bin/env python3
"""smoke.py — prove the bench fixtures still discriminate (merged from v3-yunkai).

For every fixture task: materialize a pristine bare run and assert
evaluate.py does NOT accept it; apply the reference solution and
assert it IS accepted. A benchmark whose fixtures rot into
always-green or always-red produces confident nonsense — this is the
guard. Used by CI (eval-regression) and by the repo's own gate.

    python3 eval/bench/smoke.py   # exit 0 iff all fixtures discriminate

Scope: t5-t8 only (the tasks this bench owns). t1-t4 are covered by
eval/run-bench.sh + eval/check-results.py.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BENCH = Path(__file__).resolve().parent
TASKS = ["t5-ambiguous", "t6-incomplete-tests", "t7-unwarned", "t8-resume"]


def accepted(run_dir: Path, manifest: Path, task: str) -> bool:
    out = subprocess.run(
        [sys.executable, str(BENCH / "evaluate.py"), "--run-dir", str(run_dir),
         "--manifest", str(manifest), "--task", task],
        capture_output=True, text=True,
    )
    return json.loads(out.stdout)["accepted"]


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="bench-smoke-"))
    ok = True
    for task in TASKS:
        r = subprocess.run(
            [sys.executable, str(BENCH / "prep.py"), "--task", task,
             "--arm", "bare", "--run", "0", "--root", str(root)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"{task}: prep failed: {r.stderr.strip()}")
            ok = False
            continue
        run_dir = Path(r.stdout.strip())
        manifest = root / "_manifests" / f"{task}__bare__r0.json"
        pristine = accepted(run_dir, manifest, task)
        sol = BENCH / "fixtures" / task / "solution"
        for f in sol.rglob("*"):
            if f.is_file():
                shutil.copy(f, run_dir / f.relative_to(sol))
        solved = accepted(run_dir, manifest, task)
        status = "OK" if (pristine is False and solved is True) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"{task}: pristine accepted={pristine} (want False), "
              f"reference accepted={solved} (want True) -> {status}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
