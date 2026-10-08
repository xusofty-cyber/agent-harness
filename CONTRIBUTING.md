# Contributing to agents-living

> **Language**: English is the source of truth for guides; 中文文档见下方说明。

## Bilingual documentation policy（双语文档政策）

The long-form guides are maintained in **pairs**:

| English (source) | 中文 (translation) |
|---|---|
| `README.md` | `README_zh.md` |
| `Multi-Tool Deployment and Configuration Guide.md` | `多工具部署配置指南.md` |
| `Tools Practical Usage and Skills Panorama Guide.md` | `各工具实战使用与技能全景指南.md` |

Rules:

1. **English first**: write or change the English version first, then sync the Chinese translation in the same PR. A PR that changes one side without the other will be sent back.
2. **Structure parity**: keep the same section structure and heading hierarchy on both sides, so anchors and the table of contents stay aligned. (CI checks that both files of a pair exist; structural drift is caught in review.)
3. **Filenames**: the Chinese guides keep their Chinese filenames for now (renaming would break existing links). New guides must use ASCII filenames, e.g. `Some Guide.md` / `Some Guide.zh.md`.

## Templates stay generic（模板保持通用）

`Global AGENTS.md`, `Project AGENTS.md`, `Directory AGENTS.md` and `.agents/rules/` are
**distribution templates**. Do not hardcode any specific project's architecture, branch names,
or business facts into them — use `<PLACEHOLDERS>` like `Project AGENTS.md` does.
Project-specific notes belong in `docs/internal/`, never in the templates.

## Scripts stay in sync（双脚本同步）

`deploy-agents.ps1` and `deploy-agents.sh` implement the same features. When you add a
feature to one, add it to the other in the same PR. CI enforces this via the
feature-parity markers in `tests/repo_checks.py` — extend the `PARITY` table when you
add a feature.

## Checks before pushing（提交前自检）

```bash
node tests/hooks.test.mjs        # hook behavior tests
python3 tests/repo_checks.py     # JSON/TOML, SKILL frontmatter, script parity
```

CI runs markdownlint, shellcheck, the above, plus a `deploy-agents.sh` smoke test.
Keep `main` green: fix lint violations in your branch, don't merge red.

## Versioning（版本）

Changes are recorded in `CHANGELOG.md` under `Unreleased`. The maintainer tags releases
(`vX.Y.Z`) from `main` when a coherent set of changes is done.
