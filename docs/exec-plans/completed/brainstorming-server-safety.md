# brainstorming server safety note (v3 Phase 2.7)

Decision (see DECISIONS.md D18): keep
`.agents/skills/brainstorming/scripts/server.cjs` as an opt-in skill
asset. Do NOT move it into default deployment, and do NOT delete it:
it is a vendored superpowers skill asset, and deleting it would break
the skill and upstream sync. It is not deployed by deploy-agents.sh or
run-pipeline.sh (verified by grep: no deploy reference to it); it only
runs when a user invokes the brainstorming skill and starts it.

## What was verified by reading the code (not by running a server)

- Binds to 127.0.0.1 by default (`BRAINSTORM_HOST` env override;
  browser auto-open is disabled for non-loopback hosts).
- Token auth: token from env, token file (chmod 0600), or generated
  on fallback; comparisons use timing-safe equality; the companion URL
  carries the token as a query key, and the cookie is HttpOnly +
  SameSite=Strict.
- Path traversal: `/files/` paths are resolved with realpath and
  checked to stay inside CONTENT_DIR; directory access is rejected.
- Frame safety: WebSocket frames capped at 10 MiB, unmasked client
  frames rejected, origin checked against Host for upgrades.
- Headers: X-Frame-Options DENY, CSP frame-ancestors 'none',
  Cross-Origin-Resource-Policy same-origin.
- Lifecycle: idle timeout defaults to 4 hours; owner-death and
  port-in-use handling refuse fallback when an explicit env token is
  set (so a token is never silently reused on a different port).

## What was verified live (2026-10-28, loopback probe)

The "never HTTP-probed" gap is now closed for HTTP + WebSocket
behaviour on loopback. A read-only probe started the real vendored
server on 127.0.0.1 (test port, test CONTENT_DIR in /tmp with one
harmless file, a dotfile, a symlink pointing outside, and an outside
marker file) and confirmed every claim below; an independent
re-run with a fresh token and port reproduced the auth, file-body,
symlink, and encoded-traversal results. Full probe record:
`/tmp/server-probe.md` (probe artefacts only; no repo files touched).

- Unauthenticated rejected: no-key and wrong-key requests → 403 on
  `/` and on `/files/<name>`.
- Authenticated succeeds: `?key=TOKEN` → 200 (bootstrap page; file
  body exact). Observed headers: X-Frame-Options DENY, CSP
  frame-ancestors 'none', CORP same-origin, Referrer-Policy
  no-referrer, Cache-Control no-store; cookie flags HttpOnly +
  SameSite=Strict + Path=/.
- Traversal rejected: `../`, URL-encoded `%2e%2e%2f`, symlink to
  outside, dotfile, and directory requests → all 404; the outside
  marker string never appeared in any response.
- WebSocket: unauthenticated and cross-origin
  (`Origin: http://evil.example`) upgrades destroyed with no 101;
  authenticated upgrade reached 101 and a masked message was logged
  as a user-event; an unmasked frame and a header-only 11 MiB frame
  declaration each got a 2-byte CLOSE frame and socket close.
- Server killed afterwards; port refused, no server process left.

## Still NOT probed (not claimed)

- Idle timeout (4 h default) and owner-death handling (would take
  hours / require killing the owner).
- Port-in-use fallback refusal with an explicit token.
- Absent-Origin upgrades (allowed by design; the WS client used
  always sends an Origin).
- `BRAINSTORM_OPEN_CMD` shell execution and non-loopback binds:
  deliberately not tested; the warnings below stand unchanged.

## Residual risks (operator must know)

- `BRAINSTORM_HOST` set to a non-loopback address exposes the server
  on that interface with only token-in-URL auth; tokens in URLs can
  leak via logs, referers and shell history. Keep the default
  loopback unless you understand this.
- `BRAINSTORM_OPEN_CMD` is trusted operator input and is executed
  via shell; never set it from untrusted input.
- The token in the companion URL is a secret: do not paste the URL
  into chat, tickets or screenshots. Observed in the probe: the
  server's own `server-started` stdout line prints the full
  companion URL including the key — treat server stdout as
  secret-bearing, not as safe log output.
- No server is started by any test in this repo: tests/server.test.mjs
  covers only the exported pure helpers (accept key, frame
  encode/decode, launcher mapping). Live probing above was a manual
  loopback exercise, not a repo test.
