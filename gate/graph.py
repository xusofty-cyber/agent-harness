#!/usr/bin/env python3
"""graph.py — Graph execution on top of gate/ (v3 Phase 5, merged from v3-yunyi).

Blueprint: docs/internal/graph.md. Nodes, edges, shared state and
the merge rule in that document are this program's contract.

Usage:
    python3 gate/graph.py run --spec <spec.json> --repo <path>
        --base <branch> --result <branch> --approval <file>
        [--state <file>] [--timeout <seconds>]

Spec JSON fields:
    tasks: [{id, command, verification, failure_layer}]
        command runs in the task's own worktree (on its own branch
        from --base); verification runs in the same worktree after
        it. failure_layer is one of spec|implementation|
        verification and decides the fallback route on failure.
    approval_timeout_s: seconds to wait for the approval file
        (default 300)

Flow: plan -> fan-out -> fan-in -> approve -> done.
- fan-out is SERIAL (one task after another), not parallel: the
  isolation unit is the worktree+branch, not concurrency.
- fan-in merge rule ALL: every task must verify, else NO merge
  and the run is blocked; each failed task is routed to its
  declared failure layer's node (fallback), never blanket back
  to implementation. The route is recorded only — a failed task
  is never retried or re-run by the graph itself.
- approve waits for --approval to contain {"decision":
  "approve"|"reject"}; no file within the timeout -> blocked with
  stop_reason approval_timeout.
- Merging always targets --result, never main and never --base.
  The result branch is kept for inspection either way.
- Fan-in checks every git return code: a failed merge is recorded
  as blocked (never "merged"/"done") and the run exits non-zero.
  --result must not be main, --base, or the checked-out branch,
  and must not already exist unless --force is given: silently
  deleting and rebuilding a user-named branch used to be possible
  (and --result main used to merge straight into main).

State: transitions go to the file given by --state (default:
<repo>/graph-state.jsonl, so state never scatters into the
caller's working directory). Each line: {node, task_id, outcome,
verification_exit, failure_layer, route, merge_branch, approval,
stop_reason}.

Merge adaptations vs. the v3-yunyi original:
- every command/verification run carries a timeout (--timeout,
  default 300s, aligned with the loop's per-command timeout): a
  hanging command fails the fan-out instead of hanging the graph;
- --state defaults to <repo>/graph-state.jsonl instead of the
  caller's current directory.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def _sh(args, cwd, env=None, timeout=300):
    """Run a command; a timeout is a failure (exit 124), never a hang."""
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                              env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args, 124, stdout="",
            stderr=f"timed out after {timeout}s")


def _emit(state_path, rec):
    with state_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{rec['node']}: {rec.get('task_id', '')} {rec.get('outcome', '')} {rec.get('route', '')} {rec.get('stop_reason', '')}".strip())


def cmd_run(args) -> int:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    repo = Path(args.repo)
    state_path = Path(args.state) if args.state else repo / "graph-state.jsonl"
    if state_path.exists():
        state_path.unlink()
    _emit(state_path, {"node": "plan", "outcome": "recorded",
                       "merge_branch": args.result})
    results = {}
    for task in spec["tasks"]:
        tid = task["id"]
        branch = f"graph-{tid}"
        wt = repo / ".worktrees" / tid
        _sh(["git", "worktree", "remove", "--force", str(wt)], repo)
        _sh(["git", "branch", "-D", branch], repo)
        proc = _sh(["git", "worktree", "add", str(wt), "-b", branch, args.base], repo)
        if proc.returncode != 0:
            results[tid] = {"outcome": "failed", "verification_exit": None,
                            "failure_layer": task.get("failure_layer", "implementation")}
            _emit(state_path, {"node": "fan-out", "task_id": tid, "outcome": "failed",
                               "failure_layer": results[tid]["failure_layer"]})
            continue
        cmd = _sh(["bash", "-c", task["command"]], wt, timeout=args.timeout)
        ver = _sh(["bash", "-c", task["verification"]], wt, timeout=args.timeout)
        ok = cmd.returncode == 0 and ver.returncode == 0
        results[tid] = {"outcome": "passed" if ok else "failed",
                        "verification_exit": ver.returncode,
                        "failure_layer": task.get("failure_layer", "implementation")}
        _emit(state_path, {"node": "fan-out", "task_id": tid,
                           "outcome": results[tid]["outcome"],
                           "verification_exit": ver.returncode,
                           "failure_layer": results[tid]["failure_layer"]})
        if ok:
            _sh(["git", "add", "-A"], wt)
            _sh(["git", "-c", "user.name=graph", "-c", "user.email=graph@localhost",
                 "commit", "-qm", f"graph task {tid}"], wt)
    all_pass = all(r["outcome"] == "passed" for r in results.values()) and bool(results)
    if not all_pass:
        for tid, r in results.items():
            if r["outcome"] == "failed":
                route = {"spec": "plan", "implementation": "maker",
                         "verification": "re-verify"}.get(r["failure_layer"], "maker")
                _emit(state_path, {"node": "fallback", "task_id": tid,
                                   "outcome": "blocked", "failure_layer": r["failure_layer"],
                                   "route": route})
        _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                           "stop_reason": "not_all_tasks_passed_no_merge"})
        print("graph blocked: not all tasks passed, no merge")
        return 1
    # P0-2/P1-6: the result branch is user-named, never implicit.
    # Refuse to merge onto main, onto --base, onto the checked-out
    # branch, or onto an existing branch (unless --force explicitly
    # says the operator wants that branch rebuilt). Every git call
    # below checks its return code: a failed step is blocked, never
    # reported as merged/done.
    current = _sh(["git", "branch", "--show-current"], repo)
    current_branch = current.stdout.strip() if current.returncode == 0 else ""
    if args.result in ("main", args.base, current_branch):
        _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                           "stop_reason": "result_branch_forbidden"})
        print(f"graph blocked: --result {args.result!r} must not be main, "
              f"--base ({args.base}), or the checked-out branch "
              f"({current_branch})")
        return 1
    result_exists = _sh(["git", "show-ref", "--verify",
                         f"refs/heads/{args.result}"], repo).returncode == 0
    if result_exists and not args.force:
        _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                           "stop_reason": "result_branch_exists"})
        print(f"graph blocked: result branch {args.result!r} already "
              f"exists; re-run with --force to rebuild it")
        return 1
    if result_exists:
        proc = _sh(["git", "branch", "-D", args.result], repo)
        if proc.returncode != 0:
            _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                               "stop_reason": "result_branch_delete_failed"})
            print(f"graph blocked: could not delete existing result "
                  f"branch {args.result!r}: {proc.stderr.strip()[:200]}")
            return 1
    proc = _sh(["git", "checkout", "-b", args.result, args.base], repo)
    if proc.returncode != 0:
        _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                           "stop_reason": "result_checkout_failed"})
        print(f"graph blocked: could not check out result branch "
              f"{args.result!r} from {args.base}: "
              f"{proc.stderr.strip()[:200]} (if a previous run left a "
              f"merge in progress, resolve it or run "
              f"`git merge --abort` first)")
        return 1
    for task in spec["tasks"]:
        proc = _sh(["git", "merge", "--no-ff", "-qm",
                    f"merge graph-{task['id']}",
                    f"graph-{task['id']}"], repo)
        if proc.returncode != 0:
            conflicted = _sh(["git", "diff", "--name-only",
                              "--diff-filter=U"], repo).stdout.strip()
            _emit(state_path, {"node": "fan-in", "outcome": "blocked",
                               "task_id": task["id"],
                               "stop_reason": "merge_conflict"})
            print(f"graph blocked: merge of graph-{task['id']} failed "
                  f"(conflicted: {conflicted or 'unknown'}); the repo "
                  f"is left mid-merge for inspection — resolve it or "
                  f"run `git merge --abort`. No merged/done is reported")
            return 1
    _emit(state_path, {"node": "fan-in", "outcome": "merged",
                       "merge_branch": args.result})
    approval_path = Path(args.approval)
    deadline = time.time() + float(spec.get("approval_timeout_s", 300))
    decision = None
    while time.time() < deadline:
        if approval_path.exists():
            try:
                decision = json.loads(approval_path.read_text(encoding="utf-8")).get("decision")
            except (ValueError, OSError):
                decision = None
            if decision in ("approve", "reject"):
                break
        time.sleep(0.5)
    if decision is None:
        _emit(state_path, {"node": "approve", "outcome": "blocked",
                           "approval": "timeout", "stop_reason": "approval_timeout"})
        print("graph blocked: approval timeout")
        return 1
    _emit(state_path, {"node": "approve", "outcome": decision, "approval": decision})
    if decision == "approve":
        _emit(state_path, {"node": "done", "outcome": "done", "merge_branch": args.result})
        print(f"graph done: result branch {args.result}")
        return 0
    _emit(state_path, {"node": "blocked", "outcome": "blocked", "stop_reason": "approval_rejected"})
    print("graph blocked: approval rejected")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph execution on top of gate/")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("run")
    p.add_argument("--spec", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--base", default="main")
    p.add_argument("--result", required=True)
    p.add_argument("--approval", required=True)
    p.add_argument("--state", default=None,
                   help="state file (default: <repo>/graph-state.jsonl)")
    p.add_argument("--timeout", type=int, default=300,
                   help="per-command timeout in seconds for task command/verification (default 300)")
    p.add_argument("--force", action="store_true",
                   help="allow rebuilding an already-existing --result branch (otherwise refused)")
    p.set_defaults(func=cmd_run)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
