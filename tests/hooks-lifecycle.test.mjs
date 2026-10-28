#!/usr/bin/env node
// ==============================================================================
// tests/hooks-lifecycle.test.mjs — black-box tests for the Phase 2 (2-3)
// lifecycle hooks: .claude/hooks/session-start.mjs (SessionStart) and
// .claude/hooks/post-tool-use.mjs (PostToolUse), plus the settings.json
// wiring for all five hook events. Run: `node tests/hooks-lifecycle.test.mjs`
// Uses only node built-ins (node:test + node:child_process).
// ==============================================================================
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SESSION_START = join(REPO_ROOT, ".claude/hooks/session-start.mjs");
const POST_TOOL_USE = join(REPO_ROOT, ".claude/hooks/post-tool-use.mjs");

function runHook(script, payload, cwd, env = {}) {
  const res = spawnSync("node", [script], {
    input: JSON.stringify(payload),
    cwd,
    encoding: "utf-8",
    env: { ...process.env, ...env },
  });
  return {
    exitCode: res.status,
    stdout: res.stdout || "",
    stderr: res.stderr || "",
  };
}

function runHookRaw(script, rawInput, cwd, env = {}) {
  const res = spawnSync("node", [script], {
    input: rawInput,
    cwd,
    encoding: "utf-8",
    env: { ...process.env, ...env },
  });
  return {
    exitCode: res.status,
    stdout: res.stdout || "",
    stderr: res.stderr || "",
  };
}

function makeGateDir(items, stateLines = null) {
  const dir = mkdtempSync(join(tmpdir(), "lifecycle-hook-test-"));
  mkdirSync(join(dir, "gate"));
  writeFileSync(
    join(dir, "gate", "feature_list.json"),
    JSON.stringify({ version: 1, project: "test", items }, null, 2)
  );
  if (stateLines !== null) {
    writeFileSync(join(dir, "SESSION_STATE.md"), stateLines.join("\n") + "\n");
  }
  return dir;
}

const inProgressItem = {
  id: "half-done-thing",
  priority: "p0",
  area: "test",
  title: "Half-done thing",
  user_visible_behavior: "It is half done.",
  status: "in_progress",
  verification: { command: "true" },
  evidence: null,
};

const blockedItem = {
  ...inProgressItem,
  id: "stuck-thing",
  title: "Stuck thing",
  status: "blocked",
  evidence: null,
};

// --- session-start: resume from gate state ---
test("session-start is silent when no gate state exists", () => {
  const dir = mkdtempSync(join(tmpdir(), "lifecycle-hook-test-"));
  const r = runHook(SESSION_START, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("session-start prints in_progress and blocked items", () => {
  const dir = makeGateDir([inProgressItem, blockedItem]);
  const r = runHook(SESSION_START, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stdout, /half-done-thing/);
  assert.match(r.stdout, /stuck-thing/);
  assert.match(r.stdout, /1 in_progress, 1 blocked/);
});

test("session-start includes SESSION_STATE.md lines", () => {
  const dir = makeGateDir([inProgressItem], [
    "# SESSION_STATE",
    "## Now: half-done-thing",
    "## Next: verify it",
  ]);
  const r = runHook(SESSION_START, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stdout, /Now: half-done-thing/);
});

test("session-start says nothing is in progress when the list is idle", () => {
  const dir = makeGateDir([]);
  const r = runHook(SESSION_START, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stdout, /nothing in progress/);
});

test("session-start fail-open on malformed stdin (logs, exit 0)", () => {
  const dir = mkdtempSync(join(tmpdir(), "lifecycle-hook-test-"));
  const r = runHookRaw(SESSION_START, "{not json", dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /parse failed/);
});

test("session-start fail-open on unreadable feature_list.json", () => {
  const dir = mkdtempSync(join(tmpdir(), "lifecycle-hook-test-"));
  mkdirSync(join(dir, "gate"));
  writeFileSync(join(dir, "gate", "feature_list.json"), "{broken");
  const r = runHook(SESSION_START, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /unreadable/);
});

// --- post-tool-use: cost-ledger recording ---
test("post-tool-use records one JSON line per call when gate exists", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(
    POST_TOOL_USE,
    { tool_name: "Bash", tool_input: { command: "ls" }, cwd: dir },
    dir
  );
  assert.equal(r.exitCode, 0);
  const ledger = join(dir, "gate", "cost-ledger.jsonl");
  assert.ok(existsSync(ledger));
  const lines = readFileSync(ledger, "utf-8").trim().split("\n");
  assert.equal(lines.length, 1);
  const rec = JSON.parse(lines[0]);
  assert.equal(rec.tool, "Bash");
  assert.equal(rec.hook, "post-tool-use");
  assert.ok(rec.ts);
});

test("post-tool-use appends, never overwrites", () => {
  const dir = makeGateDir([inProgressItem]);
  runHook(POST_TOOL_USE, { tool_name: "Bash", cwd: dir }, dir);
  runHook(POST_TOOL_USE, { tool_name: "Write", cwd: dir }, dir);
  const lines = readFileSync(join(dir, "gate", "cost-ledger.jsonl"), "utf-8")
    .trim()
    .split("\n");
  assert.equal(lines.length, 2);
  assert.equal(JSON.parse(lines[1]).tool, "Write");
});

test("post-tool-use writes nothing when no gate exists", () => {
  const dir = mkdtempSync(join(tmpdir(), "lifecycle-hook-test-"));
  const r = runHook(
    POST_TOOL_USE,
    { tool_name: "Bash", tool_input: { command: "ls" }, cwd: dir },
    dir
  );
  assert.equal(r.exitCode, 0);
  assert.equal(existsSync(join(dir, "gate")), false);
});

test("post-tool-use respects COST_LEDGER=0 opt-out", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(
    POST_TOOL_USE,
    { tool_name: "Bash", cwd: dir },
    dir,
    { COST_LEDGER: "0" }
  );
  assert.equal(r.exitCode, 0);
  assert.equal(existsSync(join(dir, "gate", "cost-ledger.jsonl")), false);
});

test("post-tool-use fail-open on malformed stdin (logs, exit 0)", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHookRaw(POST_TOOL_USE, "not json {{{", dir);
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /parse failed/);
  assert.equal(existsSync(join(dir, "gate", "cost-ledger.jsonl")), false);
});

// --- settings.json wires all five hook events ---
test("settings.json registers PreToolUse, Stop, SessionStart, PostToolUse, UserPromptSubmit", () => {
  const settings = JSON.parse(
    readFileSync(join(REPO_ROOT, ".claude/settings.json"), "utf-8")
  );
  const hooks = settings.hooks || {};
  for (const event of ["PreToolUse", "Stop", "SessionStart", "PostToolUse", "UserPromptSubmit"]) {
    assert.ok(Array.isArray(hooks[event]), `${event} missing from settings.json`);
    assert.ok(hooks[event].length > 0, `${event} has no hooks`);
  }
  const commands = JSON.stringify(hooks);
  assert.match(commands, /session-start\.mjs/);
  assert.match(commands, /post-tool-use\.mjs/);
  assert.match(commands, /stop-gate\.mjs/);
  assert.match(commands, /guard\.mjs/);
});
