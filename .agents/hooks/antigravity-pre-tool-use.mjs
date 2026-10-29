#!/usr/bin/env node
// ==============================================================================
// antigravity-pre-tool-use.mjs — Antigravity PreToolUse gate adapter.
// Translates Antigravity tool calls into the Claude Code payloads the
// existing .claude/hooks/*.mjs scripts understand, then translates their
// decision back into the Antigravity protocol (decision is REQUIRED):
//   Claude exit 2 / permissionDecision "deny"  -> {"decision":"deny", reason}
//   anything else (including missing hook script) -> {"decision":"allow"}
// Tool mapping (Antigravity names; the hooks reference documents
// write_to_file, but the live agy CLI 1.4.10 calls the file-write tool
// write_file with a Path argument — proven by a 2026-10-30 --print run
// in which a write_file overwrite of gate/feature_list.json sailed past
// both the matcher and this set, because neither listed write_file):
//   run_command            -> Bash,            tool_input.command = CommandLine
//   write_file             -> Write,           tool_input.file_path = Path
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
  "write_file",
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
  // write_file (live agy CLI 1.4.10) carries the path as Path; the
  // reference names carry it as TargetFile. Either alone is not enough:
  // without the Path fallback a write_file call arrives with an empty
  // path and the guards pass it.
  const filePath = args.Path || args.path || args.TargetFile || args.file_path || "";
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
