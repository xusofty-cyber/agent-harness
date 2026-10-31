#!/usr/bin/env python3
"""Monthly ablation runner (Phase 4, 4-4).

Ablation = disable one component for a bench run and see if anything
regresses. The process, run once a month:

  1. Pick one component (skill, rule, or check). Selection order: largest
     guide-only skills first (see docs/ablation/README.md).
  2. `ablation.py check --component X` — the dependency gate. If a
     distributable template or hook references X, ablation is BLOCKED:
     removing X would leave a dead reference in deployed projects.
  3. `ablation.py prepare --component X --task <id> --rep <n>` — set up a
     pack-arm run directory via eval/run-bench.sh and remove X from it.
     The agent then performs the task in that directory and records it
     with `run-bench.sh record ... --ablation X`.
  4. `ablation.py report --component X` — compare the ablation runs
     against the bare-arm baseline thresholds (same formulas as
     docs/bench/baseline-2026-10.md) and write
     docs/ablation/ablation-YYYY-MM-<component>.md.

What ablation can and cannot say: a no-regression result is NECESSARY but
NOT sufficient for removal. The bench tasks are small and do not exercise
every skill — passing without X proves X is not needed for these four
tasks, nothing more. Removal always needs the human decision line in the
report filled in by the owner. The script never recommends removal on
bench data alone; it recommends "candidate for removal" at most.

Usage:
    ablation.py check --component <skill>
    ablation.py prepare --component <skill> --task <t1|t2|t3|t4> --rep <n>
    ablation.py report --component <skill>
Exit codes: 0 ok; 1 blocked / no records / regression found by report;
2 usage error.
"""
import json
import re
import statistics
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
RESULTS = ROOT / "eval" / "results"
ABLATION_DIR = RESULTS / "ablation"
REPORTS = ROOT / "docs" / "ablation"

# Files whose references to a skill make removal unsafe: distributable
# rule templates (EN+ZH sources), hooks, gate code. Guide listings do not
# block — the guide is updated as part of a removal.
BLOCKING_SCOPES = [
    "templates/agents/*.md",
    "templates/agents/*.zh.md",
    ".claude/**/*",
    ".agents/hooks/*",
    ".agents/rules/*.md",
    ".workbuddy/**/*",
    ".dsh/*",
    "gate/*.py",
    "gate/*.md",
    "gate/*.json",
]


def skill_size(name: str) -> int:
    d = SKILLS / name
    if not d.is_dir():
        print(f"ablation: no such skill {name!r}", file=sys.stderr)
        sys.exit(2)
    return sum(p.stat().st_size for p in d.rglob("*") if p.is_file())


def blocking_refs(name: str):
    hits = []
    for pat in BLOCKING_SCOPES:
        for p in ROOT.glob(pat):
            if not p.is_file():
                continue
            if re.search(r"\.(zh-tw|fr|de)\.md$", str(p)):
                continue  # frozen translations are not sources
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if f"`{name}`" in text or f" {name} " in text or f"/{name}" in text:
                hits.append(str(p.relative_to(ROOT)))
    return sorted(set(hits))


def do_check(name: str) -> int:
    size = skill_size(name)
    refs = blocking_refs(name)
    print(f"component: {name} ({size} bytes on disk)")
    if refs:
        print("dependency gate: BLOCKED — referenced by distributable files:")
        for r in refs:
            print(f"  - {r}")
        print("Remove the references first, or pick another component.")
        return 1
    print("dependency gate: CLEAR — no template/hook references.")
    print("Note: guide listings are not blocking; update the guides on removal.")
    return 0


def do_prepare(name: str, task: str, rep: int) -> int:
    if do_check(name) != 0:
        return 1
    task_id = {"t1": "t1-bugfix", "t2": "t2-feature",
               "t3": "t3-cross-file", "t4": "t4-docs-sync"}.get(task, task)
    dest = f"/tmp/ablation/{name}/{task_id}/rep{rep}"
    r = subprocess.run(
        ["bash", str(ROOT / "eval" / "run-bench.sh"), "setup",
         "--task", task_id, "--arm", "pack", "--rep", str(rep),
         "--dest", dest],
        capture_output=True, text=True)
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return r.returncode
    removed = []
    for loc in (".agents/skills", ".claude/skills"):
        p = Path(dest) / loc / name
        if p.exists():
            subprocess.run(["rm", "-rf", str(p)], check=True)
            removed.append(f"{loc}/{name}")
    if not removed:
        print(f"ablation: {name} was not deployed in the run dir — "
              "check the profile (pack arm uses --profile full)", file=sys.stderr)
        return 1
    print(f"ablation: removed from run dir: {', '.join(removed)}")
    print(f"ablation: perform the task in {dest}, then record with:")
    print(f"  bash eval/run-bench.sh record --task {task_id} --arm pack "
          f"--rep {rep} --dir {dest} --started <epoch> --ended <epoch> "
          f"--rounds <n> --verify-attempts <n> --outcome <pass|fail> "
          f"--false-completion <0|1> --ablation {name}")
    return 0


