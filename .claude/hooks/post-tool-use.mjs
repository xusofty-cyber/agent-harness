#!/usr/bin/env node
// ==============================================================================
// post-tool-use.mjs — Claude Code PostToolUse hook (Phase 2, 2-3).
// Appends one JSON line per tool call to gate/cost-ledger.jsonl — the raw
// material for the cost ledger's proxy metrics (tools/cost-ledger.py):
// tool-call counts by tool, the cheapest available proxy for token burn
// until per-host token adapters exist (see docs/internal/token-adapters.md).
//
// Rules:
//   - Only records when gate/ exists in the working directory (gate in use).
//     Projects without a gate get no file and no noise.
//   - Opt-out: COST_LEDGER=0 disables recording entirely.
//   - Never blocks: PostToolUse cannot block a tool call anyway, and this
//     hook exits 0 on every path, including stdin parse failure (logged to
//     stderr, matching the guard.mjs convention — Phase 2, 2-4).
//   - The ledger is append-only; one line per call, no PII beyond the tool
//     name and timestamp.
// Exit code is always 0.
// ==============================================================================
import { appendFileSync, existsSync } from "node:fs";
import { join } from "node:path";

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data = {};
try {
  data = JSON.parse(input);
} catch {
  process.stderr.write(
    "[POST-TOOL-USE] stdin JSON parse failed; call not recorded (fail-open)\n"
  );
  process.exit(0);
}

if (process.env.COST_LEDGER === "0") {
  process.exit(0);
}

const cwd = data.cwd || process.cwd();
const gateDir = join(cwd, "gate");
if (!existsSync(gateDir)) {
  process.exit(0); // gate not in use here — nothing to record into
}

const tool = data.tool_name || "unknown";
try {
  appendFileSync(
    join(gateDir, "cost-ledger.jsonl"),
    JSON.stringify({
      ts: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      hook: "post-tool-use",
      tool,
    }) + "\n"
  );
} catch {
  // Ledger write failure must never break the session — silent fail-open.
}
process.exit(0);
