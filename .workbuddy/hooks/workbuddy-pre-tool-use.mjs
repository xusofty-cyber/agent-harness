#!/usr/bin/env node
// ==============================================================================
// workbuddy-pre-tool-use.mjs — WorkBuddy PreToolUse gate adapter.
// The WorkBuddy/CodeBuddy payload is already Claude-shaped ({tool_name,
// tool_input, cwd}), so this adapter forwards stdin unchanged to the
// existing Claude hooks and forwards their decision verbatim:
//   Bash                    -> guard.mjs (the blocking command guard)
//   Write | Edit |
//   NotebookEdit            -> guard-write.mjs first (warnings only,
//                              stderr forwarded), then
//                              guard-feature-list.mjs (the blocking check
//                              against direct edits to feature_list.json)
//   every other tool        -> allow (no Claude hook covers it; the
//                              gate's file and command guards are the
//                              blocking set)
// Deny: the Claude hook exits 2 and prints a hookSpecificOutput deny
// JSON (the assumed WorkBuddy/CodeBuddy shape). This adapter forwards that JSON on
// stdout, repeats its reason on stderr (so the reason survives whichever
// channel the host reads on an exit-2 block), and exits 2.
// Allow: exit 0 with no stdout — the normal permission flow continues.
// This is deliberately NOT an explicit "allow" decision: an explicit
// allow would skip the host's permission prompt, which this gate must
// never do on its own authority.
// Fail-open on every error path, matching the graded policy in guard.mjs.
// ==============================================================================

import {
  extractDenyReason,
  forwardStderr,
  printJson,
  readStdin,
  resolveProjectRoot,
  runClaudeHook,
} from "./workbuddy-common.mjs";

const WRITE_TOOLS = new Set(["Write", "Edit", "NotebookEdit"]);

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[WORKBUDDY-HOOK] PreToolUse stdin JSON parse failed; allowing (fail-open by design)\n",
  );
  process.exit(0);
}

const toolName = input.tool_name || "";
const projectRoot = resolveProjectRoot(input);

function deny(res) {
  const reason = extractDenyReason(res.stdout);
  // Forward the Claude deny JSON verbatim (already the assumed
  // WorkBuddy/CodeBuddy shape) and repeat the reason on stderr.
  try {
    const parsed = JSON.parse(res.stdout);
    printJson(parsed);
  } catch {
    printJson({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: reason,
      },
    });
  }
  process.stderr.write(`[WORKBUDDY-HOOK] Blocked: ${reason}\n`);
  process.exit(2);
}

if (toolName === "Bash") {
  const res = runClaudeHook(projectRoot, "guard.mjs", input);
  if (res) {
    forwardStderr(res);
    if (res.status === 2) deny(res);
  }
  process.exit(0);
}

if (WRITE_TOOLS.has(toolName)) {
  const warnings = runClaudeHook(projectRoot, "guard-write.mjs", input);
  if (warnings) forwardStderr(warnings);
  const res = runClaudeHook(projectRoot, "guard-feature-list.mjs", input);
  if (res) {
    forwardStderr(res);
    if (res.status === 2) deny(res);
  }
  process.exit(0);
}

// No gate hook covers this tool.
process.exit(0);
