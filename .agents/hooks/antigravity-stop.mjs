#!/usr/bin/env node
// ==============================================================================
// antigravity-stop.mjs — Antigravity Stop gate adapter.
// Runs the existing stop-gate.mjs (which reads gate/feature_list.json in
// the project root) and translates its decision:
//   Claude exit 2 (blocked)  -> {"decision":"continue", reason}
//   Claude exit 0 (allowed)  -> {"decision":"allow"}
// Deadlock guard: Antigravity's Stop payload carries no equivalent of
// Claude Code's stop_hook_active flag, so this adapter keeps its own
// state in gate/antigravity-stop-state.json, keyed by conversationId.
// A second blocked stop for the same conversation is allowed and logged
// (event: stop_allowed_hook_active) instead of looping "continue" forever.
// The human override channel is unchanged: GATE_ALLOW_STOP=1 together
// with GATE_STOP_REASON="..." lets stop-gate.mjs allow the stop and log
// a stop_override event. Fail-open on every error path.
// ==============================================================================

import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  appendGateEvent,
  clearStopState,
  printJson,
  readStdin,
  readStopState,
  resolveProjectRoot,
  runClaudeHook,
  writeStopState,
} from "./antigravity-common.mjs";

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[ANTIGRAVITY-HOOK] Stop stdin JSON parse failed; allowing (fail-open by design)\n",
  );
  printJson({ decision: "allow" });
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const conversationId = input.conversationId || "";

// No gate in use here — nothing to block.
if (!existsSync(join(projectRoot, "gate", "feature_list.json"))) {
  printJson({ decision: "allow" });
  process.exit(0);
}

// Second blocked stop for the same conversation: allow, and log it so
// the unfinished items stay visible (mirrors stop-gate's
// stop_allowed_hook_active handling).
const prior = readStopState(projectRoot);
if (prior && prior.blocked && prior.conversationId === conversationId) {
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
    // IDs are best effort; the allowance itself is what matters.
  }
  appendGateEvent(
    projectRoot,
    "antigravity-stop",
    "stop_allowed_hook_active",
    ids || null,
    "stop allowed on second attempt (antigravity-stop-state); items still in_progress",
  );
  process.stderr.write(
    "[ANTIGRAVITY-HOOK] Stop allowed: hook already blocked this stop once; allowance logged to gate/events.jsonl (stop_allowed_hook_active).\n",
  );
  printJson({ decision: "allow" });
  process.exit(0);
}

const res = runClaudeHook(projectRoot, "stop-gate.mjs", {
  cwd: projectRoot,
});
if (res && res.stderr) process.stderr.write(res.stderr);

if (res && res.status === 2) {
  // Blocked. Record it so the next attempt for this conversation is
  // allowed instead of looping.
  writeStopState(projectRoot, {
    conversationId,
    blocked: true,
    ts: new Date().toISOString(),
  });
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
    // Reason without IDs is still actionable.
  }
  printJson({
    decision: "continue",
    reason:
      `Gate items still in_progress${ids ? ` (${ids})` : ""}. ` +
      "Finish them (pass-gate.py verify) or mark them blocked, " +
      "or use a logged human override: " +
      "`pass-gate.py override --id <id> --reason \"...\"` for a single item, " +
      "or GATE_ALLOW_STOP=1 GATE_STOP_REASON=\"...\" to stop now.",
  });
  process.exit(0);
}

// Allowed (including fail-open when the hook script is missing):
// clear any stale block state for this conversation.
clearStopState(projectRoot);
printJson({ decision: "allow" });
