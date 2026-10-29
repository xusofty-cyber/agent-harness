#!/usr/bin/env node
// ==============================================================================
// tests/hooks-gate.test.mjs — black-box tests for the Phase 1 gate hooks:
// .claude/hooks/guard-feature-list.mjs (PreToolUse) and
// .claude/hooks/stop-gate.mjs (Stop). Run: `node tests/hooks-gate.test.mjs`
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
const GUARD_FL = join(REPO_ROOT, ".claude/hooks/guard-feature-list.mjs");
const STOP_GATE = join(REPO_ROOT, ".claude/hooks/stop-gate.mjs");

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

function makeGateDir(items) {
  const dir = mkdtempSync(join(tmpdir(), "gate-hook-test-"));
  mkdirSync(join(dir, "gate"));
  writeFileSync(
    join(dir, "gate", "feature_list.json"),
    JSON.stringify({ version: 1, project: "test", items }, null, 2)
  );
  return dir;
}

const passingItem = {
  id: "done-thing",
  priority: "p0",
  area: "test",
  title: "Done thing",
  user_visible_behavior: "It is done.",
  status: "passing",
  verification: { command: "true" },
  evidence: {
    command: "true",
    exit_code: 0,
    ran_at: "2026-10-28T00:00:00Z",
    output_tail: "",
  },
};

const inProgressItem = {
  ...passingItem,
  id: "half-done-thing",
  title: "Half-done thing",
  status: "in_progress",
  evidence: null,
};

// --- guard-feature-list: direct writes to feature_list.json are denied ---
test("denies Write to gate/feature_list.json (exit 2, deny decision)", () => {
  const dir = makeGateDir([passingItem]);
  const r = runHook(
    GUARD_FL,
    { tool_name: "Write", tool_input: { file_path: "gate/feature_list.json" }, cwd: dir },
    dir
  );
  assert.equal(r.exitCode, 2);
  assert.match(r.stdout, /permissionDecision":\s*"deny"/);
  assert.match(r.stderr, /pass-gate\.py/);
  // The blocked attempt leaves a trace in the event log.
  assert.match(readFileSync(join(dir, "gate", "events.jsonl"), "utf-8"), /direct_write_blocked/);
});

test("denies Edit to a nested feature_list.json path", () => {
  const dir = makeGateDir([passingItem]);
  const r = runHook(
    GUARD_FL,
    { tool_name: "Edit", tool_input: { file_path: "/x/y/gate/feature_list.json" }, cwd: dir },
    dir
  );
  assert.equal(r.exitCode, 2);
});

test("allows Write to any other file", () => {
  const dir = makeGateDir([passingItem]);
  const r = runHook(
    GUARD_FL,
    { tool_name: "Write", tool_input: { file_path: "README.md" }, cwd: dir },
    dir
  );
  assert.equal(r.exitCode, 0);
  assert.equal(existsSync(join(dir, "gate", "events.jsonl")), false);
});

test("fail-open on malformed stdin (matches guard.mjs convention)", () => {
  const res = spawnSync("node", [GUARD_FL], {
    input: "{not json",
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  assert.equal(res.status, 0);
});

// --- stop-gate: blocks stopping with in_progress items, allows otherwise ---
test("Stop hook allows stopping when no gate state exists", () => {
  const dir = mkdtempSync(join(tmpdir(), "gate-hook-test-"));
  const r = runHook(STOP_GATE, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
});

test("Stop hook blocks stopping with an in_progress item", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(STOP_GATE, { cwd: dir }, dir);
  assert.equal(r.exitCode, 2);
  assert.match(r.stderr, /half-done-thing/);
  assert.match(r.stderr, /GATE_ALLOW_STOP/);
});

test("Stop hook allows stopping when everything is passing", () => {
  const dir = makeGateDir([passingItem]);
  const r = runHook(STOP_GATE, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
});

test("Stop hook override channel works and is logged", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(
    STOP_GATE,
    { cwd: dir },
    dir,
    { GATE_ALLOW_STOP: "1", GATE_STOP_REASON: "user asked to stop now" }
  );
  assert.equal(r.exitCode, 0);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_override/);
  assert.match(events, /user asked to stop now/);
});

test("Stop hook override without a reason does not override", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(
    STOP_GATE,
    { cwd: dir },
    dir,
    { GATE_ALLOW_STOP: "1", GATE_STOP_REASON: "   " }
  );
  assert.equal(r.exitCode, 2);
});

test("Stop hook allows stopping on second attempt (stop_hook_active) and logs it", () => {
  const dir = makeGateDir([inProgressItem]);
  const r = runHook(STOP_GATE, { cwd: dir, stop_hook_active: true }, dir);
  assert.equal(r.exitCode, 0);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_allowed_hook_active/);
  assert.match(events, /half-done-thing/);
});

test("Stop hook fail-open on unreadable feature list", () => {
  const dir = mkdtempSync(join(tmpdir(), "gate-hook-test-"));
  mkdirSync(join(dir, "gate"));
  writeFileSync(join(dir, "gate", "feature_list.json"), "{broken json");
  const r = runHook(STOP_GATE, { cwd: dir }, dir);
  assert.equal(r.exitCode, 0);
});
