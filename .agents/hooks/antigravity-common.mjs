#!/usr/bin/env node
// ==============================================================================
// antigravity-common.mjs — shared helpers for the Antigravity hook adapters.
// Antigravity hooks.json protocol (https://antigravity.google/docs/hooks/):
//   - Hooks receive JSON on stdin and return JSON on stdout (camelCase fields).
//   - PreToolUse input: { toolCall: { name, args }, workspacePaths, ... }.
//   - PreToolUse output: { decision: "allow" | "deny" | "ask" | "force_ask" |
//     "auto_approve" | "deny_unless_prior_grant", reason? }.
//     The decision field is REQUIRED for PreToolUse. An adapter must never
//     print "{}" for PreToolUse: that is a no-decision result and its
//     treatment is disputed across Antigravity versions (one independent
//     test on agy 1.4.5 treated it as a deny). Always print an explicit
//     decision: "allow" when there is nothing to block, "deny" to block.
//   - Stop output: { decision: "continue" } prevents the stop; any other
//     value allows it. This file's adapters use "allow" for allow-stop.
//   - PostToolUse output: {} (the official contract).
//   - SessionStart / PreInvocation output: { injectSteps: [...] } (optional).
//   - Hooks fail open in Antigravity itself (missing binary, timeout, or
//     invalid JSON is logged and the session continues), so these adapters
//     also fail open on every error path and say so on stderr. A hook that
//     is not actually inspecting anything must be visible, not silent.
// The gate logic itself is NOT reimplemented here. Each adapter translates
// the Antigravity payload into the Claude Code payload the existing
// .claude/hooks/*.mjs scripts already understand, runs that script as a
// subprocess, and translates its decision back. That keeps one source of
// truth for the gate rules (guard.mjs, guard-write.mjs,
// guard-feature-list.mjs, stop-gate.mjs, session-start.mjs,
// post-tool-use.mjs) instead of a second, drifting copy.
// Hook command cwd (observed, agy CLI 1.4.10 --print): hook commands in
// .agents/hooks.json run with cwd = <project>/.agents (the directory
// containing hooks.json), NOT the workspace root. That is why every
// command in .agents/hooks.json is written as `node hooks/<adapter>.mjs`
// and must NOT be re-prefixed with `.agents/hooks/` (that doubles the
// path to .agents/.agents/hooks/... and makes agy reject the tool call
// instead of failing open). Antigravity IDE cwd is NOT verified by a
// live run; if a future IDE run shows a workspace-root cwd, this file
// (one workspace hooks.json for CLI and IDE alike) must be revisited
// rather than silently re-prefixed for one host at the other's expense.
// Guard script resolution: prefer <project>/.agents/hooks/<name> (where the
// deploy scripts copy the Claude hook scripts for Antigravity-only
// projects), fall back to <project>/.claude/hooks/<name> (projects that
// also deploy Claude Code hooks, and this repository itself).
// ==============================================================================

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  appendFileSync,
  existsSync,
  readFileSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HOOKS_DIR = dirname(fileURLToPath(import.meta.url));

export function readStdin() {
  return new Promise((resolve) => {
    let input = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => {
      input += chunk;
    });
    process.stdin.on("end", () => resolve(input));
  });
}

// Project root: the first mounted workspace, if it exists; else the
// process working directory, with one correction for the observed hook
// cwd: when the hook process runs with cwd = <project>/.agents (agy CLI
// 1.4.10), the project root is the parent of that directory, not the
// .agents directory itself. A workspace-root cwd is returned unchanged,
// so this fallback is correct for either cwd.
export function resolveProjectRoot(input) {
  const paths = input.workspacePaths || [];
  for (const p of paths) {
    if (typeof p === "string" && p && existsSync(p)) return p;
  }
  const cwd = process.cwd();
  if (basename(cwd) === ".agents") return dirname(cwd);
  return cwd;
}

export function resolveClaudeScript(projectRoot, scriptName) {
  const agentsPath = join(projectRoot, ".agents", "hooks", scriptName);
  if (existsSync(agentsPath)) return agentsPath;
  const claudePath = join(projectRoot, ".claude", "hooks", scriptName);
  if (existsSync(claudePath)) return claudePath;
  return null;
}

