# C/C++ Review Rules

## Correctness & Memory Safety

- **Uninitialized memory**: uninitialized variables, struct members, or class fields before read.
- **Buffer bounds**: out-of-bounds array/pointer indexing; use of unbounded C-string functions (`strcpy`, `sprintf`, `strcat`) instead of bounded alternatives or `std::string` / `std::string_view`.
- **Dangling pointers / references**: returning a reference or pointer to a stack-local or temporary variable; use-after-free or use-after-move.
- **Ownership & RAII**: raw `new` / `delete` or raw owning pointers instead of `std::unique_ptr` / `std::shared_ptr` / RAII wrappers.
- **Polymorphism**: base class with virtual functions lacking a `virtual` destructor (risk of undefined behavior on `delete`).
- **Object slicing**: passing derived objects by value to a base class parameter.

## Concurrency & Resource Safety

- **Data races**: concurrent read/write to shared mutable state without `std::mutex`, `std::atomic`, or lock guards (`std::lock_guard`, `std::scoped_lock`, `std::unique_lock`).
- **Deadlocks**: nested locks acquired in inconsistent order across threads.
- **Resource leaks**: raw OS handles (file descriptors, sockets, POSIX threads, Windows handles) not wrapped in RAII containers.
- **Null dereference**: unchecked pointer dereference; unchecked `.value()` on `std::optional` that may be empty.

## Error Handling

- Ignored return values on functions with `[[nodiscard]]` or error-bearing system calls (`close`, `write`, `malloc`).
- Catching exceptions by value (`catch (std::exception e)`) causing slicing instead of `catch (const std::exception& e)`.

## Do NOT report

- Missing `const`, `constexpr`, or `noexcept` unless it prevents a verified bug or causes an ABI mismatch.
- Style preferences (brace placement, variable naming conventions, pointer `*` alignment).
- Micro-optimizations (`std::move` on trivial types, pass-by-value for small structs) without hot-path profiling evidence.
