# Comet Integration

Wire `open-code-review` into the Comet workflow's **Verify** phase,
alongside the existing gates.

## Verify phase checklist (addition)

```text
1. Run unit/functional tests (existing)
2. Run `python3 tools/doc-impact.py` — no 🔴 must-update remains (existing)
3. Code review gate (new):
   - If `ocr` CLI is installed: `ocr delegate preview --format json`,
     then follow the open-code-review skill Tier A workflow.
   - Otherwise: follow the skill's Tier B methodology
     (`references/methodology.md` + `references/rules/`).
   - Critical/High findings must be fixed or explicitly waived with a reason
     recorded in `verification.md` before Archive.
```

## Archive phase

No change. Review findings and waivers are already captured in
`verification.md`; Archive proceeds as before.

## Notes

- The review gate is **advisory by default**, like `doc-impact.py`.
  It becomes blocking only when the project opts in (e.g. a `review-required`
  marker in the change proposal).
- Never run a pre-commit LLM review hook — deterministic checks only
  pre-commit; LLM review stays at PR/Verify scope to avoid friction
  and token waste.
