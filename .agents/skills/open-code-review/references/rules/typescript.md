# TypeScript / JavaScript Review Rules

## Correctness & Type Safety

- **Unsound type assertions**: unsafe casting (`as unknown as T` or `x as T`) bypassing runtime validation on external/untrusted input.
- **`any` escape hatches**: introducing `any` into public APIs, export boundaries, or security-sensitive modules.
- **Null / undefined handling**: unchecked property access on nullable types; assumptions that optional fields (`foo?: string`) always exist without checking.
- **Floating promises**: unawaited async calls (`fetch(...)`, `db.query(...)`) without `await` or `.catch()`, which swallow errors or race execution order.
- **Equality gotchas**: loose equality `==` / `!=` with mixed types; `NaN === NaN` (must use `Number.isNaN`).

## Concurrency & Resource Lifecycle

- **Memory leaks**: uncleaned event listeners, intervals (`setInterval`), or WebSocket observers in long-lived services or UI components.
- **State race conditions**: multiple concurrent async requests updating shared state without cancellation tokens (`AbortController`) or sequence guarding.
- **Prototype pollution**: unchecked key iteration merging objects with `__proto__` or `constructor` properties.

## Error Handling

- **Swallowed errors**: empty `catch {}` blocks without logging, metrics, or re-throwing.
- **Non-Error throws**: throwing strings or literals (`throw "failed"`) instead of `new Error(...)`, breaking stack traces and `instanceof Error` checks.

## Do NOT report

- Missing optional return type annotations where TypeScript inference is clear.
- Debates between `type` vs `interface`.
- Import ordering or formatting nits (delegated to linters / formatters).
