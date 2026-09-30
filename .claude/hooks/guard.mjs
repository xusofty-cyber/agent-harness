#!/usr/bin/env node
// ==============================================================================
// guard.mjs — Claude Code PreToolUse Security Hook (Bash matcher)
// Reads tool input from stdin JSON (official protocol).
// Uses exit 2 / permissionDecision:deny for hard blocks.
// ==============================================================================

import { execSync } from "child_process";

// Read stdin JSON
let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data;
try {
  data = JSON.parse(input);
} catch {
  // If stdin is not valid JSON, allow (don't block on parse errors)
  process.exit(0);
}

const toolName = data.tool_name || "";
const toolInput = data.tool_input || {};
const command = toolInput.command || "";

// Only process Bash tool calls
if (toolName !== "Bash") {
  process.exit(0);
}

// === Helper: get current git branch ===
function getCurrentBranch() {
  try {
    return execSync("git branch --show-current", {
      encoding: "utf-8",
      timeout: 5000,
    }).trim();
  } catch {
    return "";
  }
}

// === Helper: deny with exit 2 + permissionDecision JSON ===
function deny(reason) {
  // Output structured JSON for robust denial
  const response = {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: reason,
    },
  };
  process.stdout.write(JSON.stringify(response));
  process.exit(2);
}

// === Helper: warn (non-blocking, informational) ===
function warn(message) {
  process.stderr.write(`[SECURITY-HOOK] ⚠️ ${message}\n`);
  // exit 0 = allow, warning is informational only
}

// === Protected branch list ===
const PROTECTED_BRANCHES = [
  "develop",
  "master",
  "main",
  "staging",
];

function isProtectedBranch(branch) {
  if (!branch) return false;
  if (PROTECTED_BRANCHES.includes(branch)) return true;
  if (branch.startsWith("release")) return true;
  return false;
}

// ============================================================
// HARD BLOCKS (exit 2 — unconditionally denied)
// ============================================================

// 1. Direct commit on protected branches
if (/\bgit\s+commit\b/.test(command)) {
  const branch = getCurrentBranch();
  if (isProtectedBranch(branch)) {
    deny(
      `[SECURITY-HOOK] ❌ 禁止在受保护分支 ${branch} 上直接 commit！` +
        `新改动必须在临时分支提交，再经 merge 合入。`
    );
  }
}

// 2. Force push (any form)
if (
  /\bgit\s+push\b/.test(command) &&
  (/--force\b/.test(command) ||
    /--force-with-lease\b/.test(command) ||
    /\s-f\b/.test(command))
) {
  deny(
    `[SECURITY-HOOK] ❌ force push / force-with-lease（历史改写）永久禁止！`
  );
}

// 3. Delete protected remote branches
if (/\bgit\s+push\b/.test(command) && /--delete\b/.test(command)) {
  for (const pb of PROTECTED_BRANCHES) {
    if (command.includes(`--delete ${pb}`) || command.includes(`--delete ${pb} `)) {
      deny(
        `[SECURITY-HOOK] ❌ 删除受保护远程分支（${pb}）永久禁止！`
      );
    }
  }
  // Also check : syntax for branch deletion
  for (const pb of PROTECTED_BRANCHES) {
    if (new RegExp(`\\s:${pb}\\b`).test(command)) {
      deny(
        `[SECURITY-HOOK] ❌ 删除受保护远程分支（${pb}）永久禁止！`
      );
    }
  }
}

// Also check release* with : syntax
if (/\bgit\s+push\b/.test(command) && /\s:release/.test(command)) {
  deny(
    `[SECURITY-HOOK] ❌ 删除受保护远程分支（release*）永久禁止！`
  );
}

// 4. Rebase on protected branches
if (/\bgit\s+rebase\b/.test(command)) {
  const branch = getCurrentBranch();
  if (isProtectedBranch(branch)) {
    deny(
      `[SECURITY-HOOK] ❌ 禁止在受保护分支 ${branch} 上执行 rebase！请使用 merge。`
    );
  }
}

// ============================================================
// WARNINGS (exit 0 — non-blocking, informational)
// ============================================================

// 5. Merge/push on protected branches (needs human authorization)
if (/\bgit\s+(merge|push)\b/.test(command)) {
  const branch = getCurrentBranch();
  if (isProtectedBranch(branch)) {
    warn(
      `受保护分支 ${branch} 上的 merge/push —— 必须经人类明确授权方可执行；未授权请停下确认。`
    );
  }
}

// 6. Recursive delete
if (/\brm\s+(-rf|-r\s|-fr)/.test(command)) {
  warn(
    `检测到 rm -rf 递归删除，请确认目标路径非核心系统/项目源码目录！`
  );
}

// 7. git reset --hard
if (/\bgit\s+reset\s+--hard\b/.test(command)) {
  warn(
    `git reset --hard 会永久丢弃工作区改动！未确认请勿执行。`
  );
}

// 8. Blind git add
if (/\bgit\s+add\s+(-A|\.)\b/.test(command)) {
  warn(
    `严禁 git add . 全量盲目暂存（防止误带入编译产物与临时文件），请改用 git add <明确路径>！`
  );
}

// 9. Delete temporary remote branches (non-protected)
if (
  /\bgit\s+push\b/.test(command) &&
  (/--delete\b/.test(command) || /\s:/.test(command))
) {
  // If we haven't already denied (protected branches handled above), just warn
  warn(
    `删除临时远程分支——必须经人类明确授权并确认已合并。`
  );
}

// If nothing matched or only warnings, allow
process.exit(0);
