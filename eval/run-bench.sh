#!/bin/bash
# eval/run-bench.sh — Phase 3 benchmark runner (v3 §4.5).
#
# Isolation (P01 English independent-directory method): every run gets a
# fresh directory with its own git repo at the fixed fixture start commit.
# Arms never share a directory, so an agent cannot see another arm's files.
#
#   setup  --task <id> --arm <bare|pack|gate> --rep <n> [--dest DIR]
#          Prepare an isolated run directory and print its path + start time.
#   record --task <id> --arm <bare|pack|gate> --rep <n> --dir DIR \
#          --started <epoch> --ended <epoch> --rounds <n> \
#          --verify-attempts <n> --outcome <pass|fail> \
#          --false-completion <0|1> [--interventions <n>] [--notes TEXT]
#          Append the run record to eval/results/<task>_<arm>_rep<n>.json.
#   smoke  Run the CI smoke: T1 bare setup, start-commit hash check,
#          solution.patch applies, acceptance passes; all task specs valid.
#   measure-load
#          Deploy the pack to a temp dir and report deployed skill count
#          and size (v2 3-4: input to Phase 4 ablation).
#
# The agent executing a run fills in rounds / verify-attempts / outcome
# honestly after finishing; the runner never invents them.
# Solution patches are NEVER copied into a run directory.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURE="$ROOT/eval/fixture"
TASKS="$ROOT/eval/tasks"
RESULTS="$ROOT/eval/results"
START_COMMIT="2e583970fb952158ad83617fe436534abd38295d"
GIT_AUTHOR_NAME="agent-harness bench"
GIT_AUTHOR_EMAIL="bench@agent-harness.local"
GIT_AUTHOR_DATE="2026-10-28T00:00:00+00:00"
GIT_COMMITTER_NAME="agent-harness bench"
GIT_COMMITTER_EMAIL="bench@agent-harness.local"
GIT_COMMITTER_DATE="2026-10-28T00:00:00+00:00"
export GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_AUTHOR_DATE
export GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL GIT_COMMITTER_DATE

usage() {
    echo "usage: run-bench.sh {setup|record|smoke|measure-load} [options]" >&2
    exit 2
}

# Acceptance command for a task id. Must mirror eval/tasks/<id>/task.md.
acceptance() {
    case "$1" in
        t1-bugfix)   echo 'python3 -m pytest tests/test_calc.py::test_subtract -q' ;;
        t2-feature)  echo 'python3 -m pytest tests/test_calc.py::test_power -q && python3 -c "from calc import power; assert power(2,3)==8"' ;;
        t3-cross-file) echo 'python3 -m pytest tests/test_calc.py::test_times tests/test_cli.py -q && ! grep -rn "multiply" --include="*.py" --include="*.md" . && python3 -c "from calc import times; assert times(2,3)==6"' ;;
        t4-docs-sync) echo 'python3 -m pytest tests/test_calc.py::test_divide_rounding -q && grep -qi "round" README.md' ;;
        *) echo "unknown task: $1" >&2; exit 2 ;;
    esac
}

task_id_to_dir() {
    case "$1" in
        t1) echo "t1-bugfix" ;; t2) echo "t2-feature" ;;
        t3) echo "t3-cross-file" ;; t4) echo "t4-docs-sync" ;;
        t1-bugfix|t2-feature|t3-cross-file|t4-docs-sync) echo "$1" ;;
        *) echo "unknown task: $1" >&2; exit 2 ;;
    esac
}

