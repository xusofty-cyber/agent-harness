# Agent Harness Project Deployment Walkthrough (worked example included)

> **Language / 语言**: **English** | [简体中文](Project%20Deployment%20Walkthrough.zh.md)

> Applies to: agent-harness **v0.7.0** (released 2026-11-06)
> Positioning: this is the step-by-step walkthrough for deploying the
> harness into a real project from zero; it complements the
> specification-oriented *Multi-Tool Deployment and Configuration
> Guide*. Every command below was checked against the v0.7.0
> scripts. The running example is a fictional project **shopapi**
> (Python 3.12 + FastAPI + PostgreSQL, at `~/projects/shopapi`);
> JS and C++ equivalents are given at the key steps.

---

## 0. First, be clear: deployment has two halves

Deploying Agent Harness = **the script scaffolds** + **you fill in
the content**. Both halves are required:

| Part | Done by | Contents |
|---|---|---|
| Scaffolding | `run-pipeline.sh`, automatically | Rule files, host bridges and hooks, skills, gate code, CI/pre-push templates |
| Content | The maintainer (an agent may draft it, you confirm) | Real project facts in the three root documents, gate initialization, the first work items |

Run only the script and the agent receives empty instructions full
of placeholders, while the gate has no items to govern — that is
not a deployment.

---

## 1. Prerequisites

| Dependency | Required? | Notes |
|---|---|---|
| `git` | Yes | To clone the template repo; the target project should be a git repo too |
| `python3` | Yes | The gate (`pass-gate.py`) and pipeline tools are stdlib-only |
| `bash` | Yes on Linux/macOS | On Windows use the PowerShell scripts (see §3.3) |
| `node` | Optional | Needed by host hook scripts (e.g. Claude Code) |
| `cargo` | Optional | Only to install ai-memory cross-tool memory |

The target project needs only two things:

1. A definite root path that you can write to;
2. That you can name its three commands — **how it builds, how it
   is tested (the command that proves the project works), and how
   it starts**. Gate initialization in §5 needs them; decide them
   before you start.

---

## 2. Overview: what the pipeline does

`run-pipeline.sh` orchestrates four stages in order:

```text
Stage 1  deploy   Rules & bridges   → project AGENTS.md / the two memory-doc
                                      scaffolds / host bridges and hooks /
                                      .agents rules and skills / gate/ code /
                                      pre-push + CI gate templates
Stage 2  memory   AI memory setup   → optional; auto-SKIPs when the ai-memory
                                      CLI is absent (normal, not a failure)
Stage 3  skills   Skill check/sync  → verified against skills-lock;
                                      check-only by default, no overwriting
Stage 4  docs     Living-doc impact → checks whether doc↔code traceability
                                      has gone stale
End               Summary table     → each stage recorded honestly as
                                      PASS / SKIP / WARN / FAIL
```

Two mode semantics to remember:

- **Default advisory mode**: a failed stage is recorded `WARN` and
  the pipeline still exits 0 (but never claims PASS);
- **`--strict` mode**: any stage failure is a `FAIL` and the
  pipeline exits 1. Recommended for CI or unattended runs.

Safety semantics for existing files: an existing `AGENTS.md`,
`PROJECT_CONTEXT.md`, or `SESSION_STATE.md` in the target project
is **never overwritten** (the script reports "kept as-is"); global
rules and skills are backed up (`*.bak-<timestamp>`) before
`--update` replaces them.

---

## 3. Run the deployment

### 3.1 Option one: the unified pipeline (recommended)

```bash
# 1) Clone the template repo NEXT TO the target project
#    (do not clone it into the target project)
git clone https://github.com/xusofty-cyber/agent-harness.git
cd agent-harness

# 2) Unattended full run: target = shopapi, template language = English
./run-pipeline.sh --all -y -p ~/projects/shopapi -l en
```

Parameter cheat sheet:

