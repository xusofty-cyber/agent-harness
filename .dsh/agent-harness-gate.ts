// ==============================================================================
// agent-harness-gate.ts — DeepSeek Harness (dsh) gate plugin (Cordis).
//
// CANONICAL SOURCE. The deployed runtime file is the type-stripped
// build artifact `.dsh/agent-harness-gate.mjs`, regenerated from this
// file with Node.js built-ins only (Node >= 22.13 / 24):
//
//   node --input-type=module -e "
//     import { readFileSync, writeFileSync } from 'node:fs';
//     import { stripTypeScriptTypes } from 'node:module';
//     const src = readFileSync('.dsh/agent-harness-gate.ts', 'utf8');
//     writeFileSync('.dsh/agent-harness-gate.mjs',
//       '#!/usr/bin/env node\n' + stripTypeScriptTypes(src));"
//
// Do not hand-edit the .mjs: edit this file, regenerate, and re-run
// `node tests/dsh-gate.test.mjs`. The plugin uses only Node.js
// built-ins and erasable TypeScript syntax (no enums, namespaces, or
// parameter properties), so it needs no npm install step and no build
// tool beyond the strip above. `.dsh/tsconfig.json` is the minimal
// config for a `tsc --noEmit` check; `.dsh/node-shims.d.ts` supplies
// the Node built-in declarations because this repository has no
// package.json and vendors no @types/node.
//
// This is the dsh counterpart of the Antigravity adapters in
// .agents/hooks/. It does NOT reimplement any gate rule. Every decision
// comes from the existing Claude Code hook scripts in .claude/hooks/
// (guard.mjs, guard-write.mjs, guard-feature-list.mjs, stop-gate.mjs,
// session-start.mjs, post-tool-use.mjs), run as `node` subprocesses with
// a Claude-shaped payload, exactly as the Antigravity adapters do. That
// keeps one source of truth for the gate rules instead of a second,
// drifting copy.
//
// VERIFICATION STATUS — READ BEFORE RELYING ON THIS PLUGIN:
// dsh 插件 API 未在官方文档/真机上核实 (not verified against official
// documentation or a live dsh run in this round). This round worked
// under a no-approval-card discipline: no external documentation was
// fetched and dsh is not installed in this environment, and the local
// repository contains no Cordis plugin API specification (DECISIONS.md
// has no dsh/Cordis entry; the bridge layer records only that dsh
// reads AGENTS.md natively and that --global writes
// ${DSH_HOME:-~/.dsh}/AGENTS.md, with cordis.patch.yml mentioned only
// as out-of-scope MCP surface). The event names, payload shapes, and
// steering surfaces used below (tools/pre-execute with a
// { kind: "deny", reason } return, ctx.tools.guard(), agent/created
// with agent.inject(), tools/result, agent/turn-stopping with
// agent.steer()/followup()/inject(), and the `- insert:` patch row)
// come from earlier work's reading of dsh documentation, which was NOT
// re-verified in this round. Treat every one of them as an
// UNVERIFIED CONTRACT until a live run on an installed dsh version
// confirms that dsh accepts this plugin, fires these events with these
// payload shapes, and actually steers a turn on agent/turn-stopping.
// In particular, dsh stop enforcement is PROVISIONAL, not a hard gate:
// on a blocked stop the plugin only attempts to steer through the
// Agent surface and logs loudly on stderr when none of those methods
// exists. dsh is a developer-preview product, so re-check this plugin
// against the installed dsh version before calling it battle-tested.
//
// Plugin shape (as implemented here, unverified — see above):
//   - A plugin is a module exporting `name` and `apply(ctx, config)`.
//   - It is mounted from a Cordis patch row (`- insert:`, id
//     `agent-harness-gate`) in a profile's cordis.patch.yml, the
//     home-level $DSH_HOME/cordis.patch.yml, or a `--patch` overlay.
//     See .dsh/cordis.patch.template.yml (shipped by the deploy scripts
//     as the target project's .dsh/cordis.patch.yml).
//   - `tools/pre-execute` is a waterfall `(exec, next)` returning
//     { kind: "allow" } | { kind: "deny", reason } |
//     { kind: "ask", reason? } | { kind: "cancel" }. A listener that
//     does not call next() vetoes the rest of the chain; this plugin
//     calls next() on allow (so dsh's own approval flow still runs)
//     and returns { kind: "deny", reason } without calling next() to
//     veto. A deny is intended to reach the model as an error tool
//     result with the tool never running — unverified, see above.
//   - `ctx.tools.guard()` is the monotonic final denial: it runs after
//     the pre-execute waterfall and before the tool body, and a reason
//     returned here cannot be turned back into an allow later. This
//     plugin registers the same translation as a guard when
//     ctx.tools.guard exists, as defense in depth (the guard script
//     itself is read-only, so running it twice is harmless).
//   - `agent/created` is the creation-time event used here. dsh has no
//     SessionStart hook in this design: session history itself resumes
//     natively from dsh's append-only log. What this plugin adds at
//     creation time is the gate resume text (the same text
//     session-start.mjs prints for Claude Code), delivered via
//     agent.inject() when the agent exposes it, and only when a gate
//     (gate/feature_list.json) is in use.
//   - `tools/result` is the observation point for the immutable final
//     outcome. The cost-ledger listener here only observes: it never
//     returns a decision and never throws. Its argument shape is the
//     least-verified part of this plugin, so the listener scans all
//     its arguments defensively for a tool name and does nothing when
//     it finds none.
//   - `agent/turn-stopping` is serial and has NO next(). This plugin
//     does NOT claim a verified blocking return value here: on a
//     blocked stop it attempts to steer through the public Agent
//     surface (steer, else followup, else inject, in that order) and
//     logs loudly on stderr when none of those exists.
//
// Tool-name mapping (deliberately permissive and fail-open, because
// tool names vary across profiles and versions):
//   bash / pwsh / run_command / shell  -> Bash guard (command field)
//   write / edit / write_to_file / replace_file_content /
//   multi_replace_file_content / str_replace_editor (create /
//   str_replace / insert only; view is read-only) -> write warnings
//   plus the feature-list write block (file-path field)
//   every other tool -> allow (no Claude hook covers it; the gate's
//   file and command guards are the blocking set)
//
// Fail-open posture: this follows the graded policy already used by
// guard.mjs and the Antigravity adapters — a hook that cannot inspect
// (missing script, spawn failure, unparseable execution) is visible
// on stderr and allows, never silently allows and never blocks
// legitimate work on a malformed payload. That is a deliberate
// difference from fail-closed gates; it matches this repository's
// existing hooks. Server-side branch protection remains the real
// boundary, as with every client-side hook in this repo.
//
// Guard script resolution: prefer <project>/.dsh/hooks/<name> (where
// the deploy scripts copy the Claude hook scripts for dsh-only
// projects), fall back to <project>/.claude/hooks/<name> (projects
// that also deploy Claude Code hooks, and this repository itself).
// Project root resolution: config.projectRoot, then
// $AGENT_HARNESS_PROJECT_ROOT, then a working-directory field on the
// execution / agent object, then process.cwd() (dsh runs hook code
// from the workspace root in practice).
// ==============================================================================

