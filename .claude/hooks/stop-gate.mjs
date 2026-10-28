#!/usr/bin/env node
// ==============================================================================
// stop-gate.mjs — Claude Code Stop hook (Phase 1, v3 1-6).
// Runs the termination check: if any feature_list item is still
// in_progress, stopping is blocked and the agent is told how to finish
// or explicitly override. Prevents a session ending mid-item with the
// work silently unfinished — the "stop and forget" failure mode.
//
// Human override channel (prevents deadlock): set both
//   GATE_ALLOW_STOP=1 GATE_STOP_REASON="<why stopping now>"
// and the hook appends a stop_override event to gate/events.jsonl and
// lets the session stop. An override without a reason is not an override.
//
// Limits: Claude Code only (other hosts have no Stop hook). If there is
// no gate/feature_list.json in the working directory the gate is not in
// use and the hook exits 0. stdin parse failure is fail-open (exit 0),
// matching guard.mjs.
// Exit code 2 blocks the stop in Claude Code.
// ==============================================================================
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data = {};
try {
  data = JSON.parse(input);
} catch {
  process.exit(0);
}

const cwd = data.cwd || process.cwd();
const listPath = join(cwd, "gate", "feature_list.json");
if (!existsSync(listPath)) {
  process.exit(0); // gate not in use here
}

let list;
try {
  list = JSON.parse(readFileSync(listPath, "utf-8"));
} catch {
  process.stderr.write(
    "[GATE-HOOK] feature_list.json is unreadable; stopping anyway (fail-open)\n"
  );
  process.exit(0);
}

const inProgress = (list.items || []).filter(
  (i) => i.status === "in_progress"
);
if (inProgress.length === 0) {
  process.exit(0);
}

const override = process.env.GATE_ALLOW_STOP === "1";
const reason = (process.env.GATE_STOP_REASON || "").trim();
if (override && reason) {
  try {
    const eventsPath = join(cwd, "gate", "events.jsonl");
    let seq = 1;
    if (existsSync(eventsPath)) {
      const lines = readFileSync(eventsPath, "utf-8")
        .split("\n")
        .filter(Boolean);
      if (lines.length > 0) {
        seq = (JSON.parse(lines[lines.length - 1]).seq || 0) + 1;
      }
    }
    appendFileSync(
      eventsPath,
      JSON.stringify({
        seq,
        ts: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
        actor: "stop-gate",
        event: "stop_override",
        item_id: inProgress.map((i) => i.id).join(","),
        detail: `human override, reason: ${reason}`,
      }) + "\n"
    );
  } catch {
    // Logging must never block the override itself.
  }
  process.stderr.write(
    `[GATE-HOOK] stop allowed by human override: ${reason}\n`
  );
  process.exit(0);
}

const ids = inProgress.map((i) => i.id).join(", ");
process.stderr.write(
  `[GATE-HOOK] Stop blocked: ${inProgress.length} item(s) still in_progress (${ids}). ` +
    "Finish them (pass-gate.py verify) or mark them blocked, " +
    "or use a logged human override: " +
    "`pass-gate.py override --id <id> --reason \"...\"`" +
    " for a single item, or " +
    "GATE_ALLOW_STOP=1 GATE_STOP_REASON=\"...\" to stop now. " +
    "The override is recorded in gate/events.jsonl.\n"
);
process.exit(2);
