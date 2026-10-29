# Third-Party Licenses — agent-harness

> This file lists every vendored skill's source and license, 1:1 with
> `skills-lock.json` (42 entries: 40 skill directories + 2 source-repo
> meta entries). License values are copied from each skill's `SKILL.md`
> frontmatter `license:` field. Where the vendored copy declares no
> license, the row says so explicitly — do not assume a license from
> the upstream project's reputation; check the upstream repository.
> Regenerate by hand when `skills-lock.json` changes; the row count
> must stay equal to the lock entry count (enforced by
> `tools/count-skills.py`, which reports 42).

## Summary (2026-10-28)

- MIT (declared in vendored copy): 16
- Apache-2.0 (declared in vendored copy): 1 (`comet`)
- **⚠️ Proprietary (declared in vendored copy): 2 — `docx` and `pdf`.
  Both ship a `LICENSE.txt` with the complete terms; read it before
  redistributing or modifying them. `docx` is additionally opt-in
  only (see `--include-heavy-skills` in `deploy-agents.sh`).**
- Not declared in vendored copy (see upstream): 23

## Skills

| Skill | Source | License (as declared in vendored copy) |
|---|---|---|
| `brainstorming` | obra/superpowers | Not declared in vendored copy — see upstream |
| `caveman` | JuliusBrussee/caveman | Not declared in vendored copy — see upstream |
| `codegraph` | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | MIT |
| `comet` | [rpamis/comet](https://github.com/rpamis/comet) | Apache-2.0 |
| `cross-tool-memory` | ./agent-harness (authored in-repo) | Not declared in vendored copy — see upstream |
| `diagnosing-superpowers` | obra/superpowers | Not declared in vendored copy — see upstream |
| `dispatching-parallel-agents` | obra/superpowers | Not declared in vendored copy — see upstream |
| `docx` | anthropics/skills | **⚠️ Proprietary. LICENSE.txt has complete terms** |
| `engineering-docs` | ./agent-harness (authored in-repo) | MIT |
| `executing-plans` | obra/superpowers | Not declared in vendored copy — see upstream |
| `finishing-a-development-branch` | obra/superpowers | Not declared in vendored copy — see upstream |
| `git-advanced` | ./agent-harness (authored in-repo) | Not declared in vendored copy — see upstream |
| `living-documentation` | ./agent-harness (authored in-repo) | Not declared in vendored copy — see upstream |
| `open-code-review` | ./agent-harness (authored in-repo) | Not declared in vendored copy — see upstream |
| `openspec` | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | — (meta entry: no vendored `SKILL.md`; license per upstream repository, not declared in this repo) |
| `openspec-apply-change` | Fission-AI/OpenSpec | MIT |
| `openspec-archive-change` | Fission-AI/OpenSpec | MIT |
| `openspec-bulk-archive-change` | Fission-AI/OpenSpec | MIT |
| `openspec-continue-change` | Fission-AI/OpenSpec | MIT |
| `openspec-explore` | Fission-AI/OpenSpec | MIT |
| `openspec-ff-change` | Fission-AI/OpenSpec | MIT |
| `openspec-new-change` | Fission-AI/OpenSpec | MIT |
| `openspec-onboard` | Fission-AI/OpenSpec | MIT |
| `openspec-propose` | Fission-AI/OpenSpec | MIT |
| `openspec-sync-specs` | Fission-AI/OpenSpec | MIT |
| `openspec-update-change` | Fission-AI/OpenSpec | MIT |
| `openspec-verify-change` | Fission-AI/OpenSpec | MIT |
| `option-review` | ./agent-harness (authored in-repo) | Not declared in vendored copy — see upstream |
| `pdf` | anthropics/skills | **⚠️ Proprietary. LICENSE.txt has complete terms** |
| `ponytail` | DietrichGebert/ponytail | MIT |
| `receiving-code-review` | obra/superpowers | Not declared in vendored copy — see upstream |
| `requesting-code-review` | obra/superpowers | Not declared in vendored copy — see upstream |
| `rtk` | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | MIT |
| `subagent-driven-development` | obra/superpowers | Not declared in vendored copy — see upstream |
| `superpowers` | [obra/superpowers](https://github.com/obra/superpowers) | — (meta entry: no vendored `SKILL.md`; license per upstream repository, not declared in this repo) |
| `systematic-debugging` | obra/superpowers | Not declared in vendored copy — see upstream |
| `test-driven-development` | obra/superpowers | Not declared in vendored copy — see upstream |
| `using-git-worktrees` | obra/superpowers | Not declared in vendored copy — see upstream |
| `using-superpowers` | obra/superpowers | Not declared in vendored copy — see upstream |
| `verification-before-completion` | obra/superpowers | Not declared in vendored copy — see upstream |
| `writing-plans` | obra/superpowers | Not declared in vendored copy — see upstream |
| `writing-skills` | obra/superpowers | Not declared in vendored copy — see upstream |

## Notes

- `openspec` and `superpowers` are source-repo meta entries in
  `skills-lock.json`: they have no skill directory of their own (the
  actual skills are the `openspec-*` and superpowers skill directories
  listed above). Their licenses are whatever the upstream repositories
  declare; this repo does not restate them.
- In-repo authored skills (`./agent-harness (authored in-repo)`) are
  covered by this repository's own MIT license unless their frontmatter
  says otherwise (`engineering-docs` declares MIT explicitly; the
  others declare no license in the vendored copy).
