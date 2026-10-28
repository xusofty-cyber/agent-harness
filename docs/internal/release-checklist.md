# Release checklist — v0.3.0 (Phase 6, 6-4)

> Pre-release checklist for cutting a version. This file is the procedure;
> `tools/check-release.py` is the automated part of it. **Merging to
> `main` needs the user's explicit approval** (main frozen since
> 2026-10-28) — never merge on your own authority.

## Pre-release (on the release branch)

- [ ] `python3 tests/repo_checks.py` — all pass (record the count).
- [ ] All hook tests pass: `node tests/hooks.test.mjs`,
      `node tests/hooks-gate.test.mjs`, `node tests/hooks-lifecycle.test.mjs`
      (and any other `tests/*.test.mjs`).
- [ ] `python3 tools/sync-skills.py --check --strict` — all skills in-sync
      vs pins (online; ~30 s).
- [ ] `python3 tools/check-release.py` — exit 0 (VERSION/CHANGELOG/lock +
      deprecation policy).
- [ ] Deploy smoke: `deploy-agents.sh` to an empty directory exits 0;
      `deploy-agents.ps1` smoke in CI.
- [ ] `docs/internal/release-v0.3.0.md` draft updated with the final
      measured numbers (re-verify, do not copy old numbers).
- [ ] CHANGELOG `[Unreleased]` entries are complete and honest (what was
      done / not done / measured numbers); no `**Breaking**` entry without
      a `Migration:` note.

## Cut the release (maintainer, with user approval)

1. Rename `[Unreleased]` to `## [x.y.z] - YYYY-MM-DD` in `CHANGELOG.md`;
   write the same version into `VERSION`.
2. Re-run `python3 tools/check-release.py` (must exit 0).
3. Open a PR to `main`; get the user's explicit approval; merge.
   (Do NOT merge to main without it — main is frozen.)
4. After merge, locally: `git tag vx.y.z && git push origin vx.y.z`
   (tags can't be created through the GitHub App API).
5. Publish the GitHub Release from the tag, using
   `docs/internal/release-v0.3.0.md` as the notes (final version).

## Post-release

- [ ] Verify the tag and the Release page (tag points at the merged main).
- [ ] Verify `VERSION` on main equals the tag.
- [ ] Open a fresh `[Unreleased]` section in `CHANGELOG.md` on main.
- [ ] Update `docs/internal/SESSION_STATE.md` (breakpoint: release done).
- [ ] If the release removed a deprecated template, record the removal
      (one version cycle has passed — see CONTRIBUTING "Deprecation policy").
