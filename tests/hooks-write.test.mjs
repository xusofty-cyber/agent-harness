#!/usr/bin/env node
// ==============================================================================
// tests/hooks-write.test.mjs — black-box tests for .claude/hooks/guard-write.mjs
// Feeds Claude Code PreToolUse stdin JSON (Write/Edit tools) and asserts on
// exit code / stderr warnings. Run: `node tests/hooks-write.test.mjs`
// Uses only node built-ins (node:test + node:child_process).
// ==============================================================================

import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const GUARD_WRITE = join(REPO_ROOT, ".claude/hooks/guard-write.mjs");

function runHook(toolName, filePath) {
  const payload = JSON.stringify({
    tool_name: toolName,
    tool_input: { file_path: filePath },
  });
  const res = spawnSync("node", [GUARD_WRITE], {
    input: payload,
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  return {
    exitCode: res.status,
    stdout: res.stdout || "",
    stderr: res.stderr || "",
  };
}

// --- High-risk build/config files ---
test("warns on package.json", () => {
  const r = runHook("Write", "/project/package.json");
  assert.equal(r.exitCode, 0); // warnings are non-blocking
  assert.match(r.stderr, /high-risk files/i);
});

test("warns on CMakeLists.txt (case-insensitive)", () => {
  const r = runHook("Edit", "/project/CMakeLists.txt");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /high-risk files/i);
});

test("warns on Cargo.toml", () => {
  const r = runHook("Write", "/project/Cargo.toml");
  assert.match(r.stderr, /high-risk files/i);
});

test("warns on LICENSE", () => {
  const r = runHook("Edit", "/project/LICENSE");
  assert.match(r.stderr, /high-risk files/i);
});

// --- Credential patterns ---
test("warns on .pem file", () => {
  const r = runHook("Write", "/project/certs/server.pem");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /Credential protection/i);
});

test("warns on id_rsa", () => {
  const r = runHook("Write", "/home/user/.ssh/id_rsa");
  assert.match(r.stderr, /Credential protection/i);
});

test("warns on credentials in path", () => {
  const r = runHook("Edit", "/project/config/credentials.json");
  assert.match(r.stderr, /Credential protection/i);
});

// --- Normal files: no warnings ---
test("no warning on normal source file", () => {
  const r = runHook("Write", "/project/src/main.py");
  assert.equal(r.exitCode, 0);
  assert.equal(r.stderr, "");
});

test("no warning on markdown docs", () => {
  const r = runHook("Edit", "/project/README.md");
  assert.equal(r.exitCode, 0);
  assert.equal(r.stderr, "");
});

// --- Fail-open behavior ---
test("allows on malformed stdin (fail-open)", () => {
  const res = spawnSync("node", [GUARD_WRITE], {
    input: "not json {{{",
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  assert.equal(res.status, 0);
});

// --- Graded parse failure (merged from v3-yunyi, Phase 2.5): log + alert ---
test("logs and alerts on malformed stdin (graded policy)", () => {
  const dir = mkdtempSync(join(tmpdir(), "hook-write-parse-"));
  const res = spawnSync("node", [GUARD_WRITE], {
    input: "not json {{{",
    cwd: dir,
    encoding: "utf-8",
  });
  assert.equal(res.status, 0);
  assert.match(res.stderr, /guard-alerts\.jsonl/);
  const logPath = join(dir, ".claude", "hooks", "guard-alerts.jsonl");
  assert.equal(existsSync(logPath), true);
  const line = readFileSync(logPath, "utf-8");
  assert.match(line, /stdin_parse_failed/);
  assert.match(line, /guard-write\.mjs/);
  assert.doesNotMatch(line, /not json/); // raw stdin must never be logged
});

test("handles Edit tool with path field", () => {
  const payload = JSON.stringify({
    tool_name: "Edit",
    tool_input: { path: "/project/pom.xml" },
  });
  const res = spawnSync("node", [GUARD_WRITE], {
    input: payload,
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  assert.equal(res.status, 0);
  assert.match(res.stderr || "", /high-risk files/i);
});
