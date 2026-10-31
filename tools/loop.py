#!/usr/bin/env python3
"""tools/loop.py — Phase 5 Loop runner (v3 §4.6, v2 Phase 5).

Stdlib only. A deterministic orchestrator, not an agent: it runs maker /
verify (or checker) commands round by round, enforces the stop conditions
declared in the goal, and records every round in machine-readable state
plus an append-only event log. It never invents results — a round passes
only when the verify/checker command actually exits 0.

State (per loop, in --root):
  loop-state.json   current state: kind, goal, round, consecutive passes,
                    status, rounds[] (one record per round)
  loop-events.jsonl append-only events: seq, ts, type, detail
  last-failure.log  output tail from the most recent failed maker/verify/checker
                    (passed to the next maker round via LOOP_LAST_FAILURE_FILE
                    and LOOP_LAST_FAILURE_TAIL; removed as soon as a verify
                    round passes)
  maker/            maker working directory (maker-checker kind)
  checker/          checker working directory (isolated copy of artifacts)

Stop conditions (from init, all enforced by the runner):
  --max-rounds N         stop after N rounds without the pass condition
  --consecutive-passes N stop when verify passes N rounds in a row
  --timeout S            per-command timeout (seconds); a timeout is
                         recorded as a failed round, never silently skipped
  --max-seconds S        wall-clock budget for the whole loop
  --require-approval     when the pass condition is met, pause in
                         `awaiting-approval` instead of completing; a human
                         resumes with `approve` (recorded in the log)

Exit codes: 0 = loop complete (or awaiting approval — see status output);
1 = loop ended failed (max rounds / budget exceeded / verify never passed);
2 = usage error.

Usage:
  loop.py init --root DIR --goal-file goal.md --kind goal|maker-checker
      [--goal-id ID] [--max-rounds N] [--consecutive-passes N]
      [--timeout S] [--max-seconds S] [--require-approval]
  loop.py goal-loop --root DIR --maker CMD --verify CMD
  loop.py maker-checker --root DIR --maker CMD --checker CMD
      --artifact PATH [--artifact PATH ...]
  loop.py approve --root DIR --by NAME [--note TEXT]
  loop.py graph-validate --graph FILE
  loop.py status --root DIR
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

VERSION = "5.1.0"


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _state_path(root):
    return os.path.join(root, "loop-state.json")


def _events_path(root):
    return os.path.join(root, "loop-events.jsonl")


def _failure_log_path(root):
    return os.path.join(root, "last-failure.log")


def _load_state(root):
    with open(_state_path(root), encoding="utf-8") as f:
        return json.load(f)


def _save_state(root, state):
    with open(_state_path(root), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _append_event(root, etype, detail):
    path = _events_path(root)
    seq = 0
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    seq = json.loads(line).get("seq", seq) + 1
    ev = {"seq": seq, "ts": _now_iso(), "type": etype, "detail": detail}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def _run_cmd(cmd, cwd, timeout, env_extra):
    """Run one shell command. Returns (returncode, timed_out, duration_s, output_text)."""
    env = {k: v for k, v in os.environ.items() if k not in ("BASH_ENV", "ENV")}
    env.update(env_extra)
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, env=env,
                              capture_output=True, text=True, timeout=timeout)
        combined = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, False, time.monotonic() - started, combined
    except subprocess.TimeoutExpired as e:
        out_s = (e.stdout.decode("utf-8", "replace")
                 if isinstance(e.stdout, bytes) else (e.stdout or ""))
        err_s = (e.stderr.decode("utf-8", "replace")
                 if isinstance(e.stderr, bytes) else (e.stderr or ""))
        combined = f"{out_s}{err_s}\n[TIMEOUT after {timeout}s]"
        return 124, True, time.monotonic() - started, combined


def _round_record(state, phase, cmd, rc, timed_out, duration_s, output_tail=""):
    rec = {"round": state["round"], "phase": phase, "command": cmd,
           "returncode": rc, "timed_out": timed_out,
           "duration_s": round(duration_s, 3)}
    if output_tail:
        rec["output_tail"] = output_tail[-512:]
    return rec


def _finish_round(state, root, verify_rc, verify_timed_out):
    """Update consecutive-pass bookkeeping after a verify/checker round."""
    if verify_rc == 0 and not verify_timed_out:
        state["consecutive_passes"] += 1
        outcome = "pass"
    else:
        state["consecutive_passes"] = 0
        outcome = "timeout" if verify_timed_out else "fail"
    state["rounds"][-1]["outcome"] = outcome
    _append_event(root, "round", {"round": state["round"], "outcome": outcome,
                                  "consecutive_passes": state["consecutive_passes"]})
    return outcome


def _check_stop(state, root):
    """Return (stopped, exit_code). Handles budget, pass, max-rounds.

    Order matters: the wall-clock budget is a hard stop — exceeding it
    fails the loop even if the round just passed (a budget is not
    advisory). The pass condition is checked before max rounds, so a
    loop that meets the pass condition exactly on its last round still
    completes.
    """
    if state.get("max_seconds") and time.time() - state["started_epoch"] > state["max_seconds"]:
        state["status"] = "budget-exceeded"
        state["ended_epoch"] = int(time.time())
        _append_event(root, "budget_exceeded",
                      {"round": state["round"],
                       "elapsed_s": round(time.time() - state["started_epoch"], 1)})
        _save_state(root, state)
        print("loop: failed — wall-clock budget exceeded")
        return True, 1
    if state["consecutive_passes"] >= state["consecutive_passes_required"]:
        if state.get("require_approval") and state["status"] != "awaiting-approval":
            state["status"] = "awaiting-approval"
            _append_event(root, "approval_requested",
                          {"round": state["round"], "reason": "pass condition met"})
            _save_state(root, state)
            print(f"loop: pass condition met at round {state['round']}; "
                  "awaiting human approval (loop.py approve)")
            return True, 0
        state["status"] = "complete"
        state["ended_epoch"] = int(time.time())
        _append_event(root, "complete", {"round": state["round"]})
        _save_state(root, state)
        print(f"loop: complete at round {state['round']} "
              f"({state['consecutive_passes']} consecutive passes)")
        return True, 0
    if state["round"] >= state["max_rounds"]:
        state["status"] = "failed"
        state["ended_epoch"] = int(time.time())
        _append_event(root, "max_rounds", {"round": state["round"]})
        _save_state(root, state)
        print(f"loop: failed — max rounds ({state['max_rounds']}) reached "
              "without the pass condition")
        return True, 1
    _save_state(root, state)
    return False, 0


def _write_failure_log(root, round_no, phase, rc, output_text):
    path = _failure_log_path(root)
    tail = (output_text or "")[-4096:]
    header = f"# Round {round_no} {phase} failed (exit {rc})\n"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + tail)
    except OSError:
        pass
    return tail


def _clear_failure_log(failure_file):
    if os.path.exists(failure_file):
        try:
            os.remove(failure_file)
        except OSError:
            pass


def _run_loop(state, root, maker_cmd, verify_cmd, verify_cwd, artifact_note=None):
    """Shared round engine for goal-loop and maker-checker."""
    timeout = state.get("timeout_s")
    last_failure_tail = ""
    failure_file = os.path.abspath(_failure_log_path(root))
    while True:
        state["round"] += 1
        env_extra = {"LOOP_ROUND": str(state["round"]),
                     "LOOP_ROOT": os.path.abspath(root)}
        if last_failure_tail:
            env_extra["LOOP_LAST_FAILURE_FILE"] = failure_file
            env_extra["LOOP_LAST_FAILURE_TAIL"] = last_failure_tail[-2048:]
        maker_cwd = os.path.join(root, "maker") if state["kind"] == "maker-checker" else root
        rc, timed_out, dur, out = _run_cmd(maker_cmd, maker_cwd, timeout, env_extra)
        state["rounds"].append(
            _round_record(state, "maker", maker_cmd, rc, timed_out, dur,
                          out if (rc != 0 or timed_out) else "")
        )
        if rc != 0 or timed_out:
            last_failure_tail = _write_failure_log(
                root, state["round"], "maker", rc, out
            )
            _append_event(root, "maker_failed" if not timed_out else "maker_timeout",
                          {"round": state["round"], "returncode": rc})
            # A failed maker still counts as a round; verify is skipped and
            # the round is a fail. The loop continues until max rounds.
            state["rounds"][-1]["outcome"] = "timeout" if timed_out else "maker-failed"
            state["consecutive_passes"] = 0
            stopped, code = _check_stop(state, root)
            if stopped:
                return code
            continue
        if artifact_note:
            artifact_note()
        rc, timed_out, dur, v_out = _run_cmd(verify_cmd, verify_cwd, timeout, env_extra)
        state["rounds"].append(
            _round_record(state, "verify", verify_cmd, rc, timed_out, dur,
                          v_out if (rc != 0 or timed_out) else "")
        )
        if rc != 0 or timed_out:
            last_failure_tail = _write_failure_log(
                root, state["round"], "verify", rc, v_out
            )
        else:
            last_failure_tail = ""
            _clear_failure_log(failure_file)
        _finish_round(state, root, rc, timed_out)
        stopped, code = _check_stop(state, root)
        if stopped:
            if code == 0:
                _clear_failure_log(failure_file)
            return code


def cmd_init(args):
    root = args.root
    os.makedirs(root, exist_ok=True)
    if os.path.exists(_state_path(root)):
        print(f"init: {root} already has a loop-state.json (refusing to overwrite)",
              file=sys.stderr)
        return 2
    if not os.path.isfile(args.goal_file):
        print(f"init: goal file not found: {args.goal_file}", file=sys.stderr)
        return 2
    if args.kind == "maker-checker":
        os.makedirs(os.path.join(root, "maker"), exist_ok=True)
        os.makedirs(os.path.join(root, "checker"), exist_ok=True)
    state = {"version": 1, "kind": args.kind,
             "goal_id": args.goal_id or os.path.splitext(os.path.basename(args.goal_file))[0],
             "goal_file": os.path.abspath(args.goal_file),
             "status": "running", "round": 0, "consecutive_passes": 0,
             "max_rounds": args.max_rounds,
             "consecutive_passes_required": args.consecutive_passes,
             "timeout_s": args.timeout, "max_seconds": args.max_seconds,
             "require_approval": bool(args.require_approval),
             "started_epoch": int(time.time()), "ended_epoch": None, "rounds": []}
    _save_state(root, state)
    _append_event(root, "init", {"kind": args.kind, "goal_id": state["goal_id"],
                                 "max_rounds": args.max_rounds,
                                 "consecutive_passes_required": args.consecutive_passes,
                                 "timeout_s": args.timeout, "max_seconds": args.max_seconds,
                                 "require_approval": state["require_approval"]})
    print(f"init: {args.kind} loop '{state['goal_id']}' in {root}")
    return 0


def cmd_goal_loop(args):
    state = _load_state(args.root)
    if state["kind"] != "goal":
        print("goal-loop: state kind is not 'goal'", file=sys.stderr)
        return 2
    if state["status"] != "running":
        print(f"goal-loop: loop is {state['status']}, not running", file=sys.stderr)
        return 2
    return _run_loop(state, args.root, args.maker, args.verify, args.root)


def cmd_maker_checker(args):
    import shutil
    state = _load_state(args.root)
    if state["kind"] != "maker-checker":
        print("maker-checker: state kind is not 'maker-checker'", file=sys.stderr)
        return 2
    if state["status"] != "running":
        print(f"maker-checker: loop is {state['status']}, not running", file=sys.stderr)
        return 2
    maker_dir = os.path.join(args.root, "maker")
    checker_dir = os.path.join(args.root, "checker")

    def copy_artifacts():
        # Context isolation: the checker sees only the listed artifacts,
        # copied fresh each round — never the maker's notes or state.
        for rel in args.artifact:
            src = os.path.join(maker_dir, rel)
            dst = os.path.join(checker_dir, rel)
            os.makedirs(os.path.dirname(dst) or checker_dir, exist_ok=True)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                print(f"maker-checker: artifact not found in maker dir: {rel}",
                      file=sys.stderr)
                raise FileNotFoundError(rel)
        _append_event(args.root, "artifacts_copied",
                      {"round": state["round"], "artifacts": list(args.artifact)})

    return _run_loop(state, args.root, args.maker, args.checker, checker_dir,
                     artifact_note=copy_artifacts)


def cmd_approve(args):
    state = _load_state(args.root)
    if state["status"] != "awaiting-approval":
        print(f"approve: loop is {state['status']}, not awaiting-approval",
              file=sys.stderr)
        return 2
    state["status"] = "complete"
    state["ended_epoch"] = int(time.time())
    _append_event(args.root, "approved",
                  {"by": args.by, "note": args.note or "",
                   "round": state["round"]})
    _save_state(args.root, state)
    print(f"loop: approved by {args.by} at round {state['round']}; complete")
    return 0


def cmd_status(args):
    state = _load_state(args.root)
    print(f"loop {state['goal_id']} ({state['kind']}): {state['status']} "
          f"— round {state['round']}/{state['max_rounds']}, "
          f"consecutive passes {state['consecutive_passes']}/"
          f"{state['consecutive_passes_required']}")
    for r in state["rounds"]:
        print(f"  round {r['round']} {r['phase']}: rc={r['returncode']} "
              f"timed_out={r['timed_out']} {r['duration_s']}s"
              + (f" outcome={r['outcome']}" if "outcome" in r else ""))
    return 0


# --- graph validation (heuristic: checks the template's required parts) ---

def _section(text, heading):
    """Return the markdown section under a ## heading (case-insensitive)."""
    lines = text.splitlines()
    out, capture = [], False
    for line in lines:
        if line.startswith("## "):
            capture = line[3:].strip().lower().startswith(heading.lower())
            continue
        if capture:
            if line.startswith("# "):
                break
            out.append(line)
    return "\n".join(out)


