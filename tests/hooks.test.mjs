#!/usr/bin/env node
// ==============================================================================
// tests/hooks.test.mjs — black-box tests for .claude/hooks/guard.mjs
// Feeds Claude Code PreToolUse stdin JSON to the hook and asserts on
// exit code / stdout / stderr. Run: `node tests/hooks.test.mjs`
// Uses only node built-ins (node:test + node:child_process).
// ==============================================================================

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const GUARD = join(REPO_ROOT, ".claude/hooks/guard.mjs");

function runHook(command, cwd = REPO_ROOT) {
  const payload = JSON.stringify({
    tool_name: "Bash",
    tool_input: { command },
  });
  const res = spawnSync("node", [GUARD], {
    input: payload,
    cwd,
    encoding: "utf-8",
  });
  return {
    exitCode: res.status,
    stdout: res.stdout || "",
    stderr: res.stderr || "",
  };
}

function makeRepo(branch) {
  const dir = mkdtempSync(join(tmpdir(), "hook-test-"));
  execFileSync("git", ["init", "-b", branch, "-q"], { cwd: dir });
  execFileSync("git", ["config", "user.email", "ci@example.com"], { cwd: dir });
  execFileSync("git", ["config", "user.name", "CI"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "# test\n");
  execFileSync("git", ["add", "README.md"], { cwd: dir });
  execFileSync("git", ["commit", "-qm", "init"], { cwd: dir });
  return dir;
}

// --- Blind git add warnings (regression: old `(-A|\.)\b` never matched `git add .`) ---
test("warns on `git add .` at end of command", () => {
  const r = runHook("git add .");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /盲目暂存/);
});

test("warns on `git add .` mid-command", () => {
  const r = runHook("git add . && npm test");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /盲目暂存/);
});

test("warns on `git add -A` and `git add --all`", () => {
  for (const cmd of ["git add -A", "git add --all"]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 0, cmd);
    assert.match(r.stderr, /盲目暂存/, cmd);
  }
});

test("does NOT warn on explicit paths", () => {
  for (const cmd of ["git add src/index.js", "git add ./docs", "git add .gitignore"]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 0, cmd);
    assert.doesNotMatch(r.stderr, /盲目暂存/, cmd);
  }
});

// --- Recursive rm warnings (regression: old pattern missed `rm -R` and `rm -r` at EOL) ---
test("warns on recursive rm variants", () => {
  for (const cmd of ["rm -rf /tmp/x", "rm -fr /tmp/x", "rm -R /tmp/x", "rm -r", "rm -irf x", "rm --recursive x"]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 0, cmd);
    assert.match(r.stderr, /递归删除/, cmd);
  }
});

test("does NOT warn on plain rm or rm of dash-files", () => {
  for (const cmd of ["rm README.md", "rm -f a.log", "rm -report"]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 0, cmd);
    assert.doesNotMatch(r.stderr, /递归删除/, cmd);
  }
});

// --- Hard blocks ---
test("denies force push in any form", () => {
  for (const cmd of [
    "git push --force origin main",
    "git push -f origin main",
    "git push --force-with-lease",
  ]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 2, cmd);
    assert.match(r.stdout, /deny/);
  }
});

test("denies git clean with -d/-f flags", () => {
  for (const cmd of [
    "git clean -xdf",
    "git clean -fd",
    "git clean -f",
  ]) {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 2, cmd);
    assert.match(r.stdout, /deny/);
  }
  // dry-run without -d/-f should not be blocked
  const safe = runHook("git clean -n");
  assert.notEqual(safe.exitCode, 2, "git clean -n");
});

test("denies direct commit on protected branches, allows on feature branches", () => {
  const mainRepo = makeRepo("main");
  const denied = runHook("git commit -m 'x'", mainRepo);
  assert.equal(denied.exitCode, 2);
  assert.match(denied.stdout, /deny/);

  const featRepo = makeRepo("feature/awesome");
  const allowed = runHook("git commit -m 'x'", featRepo);
  assert.equal(allowed.exitCode, 0);
});

test("denies deleting protected remote branches", () => {
  const r = runHook("git push origin --delete main");
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /deny/);
});

test("denies rebase on protected branches", () => {
  const mainRepo = makeRepo("main");
  const r = runHook("git rebase main", mainRepo);
  assert.equal(r.exitCode, 2);
});

// --- Robustness ---
test("allows on malformed stdin (fail-open)", () => {
  const res = spawnSync("node", [GUARD], { input: "not json", encoding: "utf-8" });
  assert.equal(res.status, 0);
});