| Flag | Effect |
|---|---|
| `--all` | Run all four stages |
| `-y` | Non-interactive (unattended), no confirmation prompts |
| `-p <path>` | Target project root (default: current directory — **always pass it explicitly**) |
| `-l en` | Template language: `en` / `zh` (Simplified) / `zh-tw` (Traditional); default `en` |
| `-g` | Also deploy/update this machine's global rules (`~/.claude`, `~/.gemini`, `~/.codex`, `~/.dsh`, …) |
| `-u` | Overwrite-update global rules and external skills (automatic backup first) |
| `--strict` | Strict mode: any stage failure fails the pipeline |
| `-k` | Check-only mode (skills only diffed, docs only analysed, nothing written) |
| `--stages deploy,docs` | Run only the named stages (comma-separated: deploy / memory / skills / docs) |

Prefer not to memorize flags? `./run-pipeline.sh` with no arguments
opens the interactive wizard: six steps (language, global rules,
skill sync mode, project path, stage combination, detail level)
driven with arrow keys and spacebar.

### 3.2 Option two: rules and gate only (lightweight)

If you do not want the memory and docs stages yet, call the deploy
script directly:

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --lang en
```

It performs everything in stage 1 (rules, bridges, hooks, skills,
gate code, pre-push/CI templates).

### 3.3 Windows

```powershell
git clone https://github.com/xusofty-cyber/agent-harness.git
cd agent-harness
.\run-pipeline.ps1 -All -Yes -ProjectPath "D:\Projects\shopapi" -Language en
# Or deploy only: .\deploy-agents.ps1 -ProjectPath "D:\Projects\shopapi" -Language en
```

Every Linux command below has a PowerShell twin: swap `.sh` for
`.ps1` and flag style to `-PascalCase`; the feature sets match
one-to-one.

### 3.4 What the target project looks like afterwards (shopapi)

```text
shopapi/
├── AGENTS.md                  ← new: project rules (template, to fill — §4)
├── PROJECT_CONTEXT.md         ← new: durable project facts (template — §4)
├── SESSION_STATE.md           ← new: session breakpoint (template — §4)
├── .gitignore                 ← Harness runtime ignore block appended
│                                 (existing file is extended, not rewritten)
├── .agents/
│   ├── rules/                 ← on-demand sub-rules (engineering, Git,
│   │                             security, token discipline, …)
│   └── skills/                ← skill directories (minimal profile: 15 — §8.1)
├── .claude/                   ← Claude Code bridge and PreToolUse/Stop hooks
├── .agents/hooks.json, etc.   ← Antigravity-family bridges (one set per host)
├── gate/
│   ├── pass-gate.py           ← the gate itself (code only — no item data yet, §5)
│   ├── feature_list.schema.json
│   ├── comet_adapter.py
│   └── init.template.sh       ← gate initialization script
├── (pre-push gate)            ← installed by default: re-runs every passing
│                                 item's verification before a push (bypassable
│                                 via --no-verify, so pair it with CI + branch
│                                 protection)
└── (CI gate template)         ← the same check, running server-side
```

**Deployment is only half done at this point.** The next three
sections are the other half.

### 3.5 Grade before you deploy: scale decides the tier (never default to full)

The full harness ceremony (multi-host bridges, gate items, doc
impact) is a net burden on a small project: a single-maintainer
tool with a dozen source files can end up with more management
files than source files, and every small task pays the process tax
first. Grade the project by "scale × cost of being wrong" before
deploying, and record the tier in the project `AGENTS.md` section
"Scale Grading and Task Grading" (the template ships that section):

| Tier | Rough criteria | Deployment shape |
|---|---|---|
| Lite | ~< 50 source files, single maintainer, no cross-week work | Slim project AGENTS only (the `--profile minimal` slim template) + the project's own tests; gate item flow, check-clean and doc-impact off; bridges only for the one host actually used |
| Standard | Medium or larger, multi-person or cross-week, or one mistake is expensive | The full flow in this guide |

Mis-grading costs are asymmetric: Standard on a small project is a
daily slowness tax; Lite on a large project is expensive exactly
when something breaks. When unsure, start Lite and upgrade after
the first "a mistake slipped through" incident — upgrading is just
an additional deployment, no data is lost.

---

## 4. Essential configuration 1: fill in the three root documents

The three documents have distinct jobs; do not mix them:

| Document | Contents | When to change it |
|---|---|---|
| `AGENTS.md` | Project instructions for the agent: commands, stack, architecture red lines, definition of done | When commands or red lines change |
| `PROJECT_CONTEXT.md` | Durable project facts (SSOT): domain, architecture, module responsibilities, key constraints | When architecture or stack choices materially change |
| `SESSION_STATE.md` | Current session breakpoint, one page max: goal / in progress / next / blocked / last verification | Refresh at the end of every session |

### 4.1 Let the script scan first, then confirm by hand

```bash
cd agent-harness
# Scan git metadata, dependency manifests and CI files; drafts an
# AGENTS.md with inferred project facts and lists what it cannot infer
./deploy-agents.sh ~/projects/shopapi --initialize --lang en
# Report which placeholders are still unfilled
./deploy-agents.sh ~/projects/shopapi --check
```

Caution: framework and script facts found by `--initialize` are
**suggestions**, not verified facts. Project positioning, module
responsibilities and boundaries cannot be inferred — the maintainer
or the on-duty agent must confirm and fill them in.

### 4.2 AGENTS.md required fields, with an example

Required placeholders: project name, business positioning, owners,
repository and default branch, the five command groups (install /
dev / build / test / lint & format), the stack table, and the
architecture red lines.

The commands section of shopapi, filled in:

```bash
# 1. Dependencies
pip install -r requirements.txt        # inside the Python 3.12 venv

