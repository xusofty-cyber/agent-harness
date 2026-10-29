#!/usr/bin/env node
// ==============================================================================
// tests/antigravity-hooks.test.mjs — black-box tests for the Antigravity
// hook adapters (.agents/hooks/antigravity-*.mjs).
// Feeds Antigravity hooks.json-protocol stdin JSON to each adapter and
// asserts on its stdout decision (the official contract: PreToolUse
// decisions are REQUIRED and explicit — never "{}"; Stop "continue"
// blocks, anything else allows; PostToolUse returns {}; SessionStart
// returns injectSteps or {}).
// The adapters translate into the Claude Code hooks, so each fixture is
// a temp project with .agents/hooks/ adapters and .claude/hooks/ guard
// scripts (or, for one test, guard copies under .agents/hooks/ only).
// Run: `node tests/antigravity-hooks.test.mjs`
// Uses only node built-ins (node:test + node:child_process).
// ==============================================================================

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
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
const AGENTS_HOOKS = join(REPO_ROOT, ".agents", "hooks");
const CLAUDE_HOOKS = join(REPO_ROOT, ".claude", "hooks");
const ADAPTERS = [
  "antigravity-common.mjs",
  "antigravity-pre-tool-use.mjs",
  "antigravity-stop.mjs",
  "antigravity-session-start.mjs",
  "antigravity-post-tool-use.mjs",
];
const GUARDS = [
  "guard.mjs",
  "guard-write.mjs",
  "guard-feature-list.mjs",
  "stop-gate.mjs",
  "session-start.mjs",
  "post-tool-use.mjs",
];

function makeProject({ branch = "main", items = null, antigravityOnly = false } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "agy-hook-test-"));
  execFileSync("git", ["init", "-b", branch, "-q"], { cwd: dir });
  execFileSync("git", ["config", "user.email", "ci@example.com"], { cwd: dir });
  execFileSync("git", ["config", "user.name", "CI"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "# test\n");
  execFileSync("git", ["add", "README.md"], { cwd: dir });
  execFileSync("git", ["commit", "-qm", "init"], { cwd: dir });
  const agentsDir = join(dir, ".agents", "hooks");
  mkdirSync(agentsDir, { recursive: true });
  for (const f of ADAPTERS) copyFileSync(join(AGENTS_HOOKS, f), join(agentsDir, f));
  if (antigravityOnly) {
    for (const f of GUARDS) copyFileSync(join(CLAUDE_HOOKS, f), join(agentsDir, f));
  } else {
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

function runAdapter(dir, script, payload, env = {}) {
  const res = spawnSync("node", [join(dir, ".agents", "hooks", script)], {
    input: typeof payload === "string" ? payload : JSON.stringify(payload),
    cwd: dir,
    env: { ...process.env, ...env },
    encoding: "utf-8",
  });
  let json = null;
  try {
    json = JSON.parse(res.stdout || "");
  } catch {
    // stdout is not JSON (e.g. an adapter crash) — the test asserts on it.
  }
  return { exitCode: res.status, stdout: res.stdout || "", stderr: res.stderr || "", json };
}

function preTool(dir, tool, args) {
  return runAdapter(dir, "antigravity-pre-tool-use.mjs", {
    toolCall: { name: tool, args },
    workspacePaths: [dir],
    conversationId: "test-conversation",
  });
}

function stop(dir, conversationId = "test-conversation", env = {}) {
  return runAdapter(
    dir,
    "antigravity-stop.mjs",
    {
      executionNum: 1,
      terminationReason: "model_stop",
      fullyIdle: true,
      workspacePaths: [dir],
      conversationId,
    },
    env,
  );
}

// --- PreToolUse: commands ---

test("run_command 'npm test' is allowed", () => {
  const dir = makeProject();
  const r = preTool(dir, "run_command", { CommandLine: "npm test", Cwd: dir });
  assert.equal(r.json.decision, "allow");
});

test("run_command force push is denied", () => {
  const dir = makeProject({ branch: "main" });
  const r = preTool(dir, "run_command", {
    CommandLine: "git push --force origin main",
    Cwd: dir,
  });
  assert.equal(r.json.decision, "deny");
  assert.match(r.json.reason, /Force push/);
});

test("unknown tool is allowed (no gate hook covers it)", () => {
  const dir = makeProject();
  const r = preTool(dir, "view_file", { AbsolutePath: join(dir, "README.md") });
  assert.equal(r.json.decision, "allow");
});

test("malformed stdin is allowed (fail-open) and never prints {}", () => {
  const dir = makeProject();
  const r = runAdapter(dir, "antigravity-pre-tool-use.mjs", "{not json");
  assert.equal(r.json.decision, "allow");
});

// --- PreToolUse: writes ---

test("direct write to feature_list.json is denied and logged", () => {
  const dir = makeProject({ items: [] });
  const r = preTool(dir, "write_to_file", {
    TargetFile: join(dir, "gate", "feature_list.json"),
  });
  assert.equal(r.json.decision, "deny");
  assert.match(r.json.reason, /pass-gate\.py/);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /direct_write_blocked/);
});

test("replace_file_content on an ordinary file is allowed", () => {
  const dir = makeProject();
  const r = preTool(dir, "replace_file_content", {
    TargetFile: join(dir, "README.md"),
  });
  assert.equal(r.json.decision, "allow");
});

test("write to a credential file is allowed but warned", () => {
  const dir = makeProject();
  const r = preTool(dir, "write_to_file", {
    TargetFile: join(dir, "id_rsa"),
  });
  assert.equal(r.json.decision, "allow");
  assert.match(r.stderr, /Credential protection/);
});

test("Antigravity-only project (guard copies under .agents/hooks/) still denies", () => {
  const dir = makeProject({ items: [], antigravityOnly: true });
  const r = preTool(dir, "write_to_file", {
    TargetFile: join(dir, "gate", "feature_list.json"),
  });
  assert.equal(r.json.decision, "deny");
});

// --- Stop ---

test("Stop with an in_progress item continues, second stop allows", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const first = stop(dir);
  assert.equal(first.json.decision, "continue");
  assert.match(first.json.reason, /f1/);
  assert.equal(existsSync(join(dir, "gate", "antigravity-stop-state.json")), true);
  const second = stop(dir);
  assert.equal(second.json.decision, "allow");
  assert.equal(existsSync(join(dir, "gate", "antigravity-stop-state.json")), false);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_allowed_hook_active/);
});