def thresholds():
    """Recompute bare-arm thresholds with the Phase 3 formulas."""
    bare = sorted(RESULTS.glob("*_bare_rep*.json"))
    by_task = {}
    for f in bare:
        rec = json.loads(f.read_text(encoding="utf-8"))
        by_task.setdefault(rec["task"], []).append(rec)
    out = {}
    for task, recs in by_task.items():
        durs = [r["duration_s"] for r in recs]
        rounds = [r["rounds"] for r in recs]
        med = statistics.median(durs)
        out[task] = {
            "median_s": med,
            "duration_redline_s": med + 2 * (max(durs) - med),
            "rounds_redline": max(rounds) + 2,
        }
    return out


def do_report(name: str) -> int:
    recs = sorted(ABLATION_DIR.glob(f"*_pack-no-{name}_rep*.json"))
    if not recs:
        print(f"ablation: no records for {name} in {ABLATION_DIR}", file=sys.stderr)
        return 1
    runs = [json.loads(f.read_text(encoding="utf-8")) for f in recs]
    th = thresholds()
    lines = []
    breaches = []
    for r in runs:
        t = th.get(r["task"], {})
        d_breach = r["duration_s"] > t.get("duration_redline_s", float("inf"))
        r_breach = r["rounds"] > t.get("rounds_redline", 99)
        failed = r["outcome"] != "pass"
        fake = r["false_completion"] == 1
        status = "REGRESSION" if (d_breach or r_breach or failed or fake) else "ok"
        if status == "REGRESSION":
            breaches.append((r["task"], r["rep"], status))
        lines.append(
            f"| {r['task']} | {r['rep']} | {r['duration_s']} s "
            f"(red-line {t.get('duration_redline_s')}) | {r['rounds']} "
            f"(red-line {t.get('rounds_redline')}) | {r['outcome']} | "
            f"{r['false_completion']} | {status} |")
    verdict = "REGRESSION — keep the component" if breaches else \
        "NO REGRESSION on these four tasks"
    rec = ("CANDIDATE FOR REMOVAL (bench only — owner must still sign off; "
           "these four tasks do not exercise every skill)"
           if not breaches else "KEEP — regression observed; do not remove.")
    month = date.today().strftime("%Y-%m")
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"ablation-{month}-{name}.md"
    size = skill_size(name)
    out.write_text(
        f"# Ablation {month} — `{name}`\n\n"
        f"Component: `{name}` ({size} bytes on disk). "
        f"Dependency gate: CLEAR (no template/hook references; "
        f"checked {date.today().isoformat()}).\n\n"
        f"Method: pack-arm bench runs with `{name}` removed from the run "
        f"directory (`.agents/skills` and `.claude/skills`). Baseline "
        f"thresholds recomputed from the bare arm with the Phase 3 "
        f"formulas (duration red-line = median + 2×(max−median); rounds "
        f"red-line = max+2; completion floor 11/12; any false completion "
        f"is a breach).\n\n"
        f"## Runs ({len(runs)})\n\n"
        f"| Task | Rep | Duration | Rounds | Outcome | False completion | Status |\n"
        f"|---|---|---|---|---|---|---|\n" +
        "\n".join(lines) + "\n\n"
        f"## Verdict\n\n{verdict}.\n\n"
        f"## Recommendation\n\n{rec}\n\n"
        f"## Human decision\n\nPENDING — owner. Removal requires the owner to fill in this line "
        f"(remove / keep + reason + date). The script never removes "
        f"anything itself.\n",
        encoding="utf-8")
    print(f"wrote {out}")
    print(f"verdict: {verdict}")
    print(f"recommendation: {rec}")
    return 1 if breaches else 0


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "prepare", "report"):
        print(__doc__.split("Usage:")[0], file=sys.stderr)
        print("usage: ablation.py {check|prepare|report} --component <skill> "
              "[--task <t1|t2|t3|t4>] [--rep <n>]", file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    comp = None
    task, rep = None, None
    i = 0
    while i < len(rest):
        if rest[i] == "--component" and i + 1 < len(rest):
            comp, i = rest[i + 1], i + 2
        elif rest[i] == "--task" and i + 1 < len(rest):
            task, i = rest[i + 1], i + 2
        elif rest[i] == "--rep" and i + 1 < len(rest):
            rep, i = int(rest[i + 1]), i + 2
        else:
            print(f"ablation: unknown option {rest[i]}", file=sys.stderr)
            return 2
    if not comp:
        print("ablation: --component is required", file=sys.stderr)
        return 2
    if cmd == "check":
        return do_check(comp)
    if cmd == "prepare":
        if not task or rep is None:
            print("ablation: prepare needs --task and --rep", file=sys.stderr)
            return 2
        return do_prepare(comp, task, rep)
    return do_report(comp)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
