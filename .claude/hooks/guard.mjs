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

const PROTECTED_BRANCH_PATTERN = "(?:develop|master|main|staging|release[^\\s:]*)";

function isProtectedBranch(branch) {
  if (!branch) return false;
  if (PROTECTED_BRANCHES.includes(branch)) return true;
  if (branch.startsWith("release")) return true;
  return false;
}

// === Sensitive-path review advisory (open-code-review Phase 2) ===
// When committing/pushing files under sensitive paths, emit a non-blocking
// warning suggesting the open-code-review skill. Deterministic only —
// no LLM calls inside the hook.
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

function getRepoRoot() {
  try {
    return execSync("git rev-parse --show-toplevel", {
      encoding: "utf-8",
      timeout: 5000,
    }).trim();
  } catch {
    // Fallback: assume standard layout (.claude/hooks/ two levels below root)
    return join(dirname(fileURLToPath(import.meta.url)), "..", "..");
  }
}

// Default sensitive patterns (used when .agents/review-sensitive-paths.json
// is absent — e.g. in projects deployed without it). Projects can override
// by creating that file.
const DEFAULT_SENSITIVE_PATTERNS = [
  "**/auth/**",
  "**/crypto/**",
  "**/security/**",
  "**/payment/**",
  "**/billing/**",
  "**/*.key",
  "**/*.pem",
  "**/*.p12",
  "**/*.pfx",
  "**/secrets/**",
  "**/credentials/**",
  "**/.env*",
  "**/migrations/**",
];

function loadSensitivePatterns() {
  try {
    const cfgPath = join(getRepoRoot(), ".agents", "review-sensitive-paths.json");
    if (!existsSync(cfgPath)) return DEFAULT_SENSITIVE_PATTERNS;
    const cfg = JSON.parse(readFileSync(cfgPath, "utf-8"));
    return Array.isArray(cfg.patterns) && cfg.patterns.length > 0
      ? cfg.patterns
      : DEFAULT_SENSITIVE_PATTERNS;
  } catch {
    return DEFAULT_SENSITIVE_PATTERNS;
  }
}

function globToRegExp(glob) {
  // Supports ** (any chars incl /) and * (any chars except /).
  // A leading "**/" also matches zero directories (repo-root files).
  let re = "";
  let i = 0;
  while (i < glob.length) {
    if (glob.startsWith("**/", i)) {
      re += "(.*/)?";
      i += 3;
    } else if (glob.startsWith("**", i)) {
      re += ".*";
      i += 2;
    } else if (glob[i] === "*") {
      re += "[^/]*";
      i += 1;
    } else if ("+?^${}()|[]\\.".includes(glob[i])) {
      re += "\\" + glob[i];
      i += 1;
    } else {
      re += glob[i];
      i += 1;
    }
  }
  return new RegExp("^" + re + "$");
}

function stagedFiles() {
  try {
    return execSync("git diff --cached --name-only", {
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "ignore"],
    })
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
  } catch {
    return [];
  }
}

function pushedFiles() {
  // Files that would be pushed: local HEAD vs upstream
  try {
    return execSync("git diff --name-only @{u}...HEAD", {
      encoding: "utf-8",
      timeout: 5000,
      stdio: ["pipe", "pipe", "ignore"],
    })
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
  } catch {
    // If no upstream tracking branch (@{u}), fall back to default branch comparison
    for (const base of ["origin/main", "origin/master", "main", "master"]) {
      try {
        return execSync(`git diff --name-only ${base}...HEAD`, {
          encoding: "utf-8",
          timeout: 5000,
          stdio: ["pipe", "pipe", "ignore"],
        })
          .split("\n")
          .map((l) => l.trim())
          .filter(Boolean);
      } catch {
        // try next base
      }
    }
    // Last resort: files in current HEAD commit
    try {
      return execSync("git show -m --name-only --pretty=format: HEAD", {
        encoding: "utf-8",
        timeout: 5000,
        stdio: ["pipe", "pipe", "ignore"],
      })
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);
    } catch {
      return [];
    }
  }
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
if (/\bgit\s+push\b/.test(command)) {
  const deletedBranch = new RegExp(
    `--delete(?:=|\\s+)(${PROTECTED_BRANCH_PATTERN})(?=\\s|$)`
  ).exec(command);
  const deletedRef = new RegExp(
    `(?:^|\\s):(?:refs/heads/)?(${PROTECTED_BRANCH_PATTERN})(?=\\s|$)`
  ).exec(command);
  if (deletedBranch || deletedRef) {
    deny(
      `[SECURITY-HOOK] ❌ 删除受保护远程分支（${(deletedBranch || deletedRef)[1]}）永久禁止！`
    );
  }
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

// Push arguments can target a protected branch even when the current branch is not protected.
const pushArguments = /\bgit\s+push\b([\s\S]*)/.exec(command)?.[1] || "";
if (
  new RegExp(
    `(?:^|\\s)(?:[^\\s:]+:)?(?:refs/heads/)?${PROTECTED_BRANCH_PATTERN}(?=\\s|$)`
  ).test(pushArguments)
) {
  warn("push refspec 目标可能是受保护分支——请先确认目标并取得明确授权。");
}

// 6. Recursive delete
// NOTE: flag bundle allows any mix of rm short flags containing r/R
// (old pattern `-r\s` also missed `rm -r` at end-of-command).
if (/\brm\s+(?:-(?:[fidrRv]*[rR][fidrRv]*)(?!\S)|--recursive\b)/.test(command)) {
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
// NOTE: `\.` must not be followed by `\b` — there is no word boundary after
// "." at end-of-command or before a space, so the old pattern never matched
// `git add .`. `(?!\S)` requires end-of-command or whitespace instead.
// `--all` is the long form of `-A` and is covered too.
if (/\bgit\s+add\s+(?:(?:-A|--all)(?!\S)|\.(?!\S))/.test(command)) {
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

// 10. Sensitive-path commit/push advisory (open-code-review)
// Non-blocking: suggest the open-code-review skill when staged/pushed
// files match sensitive-path patterns. Deterministic only.
if (/\bgit\s+(commit|push)\b/.test(command)) {
  const patterns = loadSensitivePatterns();
  if (patterns.length > 0) {
    const isPush = /\bgit\s+push\b/.test(command);
    const files = isPush ? pushedFiles() : stagedFiles();
    const regexes = patterns.map(globToRegExp);
    const hits = files.filter((f) => regexes.some((re) => re.test(f)));
    if (hits.length > 0) {
      const shown = hits.slice(0, 5).join(", ");
      const more = hits.length > 5 ? ` 等共 ${hits.length} 个文件` : "";
      warn(
        `本次 ${isPush ? "push" : "commit"} 触及敏感路径（${shown}${more}）——` +
          `建议先运行 open-code-review skill（Tier A 委托 / Tier B 方法论）做一次确定性代码评审，` +
          `确认无 Critical/High 问题后再继续。`
      );
    }
  }
}

// If nothing matched or only warnings, allow
process.exit(0);
