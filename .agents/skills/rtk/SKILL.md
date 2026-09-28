---
name: rtk
description: "Runtime Toolkit (Run-to-Kill) command execution filter. Truncates long terminal outputs, filters noisy test/build logs, captures failures to local tee log files, and prevents context blowout during command execution."
license: MIT
---

# RTK: Runtime Toolkit & Output Defense

Execution outputs (verbose compiler logs, long stack traces, unformatted git statuses) constitute the largest dynamic input token source (83%-95% of API costs). RTK intercepts and shapes command execution.

## Execution Rules

1. **Filtered CLI Commands**:
   - Never run raw, unfiltered test/build commands.
   - Use quiet or terse flags:
     - Python: `pytest -q --tb=short`
     - Node: `npm test -- --reporter=dot`
     - C/C++: `ctest --output-on-failure`
     - Git: `git status -s` instead of full status.
2. **Output Redirection & Teeing**:
   - When a command generates extensive output, redirect to a local scratch file:
     ```bash
     npm run build > scratch/build.log 2>&1 || tail -n 25 scratch/build.log
     ```
   - Feed only the critical error slice back into the conversation context.
3. **Hang Prevention**:
   - Long-running commands must be bounded by timeouts or managed as background tasks rather than blocking indefinitely.
