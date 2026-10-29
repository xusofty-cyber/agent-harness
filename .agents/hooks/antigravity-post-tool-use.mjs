#!/usr/bin/env node
// ==============================================================================
// antigravity-post-tool-use.mjs — Antigravity PostToolUse gate adapter.
// Runs the existing post-tool-use.mjs, which appends one line per tool
// call to gate/cost-ledger.jsonl (only when gate/ exists; opt-out via
// COST_LEDGER=0). The Antigravity PostToolUse output contract is {},
// so this adapter always prints {} and never blocks, whatever the
// ledger hook did. The recorded tool name is the Antigravity name
// (run_command, write_to_file, ...) — the ledger records tool-call
// counts, not Claude names.
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
    "[ANTIGRAVITY-HOOK] PostToolUse stdin JSON parse failed; call not recorded (fail-open)\n",
  );
  printJson({});
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const toolName = (input.toolCall && input.toolCall.name) || "unknown";
const res = runClaudeHook(projectRoot, "post-tool-use.mjs", {
  tool_name: toolName,
  cwd: projectRoot,
});
if (res && res.stderr) process.stderr.write(res.stderr);
printJson({});
