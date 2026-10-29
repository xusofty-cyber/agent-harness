#!/usr/bin/env node
// ==============================================================================
// workbuddy-session-start.mjs — WorkBuddy SessionStart gate adapter.
// Runs the existing session-start.mjs (which prints a compact gate
// resume: in_progress / blocked items plus the SESSION_STATE breakpoint)
// and wraps its plain-text output in the assumed WorkBuddy/CodeBuddy
// SessionStart form:
//   {"hookSpecificOutput": {"hookEventName": "SessionStart",
//                            "additionalContext": "<resume>"}}
// No gate state -> session-start.mjs prints nothing -> this adapter
// prints nothing (no injection). SessionStart cannot block a session
// and never fails: every error path prints nothing and logs to stderr.
// ==============================================================================

import {
  forwardStderr,
  printJson,
  readStdin,
  resolveProjectRoot,
  runClaudeHook,
} from "./workbuddy-common.mjs";

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[WORKBUDDY-HOOK] SessionStart stdin JSON parse failed; no resume shown (fail-open)\n",
  );
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const res = runClaudeHook(projectRoot, "session-start.mjs", input);
if (res) forwardStderr(res);

const text = res ? res.stdout.trim() : "";
if (!text) process.exit(0);
printJson({
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: text,
  },
});
