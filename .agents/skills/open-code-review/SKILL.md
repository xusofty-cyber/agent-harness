---
name: open-code-review
description: Deterministic code review — file selection, rule-first matching, and line-anchored findings. Use when reviewing a diff, a branch, or a commit for bugs, security, and quality issues. Three tiers: (A) `ocr` CLI delegation when installed, (B) built-in methodology when not, (C) `ocr` direct mode with an API key. Complements `requesting-code-review` (timing) with the how.
version: 0.1.0
---

# Open Code Review

Review **finished code** with deterministic engineering, not vibes. The core insight
(adapted from [alibaba/open-code-review](https://github.com/alibaba/open-code-review),
Apache-2.0 — see `ATTRIBUTION.md`):

> For review steps that *must not go wrong* — file selection, rule matching,
> line anchoring — use deterministic logic, not the language model.
> Reserve the model for what it does best: judging logic, intent, and architecture.

Why this matters here: it directly serves `.agents/rules/token-discipline.md`.
A rule-first, file-bundled review consumes a fraction of the tokens of a
"read everything and opine" review, with higher precision (fewer false alarms).

## Relationship to `requesting-code-review`

- `requesting-code-review` decides **when** to review (after a task, before merge).
- `open-code-review` decides **how** to review (this skill).
- When `requesting-code-review` triggers, it should invoke this skill's workflow.

## Tier selection

| Tier | Condition | LLM cost |
|------|-----------|----------|
| **A — Delegate** | `ocr` CLI installed (`command -v ocr`) | Zero on OCR side; host agent does the reasoning |
| **B — Methodology** | No CLI | Host agent executes `references/methodology.md` manually |
| **C — Direct** | CLI + `OCR_LLM_TOKEN` configured | OCR calls its own model endpoint |

Default to **A** when the CLI exists, **B** otherwise. Use **C** only when the
user explicitly wants OCR to run the review itself.

## Tier A — Delegation workflow

```bash
# 1. Preview: what to review (mode, file list, exclusions)
ocr delegate preview --format json [--from <ref> --to <ref>] [--commit <hash>]

# 2. Rules: matched rules grouped by content (pass reviewable paths from step 1)
ocr delegate rule --format json <path1> <path2> ...

# 3. Diffs: use git directly from the preview's ref metadata
git diff <merge_base>..<to> -- <path>        # range mode
git show <commit> -- <path>                   # commit mode
git diff HEAD -- <path>                        # workspace mode (tracked)
```

Then review per `references/methodology.md` §3–§5 (checklist, line anchoring,
severity classification, coverage report).

## Tier B — Methodology without the CLI

1. Run `scripts/group-diff.py` (or `git diff --name-only`) to get the changed files.
2. Filter noise deterministically: lockfiles, build output, binaries, vendored
   code — see `references/methodology.md` §1.
3. Bundle related files (same feature, i18n pairs, test+implementation).
4. Match each bundle against `references/rules/` — rules first, model second.
5. Follow `references/methodology.md` §3–§5 for the review pass.

## Finding format

Every finding must carry:

| Field | Required | Notes |
|-------|----------|-------|
| `path` | yes | Repo-relative file path |
| `content` | yes | What is wrong and why |
| `start_line` / `end_line` | yes | **New-file** line numbers, verified against the diff hunk — never guessed |
| `category` | no | bug, security, performance, maintainability, test, style, documentation |
| `severity` | no | critical, high, medium, low |

## Coverage mandate

Every reviewable file must end as **reviewed** or **skipped with a concrete
reason**. Report `total_files`, `reviewed_files`, `skipped_files`, and
`coverage_rate`. Silently omitting a file is a review failure.

## Severity policy

- **Critical/High** — bugs, security issues, data-loss risks: always report.
- **Medium** — performance, error-handling gaps, maintainability: report with context.
- **Low** — style nits: report only if clearly valuable.
- Discard likely false positives silently. Precision over recall.
