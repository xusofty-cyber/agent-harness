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
  // Phase 2 (2-4): parse failure stays fail-open (exit 0 — a hook must never
  // wedge the session on malformed input), but it is no longer silent: the
  // failure is logged to stderr so a broken pipe is visible, not invisible.
  process.stderr.write("[SECURITY-HOOK] stdin JSON parse failed; allowing (fail-open by design)\n");
  process.exit(0);
}

const toolName = data.tool_name || "";
const toolInput = data.tool_input || {};
const command = toolInput.command || "";

// Only process Bash tool calls
if (toolName !== "Bash") {
  process.exit(0);
}

// Named constants for magic values
const GIT_TIMEOUT_MS = 5000;  // git subprocess timeout
const MIN_ABBREV_LEN = 6;     // min length for --force abbreviations (--forc)
const MIN_ABBREV_LONG_LEN = 8; // min length for --force-with-lease abbreviations

// === Helper: get current git branch (optionally in a specific dir) ===
// Cached per hook invocation to avoid duplicate git spawns.
const _branchCache = new Map();
function getCurrentBranch(cwd) {
  const key = cwd || ".";
  if (_branchCache.has(key)) return _branchCache.get(key);
  let branch = "";
  try {
    branch = execSync("git branch --show-current", {
      encoding: "utf-8",
      timeout: GIT_TIMEOUT_MS,
      cwd: cwd || process.cwd(),
    }).trim();
  } catch {
    // leave empty
  }
  _branchCache.set(key, branch);
  return branch;
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

// ============================================================
// COMMAND NORMALIZATION (red-team hardening)
// ------------------------------------------------------------
// Attackers evade string matching via:
//   - quotes/escapes: "git" push, 'git' push, g\it push, gi''t push
//   - global options between git and subcommand: git -c x=y push, git -C dir push
//   - command substitution resolving to git: $(which git) push, `which git` push
//   - indirection: eval "...", sh -c "...", bash -c "..."
// Phase 2 (2-4): substitutions and indirections are expanded recursively
// (depth-limited; beyond the limit we warn and stop expanding — graded,
// fail-open, never a blanket deny). A substitution inside single quotes is
// literal text, not a substitution, and is left alone. Known remaining gap:
// xargs/find -exec indirection is not expanded (out of scope for 2-4).
// We normalize the command into argv tokens before matching.
// ============================================================

// === Command substitution + indirection expansion (Phase 2, 2-4) ===
// Maximum recursion depth for substitution/indirection expansion.
const MAX_EXPAND_DEPTH = 3;
// Sentinel token standing in for a substitution that resolves to the git binary.
const GIT_TOKEN = "\x00GIT\x00";

// Find $(...) and `...` spans in cmd, respecting quotes: a substitution
// inside single quotes is literal text; inside double quotes it is live.
// Returns [{ start, end, inner }] with start/end covering the whole span.
function findSubstitutions(cmd) {
  const spans = [];
  let i = 0;
  let inSingle = false;
  let inDouble = false;
  while (i < cmd.length) {
    const c = cmd[i];
    if (inSingle) {
      if (c === "'") inSingle = false;
      i++;
      continue;
    }
    if (c === "\\" && i + 1 < cmd.length) { i += 2; continue; }
    if (c === "'" && !inDouble) { inSingle = true; i++; continue; }
    if (c === '"') { inDouble = !inDouble; i++; continue; }
    if (c === "$" && cmd[i + 1] === "(") {
      // $(...) — balanced parens, quote-aware inside.
      let depth = 1;
      let j = i + 2;
      let s1 = false;
      let s2 = false;
      while (j < cmd.length && depth > 0) {
        const d = cmd[j];
        if (s1) { if (d === "'") s1 = false; }
        else if (d === "'") s1 = true;
        else if (d === '"') s2 = !s2;
        else if (!s2 && d === "\\") { j++; }
        else if (!s2 && d === "(") depth++;
        else if (!s2 && d === ")") depth--;
        j++;
      }
      spans.push({ start: i, end: j, inner: cmd.slice(i + 2, j - 1) });
      i = j;
      continue;
    }
    if (c === "`") {
      let j = i + 1;
      while (j < cmd.length && cmd[j] !== "`") {
        if (cmd[j] === "\\" && j + 1 < cmd.length) j++;
        j++;
      }
      spans.push({ start: i, end: j + 1, inner: cmd.slice(i + 1, j) });
      i = j + 1;
      continue;
    }
    i++;
  }
  return spans;
}

// Does this substitution evaluate to the git binary?
// Covered forms: $(which git), $(command -v git), $(type git),
// $(type -p git), $(git), $(/usr/bin/git) — and the backtick equivalents.
// Anything else is opaque: the inner text is still analyzed recursively (it
// may itself contain a git call), but the outer segment gains no git argv[0].
function substitutionResolvesToGit(inner) {
  const t = inner.trim();
  return /^(which|command\s+-v|type(?:\s+-[pP])?)\s+git$/.test(t)
    || /(?:^|\/)git$/.test(t);
}

// Rewrite cmd: a git-resolving substitution becomes GIT_TOKEN, any other
// substitution becomes a space. Returns { rewritten, innerCommands } — the
// inner texts are analyzed recursively by findGitInvocations.
// Exception: a substitution that is the VALUE of a leading VAR= assignment
// (x=$(which git) ...) is opaque even if it resolves to git — in shell that
// position is an environment value for the following command, not argv[0],
// so treating it as git would be a false positive.
function rewriteSubstitutions(cmd) {
  const spans = findSubstitutions(cmd);
  if (spans.length === 0) return { rewritten: cmd, innerCommands: [] };
  let out = "";
  let last = 0;
  const innerCommands = [];
  for (const s of spans) {
    const before = cmd.slice(0, s.start);
    const tail = before.split(/\s+/).pop();
    const inAssignment = /^[A-Za-z_][A-Za-z0-9_]*=$/.test(tail);
    out += cmd.slice(last, s.start);
    out += !inAssignment && substitutionResolvesToGit(s.inner) ? ` ${GIT_TOKEN} ` : " ";
    innerCommands.push(s.inner);
    last = s.end;
  }
  out += cmd.slice(last);
  return { rewritten: out, innerCommands };
}

// Minimal shell word splitter: handles single/double quotes and backslash
// escapes well enough for security matching (not a full POSIX parser).
function shellSplit(cmd) {
  const tokens = [];
  let cur = "";
  let i = 0;
  let inSingle = false;
  let inDouble = false;
  while (i < cmd.length) {
    const c = cmd[i];
    if (inSingle) {
      if (c === "'") inSingle = false;
      else cur += c;
    } else if (inDouble) {
      if (c === '"') inDouble = false;
      else if (c === "\\" && i + 1 < cmd.length && '"\\$`'.includes(cmd[i + 1])) {
        cur += cmd[i + 1];
        i++;
      } else cur += c;
    } else {
      if (c === "'") inSingle = true;
      else if (c === '"') inDouble = true;
      else if (c === "\\" && i + 1 < cmd.length) {
        if (process.platform === "win32" && /^[A-Za-z]:/.test(cur)) {
          cur += c;
        } else {
          cur += cmd[i + 1];
          i++;
        }
      } else if (/\s/.test(c)) {
        if (cur) { tokens.push(cur); cur = ""; }
      } else if (c === ";" || c === "&" || c === "|" || c === "(" || c === ")") {
        // Command separator: treat each segment independently.
        // For security, we analyze segments separately (split here).
        if (cur) { tokens.push(cur); cur = ""; }
        tokens.push("\x00SEP\x00");
      } else cur += c;
    }
    i++;
  }
  if (cur) tokens.push(cur);
  return tokens;
}

// Split command into segments at separators, return array of token arrays.
function commandSegments(cmd) {
  const tokens = shellSplit(cmd);
  const segments = [];
  let cur = [];
  for (const t of tokens) {
    if (t === "\x00SEP\x00") {
      if (cur.length) segments.push(cur);
      cur = [];
    } else cur.push(t);
  }
  if (cur.length) segments.push(cur);
  return segments;
}

// Git global options that consume the next token as a value.
const GIT_GLOBAL_OPTS_WITH_VALUE = new Set([
  "-c", "--config",
  "-C",
  "--git-dir", "--work-tree", "--namespace", "--super-prefix",
]);

// Resolve argv[0] of a token list: strip path, leading VAR=value assignments,
// and env/command/sudo wrappers. Returns { prog, idx } or null.
function resolveProg(tokens) {
  let idx = 0;
  while (idx < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[idx])) idx++;
  if (idx >= tokens.length) return null;
  let prog = tokens[idx].split("/").pop();
  while ((prog === "env" || prog === "command" || prog === "sudo") && idx + 1 < tokens.length) {
    idx++;
    while (idx < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[idx])) idx++;
    if (idx >= tokens.length) return null;
    prog = tokens[idx].split("/").pop();
  }
  return { prog, idx };
}

