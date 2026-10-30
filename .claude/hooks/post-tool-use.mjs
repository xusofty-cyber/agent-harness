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
//   - Skill telemetry (D68): when the call is a Skill invocation, one
//     extra line ({ts, skill, session?} — the skill NAME only, never
//     its arguments or any content) goes to .claude/skill-usage.jsonl.
//     tools/skill-usage-report.py aggregates it for the monthly
//     ablation (D20). Opt-out: SKILL_LEDGER=0.
// Exit code is always 0.
// ==============================================================================
import { appendFileSync, existsSync, mkdirSync } from "node:fs";
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
const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
try {
  appendFileSync(
    join(gateDir, "cost-ledger.jsonl"),
    JSON.stringify({
      ts,
      hook: "post-tool-use",
      tool,
    }) + "\n"
  );
} catch {
  // Ledger write failure must never break the session — silent fail-open.
}

// Skill-usage telemetry (D68): name only, never args or content.
if (tool === "Skill" && process.env.SKILL_LEDGER !== "0") {
  const skill = data.tool_input && data.tool_input.skill;
  if (typeof skill === "string" && skill) {
    try {
      const claudeDir = join(cwd, ".claude");
      mkdirSync(claudeDir, { recursive: true });
      const rec = { ts, skill };
      if (typeof data.session_id === "string" && data.session_id) {
        rec.session = data.session_id;
      }
      appendFileSync(
        join(claudeDir, "skill-usage.jsonl"),
        JSON.stringify(rec) + "\n"
      );
    } catch {
      // Telemetry write failure must never break the session.
    }
  }
}
process.exit(0);
