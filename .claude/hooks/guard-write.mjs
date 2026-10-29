#!/usr/bin/env node
// ==============================================================================
// guard-write.mjs — Claude Code PreToolUse Security Hook (Write|Edit matcher)
// Reads tool input from stdin JSON (official protocol).
// Uses warnings (exit 0 + stderr) for high-risk file alerts.
// ==============================================================================

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data;
try {
  data = JSON.parse(input);
} catch {
  // Graded policy (merged from v3-yunyi, Phase 2.5), same as guard.mjs:
  // log + alert, allow. Raw stdin is never logged (it could contain file
  // content/secrets).
  try {
    const { appendFileSync, mkdirSync } = await import("node:fs");
    const { join } = await import("node:path");
    const dir = join(process.cwd(), ".claude", "hooks");
    mkdirSync(dir, { recursive: true });
    appendFileSync(join(dir, "guard-alerts.jsonl"),
      JSON.stringify({ ts: new Date().toISOString(), event: "stdin_parse_failed",
        source: "guard-write.mjs",
        detail: "stdin JSON parse failed; allowed per graded policy (log+alert, not fail-closed)" }) + "\n");
  } catch {
    // Logging failure must not change the allow decision.
  }
  process.stderr.write("[SECURITY-HOOK] Guard-write stdin parse failed — logged to .claude/hooks/guard-alerts.jsonl; call allowed per graded policy.\n");
  process.exit(0);
}

const toolInput = data.tool_input || {};
// Write/Edit tools use file_path or path
const filePath = (
  toolInput.file_path ||
  toolInput.path ||
  toolInput.target ||
  JSON.stringify(toolInput)
).toLowerCase();

// === Helper: warn (non-blocking, informational) ===
function warn(message) {
  process.stderr.write(`[SECURITY-HOOK] ${message}\n`);
}

// High-risk build/config files
const HIGH_RISK_PATTERNS = [
  ".pro",
  "cmakelists.txt",
  "package.json",
  "cargo.toml",
  "pom.xml",
  "public_struct.h",
  "protofile/",
  "license",
];

for (const pattern of HIGH_RISK_PATTERNS) {
  if (filePath.includes(pattern)) {
    warn(
      `🔴 Touching high-risk files (build config/public structure/protocol defs/license) —` +
        `Please read .agents/rules/security-boundary.md and confirm impact with human! / 请先阅读安全边界规则并向人类确认影响面！`
    );
    break;
  }
}

// Sensitive credentials
const CREDENTIAL_PATTERNS = [".pem", ".key", ".token", "credentials", "id_rsa", "secret"];

for (const pattern of CREDENTIAL_PATTERNS) {
  if (filePath.includes(pattern)) {
    warn(`🔐 Credential protection — never hardcode secrets in code/config! / 严禁在代码与配置中明文硬编码密钥！`);
    break;
  }
}

// Allow (these hooks are informational, not blocking)
process.exit(0);