// Normalize one segment: if it invokes git, return { subcommand, args, gitDir }
// or null if not a git invocation.
function parseGitInvocation(tokens) {
  if (!tokens.length) return null;
  const resolved = resolveProg(tokens);
  if (!resolved) return null;
  let { prog } = resolved;
  let idx = resolved.idx;
  if (prog === GIT_TOKEN) prog = "git"; // $(which git) / `which git` resolved to git
  if (prog !== "git") return null;
  idx++;
  // SECURITY: Detect inline alias definitions (git -c alias.x=y) - these can
  // disguise the real subcommand. Be conservative and flag for manual review.
  for (let i = idx; i < tokens.length - 1; i++) {
    if ((tokens[i] === "-c" || tokens[i] === "--config") && 
        /^alias\./.test(tokens[i + 1])) {
      // Alias detected - cannot reliably determine subcommand, treat as suspicious
      return { subcommand: "__alias__", args: tokens.slice(idx), gitDir: null, suspicious: true };
    }
  }
  // Skip global options (and their values) to find the subcommand.
  let gitDir = null;
  while (idx < tokens.length) {
    const t = tokens[idx];
    if (t === "-C") {
      gitDir = tokens[idx + 1];
      idx += 2;
      continue;
    }
    if (t.startsWith("--git-dir=")) {
      gitDir = t.slice("--git-dir=".length);
      idx++;
      continue;
    }
    if (t === "--git-dir" || t === "--work-tree") {
      gitDir = tokens[idx + 1]; // work-tree implies repo context too
      idx += 2;
      continue;
    }
    if (GIT_GLOBAL_OPTS_WITH_VALUE.has(t)) { idx += 2; continue; }
    if (t.startsWith("-") && t !== "-") { idx++; continue; }
    break;
  }
  if (idx >= tokens.length) return null;
  return {
    subcommand: tokens[idx],
    args: tokens.slice(idx + 1),
    gitDir: gitDir || null,
  };
}