import { spawnSync } from "node:child_process";
import {
  appendFileSync,
  existsSync,
  readFileSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";

export const name = "agent-harness-gate";

/** Any JSON-ish value coming from dsh; access is defensive throughout. */
type UnknownValue = unknown;
type UnknownRecord = Record<string, unknown>;

interface Translation {
  toolName: string;
  command: string;
  filePath: string;
}

interface HookResult {
  status: number | null;
  stdout: string;
  stderr: string;
}

interface PluginConfig {
  projectRoot?: string;
}

type NextFn = () => unknown;
type Listener = (...args: UnknownValue[]) => unknown;

interface CordisTools {
  guard?: (fn: (exec: UnknownValue) => string | undefined) => void;
}

interface CordisContext {
  on: (event: string, listener: Listener) => void;
  tools?: CordisTools;
}

const BASH_TOOLS = new Set([
  "bash",
  "pwsh",
  "run_command",
  "shell",
  "run_shell_command",
  "execute",
]);

const WRITE_TOOLS = new Set([
  "write",
  "edit",
  "write_to_file",
  "replace_file_content",
  "multi_replace_file_content",
  "str_replace_editor",
]);

function log(message: string): void {
  process.stderr.write(`[DSH-GATE] ${message}\n`);
}

function asRecord(value: UnknownValue): UnknownRecord | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as UnknownRecord;
  }
  return null;
}

