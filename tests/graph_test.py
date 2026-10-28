#!/usr/bin/env python3
"""Tests for gate/graph.py (merged from v3-yunyi, Phase 5).

Run: python3 tests/graph_test.py
Each test builds a scratch git repo in a temp dir; nothing here
touches the real repo or main. Stdlib only.
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "gate" / "graph.py"


def make_repo(tmp):
    repo = tmp / "repo"
    repo.mkdir()

    def sh(*a, cwd=None):
        return subprocess.run(a, cwd=cwd or repo, capture_output=True, text=True)

    sh("git", "init", "-q", "-b", "main")
    sh("git", "config", "user.email", "t@localhost")
    sh("git", "config", "user.name", "t")
    (repo / "base.txt").write_text("base\n")
    sh("git", "add", "-A")
    sh("git", "commit", "-qm", "base")
    return repo


def run_graph(tmp, repo, spec, result="result", approval=None,
              state_name="state.jsonl", timeout=None, force=False):
    spec_path = tmp / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    approval_path = tmp / "approval.json"
    if approval is not None:
        approval_path.write_text(json.dumps(approval), encoding="utf-8")
    cmd = [sys.executable, str(GRAPH), "run", "--spec", str(spec_path),
           "--repo", str(repo), "--base", "main", "--result", result,
           "--approval", str(approval_path), "--state", str(tmp / state_name)]
    if timeout is not None:
        cmd += ["--timeout", str(timeout)]
    if force:
        cmd += ["--force"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    states = []
    sp = tmp / state_name
    if sp.exists():
        states = [json.loads(l) for l in sp.read_text().strip().splitlines() if l.strip()]
    return proc, states


def task(tid, filename, content, layer="implementation"):
    return {"id": tid,
            "command": f"printf '%s' '{content}' > {filename}",
            "verification": f"test -f {filename}",
            "failure_layer": layer}


def test_fanout_isolation_and_fanin_merge():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        spec = {"tasks": [task("a", "a.txt", "A"), task("b", "b.txt", "B")],
                "approval_timeout_s": 30}
        proc, states = run_graph(tmp, repo, spec, approval={"decision": "approve"})
        assert proc.returncode == 0, proc.stdout + proc.stderr
        # Result branch has both files; base branch has neither.
        out = subprocess.run(["git", "show", "result:a.txt"], cwd=repo, capture_output=True, text=True)
        assert out.stdout == "A"
        out = subprocess.run(["git", "show", "result:b.txt"], cwd=repo, capture_output=True, text=True)
        assert out.stdout == "B"
        out = subprocess.run(["git", "show", "main:a.txt"], cwd=repo, capture_output=True, text=True)
        assert out.returncode != 0
        # Worktrees isolated: task a's worktree never saw b.txt.
        assert not (repo / ".worktrees" / "a" / "b.txt").exists()
        assert any(s["node"] == "done" for s in states)


def test_fanin_failure_no_merge_fallback_to_layer():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        bad = {"id": "bad", "command": "exit 1", "verification": "exit 1",
               "failure_layer": "verification"}
        spec = {"tasks": [task("a", "a.txt", "A"), bad], "approval_timeout_s": 30}
        proc, states = run_graph(tmp, repo, spec, approval={"decision": "approve"})
        assert proc.returncode == 1
        assert not any(s["node"] == "fan-in" and s.get("outcome") == "merged" for s in states)
        fb = [s for s in states if s["node"] == "fallback" and s["task_id"] == "bad"]
        assert fb and fb[0]["route"] == "re-verify", fb
        out = subprocess.run(["git", "rev-parse", "--verify", "result"], cwd=repo, capture_output=True, text=True)
        assert out.returncode != 0


def test_approval_timeout_fires():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        spec = {"tasks": [task("a", "a.txt", "A")], "approval_timeout_s": 1}
        proc, states = run_graph(tmp, repo, spec, approval=None)
        assert proc.returncode == 1
        assert any(s["node"] == "approve" and s.get("stop_reason") == "approval_timeout" for s in states)


def test_approval_reject_blocks():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        spec = {"tasks": [task("a", "a.txt", "A")], "approval_timeout_s": 30}
        proc, states = run_graph(tmp, repo, spec, approval={"decision": "reject"})
        assert proc.returncode == 1
        assert any(s["node"] == "approve" and s.get("outcome") == "reject" for s in states)


def test_fanin_merge_conflict_blocks_never_reports_merged():
    # P0-2: two tasks editing the same file's first line both verify,
    # but the second merge conflicts. The run must exit non-zero,
    # never emit fan-in merged or done, and leave the conflict visible.
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        (repo / "shared.txt").write_text("line1\n")
        subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "shared"], cwd=repo,
                       capture_output=True)
        spec = {"tasks": [task("a", "shared.txt", "A"),
                          task("b", "shared.txt", "B")],
                "approval_timeout_s": 30}
        proc, states = run_graph(tmp, repo, spec, approval={"decision": "approve"})
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert "blocked" in proc.stdout
        assert "graph done" not in proc.stdout
        assert not any(s["node"] == "fan-in" and s.get("outcome") == "merged"
                       for s in states)
        assert not any(s["node"] == "done" for s in states)
        assert any(s["node"] == "fan-in" and s.get("outcome") == "blocked"
                   and s.get("stop_reason") == "merge_conflict"
                   for s in states)
        out = subprocess.run(["git", "status", "--porcelain"], cwd=repo,
                             capture_output=True, text=True)
        assert "UU shared.txt" in out.stdout, out.stdout


def test_result_branch_protection():
    # P1-6: --result main merges into main (forbidden); an existing
    # result branch is refused without --force and rebuilt with it.
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        spec = {"tasks": [task("a", "a.txt", "A")], "approval_timeout_s": 30}
        proc, states = run_graph(tmp, repo, spec, result="main",
                                 approval={"decision": "approve"})
        assert proc.returncode == 1
        assert any(s["node"] == "fan-in" and s.get("outcome") == "blocked"
                   for s in states)
        log = subprocess.run(["git", "log", "--oneline", "main"], cwd=repo,
                             capture_output=True, text=True)
        assert len(log.stdout.strip().splitlines()) == 1  # base only
        # Existing branch without --force: blocked.
        subprocess.run(["git", "branch", "taken"], cwd=repo,
                       capture_output=True)
        proc, _ = run_graph(tmp, repo, spec, result="taken",
                            approval={"decision": "approve"})
        assert proc.returncode == 1
        assert "already exists" in proc.stdout
        # Same branch with --force: rebuilt.
        proc, states = run_graph(tmp, repo, spec, result="taken",
                                 approval={"decision": "approve"},
                                 force=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        out = subprocess.run(["git", "show", "taken:a.txt"], cwd=repo,
                             capture_output=True, text=True)
        assert out.stdout == "A"


def test_command_timeout_fails_fast():
    # Merge fix: a hanging task command must fail the fan-out on the
    # --timeout instead of hanging the graph (yunyi's _sh had no timeout).
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        repo = make_repo(tmp)
        hanging = {"id": "hang", "command": "sleep 30", "verification": "true",
                   "failure_layer": "implementation"}
        spec = {"tasks": [hanging], "approval_timeout_s": 30}
        started = time.time()
        proc, states = run_graph(tmp, repo, spec, approval={"decision": "approve"},
                                 timeout=2)
        elapsed = time.time() - started
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert elapsed < 15, f"timeout did not fire fast: {elapsed:.1f}s"
        assert any(s["node"] == "fan-out" and s["task_id"] == "hang"
                   and s["outcome"] == "failed" for s in states)
        assert not any(s["node"] == "fan-in" and s.get("outcome") == "merged"
                       for s in states)


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
    print("all graph tests passed")


if __name__ == "__main__":
    main()