# 2. Local development & build
uvicorn app.main:app --reload          # dev server
python -m compileall app               # no separate build step;
                                       # compile check stands in for it

# 3. Tests (must run after changes; keep output terse)
python -m pytest -q                    # full suite
python -m pytest tests/test_orders.py -q   # single file

# 4. Code quality
ruff check . && ruff format --check .
```

Stack table excerpt:

| Category | Choice | Notes |
|---|---|---|
| Language & runtime | Python 3.12 | Type annotations required |
| Core framework | FastAPI 0.11x | Route layer only validates and orchestrates |
| Persistence | PostgreSQL 16 + Redis 7 | Order state machine lives only in PG; Redis is cache-only |

Write the red lines from your project's reality, not from the
template's generic five — a red line should be a project-specific
constraint whose violation causes real damage. For shopapi:
*order amounts are stored as integer cents, never floats; stock
decrement must go through the order service's CAS update*.

Command-section equivalents for other stacks:

| Purpose | JS / Node example | C++ / CMake example |
|---|---|---|
| Install | `pnpm install --frozen-lockfile` | `cmake -B build -DCMAKE_BUILD_TYPE=Release` |
| Build | `pnpm build` | `cmake --build build -j4` |
| Full tests | `pnpm test -- --reporter=dot` | `ctest --test-dir build --output-on-failure` |
| Single-file test | `pnpm test -- src/orders.test.ts` | `ctest --test-dir build -R order_test` |
| Lint | `pnpm lint && pnpm typecheck` | `clang-tidy -p build src/*.cpp` |

### 4.3 PROJECT_CONTEXT.md required fields

One-sentence domain statement, the core module matrix (per module:
responsibility + workflow), repository and branches, runtime and
deployment shape, the stack table, directory responsibilities, key
constraints. Rule: **durable facts only** — "what we are doing this
week" belongs in SESSION_STATE, not here.

### 4.4 SESSION_STATE.md rules

Fixed sections: Goal / In progress / Next / Blocked / Last
verification (plus the header date and project name). Hard rules:
**one page maximum**; `gate/feature_list.json` is authoritative —
where this file disagrees with the list, the list wins; finished
history moves to the CHANGELOG instead of accumulating here. On
first deployment, fill it with the project's true current state.

### 4.5 Directory-level AGENTS.md: never auto-deployed, named one by one (optional)

The third tier of the rules architecture — an `AGENTS.md` inside a
subdirectory — is **generated by no automatic path**. That is a
deliberate design decision, not an omission:

- `run-pipeline.sh` has no directory parameter at all, so the
  pipeline never creates one;
- a regular `deploy-agents.sh` run (without `--initialize`) does
  not either;
- the only generation path is naming a directory explicitly, one
  per invocation:

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --initialize --lang en --directory app/orders
# Windows: .\deploy-agents.ps1 -ProjectPath "D:\Projects\shopapi" -Initialize -DirectoryPath "app/orders"
```

Rules and boundaries:

| Aspect | Behaviour |
|---|---|
| Path | Must be relative, the directory must **already exist**, and it must resolve inside the project (absolute paths or paths escaping the project are rejected) |
| Pairing | `--directory` must accompany `--initialize` or `--check`; alone it errors out. With `--check` it only reports that directory's placeholders and generates nothing |
| Existing file | If the directory already has an `AGENTS.md`, the new draft is written as `AGENTS.generated.md` beside it for review — never an overwrite |
| Content source | The same `init_guidance` scan as the project level (the directory's manifests/scripts are read as local-command suggestions); the boundary sections still need human confirmation |

Why not automatic: a directory-level file records one module's
**micro-boundaries** — its in/out scope, its dependency boundaries
towards other modules, its local fast-test command, large-file
cautions. The script can neither know which subdirectories deserve
their own rules nor scan those boundaries out of the code.
Scattering a placeholder file into every subdirectory would only
mislead the agent with empty instructions, so this tier is opt-in:
the maintainer names directories one at a time and fills each in.

When a directory earns its own file: an independent package in a
monorepo, a module whose stack or red lines differ markedly from
the project's, a high-risk directory (payments, migration scripts).
Filling guidance: write only the **delta against the project
level** (this directory's own scope, boundaries and commands);
reference the project `AGENTS.md` for shared rules instead of
copying them — copied text silently goes stale when the project
file is revised.

---

## 5. Essential configuration 2: initialize the gate (the step everyone misses)

The deploy script copies only the gate **code** into `gate/`; the
item data file `feature_list.json` is **not** created
automatically — initialization is explicit. Run it from the
**target project root**:

```bash
cd ~/projects/shopapi
sh gate/init.template.sh \
  --name shopapi \
  --verify "python -m pytest -q" \
  --start "uvicorn app.main:app --reload" \
  --build "python -m compileall app"
```

What the parameters mean and how to fill them:

| Parameter | Meaning | How to fill it |
|---|---|---|
| `--name` | Project name | Match AGENTS.md |
| `--verify` | **The command that proves the project works** (required) | Exit 0 = the project is healthy; usually the full test suite |
| `--start` | The standard start command (required) | How you run the project day to day |
| `--build` | Build command (optional) | Omit for projects with no build step; that check-clean dimension then reports SKIP |

Note: leaving any parameter empty, or leaving a `<...>` placeholder
in it, **fails initialization outright** instead of scaffolding a
broken project — deliberate fail-closed behaviour. Initialization
also smoke-runs `--verify` once; if the project is currently red,
fix the project first, then initialize.

Outputs:

```text
gate/feature_list.json    ← the item list (skeleton only for now;
                            items are added in §6)
gate/clean-state.json     ← holds the three commands, e.g.:
                            {"build": "python -m compileall app",
                             "test":  "python -m pytest -q",
                             "start": "uvicorn app.main:app --reload"}
SESSION_STATE.md          ← scaffolded here if the deploy stage
                            did not create one
DECISIONS.md              ← a decision-log skeleton, if missing
```

Initialization equivalents for other stacks:

```bash
# JS / Node
sh gate/init.template.sh --name webapp \
  --verify "pnpm test" --start "pnpm dev" --build "pnpm build"

# C++ / CMake
sh gate/init.template.sh --name engine \
  --verify "ctest --test-dir build --output-on-failure" \
  --start "./build/engine --demo" \
  --build "cmake --build build -j4"
```

---

## 6. Essential configuration 3: add items and complete one gate round

The gate's daily vocabulary has four verbs: **add → start → verify
→ check-clean**. Iron rules: only one item may be in progress at a
time (WIP=1); the only legitimate path to `passing` is `verify`
actually running the item's verification command and exiting 0,
with the evidence recorded automatically — **nobody, agent
included, may edit `feature_list.json` directly**; the hooks deny
such writes on sight.

### 6.1 Adding items (shopapi's first three)

```bash
cd ~/projects/shopapi

python3 gate/pass-gate.py add \
  --id order-create-api \
  --title "Order creation endpoint" \
  --behavior "POST /orders creates an order and returns its id; amounts stored as integer cents" \
  --command "python -m pytest tests/test_orders.py -q" \
  --level integration --priority p0

python3 gate/pass-gate.py add \
  --id order-stock-cas \
  --title "Stock decrement via CAS" \
  --behavior "No overselling under concurrency: decrement uses a version-checked atomic update" \
  --command "python -m pytest tests/test_stock_cas.py -q" \
  --level integration --priority p0 \
  --depends-on order-create-api \
  --out-of-scope "No stock reservation or timeout release (next phase)"

python3 gate/pass-gate.py add \
  --id readme-quickstart \
  --title "README quickstart" \
  --behavior "A fresh clone can run the service in three README steps" \
  --command "python -m pytest tests/test_smoke.py -q" \
  --level assert --priority p2
```

Field reference:

| Field | Meaning |
|---|---|
| `--id` | Unique short name (kebab-case); every later command uses it |
| `--behavior` | The user-visible behaviour when done — describe the outcome, not the implementation |
| `--command` | **This item's own verification command**; exit 0 is the only pass. Be specific (name the files); "run all tests" is cheating |
| `--level` | Verification strength: `assert` < `unit` < `integration` < `e2e`; cross-component p0 items are at least `integration` |
| `--depends-on` | Item ids this one depends on (repeatable). Unmet dependencies hard-block `start` by default; to proceed anyway use `start --override-deps "<reason>"` — the reason is written into the hash-chained event log |
| `--out-of-scope` | An explicit fence for what this item will not do; prevents scope creep |

### 6.2 Completing a round

```bash
python3 gate/pass-gate.py start --id order-create-api   # enter in-progress (WIP=1)
# …develop as usual: write code, run tests…
python3 gate/pass-gate.py verify --id order-create-api  # the gate re-runs the command
# exit 0 → the item becomes passing; evidence (with a hash of the
# command output summary) is recorded automatically
python3 gate/pass-gate.py status                        # all items and states
python3 gate/pass-gate.py check-clean                   # five-dimension handover check
```

On verify failure the item stays in progress; five consecutive
failures trip a circuit breaker that demands a retrospective
first. Do not normalize `override`: it is the human's audited
escape hatch (a reason is mandatory, it is written to the event
log, and CI does not accept it as a real pass) — using it routinely
is dismantling the gate.

### 6.3 Fixed actions for every session

- **Starting work**: read `SESSION_STATE.md`, then run
  `python3 gate/pass-gate.py status` to align on state;
- **Ending work**: refresh `SESSION_STATE.md` (one page), leave
  unfinished work in items or plans, and finish with a green
  `check-clean`.

### 6.4 The fast lane: a quick path for small tasks (task grading)

After the project's tier is set, grade each task once more before
starting (the template's grading section ships the stock wording;
adapt the thresholds to your project's risk profile):

- **S — fast lane**: single-file, style/copy/parameter changes —
  no gate item, no full-suite verification; read only the relevant
  files (locate first, then read closely; no aimless whole-repo
  sweeps), run that file's targeted test afterwards, and report
  in-session. Layout tweaks, changing a default, fixing a typo
  all live here.
- **M — standard lane**: multi-file with clear boundaries — one
  gate item (batch similar small changes into it), a targeted
  test set as its verification command, check-clean at wrap-up.
- **L — full lane**: state machines, external interfaces, data
  migrations, security boundaries, or one mistake is expensive —
  the complete flow, nothing skipped.

Without a fast lane, a harness is systematically slow on small
tasks: a dozen files read at start-up and an item ceremony for a
one-line change, with all the time spent on ritual. Grading rule
of thumb: blast radius visible at a glance and errors surface
immediately → S; everything else starts at M; high-cost surfaces
→ L. When in doubt grade up, and if an S task outgrows its blast
radius mid-flight, promote it to M and open the item then.

---

## 7. Host surfaces (read the row for the tools you actually use)

Enforcement differs per host after deployment; know yours:

| Host | State after deployment | Anything left to do |
|---|---|---|
| Claude Code | Bridge + hooks in place; enforced inside the client (denies direct feature_list writes, blocks Stop with an unfinished item) | Nothing; effective in a new session |
| Antigravity CLI / IDE / Desktop | Project hooks deployed; all four event kinds live-verified | Nothing; note the Desktop app uses the global registration — restart it after hook changes |
| Codex | Config-only hookup via global/project AGENTS.md | No enforcing hooks; rely on gate commands + CI |
| DeepSeek Harness (dsh) | Gate plugin deployed into `.dsh/` | **Manual activation required** (mount the Cordis plugin row); Stop steering works only after activation |
| WorkBuddy | Rule bridge deployed (protocol level) | Not yet live-verified; treat as config-only for now, do not rely on its hook enforcement |
| Any other host | Files only | Run `verify` / `check-clean` manually; pre-push + CI are the backstop |

Global rules (optional): add `-g` to the pipeline run
(`./run-pipeline.sh --all -y -g -p <project>`) or choose it in the
wizard; the Global AGENTS is written to each tool's global
location, with a backup before overwrite when `-u` is also given.
Skip `-g` for a single-project deployment so you do not disturb
other projects' environments.

---

## 8. Optional configuration

### 8.1 Skill profiles

Deployment defaults to `minimal`. The profile decides how many
skills are copied and whether the orchestration layer ships:

| Profile | Skills | Orchestration (graph/loop) | Fits |
|---|---|---|---|
| `minimal` (default) | 15 (10 gate core + 5 openspec core) | Not shipped | A new project that wants the gate + base rules |
| `standard` | 20 | Shipped | Projects using the goal loop / graph orchestration |
| `full` | 37 (all 39 with `--include-heavy-skills`) | Shipped | The full skill set |

Switch by re-deploying with `--profile standard` (etc.) on
`deploy-agents.sh`. Downgrading back to `minimal` backs up the
removed orchestration files instead of deleting them.

### 8.2 ai-memory cross-tool memory (optional)

Stage 2 reporting SKIP simply means this is opt-in. Three steps:

```bash
cargo install ai-memory                      # or fetch a binary from its GitHub Releases
cp .ai-memory.toml.example .ai-memory.toml   # take the template from the agent-harness repo
# Edit .ai-memory.toml: replace the replace-with-* placeholders with
# your workspace / project names, and place the file in the target
# project root (it is gitignored, so it cannot be committed by accident)
./setup-ai-memory.sh claude-code codex antigravity-ide   # run inside the target project
```

Leaving it off does not affect the gate or the rules in any way;
you only lose cross-tool long-term memory recall.

### 8.3 CodeGraph / RTK prompts

At the end of deployment the script detects these two optional CLIs
and asks **individually** about installing and wiring each (default:
no). Unattended (`-y`) runs skip them and print the follow-up
commands; run those manually when wanted — no re-deployment needed.

---

## 9. Deployment acceptance checklist

Run these in order; deployment counts as landed only when all pass:

```bash
cd agent-harness && ./deploy-agents.sh ~/projects/shopapi --check
# → no unfilled placeholders reported

cd ~/projects/shopapi
python3 gate/pass-gate.py status        # no validation errors; item list as expected
python3 gate/pass-gate.py check-clean   # all five dimensions pass
                                        # (SKIP on the build dimension is
                                        # acceptable when no build was configured)
python3 gate/pass-gate.py events --verify-chain   # event hash chain intact
git status                              # compare new files against §3.4;
                                        # no unexpected modifications
```

One more field test: open a fresh agent session and have it answer,
from the project files alone, "what is this project, how is it
tested, and which item is currently in progress?" Correct answers
mean the three documents are filled in well enough; wrong or missing
answers mean the documents need work — fix the documents before
blaming the model.

---

## 10. Updates and rollback

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --update   # fast-forward the template
                                                 # repo and sync managed files
```

- `--update` backs up managed rule/skill files before replacing
  them. Your hand-edited three root documents are outside the
  managed replacement set, but re-run `--check` and `check-clean`
  after an update anyway.
- To roll back one global rule file: copy the sibling
  `*.bak-<timestamp>` file back over it.
- To leave the harness entirely: delete `.agents/`, `.claude/`,
  `gate/` and the three root documents from the project. There is
  no server-side state and no lock-in.

---

## 11. FAQ

| Symptom | Cause and remedy |
|---|---|
| Stage 2 reports SKIP | The ai-memory CLI is not installed, or `.ai-memory.toml` still has placeholders. Ignore it if you do not want memory; see §8.2 to enable |
| Stage 3/4 reports WARN | In default advisory mode this means "issues found, not blocking": skill drift or stale docs. Work through the summary details, or add `--strict` to make it fail hard while you locate them |
| `init.template.sh` fails on placeholders | `--verify` / `--start` still contain `<...>` or are empty. Fill in real commands and re-run |
| The init smoke run fails | The project itself is currently red. Make the project green first, then initialize — the gate does not accept a project that starts broken |
| An existing AGENTS.md was not updated | By design: existing files are never overwritten. The new template is written to `AGENTS.generated.md` for comparison; merge by hand |
| The agent says it cannot modify feature_list.json | Correct behaviour: only pass-gate may write that file. Have it use `add / start / verify` instead of working around the hooks |
| `start` is blocked by a dependency | The dependency item is not passing yet. Either finish it first, or `start --override-deps "<reason>"` to proceed with an audited trail |
| `verify` keeps failing but the session must end | Mark the item with `block` and write the reason into SESSION_STATE; do not override it into passing |
| Desktop-app hooks do not fire | The Desktop app reads the global registration, a different surface from the CLI's project-level config; confirm the global hooks are registered and restart the Desktop app |
| Script behaviour differs on Windows | Use the `.ps1` twin with PowerShell ≥ 5.1; the two implementations are feature-aligned, and the PARITY table in `tests/repo_checks.py` is the reference if they ever diverge |

---

## Appendix: command cheat sheet

```bash
# Deploy (run inside the agent-harness repo)
./run-pipeline.sh --all -y -p <project> -l en        # full unattended pipeline
./run-pipeline.sh                                    # interactive wizard
./deploy-agents.sh <project> --initialize --lang en  # scan project facts into a draft
./deploy-agents.sh <project> --check                 # report unfilled placeholders
./deploy-agents.sh <project> --initialize --directory <subdir>   # generate a directory-level AGENTS.md (one named directory at a time)
./deploy-agents.sh <project> --update                # update managed files (auto-backup)

# Gate (run inside the target project)
sh gate/init.template.sh --name <name> --verify "<cmd>" --start "<cmd>" [--build "<cmd>"]
python3 gate/pass-gate.py add --id <id> --title "" --behavior "" --command ""
python3 gate/pass-gate.py start --id <id>
python3 gate/pass-gate.py verify --id <id>
python3 gate/pass-gate.py status
python3 gate/pass-gate.py check-clean
python3 gate/pass-gate.py events --verify-chain
```

*Compiled against agent-harness v0.7.0; if later versions change
the flags, `./run-pipeline.sh --help` and the Multi-Tool Deployment
and Configuration Guide are authoritative.*
