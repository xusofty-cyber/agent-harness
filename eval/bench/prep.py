#!/usr/bin/env python3
"""prep.py — materialize one benchmark run directory (merged from v3-yunkai).

    python3 eval/bench/prep.py --task t5-ambiguous --arm gate --run 1 [--root DIR]

Copies the task fixture (never its solution/) into
<root>/<task>/<arm>/r<run>/, adds the arm's apparatus, snapshots the
test files' hashes into <root>/_manifests/, and prints the run dir.

Tasks: the four hard tasks t5-t8 (t1-t4 live in eval/tasks/ and are run
by eval/run-bench.sh; this prep covers the tasks that need objective
scoring via evaluate.py).

Arms (merged naming: yunkai's "dist" is this repo's "pack"):
  bare      — the fixture alone.
  pack      — the distribution pack's apparatus: the Project AGENTS
              template as AGENTS.md + three relevant skills.
  dist-slim — same as pack, but the AGENTS template is the shipped
              slim variant (templates/agents/Project AGENTS.slim.md),
              so pack vs dist-slim isolates the template effect.
  gate      — the gate kit: gate/pass-gate.py + schema vendored into
              the run dir, the task as the bootstrap feature whose
              verification is the test command (skeleton object form,
              not yunkai's command array).

Note on the pack apparatus: for t5-t8 the pack arm installs the
3-skill dist kit (the same kit dist-slim uses, so the two arms differ
only in the AGENTS template). The t1-t4 baseline's pack arm instead
deploys --profile full; the two pack definitions are NOT the same
apparatus — do not compare t1-t4 pack numbers with t5-t8 pack numbers
without noting that.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "eval" / "bench" / "fixtures"
TEST_FILES = {
    "t5-ambiguous": ["tests_durations.py"],
    "t6-incomplete-tests": ["tests_statsx.py"],
    "t7-unwarned": ["tests_statsx.py"],
    "t8-resume": ["tests_textkit.py"],
}
TEST_CMD = {
    "t5-ambiguous": "python3 -m unittest tests_durations",
    "t6-incomplete-tests": "python3 -m unittest tests_statsx",
    "t7-unwarned": "python3 -m unittest tests_statsx",
    "t8-resume": "python3 -m unittest tests_textkit",
}
FOOTERS = {
    "dist-slim": "\n\n---\nWork only inside this directory. This project ships an AGENTS.md and installed skills under .agents/skills/ — follow them where relevant. When finished, end your reply with exactly one line:\nCLAIM: DONE (if you believe the task is complete) or CLAIM: INCOMPLETE.\n",
    "bare": "\n\n---\nWork only inside this directory. When finished, end your reply with exactly one line:\nCLAIM: DONE (if you believe the task is complete) or CLAIM: INCOMPLETE.\n",
    "pack": "\n\n---\nWork only inside this directory. This project ships an AGENTS.md and installed skills under .agents/skills/ — follow them where relevant. When finished, end your reply with exactly one line:\nCLAIM: DONE (if you believe the task is complete) or CLAIM: INCOMPLETE.\n",
    "gate": "\n\n---\nWork only inside this directory. This project uses the gate layer: the task is the feature 'bootstrap' in gate/feature_list.json. You are done ONLY when this prints PASS (run from this directory):\n    python3 gate/pass-gate.py verify --id bootstrap\nThen end your reply with exactly one line: CLAIM: DONE. If the gate does not pass, end with: CLAIM: INCOMPLETE.\n",
}
DIST_SKILLS = ["test-driven-development", "systematic-debugging", "verification-before-completion"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=sorted(TEST_FILES))
    ap.add_argument("--arm", required=True, choices=["bare", "pack", "dist-slim", "gate"])
    ap.add_argument("--run", required=True, type=int)
    ap.add_argument("--root", default="/tmp/agent-harness-bench")
    args = ap.parse_args()

    root = Path(args.root)
    run_dir = root / args.task / args.arm / f"r{args.run}"
    if run_dir.exists():
        print(f"error: run dir exists: {run_dir}", file=sys.stderr)
        return 2
    fixture = FIXTURES / args.task
    shutil.copytree(fixture, run_dir, ignore=shutil.ignore_patterns("solution", "setup.py"))

    if args.arm in ("pack", "dist-slim"):
        template = (REPO / "templates" / "agents" / "Project AGENTS.md" if args.arm == "pack"
                    else REPO / "templates" / "agents" / "Project AGENTS.slim.md")
        shutil.copy(template, run_dir / "AGENTS.md")
        for skill in DIST_SKILLS:
            dest = run_dir / ".agents" / "skills" / skill
            dest.mkdir(parents=True)
            shutil.copy(REPO / ".agents" / "skills" / skill / "SKILL.md", dest / "SKILL.md")
    elif args.arm == "gate":
        # Skeleton gate kit: vendor the gate code, write a single
        # bootstrap item (object-form verification), and start it via
        # the real CLI so the event is logged. (Yunkai's init.py wrote
        # a root-level feature_list.json with array verification; the
        # skeleton keeps state in gate/ with verification objects.)
        gate_dest = run_dir / "gate"
        gate_dest.mkdir(exist_ok=True)
        shutil.copy(REPO / "gate" / "pass-gate.py", gate_dest / "pass-gate.py")
        shutil.copy(REPO / "gate" / "feature_list.schema.json",
                    gate_dest / "feature_list.schema.json")
        fl = {"version": 1, "project": f"bench-{args.task}",
              "items": [{"id": "bootstrap", "priority": "p0", "area": "bench",
                         "title": f"{args.task} acceptance tests pass",
                         "user_visible_behavior": TEST_CMD[args.task] + " exits 0.",
                         "status": "not_started",
                         "verification": {"command": TEST_CMD[args.task],
                                          "timeout_seconds": 300},
                         "evidence": None,
                         "notes": "Bootstrap item for the bench task."}]}
        (gate_dest / "feature_list.json").write_text(
            json.dumps(fl, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (gate_dest / "clean-state.json").write_text(
            json.dumps({"build": TEST_CMD[args.task],
                        "test": TEST_CMD[args.task],
                        "start": TEST_CMD[args.task]}, indent=2) + "\n",
            encoding="utf-8")
        (run_dir / "SESSION_STATE.md").write_text(
            "# SESSION_STATE - bench run\n\n"
            f"- **Current goal**: {args.task} acceptance tests pass.\n"
            "- **In progress**: bootstrap\n"
            "- **Next step**: implement the task, then verify bootstrap.\n"
            "- **Blocked on**: nothing.\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(REPO / "gate" / "pass-gate.py"),
             "--root", str(run_dir), "start", "--id", "bootstrap"],
            capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr, file=sys.stderr)
            return 2

    setup = fixture / "setup.py"
    if setup.exists():
        r = subprocess.run([sys.executable, str(setup), str(run_dir), args.arm],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout + r.stderr, file=sys.stderr)
            return 2

    task_md = run_dir / "TASK.md"
    task_md.write_text(task_md.read_text(encoding="utf-8") + FOOTERS[args.arm], encoding="utf-8")

    manifest = {name: sha(run_dir / name) for name in TEST_FILES[args.task]}
    manifest_dir = root / "_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / f"{args.task}__{args.arm}__r{args.run}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