// --- Graded parse failure (merged from v3-yunyi, Phase 2.5): log + alert, not silent, not fail-closed ---
test("logs and alerts on malformed stdin (graded policy)", () => {
  const dir = mkdtempSync(join(tmpdir(), "hook-parse-"));
  const res = spawnSync("node", [GUARD], { input: "not json", cwd: dir, encoding: "utf-8" });
  assert.equal(res.status, 0);
  assert.match(res.stderr, /guard-alerts\.jsonl/);
  const logPath = join(dir, ".claude", "hooks", "guard-alerts.jsonl");
  assert.equal(existsSync(logPath), true);
  const line = readFileSync(logPath, "utf-8");
  assert.match(line, /stdin_parse_failed/);
  assert.doesNotMatch(line, /not json/); // raw stdin must never be logged
});

// --- Indirect git via resolver substitution (merged from v3-yunyi, D27) ---
// Conjunctive rule: resolver + dangerous arg in the SAME segment denies.
// The double-quoted cases are the regression the merge closes: the
// sentinel rewrite collapses "$(which git)" into one token, so the
// normalized path never sees a git argv[0] — only this raw-text check
// catches them.
test("denies resolver indirection + force push", () => {
  assert.equal(runHook("$(which git) push --force origin main").exitCode, 2);
});

test("denies resolver indirection in backticks + force push", () => {
  assert.equal(runHook("`which git` push --force origin main").exitCode, 2);
});

test("denies resolver indirection + clean -df", () => {
  assert.equal(runHook("$(which git) clean -df").exitCode, 2);
});

test("denies alternate resolver (command -v) + force-with-lease", () => {
  assert.equal(runHook("$(command -v git) push --force-with-lease").exitCode, 2);
});

test("allows benign resolver indirection (rev-parse)", () => {
  assert.equal(runHook("$(which git) rev-parse HEAD").exitCode, 0);
});

test("allows resolver alone", () => {
  assert.equal(runHook("echo $(which git)").exitCode, 0);
});

test("allows resolver indirection without a dangerous arg", () => {
  assert.equal(runHook("$(which git) push origin main").exitCode, 0);
});

test("allows dangerous token in a different segment than the resolver", () => {
  assert.equal(runHook("echo --force; $(which git) status").exitCode, 0);
});

test("allows single-quoted resolver text (literal, not executed)", () => {
  assert.equal(runHook("echo 'use $(which git) push --force'").exitCode, 0);
});

test("denies double-quoted resolver indirection + force push", () => {
  assert.equal(runHook('"$(which git)" push --force origin main').exitCode, 2);
});

test("denies resolver indirection + protected-ref delete", () => {
  assert.equal(runHook("$(which git) push --delete main").exitCode, 2);
});

test("allows benign subcommand via resolver indirection", () => {
  assert.equal(runHook("$(which git) stash list").exitCode, 0);
});

test("ignores non-Bash tools", () => {
  const payload = JSON.stringify({ tool_name: "Write", tool_input: { command: "git add ." } });
  const res = spawnSync("node", [GUARD], { input: payload, encoding: "utf-8" });
  assert.equal(res.status, 0);
  assert.equal((res.stderr || "").trim(), "");
});

// --- Sensitive-path commit advisory (open-code-review Phase 2) ---
import { mkdirSync } from "node:fs";

function makeRepoWithSensitiveConfig(branch) {
  const dir = makeRepo(branch);
  mkdirSync(join(dir, ".agents"), { recursive: true });
  writeFileSync(
    join(dir, ".agents", "review-sensitive-paths.json"),
    JSON.stringify({ patterns: ["**/auth/**", "**/*.key"] })
  );
  return dir;
}

function stageFile(dir, relPath) {
  const full = join(dir, relPath);
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, "test content\n");
  execFileSync("git", ["add", relPath], { cwd: dir });
}

test("warns (non-blocking) on commit touching sensitive paths", () => {
  const dir = makeRepoWithSensitiveConfig("feature/sso");
  stageFile(dir, "src/auth/login.py");
  const r = runHook("git commit -m 'sso'", dir);
  assert.equal(r.exitCode, 0); // advisory only, never blocks
  assert.match(r.stderr, /敏感路径/);
  assert.match(r.stderr, /open-code-review/);
});

test("stays silent on commit with only non-sensitive files", () => {
  const dir = makeRepoWithSensitiveConfig("feature/ui");
  stageFile(dir, "src/ui/button.py");
  const r = runHook("git commit -m 'ui'", dir);
  assert.equal(r.exitCode, 0);
  assert.doesNotMatch(r.stderr, /敏感路径/);
});