function strField(obj: UnknownRecord | null, key: string): string | undefined {
  if (!obj) return undefined;
  const value = obj[key];
  return typeof value === "string" ? value : undefined;
}

// Normalize a dsh tool name: strip MCP-style server qualification
// (mcp__<server>__<tool>) and lower-case, so matching is stable
// across profiles.
function normalizeToolName(raw: string): string {
  if (typeof raw !== "string") return "";
  const base = raw.includes("__") ? raw.split("__").pop() : raw;
  return (base ?? "").trim().toLowerCase();
}

// Extract { toolName, command, filePath } from a ToolExecution, across
// the field spellings dsh versions and profiles have used. Never
// throws: an unrecognised shape yields empty fields, and the caller
// fail-opens on that.
export function translateExecution(exec: UnknownValue): Translation {
  const obj = asRecord(exec);
  if (!obj) {
    return { toolName: "", command: "", filePath: "" };
  }
  const toolObj = asRecord(obj["tool"]);
  const definitionObj = asRecord(obj["definition"]);
  const rawName =
    strField(obj, "toolName") ??
    strField(toolObj, "name") ??
    strField(obj, "name") ??
    strField(definitionObj, "name") ??
    (typeof obj["tool"] === "string" ? (obj["tool"] as string) : undefined) ??
    "";
  const toolName = normalizeToolName(rawName);
  const argsRaw =
    obj["input"] ?? obj["args"] ?? obj["arguments"] ?? obj["toolInput"] ?? obj["params"] ?? {};
  const argObj = asRecord(argsRaw);
  const argsAsString = typeof argsRaw === "string" ? argsRaw : "";
  const command =
    strField(argObj, "command") ??
    strField(argObj, "CommandLine") ??
    strField(argObj, "cmd") ??
    strField(argObj, "script") ??
    strField(argObj, "code") ??
    argsAsString ??
    "";
  const filePath =
    strField(argObj, "file_path") ??
    strField(argObj, "filePath") ??
    strField(argObj, "TargetFile") ??
    strField(argObj, "path") ??
    strField(argObj, "file") ??
    strField(argObj, "filename") ??
    "";
  // str_replace_editor is read-only for `view`; only its mutating
  // operations go through the write guards. The operation value is
  // stringified exactly like the pre-TypeScript implementation did,
  // so a non-string command still counts as an unknown operation.
  if (toolName === "str_replace_editor") {
    const op = String(argObj ? argObj["command"] ?? "" : "").toLowerCase();
    if (op && !["create", "str_replace", "insert"].includes(op)) {
      return { toolName, command: "", filePath: "" };
    }
  }
  return { toolName, command, filePath };
}

export function resolveProjectRoot(input: UnknownValue, config: PluginConfig = {}): string {
  if (config && typeof config.projectRoot === "string" && config.projectRoot) {
    return config.projectRoot;
  }
  if (process.env["AGENT_HARNESS_PROJECT_ROOT"]) {
    return process.env["AGENT_HARNESS_PROJECT_ROOT"] as string;
  }
  const candidates = asRecord(input) ?? {};
  for (const key of [
    "workingDirectory",
    "workspaceRoot",
    "workspace",
    "cwd",
    "directory",
  ]) {
    const value = candidates[key];
    if (typeof value === "string" && value) return value;
  }
  // An agent wrapper object ({ agent: {...} }) — unwrap one level.
  if (candidates["agent"] && typeof candidates["agent"] === "object") {
    return resolveProjectRoot(candidates["agent"], {});
  }
  return process.cwd();
}

