#!/usr/bin/env node
// ==============================================================================
// session-start.mjs — Claude Code SessionStart hook (Phase 2, 2-3).
// Prints a compact resume so a new session picks up where the last one
// stopped, without re-reading the whole repo:
//   - in_progress / blocked items from gate/feature_list.json (if the gate
//     is in use here)
//   - the first lines of SESSION_STATE.md (project root, else
//     docs/internal/SESSION_STATE.md)
//
// SessionStart output is shown to the agent as context; the hook cannot
// block a session, and it never fails: no gate state -> silent exit 0.
// Any error (including stdin parse failure) is fail-open with a stderr
// log line, matching the guard.mjs convention (Phase 2, 2-4).
// Exit code is always 0.
// ==============================================================================
import { existsSync, readFileSync } from "node:fs";
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
    "[SESSION-START] stdin JSON parse failed; no resume shown (fail-open)\n"
  );
  process.exit(0);
}

const cwd = data.cwd || process.cwd();
const listPath = join(cwd, "gate", "feature_list.json");
if (!existsSync(listPath)) {
  process.exit(0); // gate not in use here — nothing to resume
}

let list;
try {
  list = JSON.parse(readFileSync(listPath, "utf-8"));
} catch {
  process.stderr.write(
    "[SESSION-START] gate/feature_list.json is unreadable; no resume shown (fail-open)\n"
  );
  process.exit(0);
}

const items = list.items || [];
const inProgress = items.filter((i) => i.status === "in_progress");
const blocked = items.filter((i) => i.status === "blocked");
const passing = items.filter((i) => i.status === "passing").length;

const lines = ["[SESSION-START] gate resume:"];
lines.push(
  `  items: ${items.length} total, ${inProgress.length} in_progress, ` +
    `${blocked.length} blocked, ${passing} passing`
);
for (const item of inProgress) {
  lines.push(`  ▶ in_progress: ${item.id} — ${item.title || "(no title)"}`);
}
for (const item of blocked) {
  lines.push(`  ■ blocked: ${item.id} — ${item.title || "(no title)"}`);
}
if (inProgress.length === 0 && blocked.length === 0) {
  lines.push("  (nothing in progress — pick the next item with pass-gate.py start)");
}

// SESSION_STATE.md breakpoint file, project root first, then docs/internal/.
let statePath = join(cwd, "SESSION_STATE.md");
if (!existsSync(statePath)) statePath = join(cwd, "docs", "internal", "SESSION_STATE.md");
if (existsSync(statePath)) {
  try {
    const stateLines = readFileSync(statePath, "utf-8")
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean)
      .slice(0, 12);
    if (stateLines.length > 0) {
      lines.push("  SESSION_STATE:");
      for (const l of stateLines) lines.push(`    ${l}`);
    }
  } catch {
    // unreadable breakpoint file — the gate list above is enough
  }
}

process.stdout.write(lines.join("\n") + "\n");
process.exit(0);