test("uses built-in defaults when sensitive-path config is absent", () => {
  const dir = makeRepo("feature/nodefaults"); // no .agents/review-sensitive-paths.json
  stageFile(dir, "src/auth/login.py"); // matches built-in **/auth/**
  const r = runHook("git commit -m 'x'", dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /敏感路径/);
});

test("warns on push touching sensitive paths even without upstream tracking branch", () => {
  const dir = makeRepoWithSensitiveConfig("feature/payment");
  stageFile(dir, "src/auth/token.py");
  execFileSync("git", ["commit", "-m", "add token"], { cwd: dir });
  const r = runHook("git push origin feature/payment", dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /敏感路径/);
  assert.match(r.stderr, /open-code-review/);
});

// --- Red-team regression: bypass variants must be denied ---
test("denies quoted git force push", () => {
  const r = runHook('"git" push --force origin main');
  assert.equal(r.exitCode, 2);
});

test("denies escaped git force push", () => {
  const r = runHook("g\\it push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies git -c global option force push", () => {
  const r = runHook("git -c user.name=x push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies git --git-dir force push", () => {
  const r = runHook("git --git-dir=.git push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies +refspec force push (no -f flag)", () => {
  const r = runHook("git push origin +main:main");
  assert.equal(r.exitCode, 2);
});

test("denies bundled -vf force push", () => {
  const r = runHook("git push -vf origin main");
  assert.equal(r.exitCode, 2);
});

test("denies git update-ref on protected ref", () => {
  const r = runHook("git update-ref refs/heads/main abc123def456");
  assert.equal(r.exitCode, 2);
});

test("denies commit on protected branch via -C", () => {
  const mainRepo = makeRepo("main");
  const featureRepo = makeRepo("feature/x");
  // Run from feature repo but target main repo via -C
  const r = runHook(`git -C ${mainRepo} commit -m evil`, featureRepo);
  assert.equal(r.exitCode, 2);
});

// --- P0: dangerous commands in non-first segments ---
test("denies force push after &&", () => {
  const r = runHook("npm test && git push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies force push after ;", () => {
  const r = runHook("echo ok; git push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies delete protected branch after ||", () => {
  const r = runHook("git status || git push origin --delete main");
  assert.equal(r.exitCode, 2);
});

// --- P0: delete protected branch variants ---
test("denies --delete=main form", () => {
  const r = runHook("git push origin --delete=main");
  assert.equal(r.exitCode, 2);
});

test("denies :main refspec deletion", () => {
  const r = runHook("git push origin :main");
  assert.equal(r.exitCode, 2);
});

test("denies :refs/heads/main deletion", () => {
  const r = runHook("git push origin :refs/heads/main");
  assert.equal(r.exitCode, 2);
});

test("denies quoted git delete protected", () => {
  const r = runHook('"git" push origin --delete main');
  assert.equal(r.exitCode, 2);
});

// --- P1: warning branches ---
test("warns on push to protected branch", () => {
  const mainRepo = makeRepo("main");
  const r = runHook("git push origin main", mainRepo);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /protected branch/);
});

test("warns on git reset --hard", () => {
  const r = runHook("git reset --hard HEAD~1");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /reset --hard/);
});

// --- P1: false positives (normal ops must pass) ---
test("allows push to feature branch", () => {
  const r = runHook("git push origin feature/my-work");
  assert.equal(r.exitCode, 0);
});

test("allows normal push without force flags", () => {
  const r = runHook("git push origin main");
  assert.equal(r.exitCode, 0);
  // Should warn (protected target) but not deny
});

test("allows git push with -v (not force)", () => {
  const r = runHook("git push -v origin feature/x");
  assert.equal(r.exitCode, 0);
});

test("denies --force-with-lease=<ref> form", () => {
  const r = runHook("git push --force-with-lease=main:abc123 origin main");
  assert.equal(r.exitCode, 2);
});

test("denies abbreviated --forc", () => {
  const r = runHook("git push --forc origin main");
  assert.equal(r.exitCode, 2);
});

test("denies abbreviated --force-w", () => {
  const r = runHook("git push --force-w origin main");
  assert.equal(r.exitCode, 2);
});

test("denies env var prefix bypass", () => {
  const r = runHook("FOO=bar git push --force origin main");
  assert.equal(r.exitCode, 2);
});

// --- Phase 2 (2-4): command substitution + indirection bypasses ---
test("denies $(git push --force) substitution", () => {
  const r = runHook("$(git push --force origin main)");
  assert.equal(r.exitCode, 2);
});

test("denies $(which git) push --force", () => {
  const r = runHook("$(which git) push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies `which git` push --force (backticks)", () => {
  const r = runHook("`which git` push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies $(command -v git) push --force", () => {
  const r = runHook("$(command -v git) push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies sudo $(which git) push --force", () => {
  const r = runHook("sudo $(which git) push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("denies eval \"git push --force\"", () => {
  const r = runHook("eval \"git push --force origin main\"");
  assert.equal(r.exitCode, 2);
});

test("denies sh -c 'git push --force'", () => {
  const r = runHook("sh -c 'git push --force origin main'");
  assert.equal(r.exitCode, 2);
});

test("denies bash -c \"git push --force\"", () => {
  const r = runHook("bash -c \"git push --force origin main\"");
  assert.equal(r.exitCode, 2);
});

test("denies assignment-prefixed git push --force after benign substitution", () => {
  const r = runHook("FOO=$(git rev-parse HEAD) git push --force origin main");
  assert.equal(r.exitCode, 2);
});

test("allows echo $(git rev-parse HEAD) (benign inner command)", () => {
  const r = runHook("echo $(git rev-parse HEAD)");
  assert.equal(r.exitCode, 0);
});

test("allows echo $(which git) push --force (git path is an echo argument)", () => {
  const r = runHook("echo $(which git) push --force origin main");
  assert.equal(r.exitCode, 0);
});

test("allows x=$(which git) push --force (substitution is an assignment value)", () => {
  const r = runHook("x=$(which git) push --force origin main");
  assert.equal(r.exitCode, 0);
});

test("allows single-quoted '$(which git)' literal", () => {
  const r = runHook("echo '$(which git) push --force origin main'");
  assert.equal(r.exitCode, 0);
});

// --- Guard hardening (merged from v3-yunkai, tests/guard_hardening.test.mjs) ---
// Yunkai's 5th test (unparseable stdin is logged to guard.log) is NOT
// ported: this branch logs parse failures to guard-alerts.jsonl instead
// (yunyi's mechanism), and that is already covered by the "malformed
// stdin is fail-open but logs the parse failure" test below.
test("denies force push hidden in $() inside echo (yunkai)", () => {
  const r = runHook("echo $(git push --force origin main)");
  assert.equal(r.exitCode, 2);
});

test("denies force push hidden in backticks inside echo (yunkai)", () => {
  const r = runHook("echo `git push -f`");
  assert.equal(r.exitCode, 2);
});

test("denies nested substitution at depth 2 (yunkai)", () => {
  const r = runHook("echo $(echo $(git push --force))");
  assert.equal(r.exitCode, 2);
});

test("allows benign substitution $(git --version) (yunkai)", () => {
  const r = runHook("echo $(git --version)");
  assert.equal(r.exitCode, 0);
});

test("malformed stdin is fail-open but logs the parse failure", () => {
  const res = spawnSync("node", [GUARD], {
    input: "this is not json",
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  assert.equal(res.status, 0);
  assert.match(res.stderr || "", /parse failed/i);
});

test("denies inline git alias", () => {
  // P1-2: previously warn-only; an alias definition hides the real
  // subcommand, so a -c alias.p=push + p --force line must deny.
  const r = runHook("git -c alias.p=push p --force origin main");
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /alias/i);
});

// --- P1-2 guard bypass closures (each was ALLOW before the fix) ---
for (const cmd of [
  "sudo -u root git push --force origin main",
  "env -i git push --force origin main",
  "timeout 5 git push --force origin main",
  "nice git push --force origin main",
  "nice -n 5 git push --force origin main",
  "git -c alias.p=push p origin main",
  "G=$(which git); $G push --force origin main",
  "$(echo $(which git)) push --force origin main",
  "x=\"git push --force origin main\"; eval $x",
  "xargs git push --force origin main",
  "find . -exec git push --force origin main \\;",
]) {
  test(`denies guard bypass: ${cmd}`, () => {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 2, `expected deny for: ${cmd}\n${r.stdout}\n${r.stderr}`);
  });
}

// And the harmless forms must stay allowed.
for (const cmd of [
  "git push origin main",
  "echo $(git rev-parse HEAD)",
  "git rev-parse HEAD",
  "x=$(which git)",
  "sudo -l",
  "command -v git",
]) {
  test(`still allows harmless: ${cmd}`, () => {
    const r = runHook(cmd);
    assert.equal(r.exitCode, 0, `expected allow for: ${cmd}\n${r.stdout}\n${r.stderr}`);
  });
}