// Check all segments; return list of git invocations.
// Phase 2 (2-4): expands command substitutions and eval/sh -c indirection
// recursively (depth-limited). Beyond MAX_EXPAND_DEPTH we warn and stop —
// graded fail-open, never a blanket deny.
function findGitInvocations(cmd, depth = 0) {
  if (depth > MAX_EXPAND_DEPTH) {
    warn(`Deeply nested command indirection (depth > ${MAX_EXPAND_DEPTH}) — manual review recommended. / 命令嵌套过深，建议人工复核。`);
    return [];
  }
  const out = [];
  const { rewritten, innerCommands } = rewriteSubstitutions(cmd);
  for (const inner of innerCommands) {
    out.push(...findGitInvocations(inner, depth + 1));
  }
  for (const seg of commandSegments(rewritten)) {
    const inv = parseGitInvocation(seg);
    if (inv) { out.push(inv); continue; }
    // Indirection: eval "..." / sh|bash|zsh|dash -c "..." — analyze the
    // argument as a command of its own.
    const resolved = resolveProg(seg);
    if (!resolved) continue;
    const { prog } = resolved;
    const rest = seg.slice(resolved.idx + 1);
    if (prog === "eval") {
      out.push(...findGitInvocations(rest.join(" "), depth + 1));
    } else if (["sh", "bash", "zsh", "dash"].includes(prog)) {
      const cIdx = rest.indexOf("-c");
      if (cIdx !== -1 && rest[cIdx + 1] !== undefined) {
        out.push(...findGitInvocations(rest[cIdx + 1], depth + 1));
      }
    }
  }
  return out;
}

const gitInvocations = findGitInvocations(command);
const hasGitSubcommand = (sub) =>
  gitInvocations.some((g) => g.subcommand === sub);
// Branch check follows -C/--git-dir when present.
function branchFor(inv) {
  return getCurrentBranch(inv.gitDir || undefined);
}

