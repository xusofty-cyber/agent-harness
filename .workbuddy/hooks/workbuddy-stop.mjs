#!/usr/bin/env node
// ==============================================================================
// workbuddy-stop.mjs — WorkBuddy Stop gate adapter.
// Runs the existing stop-gate.mjs (which reads gate/feature_list.json in
// the project root) and translates its decision into the assumed
// WorkBuddy/CodeBuddy Stop form ("decision": "block" is assumed deprecated):
//   Claude exit 2 (blocked) -> {"continue": false, "reason": "..."}
//   Claude exit 0 (allowed) -> no stdout, exit 0 (the stop proceeds)
// Deadlock guard: the assumed Stop payload carries no equivalent of
// Claude Code's stop_hook_active flag, so this adapter keeps its own
// state in gate/workbuddy-stop-state.json, keyed by session_id. A second
// blocked stop for the same session is allowed and logged (event:
// stop_allowed_hook_active) instead of looping "continue": false
// forever. If the host does pass stop_hook_active, stop-gate.mjs handles
// the second attempt itself and this state is never consulted.
// The human override channel is unchanged: GATE_ALLOW_STOP=1 together
// with GATE_STOP_REASON="..." lets stop-gate.mjs allow the stop and log
// a stop_override event. Fail-open on every error path.
// ==============================================================================

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  appendGateEvent,
  clearStopState,
  extractStopReason,
  forwardStderr,
  printJson,
  readStdin,
  readStopState,
  resolveProjectRoot,
  runClaudeHook,
  writeStopState,
} from "./workbuddy-common.mjs";

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[WORKBUDDY-HOOK] Stop stdin JSON parse failed; allowing (fail-open by design)\n",
  );
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const sessionId = input.session_id || "";

// No gate in use here — nothing to block.
if (!existsSync(join(projectRoot, "gate", "feature_list.json"))) {
  process.exit(0);
}

const res = runClaudeHook(projectRoot, "stop-gate.mjs", input);
if (!res) process.exit(0);
forwardStderr(res);
if (res.status !== 2) process.exit(0);

// Blocked by stop-gate.mjs. If this session was already blocked once
// and the host did not set stop_hook_active, allow this second attempt
// rather than trapping the session in a continue-loop.
if (input.stop_hook_active !== true) {
  const prior = readStopState(projectRoot);
  if (prior && prior.blocked && prior.sessionId === sessionId) {
    clearStopState(projectRoot);
    let ids = "";
    try {
      const list = JSON.parse(
        readFileSync(join(projectRoot, "gate", "feature_list.json"), "utf-8"),
      );
      ids = (list.items || [])
        .filter((i) => i.status === "in_progress")
        .map((i) => i.id)
        .join(",");
    } catch {
      // Item ids are a log nicety, not the decision.
    }
    appendGateEvent(
      projectRoot,
      "workbuddy-stop",
      "stop_allowed_hook_active",
      ids,
      "stop allowed on second attempt (workbuddy-stop-state); items still in_progress",
    );
    process.stderr.write(
      "[WORKBUDDY-HOOK] Stop allowed: hook already blocked this stop once; allowance logged to gate/events.jsonl (stop_allowed_hook_active).\n",
    );
    process.exit(0);
  }
  writeStopState(projectRoot, { blocked: true, sessionId });
}

printJson({ continue: false, reason: extractStopReason(res.stderr) });
process.exit(0);
