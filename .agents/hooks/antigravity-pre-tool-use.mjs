#!/usr/bin/env node
// ==============================================================================
// antigravity-pre-tool-use.mjs — Antigravity PreToolUse gate adapter.
// Translates Antigravity tool calls into the Claude Code payloads the
// existing .claude/hooks/*.mjs scripts understand, then translates their
// decision back into the Antigravity protocol (decision is REQUIRED):
//   Claude exit 2 / permissionDecision "deny"  -> {"decision":"deny", reason}
//   anything else (including missing hook script) -> {"decision":"allow"}
// Tool mapping (Antigravity names, from the official hooks reference):
//   run_command            -> Bash,            tool_input.command = CommandLine
//   write_to_file /
//   replace_file_content /
//   multi_replace_file_content
//                          -> Write,           tool_input.file_path = TargetFile
//   every other tool       -> allow (no Claude hook covers it; the gate's
//                             file and command guards are the blocking set)
// For write tools, guard-write.mjs runs first (warnings only, stderr
// forwarded) and guard-feature-list.mjs second (the blocking check).
// Fail-open on every error path, matching the graded policy in guard.mjs:
// a hook that cannot inspect must be visible (stderr) and must not block
// legitimate work on a malformed payload.
// ==============================================================================

import {
  extractDenyReason,
  forwardStderr,
  printAllow,
  printDeny,
  readStdin,
  resolveProjectRoot,
  runClaudeHook,
} from "./antigravity-common.mjs";

const WRITE_TOOLS = new Set([
  "write_to_file",
  "replace_file_content",
  "multi_replace_file_content",
]);

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[ANTIGRAVITY-HOOK] PreToolUse stdin JSON parse failed; allowing (fail-open by design)\n",
  );
  printAllow();
  process.exit(0);
}

const toolCall = input.toolCall || {};
const toolName = toolCall.name || "";
const args = toolCall.args || {};
const projectRoot = resolveProjectRoot(input);

if (toolName === "run_command") {
  const command = args.CommandLine || "";
  const res = runClaudeHook(
    projectRoot,
    "guard.mjs",
    { tool_name: "Bash", tool_input: { command }, cwd: projectRoot },
  );
  forwardStderr(res);
  if (res && res.status === 2) {
    printDeny(extractDenyReason(res.stdout));
  } else {
    printAllow();
  }
  process.exit(0);
}

if (WRITE_TOOLS.has(toolName)) {
  const filePath = args.TargetFile || "";
  const writeRes = runClaudeHook(
    projectRoot,
    "guard-write.mjs",
    { tool_name: "Write", tool_input: { file_path: filePath }, cwd: projectRoot },
  );
  forwardStderr(writeRes);
  const listRes = runClaudeHook(
    projectRoot,
    "guard-feature-list.mjs",
    { tool_name: "Write", tool_input: { file_path: filePath }, cwd: projectRoot },
  );
  forwardStderr(listRes);
  if (listRes && listRes.status === 2) {
    printDeny(extractDenyReason(listRes.stdout));
  } else {
    printAllow();
  }
  process.exit(0);
}

// No gate hook covers this tool — allow, and let Antigravity's own
// permission prompts apply.
printAllow();
