# Contributing to agent-harness

> **Language**: English is the source of truth for guides; 中文文档见下方说明。

## Multilingual documentation policy（多语言文档政策）

The long-form guides are maintained with English as source of truth and supported across multiple languages:

| English (source) | 中文 (简体) | 中文 (繁體) | Français | Deutsch |
|---|---|---|---|---|
| `README.md` | `README.zh.md` | `README.zh-tw.md` | `README.fr.md` | `README.de.md` |
| `docs/guides/Multi-Tool Deployment and Configuration Guide.md` | `docs/guides/Multi-Tool Deployment and Configuration Guide.zh.md` | `docs/guides/Multi-Tool Deployment and Configuration Guide.zh-tw.md` | `docs/guides/Multi-Tool Deployment and Configuration Guide.fr.md` | `docs/guides/Multi-Tool Deployment and Configuration Guide.de.md` |
| `docs/guides/Tools Practical Usage and Skills Panorama Guide.md` | `docs/guides/Tools Practical Usage and Skills Panorama Guide.zh.md` | `docs/guides/Tools Practical Usage and Skills Panorama Guide.zh-tw.md` | `docs/guides/Tools Practical Usage and Skills Panorama Guide.fr.md` | `docs/guides/Tools Practical Usage and Skills Panorama Guide.de.md` |
| `docs/guides/Skills Usage Guide.md` | `docs/guides/Skills Usage Guide.zh.md` | `docs/guides/Skills Usage Guide.zh-tw.md` | `docs/guides/Skills Usage Guide.fr.md` | `docs/guides/Skills Usage Guide.de.md` |

Rules:

1. **English first**: write or change the English version first, then sync the translations in the same PR.
2. **Structure parity**: keep the same section structure and heading hierarchy across all language variants, so anchors and the table of contents stay aligned. CI enforces `##` section-count parity via `tests/repo_checks.py`.
3. **Filenames**: guides use ASCII filenames; translations use language code suffixes (`.zh.md`, `.zh-tw.md`, `.fr.md`, `.de.md`).

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

## Symlink risk（软链风险）

`.agents/rules/engineering.md` is a symlink to `engineering-spec.md`
(one file, two names). It works in a normal `git clone`, but it can break
when the repo is consumed as a zip download or on filesystems / Windows
setups that do not restore symlinks: the link becomes a dangling pointer
or a plain text file containing the target path, and any tool that reads
`engineering.md` then sees nothing (or the literal target name) instead
of the rule. Current mitigation: none — no check detects a broken link,
and the deploy scripts copy it as-is. If you touch this file, edit
`engineering-spec.md` (the real file) and verify the link still resolves
(`ls -l .agents/rules/engineering.md`) before pushing. Replacing the
symlink with a real duplicate file would fix the risk but reintroduce
drift between the two copies; that trade-off is recorded in
`DECISIONS.md` (N5) and is still open.

## Checks before pushing（提交前自检）

```bash
node tests/hooks.test.mjs        # hook behavior tests
python3 tests/repo_checks.py     # JSON/TOML, SKILL frontmatter, script parity
```

CI runs markdownlint, shellcheck, the above, plus a `deploy-agents.sh` smoke test.
Keep `main` green: fix lint violations in your branch, don't merge red.

## Updating vendored skills (true lock，Phase 6, 6-1)

`skills-lock.json` is a real lock, not metadata. Every github-source entry
pins an upstream commit (`pinnedCommit`) and the SHA256 of the vendored
content (`computedHash`); CI verifies both (offline in
`tests/repo_checks.py` §5/§5b/§5c, online via
`tools/sync-skills.py --check --strict`).

- **To update a vendored skill**: on a branch, run
  `python3 tools/sync-skills.py --apply [--skill NAME]`, review the diff
  (skill file + `computedHash`), and open a PR — upstream updates always
  go through review, never silently. Never hand-edit `computedHash`.
- **To re-pin** (move a skill to a newer upstream commit): update
  `pinnedCommit` + `pinnedAt` (and `pinnedFrom`, noting how the commit was
  chosen), then run `--apply` to refresh the hash. A pin that no longer
  resolves upstream fails CI.
- **Never run `--apply` on `main`** and never edit the lock to cover a file
  state that was never reviewed (§5b ties hash changes to file changes).
- **Meta entries** (`openspec`, `superpowers`, `"meta": true`) pin suite
  repos, not deployable skills. They are annotated, never deleted (D10).

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

### Deprecation policy（废弃策略，Phase 6, 6-3）

- A template breaking change (renamed/removed field or section, changed
  semantics) must be recorded in `CHANGELOG.md` under `[Unreleased]` as a
  `**Breaking**` bullet (or under `### Deprecated`) **with a `Migration:`
  note** explaining how existing users move to the new form. `tools/check-release.py`
  fails the build if the note is missing.
- The old form stays available for **one full version cycle**: it is kept
  (deprecated, not deleted) in the release that introduces the replacement,
  and may only be removed in the release after that. Removal itself is
  recorded as a `**Breaking**` entry with a `Migration:` note.
- A deprecated template/skill is marked `status: deprecated` in its
  frontmatter and listed in `CHANGELOG.md` `### Deprecated`; removal needs
  owner sign-off (same rule as the monthly ablation process).

### Release process

1. Record entries under `CHANGELOG.md` → `## [Unreleased]`.
2. To cut a release: rename `[Unreleased]` to `## [x.y.z] - YYYY-MM-DD`,
   write the same version into the `VERSION` file (CI checks they match),
   run `python3 tools/check-release.py` (must exit 0: version/lock
   consistency + every breaking entry has a `Migration:` note),
   merge to `main`.
3. After merge: `git tag vx.y.z && git push origin vx.y.z`
   (tags can't be created through the GitHub App API — do it locally).