do_setup() {
    local task="" arm="" rep="" dest=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --task) task="$(task_id_to_dir "$2")"; shift 2 ;;
            --arm) arm="$2"; shift 2 ;;
            --rep) rep="$2"; shift 2 ;;
            --dest) dest="$2"; shift 2 ;;
            *) echo "setup: unknown option $1" >&2; exit 2 ;;
        esac
    done
    [ -n "$task" ] && [ -n "$arm" ] && [ -n "$rep" ] || { echo "setup: --task/--arm/--rep required" >&2; exit 2; }
    case "$arm" in bare|pack|gate) ;; *) echo "setup: arm must be bare|pack|gate" >&2; exit 2 ;; esac
    [ -d "$TASKS/$task" ] || { echo "setup: no such task $task" >&2; exit 2; }
    dest="${dest:-/tmp/bench/${task}/${arm}/rep${rep}}"
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -r "$FIXTURE/." "$dest/"
    (cd "$dest" && git init -q && git add -A && git commit -q -m "tinycalc fixture: starting commit for Phase 3 benchmarks")
    local head
    head="$(cd "$dest" && git rev-parse HEAD)"
    if [ "$head" != "$START_COMMIT" ]; then
        echo "setup: start commit mismatch: got $head, want $START_COMMIT" >&2
        exit 1
    fi
    if [ "$arm" = "pack" ] || [ "$arm" = "gate" ]; then
        # Phase 4 (4-1): pack/gate arms deploy --profile full — the
        # distribution pack as shipped before Phase 4 (38 skills). The
        # default profile is minimal (10); using it here would make the
        # pack arm a different comparison than Phase 3 designed. The
        # pack arm was never measured before this change (0/12), so no
        # measured data is redefined by pinning it now.
        bash "$ROOT/deploy-agents.sh" "$dest" --profile full >/tmp/bench-deploy.log 2>&1 || {
            echo "setup: deploy-agents.sh failed (see /tmp/bench-deploy.log)" >&2; exit 1; }
    fi
    if [ "$arm" = "gate" ]; then
        python3 "$ROOT/gate/pass-gate.py" --root "$dest" init --project "bench-$task" --force >/dev/null 2>&1 || {
            echo "setup: pass-gate init failed" >&2; exit 1; }
        python3 "$ROOT/gate/pass-gate.py" --root "$dest" add --id "$task" \
            --title "Benchmark task $task" \
            --behavior "acceptance command exits 0" \
            --command "$(acceptance "$task")" >/dev/null 2>&1 || {
            echo "setup: pass-gate add failed" >&2; exit 1; }
        python3 "$ROOT/gate/pass-gate.py" --root "$dest" start --id "$task" >/dev/null 2>&1 || {
            echo "setup: pass-gate start failed" >&2; exit 1; }
    fi
    local started
    started="$(date +%s)"
    echo "dir=$dest"
    echo "task=$task arm=$arm rep=$rep start_commit=$head started=$started"
    echo "acceptance: $(acceptance "$task")"
}

do_record() {
    local task="" arm="" rep="" dir="" started="" ended="" rounds=""
    local verify_attempts="" outcome="" false_completion="" interventions=0 notes=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --task) task="$(task_id_to_dir "$2")"; shift 2 ;;
            --arm) arm="$2"; shift 2 ;;
            --rep) rep="$2"; shift 2 ;;
            --dir) dir="$2"; shift 2 ;;
            --started) started="$2"; shift 2 ;;
            --ended) ended="$2"; shift 2 ;;
            --rounds) rounds="$2"; shift 2 ;;
            --verify-attempts) verify_attempts="$2"; shift 2 ;;
            --outcome) outcome="$2"; shift 2 ;;
            --false-completion) false_completion="$2"; shift 2 ;;
            --interventions) interventions="$2"; shift 2 ;;
            --notes) notes="$2"; shift 2 ;;
            *) echo "record: unknown option $1" >&2; exit 2 ;;
        esac
    done
    for v in task arm rep dir started ended rounds verify_attempts outcome false_completion; do
        [ -n "${!v}" ] || { echo "record: --${v//_/-} required" >&2; exit 2; }
    done
    case "$outcome" in pass|fail) ;; *) echo "record: outcome must be pass|fail" >&2; exit 2 ;; esac
    case "$false_completion" in 0|1) ;; *) echo "record: false-completion must be 0|1" >&2; exit 2 ;; esac
    local duration=$((ended - started))
    local host model
    host="$(hostname)"
    model="${BENCH_MODEL:-Muse Spark}"
    local out="$RESULTS/${task}_${arm}_rep${rep}.json"
    mkdir -p "$RESULTS"
    python3 - "$out" <<PYEOF
