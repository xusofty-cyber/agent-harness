# Security Review Rules

Applies to **every** bundle regardless of language. Check mechanically first.

## Injection

- **Shell**: unquoted variable expansions (`$var` without quotes) in commands
  that touch filenames or user input; `eval` on non-constant strings;
  `curl ... | sh` without checksum verification.
- **SQL**: string-interpolated queries (`f"SELECT ... {x}"`, `"..." + x`);
  require parameterized queries.
- **JavaScript**: `eval()`, `new Function()` with dynamic input; `innerHTML`
  with unsanitized data; prototype pollution via unchecked `__proto__` keys.

## Secrets

- Hardcoded API keys, tokens, passwords, private keys in the diff.
- Secrets printed to logs or error messages.
- `.env` / credential files added to version control.
- **Do NOT report**: placeholder values (`xxx`, `YOUR_KEY_HERE`), test
  fixtures clearly marked as fake, references to env vars (`process.env.X`).

## Command & path safety

- `rm -rf` with a variable path that could be empty or `/`.
- Path traversal: user input joined into file paths without normalization.
- `subprocess` / `exec` with `shell=True` on dynamic input.

## Auth & access

- Missing authorization checks on new endpoints/handlers.
- Privilege escalation via user-controlled role/permission fields.
- Insecure randomness (`Math.random`, `random.random`) for tokens/secrets.

## Do NOT report

- Theoretical attacks requiring the attacker to already have code execution.
- "Use a WAF" style generic advice without a concrete code location.
- Findings in test fixtures or documentation examples.