def cmd_graph_validate(args):
    errors = []
    try:
        text = open(args.graph, encoding="utf-8").read()
    except OSError as e:
        print(f"graph-validate: cannot read {args.graph}: {e}", file=sys.stderr)
        return 2
    for heading in ("nodes", "edges", "shared state", "routing rules",
                    "approval", "timeout", "fan-out"):
        if not _section(text, heading).strip():
            errors.append(f"missing or empty section: ## {heading}")
    nodes = _section(text, "nodes")
    kinds = {"agent": False, "deterministic": False, "human": False}
    for kind in kinds:
        if kind in nodes.lower():
            kinds[kind] = True
    for kind, present in kinds.items():
        if not present:
            errors.append(f"nodes table has no '{kind}' node kind")
    approval = _section(text, "approval")
    for kw in ("what happened", "what changed", "why human", "approve", "reject"):
        if kw not in approval.lower():
            errors.append(f"approval node lacks: {kw}")
    timeout = _section(text, "timeout")
    import re
    if not re.search(r"\d+\s*(s|sec|seconds|ms)", timeout.lower()):
        errors.append("timeout rule has no numeric timeout value")
    fanout = _section(text, "fan-out")
    if "merge" not in fanout.lower():
        errors.append("fan-out section states no merge rule")
    elif "all must pass" not in fanout.lower() and "any one passes" not in fanout.lower() \
            and "one passes" not in fanout.lower():
        errors.append("merge rule must be 'all must pass' or 'any one passes'")
    if errors:
        for e in errors:
            print(f"graph-validate: FAIL — {e}")
        return 1
    print(f"graph-validate: OK — {args.graph}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="loop.py", description="Phase 5 Loop runner (stdlib only).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create loop state from a goal file")
    p.add_argument("--root", required=True)
    p.add_argument("--goal-file", required=True)
    p.add_argument("--kind", choices=["goal", "maker-checker"], required=True)
    p.add_argument("--goal-id")
    p.add_argument("--max-rounds", type=int, default=10)
    p.add_argument("--consecutive-passes", type=int, default=2)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--max-seconds", type=int, default=0)
    p.add_argument("--require-approval", action="store_true")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("goal-loop", help="run Goal Loop rounds")
    p.add_argument("--root", required=True)
    p.add_argument("--maker", required=True)
    p.add_argument("--verify", required=True)
    p.set_defaults(fn=cmd_goal_loop)

    p = sub.add_parser("maker-checker", help="run Maker-Checker rounds")
    p.add_argument("--root", required=True)
    p.add_argument("--maker", required=True)
    p.add_argument("--checker", required=True)
    p.add_argument("--artifact", action="append", required=True)
    p.set_defaults(fn=cmd_maker_checker)

    p = sub.add_parser("approve", help="record human approval")
    p.add_argument("--root", required=True)
    p.add_argument("--by", required=True)
    p.add_argument("--note")
    p.set_defaults(fn=cmd_approve)

    p = sub.add_parser("graph-validate", help="validate a graph.md")
    p.add_argument("--graph", required=True)
    p.set_defaults(fn=cmd_graph_validate)

    p = sub.add_parser("status", help="print loop state")
    p.add_argument("--root", required=True)
    p.set_defaults(fn=cmd_status)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
