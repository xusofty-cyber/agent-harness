---
name: option-review
description: Use when 2+ viable approaches exist for a task and a choice must be made — e.g. "should I do A or B?", "which approach is better?", "help me choose between these options". Fans out isolated reviewers (security, engineering, reversibility, simplicity, cross-tool), each in a separate subagent, and returns a decision matrix. Also user-invokable as /option-review.
version: 0.1.1
---

# Option Review

Review **unmade decisions**, not finished code. When multiple viable options exist,
each gets examined from five independent angles before the user picks one.

Related skills: `requesting-code-review` reviews completed work (post-decision);
`option-review` reviews candidate approaches (pre-decision). They complement, never overlap.

## When to use (model-invoked)

Trigger automatically when **all** of these hold:

1. You have generated or been given **2 or more viable options** for a decision.
2. The options differ in **approach**, not just parameters
   (e.g. "REST vs gRPC" qualifies; "timeout 30s vs 60s" does not).
3. The user has **not yet chosen**.
4. The decision has **architectural, structural, security, or irreversible impact**
   (e.g. storage/state strategy, library selection, API contract, migration path).
   For routine local choices (naming, loop styles, minor refactorings), choose the
   simpler path directly (YAGNI / Ponytail) without triggering a multi-agent review.

Do **not** trigger for: single-option confirmations, trivial parameter choices,
routine low-impact coding choices, or decisions the user already made.

## Protocol

### 1. Neutralize the options

Rewrite each option as a neutral description: what it does, key mechanics,
known trade-offs. **Strip your own preference** — no "recommended",
no ordering by preference, no loaded adjectives. Number them (A, B, C…).

If a material fact needed for review is unknown and look-up-able
(filesystem, repo, docs), find it yourself first. Do not ask the user
for anything you could look up.

### 2. Fan out reviewers in parallel

Dispatch **one subagent per dimension** (see `references/rubrics.md`),
all in a single parallel batch. Each reviewer receives **only**:

- the neutralized options,
- its own dimension rubric.

Reviewers get **no session history, no other reviewer's output,
no hint of your preference**. Isolation is the point: independent
angles must not anchor on each other.

#### Fallback (single-agent harnesses)

When the host environment does not support subagent dispatch (e.g. single-agent
CLI or missing delegation tools), evaluate the five dimensions sequentially
in your internal reasoning. Strictly isolate each perspective against its rubric
in `references/rubrics.md` without letting conclusions from one angle bias the next.

### 3. Collect verdicts

Each reviewer returns, per option:

- verdict: `✅` (fits) / `⚠️` (concern) / `❌` (rejects)
- one-line rationale (max 30 words)

### 4. Synthesize

Build the decision matrix (options × dimensions). Then:

1. **Matrix first** — the user reads the full picture before your take.
2. **Recommendation** — one option, with the 1–2 decisive reasons.
3. **Dissent** — surface reviewer disagreements explicitly.
   Never average a `❌` away; a single-dimension rejection is a veto
   worth naming, even if you still recommend that option.

### 5. Present and stop

Present matrix → recommendation → dissent. Then **stop and wait**.
Do not start implementing. The choice is the user's.

## User-invoked mode (`/option-review`)

The user may invoke directly with options pasted in, or by pointing
at a decision ("review the approaches for X"). If options are vague,
first neutralize them from the conversation context (step 1), then
run the same protocol from step 2.