import json, sys
rec = {
    "task": "$task",
    "arm": "$arm",
    "rep": $rep,
    "start_commit": "$START_COMMIT",
    "host": "$host",
    "model": "$model",
    "run_dir": "$dir",
    "started_epoch": $started,
    "ended_epoch": $ended,
    "duration_s": $duration,
    "rounds": $rounds,
    "verify_attempts": $verify_attempts,
    "interventions": $interventions,
    "outcome": "$outcome",
    "false_completion": $false_completion,
    "notes": "$notes",
}
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(rec, f, indent=2, sort_keys=True)
    f.write("\n")
print(f"recorded {sys.argv[1]}: outcome=$outcome duration_s=$duration")
PYEOF
}

do_smoke() {
    local tmp
    tmp="$(mktemp -d)"
    trap "rm -rf '$tmp'" EXIT
    echo "smoke: task specs"
    for d in "$TASKS"/*/; do
        local t
        t="$(basename "$d")"
        for field in start_commit acceptance budget_time budget_rounds; do
            grep -q "$field" "$d/task.md" || { echo "smoke: $t/task.md lacks $field" >&2; exit 1; }
        done
        grep -q "$START_COMMIT" "$d/task.md" || { echo "smoke: $t/task.md start_commit != $START_COMMIT" >&2; exit 1; }
        [ -f "$d/solution.patch" ] || { echo "smoke: $t/solution.patch missing" >&2; exit 1; }
    done
    echo "smoke: T1 bare setup + solution + acceptance"
    local out
    out="$(bash "$0" setup --task t1-bugfix --arm bare --rep 0 --dest "$tmp/t1")"
    echo "$out"
    local dir
    dir="$(echo "$out" | sed -n 's/^dir=//p')"
    (cd "$dir" && git apply "$TASKS/t1-bugfix/solution.patch") || { echo "smoke: solution.patch does not apply" >&2; exit 1; }
    (cd "$dir" && eval "$(acceptance t1-bugfix)") || { echo "smoke: acceptance fails after solution" >&2; exit 1; }
    echo "smoke: OK"
}

do_measure_load() {
    # Phase 4 (4-1): report all three profiles. "deployed_total_bytes"
    # counts the whole deployed directory (rules, templates, hooks);
    # "skills_bytes" counts .agents/skills only. Do not compare the two
    # as if they measured the same thing.
    local tmp
    tmp="$(mktemp -d)"
    trap "rm -rf '$tmp'" EXIT
    for profile in minimal standard full; do
        bash "$ROOT/deploy-agents.sh" "$tmp/pack-$profile" --profile "$profile" >/tmp/bench-deploy.log 2>&1 || {
            echo "measure-load: deploy --profile $profile failed (see /tmp/bench-deploy.log)" >&2; exit 1; }
    done
    python3 - "$tmp" <<'PYEOF'
import json, sys
from pathlib import Path
tmp = Path(sys.argv[1])
out = {}
for profile in ("minimal", "standard", "full"):
    root = tmp / f"pack-{profile}"
    sdir = root / ".agents" / "skills"
    skills = sorted(p for p in sdir.glob("*/SKILL.md")) if sdir.is_dir() else []
    skills_bytes = sum(p.stat().st_size for p in sdir.rglob("*") if p.is_file()) if sdir.is_dir() else 0
    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    out[profile] = {
        "deployed_skill_dirs": len(skills),
        "skills_bytes": skills_bytes,
        "deployed_total_bytes": total,
        "largest_skills": sorted(
            ((p.parent.name, p.stat().st_size) for p in skills),
            key=lambda x: -x[1])[:5],
    }
print(json.dumps(out, indent=2))
PYEOF
}

cmd="${1:-}"
shift || true
case "$cmd" in
    setup) do_setup "$@" ;;
    record) do_record "$@" ;;
    smoke) do_smoke "$@" ;;
    measure-load) do_measure_load "$@" ;;
    *) usage ;;
esac
