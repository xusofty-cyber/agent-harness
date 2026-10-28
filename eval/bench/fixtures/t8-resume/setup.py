#!/usr/bin/env python3
"""t8-resume setup: leave each arm the kind of session-1 traces its
apparatus would produce. Usage: setup.py <run_dir> <arm>

Merged from v3-yunkai; adapted to the skeleton's gate:
  - arm "dist" renamed "pack" (merged arm naming);
  - state lives in gate/feature_list.json (not the run-dir root);
  - verification is the skeleton's object form
    {"command": ..., "timeout_seconds": ...} with p0/p1/p2 priorities
    (not yunkai's command array / integer priorities);
  - the skeleton's pass-gate requires an item to be in_progress before
    verify, and enforces WIP=1, so the gate branch first blocks the
    umbrella bootstrap (it is in_progress from prep), then starts and
    pre-verifies textkit-slugify. The umbrella stays blocked until the
    agent finishes the sub-features and unblocks it.
"""
import json
import subprocess
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
arm = sys.argv[2]


def verify(feature_id: str) -> None:
    r = subprocess.run(
        [sys.executable, "gate/pass-gate.py", "verify", "--id", feature_id],
        cwd=run_dir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        raise SystemExit(f"t8 gate setup: pre-verify of {feature_id} failed")


if arm == "bare":
    p = run_dir / "textkit.py"
    note = ('# Session note: slugify is done and its tests pass. Still TODO:\n'
            '# truncate_middle and word_wrap (stubs). tests_textkit.py is the spec.\n')
    p.write_text(note + p.read_text(encoding="utf-8"), encoding="utf-8")

elif arm in ("pack", "dist-slim"):
    (run_dir / "SESSION_STATE.md").write_text(
        "# Session notes (session 1)\n\n"
        "- slugify: implemented in textkit.py, its tests pass.\n"
        "- Remaining: truncate_middle, then word_wrap. Both are stubs\n"
        "  raising NotImplementedError; tests_textkit.py is the spec.\n"
        "- Nothing blocked. Run the full suite to see where things stand.\n",
        encoding="utf-8")

elif arm == "gate":
    fl_path = run_dir / "gate" / "feature_list.json"
    data = json.loads(fl_path.read_text(encoding="utf-8"))
    boot = data["items"][0]
    boot["title"] = "Full textkit suite green (resume task complete)"
    boot["user_visible_behavior"] = ("All three textkit utilities implemented; "
                                     "python3 -m unittest tests_textkit passes completely.")
    boot["notes"] = "Umbrella item for the resume task; verify after the sub-features."
    boot["priority"] = "p2"
    subs = [
        {"id": "textkit-slugify", "area": "textkit", "priority": "p0",
         "title": "slugify implemented (session 1)",
         "user_visible_behavior": "slugify passes TestSlugify.",
         "status": "not_started",
         "verification": {"command": "python3 -m unittest tests_textkit.TestSlugify",
                          "timeout_seconds": 300},
         "evidence": None, "notes": "Completed in session 1; verified at prep time."},
        {"id": "textkit-truncate", "area": "textkit", "priority": "p1",
         "title": "truncate_middle implemented",
         "user_visible_behavior": "truncate_middle passes TestTruncateMiddle.",
         "status": "not_started",
         "verification": {"command": "python3 -m unittest tests_textkit.TestTruncateMiddle",
                          "timeout_seconds": 300},
         "evidence": None, "notes": "Stub at session-1 end."},
        {"id": "textkit-wrap", "area": "textkit", "priority": "p1",
         "title": "word_wrap implemented",
         "user_visible_behavior": "word_wrap passes TestWordWrap.",
         "status": "not_started",
         "verification": {"command": "python3 -m unittest tests_textkit.TestWordWrap",
                          "timeout_seconds": 300},
         "evidence": None, "notes": "Stub at session-1 end."},
    ]
    data["items"] = subs + [boot]
    fl_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Bootstrap is in_progress from prep; block it so slugify can start
    # (WIP=1), then start + pre-verify slugify for real.
    r = subprocess.run(
        [sys.executable, "gate/pass-gate.py", "block", "--id", "bootstrap",
         "--reason", "session 1: umbrella held while sub-features are worked"],
        cwd=run_dir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        raise SystemExit("t8 gate setup: block of bootstrap failed")
    r = subprocess.run(
        [sys.executable, "gate/pass-gate.py", "start", "--id", "textkit-slugify"],
        cwd=run_dir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        raise SystemExit("t8 gate setup: start of textkit-slugify failed")
    verify("textkit-slugify")
    (run_dir / "SESSION_STATE.md").write_text(
        "# SESSION_STATE - t8-resume\n\n"
        "- **Current goal**: finish the three textkit utilities (tests are the spec).\n"
        "- **Done**: textkit-slugify (passing, gate evidence in gate/feature_list.json).\n"
        "- **Held**: bootstrap (blocked) — unblock it after the sub-features pass.\n"
        "- **Next step**: implement truncate_middle (feature textkit-truncate), then word_wrap.\n"
        "- **Blocked on**: nothing.\n"
        "- **Last verification**: python3 -m unittest tests_textkit.TestSlugify - pass (session 1).\n",
        encoding="utf-8")
print(f"t8 setup applied for arm={arm}")
