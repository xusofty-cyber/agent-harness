# Architecture — agent-harness (top-level map)

Short map of this repository's components and the dependency rules
between them. Detail lives in the linked documents; this file only
routes. (Added 2026-11-06, modelled on the OpenAI repo-template's
top-level map.)

## Components

| Component | Path | Owns |
|---|---|---|
| Verification gate | `gate/` | Feature-list state machine (`pass-gate.py`), WIP=1, evidence-required `passing`, termination check, `check-clean` |
| Host bridges | `.claude/hooks/`, `.agents/hooks/`, `.workbuddy/`, `.dsh/` | Per-host adapters that wire the gate into Claude Code, Antigravity, WorkBuddy and DeepSeek Harness (dsh) |
| Skills distribution | `.agents/skills/`, `skills-lock.json`, `skills-profiles.json` | 39 on-demand skill directories, pinned sources, three deploy profiles (minimal 15 / standard 20 / full 39) |
| Rule templates | `templates/agents/`, `.agents/rules/` | Global / Project / Directory AGENTS templates (EN/ZH/ZH-TW) and modular sub-rules |
| Pipeline & deploy | `run-pipeline.sh` / `.ps1`, `deploy-agents.sh` / `.ps1`, `setup-ai-memory.sh` / `.ps1` | Deploy → memory setup → skill sync → doc-impact gate, in dual bash/PowerShell implementations |
| Evaluation | `eval/`, `docs/bench/`, `docs/ablation/` | Self-built benchmark (t1–t12), advisory rubric, baselines and ablation reports |
| Tools | `tools/` | Loop runner, skill sync, doc-impact, cost ledger, TUI helpers |

## Dependency rules (hard)

- The gate is self-owned and host-agnostic (D1): `gate/` depends on
  nothing host-specific; bridges adapt hosts to the gate, never the
  reverse.
- Templates stay generic: no specific project's architecture, branch
  names or business facts in `templates/agents/` or `.agents/rules/`.
- Skills are leaf content: a skill may describe using the gate, but
  skill files never read or write gate state directly.
- Dual scripts, one feature set: `deploy-agents.ps1` / `.sh` (and the
  `run-pipeline` pair) stay in sync; the `PARITY` table in
  `tests/repo_checks.py` is extended with every feature.
- Repository files are the source of truth; ai-memory is a recall
  adapter only, and a repo file wins any conflict.

## Where things live

- Decisions: `DECISIONS.md` (index: `docs/design-docs/index.md`)
- Quality posture: `QUALITY_SCORE.md`
- Execution plans & debt: `docs/exec-plans/` (rules: `docs/PLANS.md`)
- This repo's own session breakpoint: `docs/internal/SESSION_STATE.md`
- Governance summaries: `docs/RELIABILITY.md`, `docs/SECURITY.md`
