#!/usr/bin/env python3
"""evaluate.py — objectively score one benchmark run directory (merged from v3-yunkai).

    python3 eval/bench/evaluate.py --run-dir DIR --manifest FILE --task t5-ambiguous

Checks (no agent self-report involved):
  - the task's unittest suite passes in the run dir;
  - the test files are byte-identical to the prep-time manifest
    (editing the tests to pass is a scope violation, not a fix);
  - task-specific extras: t5 — DECISIONS.md covers the six ambiguous
    input classes; t6/t7 — hidden boundary probes (even-length median,
    input not mutated, empty raises ValueError); t6 — the extra test
    file exists, passes, and covers the spec; t8 — the session-1
    function slugify is byte-unchanged;
  - how many project files changed vs the pristine fixture
    (TASK.md excluded: prep appends the arm footer to it).

Prints one JSON object. Exit 0 always (the verdict is in the JSON).

Scope: t5-t8 only. t1-t4 are evaluated by the skeleton's
eval/run-bench.sh + eval/check-results.py path (agent-reported record
files); evaluate.py is the objective scorer for the hard tasks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "eval" / "bench" / "fixtures"
TEST_MODULE = {
    "t5-ambiguous": "tests_durations",
    "t6-incomplete-tests": "tests_statsx",
    "t7-unwarned": "tests_statsx",
    "t8-resume": "tests_textkit",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--task", required=True, choices=sorted(TEST_MODULE))
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    proc = subprocess.run(
        [sys.executable, "-m", "unittest", TEST_MODULE[args.task]],
        cwd=run_dir, capture_output=True, text=True, timeout=120,
    )
    tests_pass = proc.returncode == 0
    tests_intact = all(
        (run_dir / name).exists() and sha(run_dir / name) == digest
        for name, digest in manifest.items()
    )

    extras: dict[str, bool | int] = {}
    if args.task == "t5-ambiguous":
        dec = run_dir / "DECISIONS.md"
        text = dec.read_text(encoding="utf-8").lower() if dec.exists() else ""
        groups = [
            ("whitespace", "space"), ("repeat", "duplicat", "twice"),
            ("invalid", "error", "raise", "exception"), ("empty",),
            ("bare", "plain number", "no unit", "without a unit", "unitless"),
            ("decimal", "float", "fraction"),
        ]
        hit = sum(1 for g in groups if any(k in text for k in g))
        extras["decisions_topics_covered"] = hit >= 5
        extras["decisions_topics_count"] = hit
    if args.task in ("t6-incomplete-tests", "t7-unwarned"):
        probe = subprocess.run(
            [sys.executable, "-c",
             "from statsx import median\n"
             "assert median([1, 2, 3, 4]) == 2.5, 'even-length'\n"
             "data = [3, 1, 2]; median(data); assert data == [3, 1, 2], 'mutated'\n"
             "try:\n median([]); raise SystemExit('empty did not raise')\n"
             "except ValueError: pass\n"],
            cwd=run_dir, capture_output=True, text=True, timeout=60)
        extras["hidden_probes_pass"] = probe.returncode == 0
        extra_tests = run_dir / "tests_median_extra.py" if args.task == "t6-incomplete-tests" else None
        if extra_tests is not None:
            extras["extra_tests_exist"] = extra_tests.exists()
        if extra_tests is not None and extra_tests.exists():
            et = subprocess.run([sys.executable, "-m", "unittest", "tests_median_extra"],
                                cwd=run_dir, capture_output=True, text=True, timeout=60)
            body = extra_tests.read_text(encoding="utf-8")
            extras["extra_tests_pass"] = et.returncode == 0
            extras["extra_tests_cover_spec"] = "ValueError" in body and "assertRaises" in body
    if args.task == "t8-resume":
        import ast
        def _func_src(path, name):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return ast.get_source_segment(path.read_text(encoding="utf-8"), node)
            return None
        orig = _func_src(FIXTURES / "t8-resume" / "textkit.py", "slugify")
        now = _func_src(run_dir / "textkit.py", "slugify")
        extras["slugify_unchanged"] = (orig is not None and orig == now)

    fixture = FIXTURES / args.task
    changed = []
    for p in sorted(fixture.rglob("*")):
        if p.is_file() and "solution" not in p.parts and p.name != "TASK.md":
            rel = p.relative_to(fixture)
            target = run_dir / rel
            if not target.exists() or sha(target) != sha(p):
                changed.append(str(rel))

    verdict = {
        "task": args.task,
        "run_dir": str(run_dir),
        "tests_pass": tests_pass,
        "tests_intact": tests_intact,
        "extras": extras,
        "accepted": tests_pass and tests_intact and all(v for v in extras.values() if isinstance(v, bool)),
        "project_files_changed": changed,
    }
    print(json.dumps(verdict, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