// === Sensitive-path review advisory (open-code-review Phase 2) ===
// (unchanged — see original file for full implementation)
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// Prefer __dirname derivation (hook lives at .claude/hooks/); only fall back
// to git when the derived path doesn't look like a repo root.
let _repoRoot = null;
function getRepoRoot() {
  if (_repoRoot) return _repoRoot;
  const derived = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
  try {
    if (existsSync(join(derived, ".agents")) || existsSync(join(derived, ".git"))) {
      _repoRoot = derived;
      return _repoRoot;
    }
  } catch {
    // fall through to git
  }
  try {
    _repoRoot = execSync("git rev-parse --show-toplevel", {
      encoding: "utf-8",
      timeout: GIT_TIMEOUT_MS,
    }).trim();
  } catch {
    _repoRoot = derived;
  }
  return _repoRoot;
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
      timeout: GIT_TIMEOUT_MS,
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
      timeout: GIT_TIMEOUT_MS,
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
          timeout: GIT_TIMEOUT_MS,
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
        timeout: GIT_TIMEOUT_MS,
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
// Operate on NORMALIZED git invocations, not raw strings.
// ============================================================

// 1. Direct commit on protected branches
for (const inv of gitInvocations) {
  if (inv.subcommand === "commit") {
    const branch = branchFor(inv);
    if (isProtectedBranch(branch)) {
      deny(
        `[SECURITY-HOOK] ❌ Direct commit on protected branch '${branch}' is prohibited! / 禁止在受保护分支上直接 commit！` +
          ` Make changes on a temp branch, then merge. / 新改动必须在临时分支提交，再经 merge 合入。`
      );
    }
  }
}

// 2. Force push (any form) — includes +refspec and bundled -f flags
function isForcePush(inv) {
  if (inv.subcommand !== "push") return false;
  for (const a of inv.args) {
    // Git accepts unambiguous abbreviations: --forc, --for, --fo all mean --force.
    // Check both directions: a starts with --force (e.g. --force-with-lease=),
    // or --force starts with a (abbreviation, e.g. --forc). Minimum 5 chars to avoid --fo matching --format.
    if (a.startsWith("--force")) return true;
    if (a.startsWith("--") && "--force".startsWith(a) && a.length >= MIN_ABBREV_LEN) return true;
    // Same for --force-with-lease and --force-if-includes abbreviations
    if (a.startsWith("--") && ("--force-with-lease".startsWith(a) || "--force-if-includes".startsWith(a)) && a.length >= MIN_ABBREV_LONG_LEN) return true;
    // Bundled short flags: -vf, -fv, -f → contains 'f' as a short flag
    if (/^-[a-zA-Z]+$/.test(a) && !a.startsWith("--") && a.includes("f")) return true;
    // +refspec prefix = force update for that ref
    if (a.startsWith("+")) return true;
  }
  return false;
}

for (const inv of gitInvocations) {
  // SECURITY: Inline git aliases obscure the real subcommand - warn user
  if (inv.suspicious && inv.subcommand === "__alias__") {
    warn(
      `⚠️ Inline git alias detected - subcommand obfuscated, manual review recommended. / 检测到内联 git 别名，子命令被混淆，建议人工复核。`
    );
  }
  if (isForcePush(inv)) {
    deny(
      `[SECURITY-HOOK] ❌ Force push / +refspec (history rewrite) permanently prohibited! / 永久禁止！`
    );
  }
}

// 3. Delete protected remote branches
const PROTECTED_REF_RE = new RegExp(`^(?:refs/heads/)?${PROTECTED_BRANCH_PATTERN}$`);
for (const inv of gitInvocations) {
  if (inv.subcommand !== "push") continue;
  const args = inv.args;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    // --delete <branch> / --delete=<branch>
    if (a === "--delete" || a === "-d") {
      const target = args[i + 1];
      if (target && PROTECTED_REF_RE.test(target)) {
        deny(`[SECURITY-HOOK] ❌ Deleting protected remote branch '${target}' permanently prohibited! / 永久禁止！`);
      }
    } else if (a.startsWith("--delete=")) {
      const target = a.slice("--delete=".length);
      if (PROTECTED_REF_RE.test(target)) {
        deny(`[SECURITY-HOOK] ❌ Deleting protected remote branch '${target}' permanently prohibited! / 永久禁止！`);
      }
    }
    // :<branch> / :refs/heads/<branch> refspec deletion
    else if (/^:(?!\/)/.test(a)) {
      const target = a.slice(1);
      if (target && PROTECTED_REF_RE.test(target)) {
        deny(`[SECURITY-HOOK] ❌ Deleting protected remote branch '${target}' permanently prohibited! / 永久禁止！`);
      }
    }
  }
}

// 3b. git clean with -d/-f (destroys untracked files)
for (const inv of gitInvocations) {
  if (inv.subcommand === "clean") {
    const hasDestructive = inv.args.some((a) => {
      if (/^-[a-zA-Z]+$/.test(a) && !a.startsWith("--")) {
        return /[dfDF]/.test(a); // -d, -f (also -D, -F)
      }
      return a === "--force";
    });
    if (hasDestructive) {
      deny(`[SECURITY-HOOK] ❌ git clean -d/-f (deletes untracked files) permanently prohibited! / 永久禁止！`);
    }
  }
}

// 3c. git update-ref touching protected refs
for (const inv of gitInvocations) {
  if (inv.subcommand === "update-ref") {
    for (const a of inv.args) {
      // ref is typically args[0] (or after -m msg / --no-deref)
      if (PROTECTED_REF_RE.test(a)) {
        deny(`[SECURITY-HOOK] ❌ git update-ref rewriting protected ref '${a}' permanently prohibited! / 永久禁止！`);
      }
    }
  }
}

