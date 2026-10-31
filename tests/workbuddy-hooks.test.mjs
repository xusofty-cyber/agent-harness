#!/usr/bin/env node
// ==============================================================================
// tests/workbuddy-hooks.test.mjs — black-box tests for the WorkBuddy
// hook adapters (.workbuddy/hooks/workbuddy-*.mjs).
// Feeds assumed WorkBuddy/CodeBuddy hooks-protocol stdin JSON (the
// Claude-shaped payload {tool_name, tool_input, cwd, session_id, ...};
// the protocol shape is UNVERIFIED against official docs / a live build
// in this run — see the guides) to each adapter and
// asserts on its stdout decision and exit code:
//   PreToolUse: exit 2 + hookSpecificOutput permissionDecision "deny"
//     blocks; exit 0 with no stdout lets the normal permission flow
//     continue (an explicit "allow" is never printed, so the gate alone
//     can never skip the host's permission prompt).
//   Stop: {"continue": false, "reason": ...} blocks (the assumed form;
//     "decision": "block" is assumed deprecated); exit 0 with no stdout allows.
//   SessionStart: {"hookSpecificOutput": {"hookEventName": "SessionStart",
//     "additionalContext": ...}} injects the gate resume, or no stdout.
//   PostToolUse: exit 0, no stdout, one cost-ledger line appended.
// The adapters forward to the Claude Code hooks, so each fixture is a
// temp project with .workbuddy/hooks/ adapters and .claude/hooks/ guard
// scripts (or, for one test, guard copies under .workbuddy/hooks/ only).
// Run: `node tests/workbuddy-hooks.test.mjs`
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
const WORKBUDDY_HOOKS = join(REPO_ROOT, ".workbuddy", "hooks");
const CLAUDE_HOOKS = join(REPO_ROOT, ".claude", "hooks");
const ADAPTERS = [
  "workbuddy-common.mjs",
  "workbuddy-pre-tool-use.mjs",
  "workbuddy-stop.mjs",
  "workbuddy-session-start.mjs",
  "workbuddy-post-tool-use.mjs",
];
const GUARDS = [
  "guard.mjs",
  "guard-write.mjs",
  "guard-feature-list.mjs",
  "stop-gate.mjs",
  "session-start.mjs",
  "post-tool-use.mjs",
];