function resolveClaudeScript(projectRoot: string, scriptName: string): string | null {
  const dshPath = join(projectRoot, ".dsh", "hooks", scriptName);
  if (existsSync(dshPath)) return dshPath;
  const claudePath = join(projectRoot, ".claude", "hooks", scriptName);
  if (existsSync(claudePath)) return claudePath;
  return null;
}

// Run one Claude hook script with a Claude-shaped payload. Returns
// { status, stdout, stderr } or null when the script is missing or the
// spawn itself failed (fail-open: the caller treats null as "allow").
function runClaudeHook(
  projectRoot: string,
  scriptName: string,
  claudePayload: UnknownRecord,
): HookResult | null {
  const script = resolveClaudeScript(projectRoot, scriptName);
  if (!script) {
    log(`${scriptName} not found under .dsh/hooks/ or .claude/hooks/; allowing (fail-open)`);
    return null;
  }
  try {
    const res = spawnSync("node", [script], {
      input: JSON.stringify(claudePayload),
      cwd: projectRoot,
      env: { ...process.env },
      encoding: "utf-8",
      timeout: 25000,
    });
    return {
      status: res.status,
      stdout: res.stdout || "",
      stderr: res.stderr || "",
    };
  } catch {
    log(`${scriptName} failed to run; allowing (fail-open)`);
    return null;
  }
}

function extractDenyReason(stdout: string): string {
  try {
    const parsed = asRecord(JSON.parse(stdout) as UnknownValue);
    const hookOutput = asRecord(parsed ? parsed["hookSpecificOutput"] : null);
    const reason = hookOutput ? hookOutput["permissionDecisionReason"] : undefined;
    if (typeof reason === "string" && reason) return reason;
  } catch {
    // Not JSON — fall through to the default reason.
  }
  return "Blocked by the agent-harness gate hook.";
}

function forwardStderr(res: HookResult | null): void {
  if (res && res.stderr) process.stderr.write(res.stderr);
}

// Shared decision translation for both tools/pre-execute and the
// monotonic ctx.tools.guard(). Returns a deny reason string, or null
// to allow. Synchronous: the Claude scripts are run with spawnSync.
function decideExecution(projectRoot: string, exec: UnknownValue): string | null {
  const { toolName, command, filePath } = translateExecution(exec);
  if (BASH_TOOLS.has(toolName)) {
    const res = runClaudeHook(projectRoot, "guard.mjs", {
      tool_name: "Bash",
      tool_input: { command },
      cwd: projectRoot,
    });
    forwardStderr(res);
    if (res && res.status === 2) return extractDenyReason(res.stdout);
    return null;
  }
  if (WRITE_TOOLS.has(toolName)) {
    const writeRes = runClaudeHook(projectRoot, "guard-write.mjs", {
      tool_name: "Write",
      tool_input: { file_path: filePath },
      cwd: projectRoot,
    });
    forwardStderr(writeRes);
    const listRes = runClaudeHook(projectRoot, "guard-feature-list.mjs", {
      tool_name: "Write",
      tool_input: { file_path: filePath },
      cwd: projectRoot,
    });
    forwardStderr(listRes);
    if (listRes && listRes.status === 2) return extractDenyReason(listRes.stdout);
    return null;
  }
  return null;
}

function readInProgressIds(projectRoot: string): string {
  try {
    const parsed = asRecord(
      JSON.parse(readFileSync(join(projectRoot, "gate", "feature_list.json"), "utf-8")) as UnknownValue,
    );
    const items = parsed ? parsed["items"] : undefined;
    if (!Array.isArray(items)) return "";
    return items
      .filter((i) => asRecord(i)?.["status"] === "in_progress")
      .map((i) => String(asRecord(i)?.["id"] ?? ""))
      .filter((id) => id !== "")
      .join(",");
  } catch {
    return "";
  }
}

