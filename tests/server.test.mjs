#!/usr/bin/env node
// tests/server.test.mjs — unit tests for the brainstorming skill's local
// server helpers (.agents/skills/brainstorming/scripts/server.cjs, v3 2.7).
// Only the pure, exported helpers are tested here (no HTTP server is
// started, no port is bound, no browser is opened). Run:
//   node tests/server.test.mjs
// Uses only node built-ins (node:test + node:assert).
import { test } from "node:test";
import assert from "node:assert/strict";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const server = require(join(REPO_ROOT, ".agents/skills/brainstorming/scripts/server.cjs"));

test("WebSocket accept key matches the RFC 6455 example", () => {
  // RFC 6455 §1.3 example: key "dGhlIHNhbXBsZSBub25jZQ==" ->
  // accept "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=".
  assert.equal(server.computeAcceptKey("dGhlIHNhbXBsZSBub25jZQ=="), "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=");
});

test("encodeFrame produces a server text frame, decodeFrame reads a masked client frame", () => {
  const frame = server.encodeFrame(server.OPCODES.TEXT, Buffer.from("hello", "utf-8"));
  assert.equal(frame[0], 0x81);
  assert.equal(frame[1], 5);
  assert.equal(frame.slice(2).toString("utf-8"), "hello");
  // Masked client frame: FIN+TEXT, masked flag + length 5, 4 mask bytes,
  // then payload XOR mask.
  const mask = [0x37, 0xfa, 0x21, 0x3d];
  const masked = Buffer.from("hello").map((b, i) => b ^ mask[i % 4]);
  const client = Buffer.concat([Buffer.from([0x81, 0x85, ...mask]), masked]);
  const decoded = server.decodeFrame(client);
  assert.equal(decoded.payload.toString("utf-8"), "hello");
});

test("decodeFrame rejects unmasked client frames", () => {
  const frame = Buffer.from([0x81, 0x05, ...Buffer.from("hello")]);
  assert.throws(() => server.decodeFrame(frame), /masked/);
});

test("decodeFrame rejects oversized payloads", () => {
  assert.ok(server.MAX_FRAME_PAYLOAD_BYTES === 10 * 1024 * 1024);
  // Masked frame, 127-length form, declared length 1 GiB (> 10 MiB cap).
  const frame = Buffer.from([0x81, 0xff, 0, 0, 0, 0, 0x40, 0, 0, 0, 0, 0, 0, 0]);
  assert.throws(() => server.decodeFrame(frame), /exceeds/);
});

test("browser launcher is platform-correct and argv-based (no shell)", () => {
  assert.deepEqual(server.browserLauncherForPlatform("http://localhost:1/?key=x", { platform: "darwin" }),
    { bin: "open", args: ["http://localhost:1/?key=x"] });
  assert.deepEqual(server.browserLauncherForPlatform("http://localhost:1/?key=x", { platform: "win32" }),
    { bin: "rundll32.exe", args: ["url.dll,FileProtocolHandler", "http://localhost:1/?key=x"] });
  assert.equal(server.browserLauncherForPlatform("http://localhost:1/?key=x", { platform: "linux", env: {} }), null);
});
