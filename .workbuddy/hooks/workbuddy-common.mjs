#!/usr/bin/env node
// ==============================================================================
// workbuddy-common.mjs — shared helpers for the WorkBuddy hook adapters.
// WorkBuddy (Tencent CodeBuddy successor) hooks are ASSUMED here to
// follow a Claude Code-compatible protocol. UNVERIFIED: the official
// WorkBuddy/CodeBuddy hook documentation was NOT fetched in the run
// that built this layer (no external fetches during the night window)
// and no installed WorkBuddy build was available, so the hook format,
// the settings-file location, and the output forms below are provisional
// until a live run on an installed WorkBuddy version confirms them.
// The protocol shape this layer implements:
//   - Hooks are declared in settings.json as
//     {"hooks": {<Event>: [{"matcher": "<tool>", "hooks":
//     [{"type": "command", "command": "...", "timeout": <seconds>}]}]}}.
//     Project settings live in .codebuddy/settings.json in the CodeBuddy
//     docs; this repository deploys the WorkBuddy build's settings to
//     .workbuddy/settings.json (the directory this repository already uses
//     for the WorkBuddy rules bridge), with the legacy path documented as
//     a fallback in the guides. The settings-file location on an installed
//     WorkBuddy build was NOT verified live (no WorkBuddy binary in this
//     environment); see the guides and the PR body.
//   - A hook receives JSON on stdin: { tool_name, tool_input, cwd,
//     session_id, ... } for tool events.
//   - PreToolUse output (assumed): exit 2 blocks (stderr is fed back as
//     the reason), or exit 0 plus {"hookSpecificOutput":
//     {"hookEventName": "PreToolUse", "permissionDecision": "allow" |
//     "deny" | "ask", "permissionDecisionReason": "..."}}. Exit 0 with no
//     stdout lets the normal permission flow continue (it is NOT an
//     approval).
//   - Stop output (assumed current form; "decision": "block" is assumed
//     deprecated): {"continue": false, "reason": "..."} prevents stopping.
//   - SessionStart output (assumed): {"hookSpecificOutput":
//     {"hookEventName": "SessionStart", "additionalContext": "..."}}
//     injects context.
//   - PostToolUse output (assumed): {"hookSpecificOutput":
//     {"hookEventName": "PostToolUse", "additionalContext": "..."}} for
//     context injection; it cannot block a tool call that already ran.
// The gate logic itself is NOT reimplemented here. Unlike the Antigravity
// adapters (which must translate a different payload shape), the
// WorkBuddy payload is assumed already Claude-shaped, so these adapters
// forward the stdin JSON unchanged to the existing .claude/hooks/*.mjs
// scripts and translate only the outputs whose assumed form differs:
// SessionStart plain text -> additionalContext JSON, Stop exit 2 ->
// {"continue": false, "reason": ...}. PreToolUse deny JSON is already in
// the assumed shape and is forwarded verbatim (plus the reason on
// stderr, so the reason survives whichever channel the host reads).
// Guard script resolution: prefer <project>/.workbuddy/hooks/<name>
// (where the deploy scripts copy the Claude hook scripts for
// WorkBuddy-only projects), fall back to <project>/.claude/hooks/<name>
// (projects that also deploy Claude Code hooks, and this repository
// itself). Every error path fails open and says so on stderr, matching
// the graded policy in guard.mjs: a hook that cannot inspect must be
// visible, not silent, and must not block legitimate work.
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
import { dirname, join } from "node:path";
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

// Project root: the payload's cwd, if it exists; else the process
// working directory (hook commands run from the workspace root).
export function resolveProjectRoot(input) {
  if (typeof input.cwd === "string" && input.cwd && existsSync(input.cwd)) {
    return input.cwd;
  }
  return process.cwd();
}

export function resolveClaudeScript(projectRoot, scriptName) {
  const workbuddyPath = join(projectRoot, ".workbuddy", "hooks", scriptName);
  if (existsSync(workbuddyPath)) return workbuddyPath;
  const claudePath = join(projectRoot, ".claude", "hooks", scriptName);
  if (existsSync(claudePath)) return claudePath;
  return null;
}

// Run one Claude hook script with the (already Claude-shaped) payload.
// Returns { status, stdout, stderr } or null when the script is missing
// or the spawn itself failed (fail-open: the caller treats null as
// "allow" / "no injection").
export function runClaudeHook(projectRoot, scriptName, payload, env = {}) {
  const script = resolveClaudeScript(projectRoot, scriptName);
  if (!script) {
    process.stderr.write(
      `[WORKBUDDY-HOOK] ${scriptName} not found under .workbuddy/hooks/ or .claude/hooks/; allowing (fail-open)\n`,
    );
    return null;
  }
  try {
    const res = spawnSync("node", [script], {
      input: JSON.stringify(payload),
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
      `[WORKBUDDY-HOOK] ${scriptName} failed to run; allowing (fail-open)\n`,
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

// stop-gate.mjs reports a block on stderr ("[GATE-HOOK] Stop blocked: ...").
// Strip the tag and collapse to one reason string for the Stop JSON form.
export function extractStopReason(stderr) {
  const text = (stderr || "")
    .split("\n")
    .map((line) => line.replace(/^\[GATE-HOOK\]\s*/, "").trim())
    .filter(Boolean)
    .join(" ");
  return text || "Stop blocked by the agent-harness gate hook.";
}

export function forwardStderr(res) {
  if (res && res.stderr) process.stderr.write(res.stderr);
}

export function printJson(obj) {
  process.stdout.write(JSON.stringify(obj));
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

// Stop-block state, mirroring Claude Code's stop_hook_active deadlock
// guard. The CodeBuddy/WorkBuddy Stop documentation shows no
// stop_hook_active equivalent in its payload, so this adapter keeps its
// own: the first blocked stop for a session is recorded; a second
// blocked stop for the same session is allowed (and logged), so a
// session can never be trapped in a continue-loop by this hook. If the
// host does pass stop_hook_active, stop-gate.mjs already handles the
// second attempt itself and this state is never consulted. (The assumed
// Stop payload carries no stop_hook_active equivalent; unverified.)
export function stopStatePath(projectRoot) {
  return join(projectRoot, "gate", "workbuddy-stop-state.json");
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
    writeFileSync(stopStatePath(projectRoot), JSON.stringify(state) + "\n", "utf-8");
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