// Run one Claude hook script with a Claude-shaped payload. Returns
// { status, stdout, stderr } or null when the script is missing or the
// spawn itself failed (fail-open: the caller treats null as "allow").
export function runClaudeHook(projectRoot, scriptName, claudePayload, env = {}) {
  const script = resolveClaudeScript(projectRoot, scriptName);
  if (!script) {
    process.stderr.write(
      `[ANTIGRAVITY-HOOK] ${scriptName} not found under .agents/hooks/ or .claude/hooks/; allowing (fail-open)\n`,
    );
    return null;
  }
  try {
    const res = spawnSync("node", [script], {
      input: JSON.stringify(claudePayload),
      cwd: projectRoot,
      env: { ...process.env, ...env },
      encoding: "utf-8",
      timeout: 25000,
    });
    return {
      status: res.status,
      stdout: res.stdout || "",
      stderr: res.stderr || "",
    };
  } catch {
    process.stderr.write(
      `[ANTIGRAVITY-HOOK] ${scriptName} failed to run; allowing (fail-open)\n`,
    );
    return null;
  }
}

// Extract the human-readable deny reason from a Claude hook's stdout
// (hookSpecificOutput.permissionDecisionReason), if present.
export function extractDenyReason(stdout) {
  try {
    const parsed = JSON.parse(stdout);
    const reason =
      parsed.hookSpecificOutput &&
      parsed.hookSpecificOutput.permissionDecisionReason;
    if (typeof reason === "string" && reason) return reason;
  } catch {
    // Not JSON — fall through to the default reason.
  }
  return "Blocked by the agent-harness gate hook.";
}

export function forwardStderr(res) {
  if (res && res.stderr) process.stderr.write(res.stderr);
}

export function printJson(obj) {
  process.stdout.write(JSON.stringify(obj));
}

export function printAllow() {
  printJson({ decision: "allow" });
}

export function printDeny(reason) {
  printJson({ decision: "deny", reason });
}

// Best-effort append to gate/events.jsonl, keeping the sequence monotonic
// (max integer seq across the whole log + 1, as in stop-gate.mjs).
// Never throws: logging must never change a hook decision.
export function appendGateEvent(projectRoot, actor, event, itemId, detail) {
  try {
    const eventsPath = join(projectRoot, "gate", "events.jsonl");
    let seq = 1;
    let lastLine = null;
    if (existsSync(eventsPath)) {
      const lines = readFileSync(eventsPath, "utf-8")
        .split("\n")
        .map((l) => l.replace(/\r$/, ""))
        .filter((l) => l.trim().length > 0);
      for (const line of lines) {
        lastLine = line;
        try {
          const s = JSON.parse(line).seq;
          if (Number.isInteger(s) && s >= seq) seq = s + 1;
        } catch {
          // Skip unparseable lines; repo_checks §3k flags them separately.
        }
      }
    }
    const prev =
      lastLine !== null
        ? createHash("sha256").update(lastLine, "utf8").digest("hex")
        : "";
    const rec = {
      seq,
      ts: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      actor,
      event,
      item_id: itemId,
      detail,
      prev,
    };
    const sortedKeys = Object.keys(rec).sort();
    const canonical =
      "{" +
      sortedKeys
        .map((k) => `${JSON.stringify(k)}:${JSON.stringify(rec[k])}`)
        .join(",") +
      "}";
    rec.hash = createHash("sha256")
      .update(prev + canonical, "utf8")
      .digest("hex");
    appendFileSync(eventsPath, JSON.stringify(rec) + "\n");
    const headPath = join(projectRoot, "gate", "events-head.json");
    const headTmp = `${headPath}.${process.pid}.tmp`;
    writeFileSync(
      headTmp,
      JSON.stringify({ seq: rec.seq, hash: rec.hash }) + "\n",
      "utf-8",
    );
    renameSync(headTmp, headPath);
  } catch {
    // Logging failure must not change the decision.
  }
}

// Stop-block state, mirroring Claude Code's stop_hook_active deadlock guard.
// Antigravity's Stop payload carries no such flag, so the adapter keeps its
// own: the first blocked stop for a conversation is recorded; a second
// blocked stop for the same conversation is allowed (and logged), so a
// session can never be trapped in a continue-loop by this hook.
export function stopStatePath(projectRoot) {
  return join(projectRoot, "gate", "antigravity-stop-state.json");
}

export function readStopState(projectRoot) {
  try {
    const raw = readFileSync(stopStatePath(projectRoot), "utf-8");
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // No state, or unreadable — treat as no prior block.
  }
  return null;
}

export function writeStopState(projectRoot, state) {
  try {
    writeFileSync(
      stopStatePath(projectRoot),
      JSON.stringify(state) + "\n",
      "utf-8",
    );
  } catch {
    // State write failure must not change the decision.
  }
}

export function clearStopState(projectRoot) {
  try {
    unlinkSync(stopStatePath(projectRoot));
  } catch {
    // Already absent — fine.
  }
}

export { HOOKS_DIR };
