#!/usr/bin/env node
// ==============================================================================
// workbuddy-post-tool-use.mjs — WorkBuddy PostToolUse gate adapter.
// Runs the existing post-tool-use.mjs, which appends one line per tool
// call to gate/cost-ledger.jsonl (only when gate/ exists; opt-out via
// COST_LEDGER=0). PostToolUse fires after the tool has executed, so it
// cannot block anything: this adapter always exits 0 with no stdout,
// whatever the ledger hook did. The recorded tool name is the WorkBuddy
// name (Bash, Write, ...) — the ledger records tool-call counts, not
// Claude names. Fail-open on every error path.
// ==============================================================================

import {
  forwardStderr,
  readStdin,
  resolveProjectRoot,
  runClaudeHook,
} from "./workbuddy-common.mjs";

let input;
try {
  input = JSON.parse(await readStdin());
} catch {
  process.stderr.write(
    "[WORKBUDDY-HOOK] PostToolUse stdin JSON parse failed; call not recorded (fail-open)\n",
  );
  process.exit(0);
}

const projectRoot = resolveProjectRoot(input);
const res = runClaudeHook(projectRoot, "post-tool-use.mjs", input);
if (res) forwardStderr(res);
process.exit(0);