function makeProject({ branch = "main", items = null, workbuddyOnly = false } = {}) {
  const dir = mkdtempSync(join(tmpdir(), "wb-hook-test-"));
  execFileSync("git", ["init", "-b", branch, "-q"], { cwd: dir });
  execFileSync("git", ["config", "user.email", "ci@example.com"], { cwd: dir });
  execFileSync("git", ["config", "user.name", "CI"], { cwd: dir });
  writeFileSync(join(dir, "README.md"), "# test\n");
  execFileSync("git", ["add", "README.md"], { cwd: dir });
  execFileSync("git", ["commit", "-qm", "init"], { cwd: dir });
  const wbDir = join(dir, ".workbuddy", "hooks");
  mkdirSync(wbDir, { recursive: true });
  for (const f of ADAPTERS) copyFileSync(join(WORKBUDDY_HOOKS, f), join(wbDir, f));
  if (workbuddyOnly) {
    for (const f of GUARDS) copyFileSync(join(CLAUDE_HOOKS, f), join(wbDir, f));
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
  const res = spawnSync("node", [join(dir, ".workbuddy", "hooks", script)], {
    input: typeof payload === "string" ? payload : JSON.stringify(payload),
    cwd: dir,
    env: { ...process.env, ...env },
    encoding: "utf-8",
  });
  let json = null;
  try {
    json = JSON.parse(res.stdout || "");
  } catch {
    // stdout is not JSON (e.g. an allow with no stdout) — asserted on directly.
  }
  return { exitCode: res.status, stdout: res.stdout || "", stderr: res.stderr || "", json };
}

function preTool(dir, tool, args) {
  return runAdapter(dir, "workbuddy-pre-tool-use.mjs", {
    tool_name: tool,
    tool_input: args,
    cwd: dir,
    session_id: "test-session",
  });
}

function stop(dir, env = {}) {
  return runAdapter(
    dir,
    "workbuddy-stop.mjs",
    { cwd: dir, session_id: "test-session" },
    env,
  );
}

// --- PreToolUse: commands ---

test("Bash 'npm test' is allowed (exit 0, no stdout decision)", () => {
  const dir = makeProject();
  const r = preTool(dir, "Bash", { command: "npm test" });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("Bash force push is denied (exit 2 + deny JSON + stderr reason)", () => {
  const dir = makeProject({ branch: "main" });
  const r = preTool(dir, "Bash", { command: "git push --force origin main" });
  assert.equal(r.exitCode, 2);
  assert.equal(r.json.hookSpecificOutput.permissionDecision, "deny");
  assert.match(r.json.hookSpecificOutput.permissionDecisionReason, /Force push/);
  assert.match(r.stderr, /Blocked/);
});

test("unknown tool is allowed (no gate hook covers it)", () => {
  const dir = makeProject();
  const r = preTool(dir, "Read", { file_path: join(dir, "README.md") });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("malformed stdin is allowed (fail-open)", () => {
  const dir = makeProject();
  const r = runAdapter(dir, "workbuddy-pre-tool-use.mjs", "{not json");
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /fail-open/);
});

// --- PreToolUse: writes ---

test("direct write to feature_list.json is denied and logged", () => {
  const dir = makeProject({ items: [] });
  const r = preTool(dir, "Write", {
    file_path: join(dir, "gate", "feature_list.json"),
  });
  assert.equal(r.exitCode, 2);
  assert.equal(r.json.hookSpecificOutput.permissionDecision, "deny");
  assert.match(r.json.hookSpecificOutput.permissionDecisionReason, /pass-gate\.py/);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /direct_write_blocked/);
});

test("Edit on an ordinary file is allowed", () => {
  const dir = makeProject();
  const r = preTool(dir, "Edit", { file_path: join(dir, "README.md") });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("write to a credential file is allowed but warned", () => {
  const dir = makeProject();
  const r = preTool(dir, "Write", { file_path: join(dir, "id_rsa") });
  assert.equal(r.exitCode, 0);
  assert.match(r.stderr, /Credential protection/);
});

test("WorkBuddy-only project (guard copies under .workbuddy/hooks/) still denies", () => {
  const dir = makeProject({ items: [], workbuddyOnly: true });
  const r = preTool(dir, "Write", {
    file_path: join(dir, "gate", "feature_list.json"),
  });
  assert.equal(r.exitCode, 2);
  assert.equal(r.json.hookSpecificOutput.permissionDecision, "deny");
});

// --- Stop ---

test("Stop with an in_progress item blocks, second stop allows", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const first = stop(dir);
  assert.equal(first.exitCode, 0);
  assert.equal(first.json.continue, false);
  assert.match(first.json.reason, /f1/);
  assert.equal(existsSync(join(dir, "gate", "workbuddy-stop-state.json")), true);
  const second = stop(dir);
  assert.equal(second.exitCode, 0);
  assert.equal(second.stdout, "");
  assert.equal(existsSync(join(dir, "gate", "workbuddy-stop-state.json")), false);
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_allowed_hook_active/);
});

test("Stop with no in_progress item allows", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Done", status: "passing" }],
  });
  const r = stop(dir);
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("Stop with no gate in use allows", () => {
  const dir = makeProject({ items: null });
  const r = stop(dir);
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("Stop human override (GATE_ALLOW_STOP + reason) allows and logs", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const r = stop(dir, {
    GATE_ALLOW_STOP: "1",
    GATE_STOP_REASON: "stopping for the day",
  });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
  const events = readFileSync(join(dir, "gate", "events.jsonl"), "utf-8");
  assert.match(events, /stop_override/);
});

test("Stop malformed stdin is allowed (fail-open)", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const r = runAdapter(dir, "workbuddy-stop.mjs", "{not json");
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

// --- SessionStart / PostToolUse ---

test("SessionStart injects the gate resume as additionalContext", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const r = runAdapter(dir, "workbuddy-session-start.mjs", {
    cwd: dir,
    session_id: "test-session",
  });
  assert.equal(r.exitCode, 0);
  assert.equal(r.json.hookSpecificOutput.hookEventName, "SessionStart");
  assert.match(r.json.hookSpecificOutput.additionalContext, /f1/);
});

test("SessionStart without a gate prints nothing", () => {
  const dir = makeProject({ items: null });
  const r = runAdapter(dir, "workbuddy-session-start.mjs", {
    cwd: dir,
    session_id: "test-session",
  });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
});

test("PostToolUse exits 0 with no stdout and appends a cost-ledger line", () => {
  const dir = makeProject({ items: [] });
  const r = runAdapter(dir, "workbuddy-post-tool-use.mjs", {
    tool_name: "Bash",
    tool_input: { command: "npm test" },
    cwd: dir,
    session_id: "test-session",
  });
  assert.equal(r.exitCode, 0);
  assert.equal(r.stdout, "");
  const ledger = readFileSync(join(dir, "gate", "cost-ledger.jsonl"), "utf-8");
  assert.match(ledger, /post-tool-use/);
  assert.match(ledger, /Bash/);
});

test("Stop blocked event writes hash-chained record and events-head.json that pass verify-chain", () => {
  const dir = makeProject({
    items: [{ id: "f1", title: "Do the thing", status: "in_progress" }],
  });
  const first = stop(dir);
  assert.equal(first.exitCode, 0);
  assert.equal(first.json.continue, false);
  assert.equal(existsSync(join(dir, "gate", "events-head.json")), true);
  const verify = spawnSync(
    "python3",
    [join(REPO_ROOT, "gate", "pass-gate.py"), "--root", dir, "events", "--verify-chain"],
    { encoding: "utf-8" },
  );
  assert.equal(verify.status, 0, verify.stdout + verify.stderr);
  assert.match(verify.stdout, /event chain OK/);
});
