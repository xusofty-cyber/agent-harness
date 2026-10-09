# Shell Review Rules

## Correctness

- Unquoted variables: `"$var"` not `$var`, especially in `[ ]`, `rm`, `cp`.
- `set -euo pipefail` missing in scripts that must fail fast.
- `cd` without checking success (`cd "$d" || exit 1`).
- Parsing `ls` output instead of globbing.
- `$?` checked after an intervening command clobbered it.

## Portability & safety

- Bashisms (`[[ ]]`, `(( ))`, `local`) in `#!/bin/sh` scripts.
- `rm -rf "$dir/"` where `$dir` may be empty → catastrophic.
- `curl | bash` without integrity check.
- Temp files: use `mktemp`, never predictable `/tmp` names.

## Error handling

- Silent failures: commands whose failure is ignored in critical paths.
- `grep` in `if` without handling "no match" (exit 1) vs error (exit 2).

## Do NOT report

- `shellcheck` SC2086-style nits already covered by CI linting —
  focus on logic, not what the linter catches.
- Preferring `[[ ]]` over `[ ]` in scripts already declared `#!/bin/bash`.
