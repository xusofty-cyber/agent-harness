#!/usr/bin/env node
// ==============================================================================
// guard-feature-list.mjs — Claude Code PreToolUse hook (Write|Edit|NotebookEdit)
// Blocks DIRECT writes to any feature_list.json. The only writer allowed is
// gate/pass-gate.py (invoked through Bash, which this hook does not see).
// This is one leg of the anti-tamper triple (Phase 1, v3 1-5):
//   (a) this hook, (b) CI re-verification in tests/repo_checks.py §3k,
//   (c) the append-only event log gate/events.jsonl.
// Limits, stated honestly (see gate/README.md):
//   - Claude Code only. Other hosts have no PreToolUse hook; on them the
//     CI check (b) and the event log (c) are the only defences.
//   - A determined agent can still rewrite the file through Bash (sed,
//     python, heredoc). This hook raises the cost of a casual fake pass
//     and makes it visible, it does not make fakery impossible.
//   - stdin parse failure is fail-open (exit 0), matching guard.mjs.
// Exit code 2 + JSON decision "deny" blocks the tool call in Claude Code.
// ==============================================================================
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

let data;
try {
  data = JSON.parse(input);
} catch {
  process.exit(0);
}

const toolInput = data.tool_input || {};
const filePath = (
  toolInput.file_path ||
  toolInput.path ||
  toolInput.notebook_path ||
  ""
).toLowerCase();

const isFeatureList =
  filePath.endsWith("feature_list.json") ||
  filePath.endsWith("feature_list.json.tmp");

if (!isFeatureList) {
  process.exit(0);
}

// Deny the direct write and tell the agent the lawful path.
const reason =
  "Direct writes to feature_list.json are blocked. " +
  "Use gate/pass-gate.py (start / verify / block / reopen / override) " +
  "so the status change is verified and logged to gate/events.jsonl. " +
  "See gate/README.md.";
process.stdout.write(
  JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: reason,
    },
  })
);
process.stderr.write(`[GATE-HOOK] ${reason}\n`);

// Leave a trace of the blocked attempt (best effort; never fail the hook).
// Sequence continues from the last event so the log stays monotonic.
try {
  const cwd = data.cwd || process.cwd();
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
      actor: "guard-feature-list",
      event: "direct_write_blocked",
      item_id: null,
      detail: `${data.tool_name || "Write/Edit"} to ${toolInput.file_path || toolInput.path || "?"} denied`,
    }) + "\n"
  );
} catch {
  // The events file may not exist (gate not initialised) — not an error.
}
process.exit(2);