interface StopState {
  agentKey: string;
  blocked: boolean;
}

function stopStatePath(projectRoot: string): string {
  return join(projectRoot, "gate", "dsh-stop-state.json");
}

function readStopState(projectRoot: string): StopState | null {
  try {
    const parsed = asRecord(
      JSON.parse(readFileSync(stopStatePath(projectRoot), "utf-8")) as UnknownValue,
    );
    if (parsed && typeof parsed["agentKey"] === "string" && parsed["blocked"] === true) {
      return { agentKey: parsed["agentKey"] as string, blocked: true };
    }
  } catch {
    // No state, or unreadable — treat as no prior block.
  }
  return null;
}

function writeStopState(projectRoot: string, state: StopState): void {
  try {
    writeFileSync(stopStatePath(projectRoot), JSON.stringify(state) + "\n", "utf-8");
  } catch {
    // State write failure must not change the outcome.
  }
}

function clearStopState(projectRoot: string): void {
  try {
    unlinkSync(stopStatePath(projectRoot));
  } catch {
    // Already absent — fine.
  }
}

function agentKey(agent: UnknownValue): string {
  const obj = asRecord(agent);
  if (!obj) return "default";
  const key =
    strField(obj, "sessionId") ??
    strField(obj, "session_id") ??
    strField(obj, "id") ??
    strField(obj, "conversationId") ??
    "default";
  return key;
}

function unwrapAgent(value: UnknownValue): UnknownValue {
  const obj = asRecord(value);
  if (obj && obj["agent"] && typeof obj["agent"] === "object") {
    return obj["agent"];
  }
  return value;
}

function callAgentMethod(agent: UnknownValue, method: string, arg: string): boolean {
  const obj = asRecord(agent);
  if (!obj) return false;
  const fn = obj[method];
  if (typeof fn === "function") {
    (fn as (msg: string) => void).call(agent, arg);
    return true;
  }
  return false;
}

