#!/usr/bin/env node
// ==============================================================================
// tests/dsh-gate.test.mjs — protocol-level tests for the dsh gate plugin
// (.dsh/agent-harness-gate.mjs).
//
// dsh is NOT installed in this environment, so there is no live dsh
// runtime to test against. These tests therefore do what the
// Antigravity adapter tests do: drive the plugin through a mock
// Cordis context (ctx.on / ctx.tools.guard capturing listeners) and
// assert on the decisions it returns, with real Claude hook scripts
// copied into a temp project. They prove the payload translation and
// the decision translation; they do NOT prove dsh accepts the plugin,
// fires these events with these payload shapes, or steers a turn on
// agent/turn-stopping. Those three points are the live-run gap stated
// in the plugin header, the guides, and the PR body.
// Run: `node tests/dsh-gate.test.mjs`
// Uses only node built-ins (node:test + node:child_process).
// ==============================================================================

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PLUGIN = join(REPO_ROOT, ".dsh", "agent-harness-gate.mjs");
const CLAUDE_HOOKS = join(REPO_ROOT, ".claude", "hooks");
const GUARDS = [
  "guard.mjs",
  "guard-write.mjs",
  "guard-feature-list.mjs",
  "stop-gate.mjs",
  "session-start.mjs",
  "post-tool-use.mjs",
];

const plugin = await import(PLUGIN);

function makeProject({ items = null, withHooks = true } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "dsh-gate-test-"));
  execFileSync("git", ["init", "-b", "main", "-q"], { cwd: dir });
  execFileSync("git", ["config", "user.email", "ci@example.com"], { cwd: dir });
  execFileSync("git", ["config", "user.name", "CI"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "# test\n");
  execFileSync("git", ["add", "README.md"], { cwd: dir });
  execFileSync("git", ["commit", "-qm", "init"], { cwd: dir });
  if (withHooks) {
    const claudeDir = join(dir, ".claude", "hooks");
    mkdirSync(claudeDir, { recursive: true });
    for (const f of GUARDS) copyFileSync(join(CLAUDE_HOOKS, f), join(claudeDir, f));
  }
  if (items !== null) {
    const gateDir = join(dir, "gate");
    mkdirSync(gateDir, { recursive: true });
    writeFileSync(
      join(gateDir, "feature_list.json"),
      JSON.stringify({ items }, null, 2),
    );
    writeFileSync(join(gateDir, "events.jsonl"), "");
  }
  return dir;
}

function makeCtx() {
  const listeners = {};
  const ctx = {
    listeners,
    on(event, fn) {
      listeners[event] = fn;
    },
    tools: {
      guardFn: null,
      guard(fn) {
        this.guardFn = fn;
      },
    },
  };
  return ctx;
}

function applyTo(dir) {
  const ctx = makeCtx();
  plugin.apply(ctx, { projectRoot: dir });
  return ctx;
}

async function preExecute(ctx, exec) {
  const next = async () => ({ kind: "allow", viaNext: true });
  return ctx.listeners["tools/pre-execute"](exec, next);
}

// --- Translation unit tests (no subprocess) ---

test("translate: bash command from input.command and CommandLine", () => {
  assert.equal(
    plugin.translateExecution({ toolName: "bash", input: { command: "git status" } }).command,
    "git status",
  );
  assert.equal(
    plugin.translateExecution({ toolName: "bash", args: { CommandLine: "git status" } }).command,
    "git status",
  );
});

test("translate: mcp-qualified tool names are stripped", () => {
  assert.equal(
    plugin.translateExecution({ toolName: "mcp__fs__read", input: {} }).toolName,
    "read",
  );
});

test("translate: str_replace_editor view is not a write", () => {
  const t = plugin.translateExecution({
    toolName: "str_replace_editor",
    input: { command: "view", path: "/tmp/x.txt" },
  });
  assert.equal(t.filePath, "");
});

test("translate: malformed executions fail open to empty fields", () => {
  assert.deepEqual(plugin.translateExecution(null), {
    toolName: "",
    command: "",
    filePath: "",
  });
  assert.deepEqual(plugin.translateExecution("not-an-object"), {
    toolName: "",
    command: "",
    filePath: "",
  });
});

// --- PreToolUse gate ---

test("pre-execute: force push is denied", async () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "bash",
    input: { command: "git push --force origin main" },
  });
  assert.equal(res.kind, "deny");
  assert.match(res.reason, /Force push/);
});

test("pre-execute: benign bash calls next()", async () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "bash",
    input: { command: "git status" },
  });
  assert.equal(res.kind, "allow");
  assert.equal(res.viaNext, true);
});