// 4. Rebase on protected branches
for (const inv of gitInvocations) {
  if (inv.subcommand === "rebase") {
    const branch = branchFor(inv);
    if (isProtectedBranch(branch)) {
      deny(
        `[SECURITY-HOOK] ❌ Rebase on protected branch '${branch}' is prohibited! Use merge instead. / 禁止在受保护分支上执行 rebase！请使用 merge。`
      );
    }
  }
}

// ============================================================
// WARNINGS (exit 0 — non-blocking, informational)
// ============================================================

// 5. Merge/push on protected branches (needs human authorization)
for (const inv of gitInvocations) {
  if (inv.subcommand === "merge" || inv.subcommand === "push") {
    const branch = branchFor(inv);
    if (isProtectedBranch(branch)) {
      warn(
        `Merge/push on protected branch '${branch}' requires explicit human authorization. / 必须经人类明确授权。`
      );
      break;
    }
  }
}

// Push arguments can target a protected branch even when the current branch is not protected.
for (const inv of gitInvocations) {
  if (inv.subcommand !== "push") continue;
  const hit = inv.args.some((a) => {
    // strip leading + (force) for target matching; force itself already denied above
    const t = a.startsWith("+") ? a.slice(1) : a;
    // refspec forms: <src>:<dst>, :<dst> (delete), <dst>
    const dst = t.includes(":") ? t.split(":").pop() : t;
    return dst && PROTECTED_REF_RE.test(dst);
  });
  if (hit) {
    warn("Push refspec may target a protected branch — confirm target and get authorization. / 请先确认目标并取得明确授权。");
    break;
  }
}

// 6. Recursive delete
// NOTE: flag bundle allows any mix of rm short flags containing r/R
if (/\brm\s+(?:-(?:[fidrRv]*[rR][fidrRv]*)(?!\S)|--recursive\b)/.test(command)) {
  warn(
    `Detected recursive rm -rf — verify target is not a system/project source directory! / 检测到 rm -rf 递归删除，请确认目标路径！`
  );
}

// 7. git reset --hard
if (hasGitSubcommand("reset") && gitInvocations.some((g) =>
  g.subcommand === "reset" && g.args.includes("--hard"))) {
  warn(
    `git reset --hard permanently discards working tree changes! Do not run unconfirmed. / 会永久丢弃工作区改动！`
  );
}

// 8. Blind git add
for (const inv of gitInvocations) {
  if (inv.subcommand === "add") {
    const blind = inv.args.some((a) =>
      a === "." || a === "-A" || a === "--all");
    if (blind) {
      warn(
        `Blind 'git add .' is prohibited (may stage build artifacts/temp files); use 'git add <explicit-path>'. / 严禁 git add . 盲目暂存，请改用明确路径。`
      );
      break;
    }
  }
}

// 9. Delete temporary remote branches (non-protected)
for (const inv of gitInvocations) {
  if (inv.subcommand === "push") {
    const deletes = inv.args.some((a) =>
      a === "--delete" || a === "-d" || a.startsWith("--delete=") || /^:[^/]/.test(a));
    if (deletes) {
      // If we haven't already denied (protected branches handled above), just warn
      warn(
        `Deleting a remote branch requires explicit human authorization and merge confirmation. / 必须经人类明确授权并确认已合并。`
      );
      break;
    }
  }
}

// 10. Sensitive-path commit/push advisory (open-code-review)
// Non-blocking: suggest the open-code-review skill when staged/pushed
// files match sensitive-path patterns. Deterministic only.
if (hasGitSubcommand("commit") || hasGitSubcommand("push")) {
  const patterns = loadSensitivePatterns();
  if (patterns.length > 0) {
    const isPush = hasGitSubcommand("push");
    const files = isPush ? pushedFiles() : stagedFiles();
    const regexes = patterns.map(globToRegExp);
    const hits = files.filter((f) => regexes.some((re) => re.test(f)));
    if (hits.length > 0) {
      const shown = hits.slice(0, 5).join(", ");
      const more = hits.length > 5 ? ` 等共 ${hits.length} 个文件` : "";
      warn(
        `本次 ${isPush ? "push" : "commit"} 触及敏感路径（${shown}${more}）——` +
          `建议先运行 open-code-review skill 做一次代码评审 / run the open-code-review skill first, ` +
          `确认无 Critical/High 问题后再继续。`
      );
    }
  }
}

// If nothing matched or only warnings, allow
process.exit(0);
