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
      `🔴 触碰高风险文件（构建配置/公共结构/协议定义/授权许可）——` +
        `请先阅读 .agents/rules/security-boundary.md 并向人类确认影响面！`
    );
    break;
  }
}

// Sensitive credentials
const CREDENTIAL_PATTERNS = [".pem", ".key", ".token", "credentials", "id_rsa", "secret"];

for (const pattern of CREDENTIAL_PATTERNS) {
  if (filePath.includes(pattern)) {
    warn(`🔐 敏感凭证防护——严禁在代码与配置中明文硬编码密钥！`);
    break;
  }
}

// Allow (these hooks are informational, not blocking)
process.exit(0);
