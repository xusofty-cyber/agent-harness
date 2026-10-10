# Session State & Checkpoint Log (SESSION_STATE.md)

> **Role & Purpose**: This document records execution checkpoints, completed modifications, verification evidence, and pending items for the current session, ensuring seamless handoffs across sessions and AI tools. Update at meaningful task boundaries and prune obsolete entries.

---

## 1. Current Task Overview

- **Associated Task / Issue**: <Task identifier, feature name, or ticket ID>
- **Session Goal**: <Specific objectives and deliverables for this session>

---

## 2. Root Cause Analysis / Technical Design

1. **Core Mechanism**: <Root cause explanation or high-level technical design>
2. **Strategy**: <Smallest working change and regression-prevention strategy>

---

## 3. Code Modifications & Deliverables

- **Modified Files & Key Changes**:
  - `<file_path_1>`: <Summary of changes>
  - `<file_path_2>`: <Summary of changes>

---

## 4. Verification Evidence Gate

1. **Build / Test Execution**:
   - Command: `<e.g., npm test / pytest / make>`
   - Result: `Exit code 0, all tests passing`
2. **Reproducible Proof**:
   - <Include actual test output, log excerpts, or diff validation>

---

## 5. Current Breakpoint & Next Steps

1. **Current Breakpoint**: <Exact stopping point and state when pausing execution>
2. **Next Steps**:
   - [ ] Step 1: <Next action item>
   - [ ] Step 2: <Next action item>
3. **Open Risks / Decisions Needed**:
   - <Unresolved questions, blockers, or decisions requiring user confirmation>