export function apply(ctx: CordisContext, config: PluginConfig = {}): void {
  // --- tools/pre-execute: the blocking gate (contract unverified). ---
  ctx.on("tools/pre-execute", async (exec: UnknownValue, next: UnknownValue) => {
    let projectRoot: string;
    try {
      projectRoot = resolveProjectRoot(exec, config);
      const reason = decideExecution(projectRoot, exec);
      if (reason) return { kind: "deny", reason };
    } catch {
      log("pre-execute translation failed; allowing (fail-open by design)");
    }
    return (next as NextFn)();
  });

  // --- ctx.tools.guard(): monotonic final denial (same translation). ---
  try {
    if (ctx.tools && typeof ctx.tools.guard === "function") {
      ctx.tools.guard((exec: UnknownValue) => {
        try {
          const projectRoot = resolveProjectRoot(exec, config);
          return decideExecution(projectRoot, exec) ?? undefined;
        } catch {
          log("guard translation failed; abstaining (fail-open by design)");
          return undefined;
        }
      });
    }
  } catch {
    log("ctx.tools.guard registration failed; pre-execute gate still applies");
  }

  // --- tools/result: cost-ledger observation only. Never blocks. ---
  ctx.on("tools/result", (...args: UnknownValue[]) => {
    try {
      let toolName = "unknown";
      for (const arg of args) {
        if (!arg || typeof arg !== "object") continue;
        const { toolName: parsed } = translateExecution(arg);
        if (parsed) {
          toolName = parsed;
          break;
        }
        const toolNameField = strField(asRecord(arg), "toolName");
        if (toolNameField) {
          toolName = normalizeToolName(toolNameField);
          break;
        }
      }
      const projectRoot = resolveProjectRoot(args[0], config);
      const res = runClaudeHook(projectRoot, "post-tool-use.mjs", {
        tool_name: toolName,
        cwd: projectRoot,
      });
      forwardStderr(res);
    } catch {
      // Ledger observation must never break the session — silent fail-open.
    }
  });

  // --- agent/created: gate resume injection (dsh has no SessionStart). ---
  ctx.on("agent/created", (value: UnknownValue) => {
    try {
      const agent = unwrapAgent(value);
      const projectRoot = resolveProjectRoot(agent, config);
      if (!existsSync(join(projectRoot, "gate", "feature_list.json"))) return;
      const res = runClaudeHook(projectRoot, "session-start.mjs", {
        cwd: projectRoot,
      });
      forwardStderr(res);
      const text = res ? res.stdout.trim() : "";
      if (!text) return;
      if (!callAgentMethod(agent, "inject", text)) {
        log("gate resume available but agent.inject is absent; resume not injected");
      }
    } catch {
      log("agent/created resume failed; session continues (fail-open)");
    }
  });

  // --- agent/turn-stopping: stop gate (PROVISIONAL — see header). ---
  // Serial, no next(). A second blocked stop for the same agent is
  // allowed (state cleared, stop-gate itself logs the allowance when
  // passed stop_hook_active), mirroring the Antigravity deadlock guard,
  // so a session can never be trapped in a continue-loop by this hook.
  ctx.on("agent/turn-stopping", (value: UnknownValue) => {
    try {
      const agent = unwrapAgent(value);
      const projectRoot = resolveProjectRoot(agent, config);
      if (!existsSync(join(projectRoot, "gate", "feature_list.json"))) return;
      const key = agentKey(agent);
      const prior = readStopState(projectRoot);
      if (prior && prior.blocked && prior.agentKey === key) {
        clearStopState(projectRoot);
        const res = runClaudeHook(projectRoot, "stop-gate.mjs", {
          cwd: projectRoot,
          stop_hook_active: true,
        });
        forwardStderr(res);
        log("stop allowed on second attempt for this agent; items still in_progress");
        return;
      }
      const res = runClaudeHook(projectRoot, "stop-gate.mjs", {
        cwd: projectRoot,
      });
      forwardStderr(res);
      if (res && res.status === 2) {
        writeStopState(projectRoot, { agentKey: key, blocked: true });
        const ids = readInProgressIds(projectRoot);
        const message =
          `Gate items still in_progress${ids ? ` (${ids})` : ""}. ` +
          "Finish them (pass-gate.py verify) or mark them blocked, " +
          "or use a logged human override: " +
          "`pass-gate.py override --id <id> --reason \"...\"` for a single item, " +
          "or GATE_ALLOW_STOP=1 GATE_STOP_REASON=\"...\" to stop now.";
        if (
          !callAgentMethod(agent, "steer", message) &&
          !callAgentMethod(agent, "followup", message) &&
          !callAgentMethod(agent, "inject", message)
        ) {
          log(
            "stop-gate BLOCKED this stop but no agent steering surface (steer/followup/inject) was found; " +
              "the turn may still end — live dsh verification is required before treating dsh stop enforcement as a hard gate",
          );
        }
        // Best-effort event line, mirroring the Antigravity stop adapter's
        // logging (never throws, never changes the outcome).
        try {
          const eventsPath = join(projectRoot, "gate", "events.jsonl");
          let seq = 1;
          if (existsSync(eventsPath)) {
            for (const line of readFileSync(eventsPath, "utf-8").split("\n").filter(Boolean)) {
              try {
                const s = asRecord(JSON.parse(line) as UnknownValue)?.["seq"];
                if (typeof s === "number" && Number.isInteger(s) && s >= seq) seq = s + 1;
              } catch {
                // Skip unparseable lines.
              }
            }
          }
          appendFileSync(
            eventsPath,
            JSON.stringify({
              seq,
              ts: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
              actor: "dsh-turn-stopping",
              event: "stop_blocked",
              item_id: ids || null,
              detail: "stop-gate blocked; steering attempted (provisional, see plugin header)",
            }) + "\n",
          );
        } catch {
          // Logging failure must not change the outcome.
        }
      } else {
        clearStopState(projectRoot);
      }
    } catch {
      log("agent/turn-stopping handling failed; stop proceeds (fail-open)");
    }
  });
}
