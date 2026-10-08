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
import { mkdtempSync, writeFileSync } from "node:fs";
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

test("ignores non-Bash tools", () => {
  const payload = JSON.stringify({ tool_name: "Write", tool_input: { command: "git add ." } });
  const res = spawnSync("node", [GUARD], { input: payload, encoding: "utf-8" });
  assert.equal(res.status, 0);
  assert.equal((res.stderr || "").trim(), "");
});