test("pre-execute: direct write to feature_list.json is denied", async () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "write",
    input: { file_path: "gate/feature_list.json" },
  });
  assert.equal(res.kind, "deny");
  assert.match(res.reason, /feature_list\.json/);
});

test("pre-execute: ordinary write is allowed", async () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "write",
    input: { file_path: "src/app.py" },
  });
  assert.equal(res.kind, "allow");
});

test("pre-execute: uncovered tools are allowed via next()", async () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "read",
    input: { path: "README.md" },
  });
  assert.equal(res.kind, "allow");
  assert.equal(res.viaNext, true);
});

test("pre-execute: missing Claude scripts fail open", async () => {
  const dir = makeProject({ withHooks: false });
  const ctx = applyTo(dir);
  const res = await preExecute(ctx, {
    toolName: "bash",
    input: { command: "git push --force origin main" },
  });
  assert.equal(res.kind, "allow");
  assert.equal(res.viaNext, true);
});

// --- Monotonic guard ---

test("tools.guard: force push returns a reason, benign returns undefined", () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  assert.equal(typeof ctx.tools.guardFn, "function");
  assert.match(
    ctx.tools.guardFn({ toolName: "bash", input: { command: "git push --force" } }),
    /Force push/,
  );
  assert.equal(
    ctx.tools.guardFn({ toolName: "bash", input: { command: "git status" } }),
    undefined,
  );
});

// --- Cost ledger (tools/result observation) ---

test("tools/result: appends a ledger line when gate/ exists", () => {
  const dir = makeProject({ items: [] });
  const ctx = applyTo(dir);
  ctx.listeners["tools/result"]({ toolName: "bash" });
  const ledger = readFileSync(join(dir, "gate", "cost-ledger.jsonl"), "utf-8");
  const line = JSON.parse(ledger.trim().split("\n").pop());
  assert.equal(line.tool, "bash");
  assert.equal(line.hook, "post-tool-use");
});

test("tools/result: records nothing when gate/ is absent", () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  ctx.listeners["tools/result"]({ toolName: "bash" });
  assert.equal(existsSync(join(dir, "gate", "cost-ledger.jsonl")), false);
});

// --- Session resume (agent/created) ---

test("agent/created: injects the gate resume when a gate is in use", () => {
  const dir = makeProject({
    items: [{ id: "t1", status: "in_progress" }],
  });
  const ctx = applyTo(dir);
  const injected = [];
  ctx.listeners["agent/created"]({
    id: "agent-1",
    inject: (text) => injected.push(text),
  });
  assert.equal(injected.length, 1);
  assert.match(injected[0], /t1/);
});

test("agent/created: injects nothing when no gate is in use", () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  const injected = [];
  ctx.listeners["agent/created"]({
    id: "agent-1",
    inject: (text) => injected.push(text),
  });
  assert.equal(injected.length, 0);
});

// --- Stop gate (agent/turn-stopping, provisional steering) ---

test("turn-stopping: blocked stop steers once, then allows", () => {
  const dir = makeProject({
    items: [{ id: "t1", status: "in_progress" }],
  });
  const ctx = applyTo(dir);
  const steered = [];
  const agent = { id: "agent-1", steer: (msg) => steered.push(msg) };
  ctx.listeners["agent/turn-stopping"](agent);
  assert.equal(steered.length, 1);
  assert.match(steered[0], /t1/);
  assert.equal(existsSync(join(dir, "gate", "dsh-stop-state.json")), true);
  ctx.listeners["agent/turn-stopping"](agent);
  assert.equal(steered.length, 1);
  assert.equal(existsSync(join(dir, "gate", "dsh-stop-state.json")), false);
});

test("turn-stopping: allowed stop does not steer", () => {
  const dir = makeProject({
    items: [{ id: "t1", status: "passing" }],
  });
  const ctx = applyTo(dir);
  const steered = [];
  ctx.listeners["agent/turn-stopping"]({
    id: "agent-1",
    steer: (msg) => steered.push(msg),
  });
  assert.equal(steered.length, 0);
});

test("turn-stopping: blocked stop without a steering surface does not throw", () => {
  const dir = makeProject({
    items: [{ id: "t1", status: "in_progress" }],
  });
  const ctx = applyTo(dir);
  assert.doesNotThrow(() => ctx.listeners["agent/turn-stopping"]({ id: "agent-1" }));
});

// --- Registration surface ---

test("apply: registers exactly the documented listeners", () => {
  const dir = makeProject();
  const ctx = applyTo(dir);
  assert.deepEqual(Object.keys(ctx.listeners).sort(), [
    "agent/created",
    "agent/turn-stopping",
    "tools/pre-execute",
    "tools/result",
  ]);
  assert.equal(plugin.name, "agent-harness-gate");
});
