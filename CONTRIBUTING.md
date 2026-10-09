# Contributing to agents-living

> **Language**: English is the source of truth for guides; 中文文档见下方说明。

## Bilingual documentation policy（双语文档政策）

The long-form guides are maintained in **pairs**:

| English (source) | 中文 (translation) |
|---|---|
| `README.md` | `README_zh.md` |
| `Multi-Tool Deployment and Configuration Guide.md` | `Multi-Tool Deployment and Configuration Guide.zh.md` |
| `Tools Practical Usage and Skills Panorama Guide.md` | `Tools Practical Usage and Skills Panorama Guide.zh.md` |

Rules:

1. **English first**: write or change the English version first, then sync the Chinese translation in the same PR. A PR that changes one side without the other will be sent back.
2. **Structure parity**: keep the same section structure and heading hierarchy on both sides, so anchors and the table of contents stay aligned. CI enforces `##` section-count parity per pair via `tests/repo_checks.py`; deeper drift is caught in review.
3. **Filenames**: guides use ASCII filenames; Chinese translations use the `.zh.md` suffix (e.g. `Some Guide.zh.md`). No non-ASCII filenames for new documents.

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

### Skill versions

Skills authored in this repo (`sourceType: "local"` in `skills-lock.json`,
currently `cross-tool-memory`) must declare a semver `version:` in their
`SKILL.md` frontmatter, matching the `version` in their lock entry.
Vendored skills (openspec, superpowers, …) are versioned upstream — do not
add a local `version:` to them. Bump a skill's version when its behavior
changes (patch: wording/threshold tweaks; minor: new trigger scenarios;
major: incompatible behavior change). A skill version bump does not force a
repository version bump. Template changes under a skill's `templates/`
count as behavior changes: field/section restructuring → minor bump,
wording/example tweaks → patch bump; combined with body changes, bump once.

### Release process

1. Record entries under `CHANGELOG.md` → `## [Unreleased]`.
2. To cut a release: rename `[Unreleased]` to `## [x.y.z] - YYYY-MM-DD`,
   write the same version into the `VERSION` file (CI checks they match),
   merge to `main`.
3. After merge: `git tag vx.y.z && git push origin vx.y.z`
   (tags can't be created through the GitHub App API — do it locally).