test("Stop with no in_progress item allows", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Done", status: "passing" }],
  });
  const r = stop(dir);
  assert.equal(r.json.decision, "allow");
});

test("Stop with no gate in use allows", () => {
  const dir = makeProject({ items: null });
  const r = stop(dir);
  assert.equal(r.json.decision, "allow");
});

test("Stop human override (GATE_ALLOW_STOP + reason) allows and logs", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const r = stop(dir, "test-conversation", {
    GATE_ALLOW_STOP: "1",
    GATE_STOP_REASON: "stopping for the day",
  });
  assert.equal(r.json.decision, "allow");
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_override/);
});

// --- SessionStart / PostToolUse ---

test("SessionStart injects the gate resume, including in_progress ids", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const r = runAdapter(dir, "antigravity-session-start.mjs", {
    workspacePaths: [dir],
    conversationId: "test-conversation",
  });
  assert.ok(Array.isArray(r.json.injectSteps));
  assert.match(r.json.injectSteps[0].systemMessage.systemMessage, /f1/);
});

test("SessionStart without a gate prints {}", () => {
  const dir = makeProject({ items: null });
  const r = runAdapter(dir, "antigravity-session-start.mjs", {
    workspacePaths: [dir],
    conversationId: "test-conversation",
  });
  assert.deepEqual(r.json, {});
});

test("PostToolUse prints {} and appends a cost-ledger line", () => {
  const dir = makeProject({ items: [] });
  const r = runAdapter(dir, "antigravity-post-tool-use.mjs", {
    toolCall: { name: "run_command", args: { CommandLine: "npm test" } },
    workspacePaths: [dir],
    conversationId: "test-conversation",
  });
  assert.deepEqual(r.json, {});
  const ledger = readFileSync(join(dir, "gate", "cost-ledger.jsonl"), "utf-8");
  assert.match(ledger, /run_command/);
});
