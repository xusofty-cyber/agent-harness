// node-shims.d.ts — minimal Node.js built-in declarations for the dsh
// gate plugin's isolated `tsc --noEmit` check (see .dsh/tsconfig.json).
//
// This file exists ONLY because this repository has no package.json
// and vendors no @types/node. It declares exactly the built-in
// surfaces agent-harness-gate.ts uses, with the shapes that code
// relies on — it is not a substitute for @types/node, and a consumer
// that has real Node types should not include this file in its own
// tsc program. At runtime these declarations are erased; the plugin
// imports the real Node built-ins.

declare module "node:child_process" {
  export interface SpawnSyncOptions {
    input?: string;
    cwd?: string;
    env?: Record<string, string | undefined>;
    encoding?: string;
    timeout?: number;
  }
  export interface SpawnSyncReturns {
    status: number | null;
    stdout: string;
    stderr: string;
  }
  export function spawnSync(
    command: string,
    args: string[],
    options: SpawnSyncOptions,
  ): SpawnSyncReturns;
}

declare module "node:crypto" {
  export interface Hash {
    update(data: string, encoding?: string): Hash;
    digest(encoding: "hex"): string;
  }
  export function createHash(algorithm: string): Hash;
}

declare module "node:fs" {
  export function appendFileSync(path: string, data: string): void;
  export function existsSync(path: string): boolean;
  export function readFileSync(path: string, encoding: string): string;
  export function renameSync(oldPath: string, newPath: string): void;
  export function unlinkSync(path: string): void;
  export function writeFileSync(path: string, data: string, encoding: string): void;
}

declare module "node:path" {
  export function join(...parts: string[]): string;
}

declare const process: {
  cwd: () => string;
  pid: number;
  env: Record<string, string | undefined>;
  stderr: { write: (text: string) => void };
};
