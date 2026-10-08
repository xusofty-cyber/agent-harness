# Option Review — Dimension Rubrics

Each reviewer scores every option `✅` / `⚠️` / `❌` with a one-line rationale.
Judge the option **as described**; do not invent unstated safeguards or assume
best-case execution.

## 1. Security

Aligned with `.agents/rules/security-boundary.md`.

- `✅`: No new attack surface; secrets stay out of code/config; no injection vectors.
- `⚠️`: Adds attack surface that is containable, or relies on a safeguard
  the option does not itself establish.
- `❌`: Puts secrets in code/config, opens an unauthenticated privileged path,
  or introduces an injection vector with no mitigation.

## 2. Engineering

- `✅`: Follows the repo's existing patterns; small, testable seams;
  a new maintainer can understand it in one sitting.
- `⚠️`: Introduces a new pattern or dependency the repo does not already carry,
  or a seam that is hard to test through its interface.
- `❌`: Fights the repo's architecture, duplicates existing capability,
  or makes future changes measurably harder.

## 3. Reversibility

One-way door vs two-way door.

- `✅`: Two-way door — fully reversible with a revert or config flip;
  blast radius limited to the change itself.
- `⚠️`: Reversible but costly (data migration, coordinated rollout),
  or blast radius extends beyond the immediate change.
- `❌`: One-way door — irreversible side effects (data loss, external
  state, published contracts) with no rollback path.

Rule of thumb: an irreversible option needs a proportionally stronger
justification from the other dimensions to survive.

## 4. Simplicity

- `✅`: Fewest moving parts that solve the problem; no speculative generality.
- `⚠️`: Adds machinery for plausible-but-unstated future needs,
  or one extra integration seam.
- `❌`: Builds for hypothetical futures (YAGNI), or complexity
  disproportionate to the problem size.

## 5. Cross-tool

Distinctive to this repo: options must hold across
Claude Code, Codex, and Antigravity IDE.

- `✅`: Uses only portable mechanisms (files, scripts, plain config);
  no tool-specific feature is load-bearing.
- `⚠️`: Leans on a feature present in some tools but not all
  (e.g. Claude Code frontmatter hooks); needs a documented fallback.
- `❌`: Depends on a single tool's proprietary behavior with no fallback —
  the option silently breaks outside that tool.
