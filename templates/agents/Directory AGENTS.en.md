# Directory AGENTS.md

> **Usage Note**: This file is an on-demand micro-module patch, used **only** in monorepo subpackages (`packages/*`), separated frontend/backend directories, or submodules with strict isolation boundaries. Standard subdirectories inherit project root rules by default; never create this file indiscriminately.

## Module Purpose

- **Module Name**: `<MODULE_NAME>`
- **Directory Path**: `<DIRECTORY_PATH>`
- **Core Responsibility**: `<RESPONSIBILITY>` (one sentence explaining the primary responsibility of this directory)

## Boundary Definition (In / Out Scope)

- **In-Scope**:
  - `<IN_SCOPE_ITEM_1>`
  - `<IN_SCOPE_ITEM_2>`
- **Out-of-Scope**:
  - `<OUT_OF_SCOPE_ITEM_1>` (hand off to the corresponding module or project root if requirements involve this)
  - `<OUT_OF_SCOPE_ITEM_2>`

## Dependency and Isolation Constraints

- **Allowed Dependencies**: `<ALLOWED_DEPENDENCIES>` only (base utilities or public contracts).
- **Forbidden Dependencies**: Never reference `<FORBIDDEN_DEPENDENCIES>` directly (prevents layer breakage or cyclic dependencies).
- **Public Exports**: All exposed methods and types from this module must be explicitly exported at a unified entry point (e.g., `index.ts` / `__init__.py` / `mod.rs` / `include/`); external deep imports of internal private implementations are forbidden.

## Fast Local Verification Commands (Avoid Token Bloat from Full Test Runs)

> Run lightweight verification for this module first after modifications; expand verification scope only when changes impact cross-module behavior.

```bash
# Unit tests and fast verification for this module (with concise output flags)
<LOCAL_TEST_COMMAND>           # e.g.: npm test -- packages/core --reporter=dot / pytest tests/core -q

# Linting for this module
<LOCAL_LINT_COMMAND>           # e.g.: npm run lint --filter core
```

## Local Memory Boundaries

- Record only active boundaries, dependencies, commands, and maintenance constraints unique to this directory; redundant rules should inherit from the project root.
- Do not create directory-level `MEMORY.md` or copy project history by default. Long-term facts belong in root `PROJECT_CONTEXT.md`; active breakpoints belong in root `SESSION_STATE.md`.
- Verify that directory rules still match active code upon modification; delete or correct obsolete local constraints.
- Never store credentials, private keys, raw personal data, complete conversation/tool logs, or unnecessary personal info in directory rules or memories.
- Cross-tool memory services operate at the project namespace level; normative boundaries for this directory live only in this file without nested memory stores. Directory facts in memory must be cross-checked against this file.

## Large / Legacy File Safe Maintenance Rules (For single files > 100KB)

- **Pinpoint Location**: When dealing with oversized source files, always locate exact functions and line numbers first; full-file rewrites or large-scale reformatting are prohibited;
- **Style Consistency First**: New code must strictly adhere to the existing style of the file (naming conventions, indentation, error handling); never mix conflicting heterogeneous styles;
- **No Unintended Exposure**: Private helper functions and internal structs must never be exposed directly in public headers.

## Change Checklist

- [ ] Changes are strictly within module responsibility (In-Scope), introducing no forbidden dependencies.
- [ ] Targeted local edits used for oversized files, preserving existing code style.
- [ ] New capabilities exposed only through the public module entry point, maintaining encapsulation.
- [ ] Appropriate verification proportional to change risks executed; unexecuted items and reasons documented.
