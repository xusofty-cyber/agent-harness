# Deterministic Review Methodology

Use this when the `ocr` CLI is **not** installed (Tier B). It replicates the
deterministic half of the open-code-review pipeline by hand.

## 1. File selection (deterministic, zero model judgment)

Get the changed files, then filter noise **by pattern, not by reading**:

**Always exclude:**
- Lockfiles: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`,
  `Cargo.lock`, `go.sum`
- Build output: `dist/`, `build/`, `out/`, `*.min.js`, `*.bundle.js`
- Binaries and media: `*.png`, `*.jpg`, `*.ico`, `*.woff2`, `*.pdf`, `*.zip`
- Vendored / generated: `vendor/`, `node_modules/`, `*.pb.go`, `*_generated.py`,
  `migrations/` auto-generated files
- Secrets-adjacent: never review the *content* of `.env`, `*.pem`, `*.key`
  beyond confirming they are not committed (they must not be)

**Keep:** everything else, including tests, configs, docs, and scripts.

## 2. File bundling (deterministic grouping)

Group related files into one review unit before reading anything:

- Implementation + its test (`foo.py` + `test_foo.py`)
- i18n pairs (`message_en.properties` + `message_zh.properties`)
- Same feature across layers (migration + model + handler)
- Config + code that consumes it

Review one bundle at a time. Bundles are independent — they can be reviewed
in parallel by subagents.

## 3. Rule-first review pass

For each bundle:

1. Identify the languages involved; load the matching files from
   `references/rules/` (`security.md` always applies).
2. Check the diff **against the rules first** — pattern-match mechanically.
3. Only then use model judgment for logic, intent, and architecture.

Rules carry "do NOT report" guards. Respect them: a finding the rules
exclude is noise, not diligence.

## 4. Line anchoring (no position drift)

- Derive line numbers from **diff hunk headers** (`@@ -a,b +c,d @@`),
  counting added lines from `c`. Never eyeball line numbers from file reads.
- `start_line` / `end_line` refer to the **new** file.
- If you cannot anchor a finding to an exact line range, say so explicitly
  rather than guessing.

## 5. Reflection pass

Before reporting, re-examine each finding:

1. Is the line range correct? (re-derive from the hunk)
2. Is it a real defect or a style preference? (drop the latter unless critical)
3. Does a rule's "do NOT report" guard cover it? (drop if yes)
4. Would you bet reputation on it? (drop if no)

## 6. Coverage report

List every reviewable file as `reviewed` or `skipped: <reason>`.
Compute `coverage_rate = reviewed / total`. Anything below 100% must explain
each skip. A file you never opened is not "reviewed".
