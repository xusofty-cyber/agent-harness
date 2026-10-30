# Observability guide — make the running system debuggable

The gate proves behaviour *before* handover: a verification command
exits 0. Observability is the other half — when the system misbehaves
*while running*, can you find out why from what it emitted, without
attaching a debugger or re-running it under observation? This guide
is the lightweight convention for projects that use agent-harness.
It is deliberately small: three habits, one debugging loop.

## 1. Structured logs with a trace id

One JSON object per log line, on one line, to stdout (a file is fine
for a CLI). Minimum fields:

| Field | Meaning |
|---|---|
| `ts` | UTC timestamp, ISO 8601 |
| `level` | `debug` / `info` / `warn` / `error` |
| `trace_id` | One id per unit of work (request, job, CLI run, session) |
| `component` | The module/subsystem emitting the line |
| `event` | Stable machine-readable event name (`reminder_sent`) |
| `msg` | Human-readable detail; variables go in extra fields, not in the string |

Rules that make the logs worth having:

- **Generate `trace_id` at the entry point** (HTTP request, queue
  job, CLI invocation) and pass it through every call, queue message
  and subprocess. A failure you cannot correlate across components
  is three mysteries, not one.
- **Log decisions, not just errors**: inputs received (ids, counts —
  not payloads), branches taken, external calls made (target,
  duration, status), retries, and the final outcome of each unit of
  work. An error line with no preceding info lines is a dead end.
- **Never log secrets or personal data**: no tokens, passwords,
  credentials, or raw user content. Log the *id* of the thing, not
  the thing. Masking belongs in the logging call itself, not in a
  cleanup pass afterwards.
- Keep event names stable. Renaming an `event` breaks every saved
  query and every debugging habit built on it — treat names like an
  API.

## 2. One health-check command

Every project gets exactly one health-check command with this
contract:

- **Name/location**: one obvious place — `scripts/healthcheck`, a
  `health` script in the project manifest, or an equivalent the
  project documents in `PROJECT_CONTEXT.md`.
- **Behaviour**: checks the real dependencies the system needs to do
  its job (datastore reachable and migrations applied, queue/cache
  reachable, required config present), prints one line per check
  (`ok`/`FAIL` + name + short detail), and exits 0 only if all pass.
- **Cheap and read-only**: seconds, not minutes; no writes, no
  repairs, no retries that hide a flaky dependency. A health check
  that fixes things is a deployment script wearing a costume.
- It is the first command to run when anything is reported broken,
  and the last command to run after a fix.

## 3. Wire it into the gate

The health check earns its keep when the harness runs it without
being asked:

- Put it in `gate/clean-state.json`. The five dimensions have fixed
  slots, so compose: chain it into `start` (start the standard path,
  then probe it — e.g. `"start": "<start command> && <health
  command>"`) or into `test` when it is fast enough to run with the
  suite. `check-clean` then fails a handover whose system starts
  but is not healthy.
- Use it as (part of) the `verification.command` of feature-list
  items whose behaviour is runtime health: a `passing` then means
  "the running system answered healthy", not just "the code exists".
- Record the command itself in `PROJECT_CONTEXT.md`, next to the
  build/test/start commands, so the next session finds it without
  archaeology.

## 4. The log-based debugging loop

When something is wrong in the running system:

1. **Reproduce from logs first.** Find the failing unit of work and
   its `trace_id`; read the whole trace before touching code. Note
   the last *expected* event and the first *unexpected* one — the
   bug lives between them.
2. **State the hypothesis in one sentence**: "Component X received
   Y but emitted Z because …". If the trace cannot confirm or refute
   it, the gap is observability debt — say so explicitly.
3. **Fix the observability gap before the bug, if there is one.**
   Add the missing log line (stable event name, ids not payloads),
   re-run, and only then fix the behaviour. Otherwise the next
   incident starts from the same blindness.
4. **Fix, then regression-check twice**: the automated test suite,
   and the *same log query* that showed the failure — it must now
   show the healthy trace. A fix nobody re-observes is a hope, not
   a verification.
5. **Close the loop**: if the incident revealed a class of failure,
   add the cheapest guard that would have caught it earlier (a test,
   a health check, an alert on the event name) — and record it in
   the project's decision log if it changes a convention.

## 5. Checklist

- [ ] Logs are one-JSON-per-line with `ts`, `level`, `trace_id`,
      `component`, `event`
- [ ] `trace_id` is created at the entry point and propagated
- [ ] No secrets or personal data in any log field
- [ ] One documented health-check command; exit 0 = healthy;
      read-only; seconds-fast
- [ ] Health command wired into `gate/clean-state.json` and named
      in `PROJECT_CONTEXT.md`
- [ ] The last incident was debugged from a trace, and its
      observability gap (if any) got a log line, not just a fix
