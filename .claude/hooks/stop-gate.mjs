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
// Deadlock guard (merge, from v3-yunyi/v3-yunkai): Claude Code sets
// stop_hook_active when this hook already blocked the same stop once.
// Blocking again would loop forever, so a second attempt is allowed —
// but the allowance is logged to gate/events.jsonl
// (stop_allowed_hook_active) so the unfinished items stay visible.
//
// Limits: Claude Code only (other hosts have no Stop hook). If there is
// no gate/feature_list.json in the working directory the gate is not in
// use and the hook exits 0. stdin parse failure is fail-open (exit 0),
// matching guard.mjs.
// Exit code 2 blocks the stop in Claude Code.
// ==============================================================================
import { createHash } from "node:crypto";
import { appendFileSync, existsSync, readFileSync, renameSync, writeFileSync } from "node:fs";

function appendChainedEvent(cwd, event, itemId, detail) {
  const eventsPath = join(cwd, "gate", "events.jsonl");
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
        // skip; flagged by §3k, not by this hook
      }
    }
  }
  const prev = lastLine !== null ? createHash("sha256").update(lastLine, "utf8").digest("hex") : "";
  const rec = {
    seq,
    ts: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    actor: "stop-gate",
    event,
    item_id: itemId,
    detail,
    prev,
  };
  const sortedKeys = Object.keys(rec).sort();
  const canonical = "{" + sortedKeys.map((k) => `${JSON.stringify(k)}:${JSON.stringify(rec[k])}`).join(",") + "}";
  rec.hash = createHash("sha256").update(prev + canonical, "utf8").digest("hex");
  appendFileSync(eventsPath, JSON.stringify(rec) + "\n");
  const headPath = join(cwd, "gate", "events-head.json");
  const headTmp = headPath + ".tmp";
  writeFileSync(headTmp, JSON.stringify({ seq: rec.seq, hash: rec.hash }) + "\n", "utf-8");
  renameSync(headTmp, headPath);
}
import { join } from "node:path";

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data = {};
try {
  data = JSON.parse(input);
} catch {
  // Phase 2 (2-4): parse failure stays fail-open (exit 0), but it is logged
  // to stderr instead of silently allowed.
  process.stderr.write("[STOP-GATE] stdin JSON parse failed; allowing (fail-open by design)\n");
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

// Deadlock guard: this hook already blocked this stop once
// (stop_hook_active). The agent saw the guidance above and is choosing
// to stop anyway; blocking again would loop forever. Allow, and log the
// allowance so the unfinished items stay visible.
if (data.stop_hook_active === true) {
  try {
    appendChainedEvent(
      cwd,
      "stop_allowed_hook_active",
      inProgress.map((i) => i.id).join(","),
      "stop allowed on second attempt (stop_hook_active); items still in_progress"
    );
  } catch {
    // Logging must never block the stop itself.
  }
  process.stderr.write(
    `[GATE-HOOK] Stop allowed: hook already blocked this stop once (stop_hook_active); ` +
      `${inProgress.length} item(s) still in_progress (${inProgress.map((i) => i.id).join(", ")}). ` +
      "Allowance logged to gate/events.jsonl (stop_allowed_hook_active).\n"
  );
  process.exit(0);
}

const override = process.env.GATE_ALLOW_STOP === "1";
const reason = (process.env.GATE_STOP_REASON || "").trim();
if (override && reason) {
  try {
    appendChainedEvent(
      cwd,
      "stop_override",
      inProgress.map((i) => i.id).join(","),
      `human override, reason: ${reason}`
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
