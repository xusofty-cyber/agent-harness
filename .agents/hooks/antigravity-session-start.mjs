#!/usr/bin/env node
// ==============================================================================
// antigravity-session-start.mjs — Antigravity SessionStart gate adapter.
// Runs the existing session-start.mjs (which prints a compact gate
// resume: in_progress / blocked items plus the SESSION_STATE breakpoint)
// and wraps its plain-text output in the Antigravity injectSteps schema:
//   {"injectSteps": [{"systemMessage": {"systemMessage": "<resume>"}}]}
// No gate state -> session-start.mjs prints nothing -> this adapter
// prints {} (no injection). SessionStart cannot block a session and
// never fails: every error path prints {} and logs to stderr.
// ==============================================================================

import {
  printJson,
  readStdin,
  resolveProjectRoot,
  runClaudeHook,
} from "./antigravity-common.mjs";

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[ANTIGRAVITY-HOOK] SessionStart stdin JSON parse failed; no resume shown (fail-open)\n",
  );
  printJson({});
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const res = runClaudeHook(projectRoot, "session-start.mjs", {
  cwd: projectRoot,
});
if (res && res.stderr) process.stderr.write(res.stderr);

const text = res ? res.stdout.trim() : "";
if (!text) {
  printJson({});
  process.exit(0);
}
printJson({
  injectSteps: [{ systemMessage: { systemMessage: text } }],
});
