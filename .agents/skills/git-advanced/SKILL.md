---
name: git-advanced
description: Use for advanced Git operations: resolving merge conflicts collaboratively, cherry-pick and revert workflows, git bisect bug hunting, reflog disaster recovery, or as a Git command reference. Low-frequency operations — not for everyday commit/push workflows (see git-workflow.md rules instead).
version: 0.1.0
---

# Git Advanced Operations

On-demand reference for Git operations beyond the everyday workflow.
For authorization rules, branch strategy, and commit discipline,
follow `.agents/rules/git-workflow.md` instead.

---

## 1. Conflict Resolution Protocol（冲突协同解决）

**Core principle (from git-workflow.md): every conflict must be resolved
collaboratively with the human. AI never auto-picks one side.**

```bash
git status                    # "both modified" = conflicted files
git diff <conflict-file>      # inspect the conflict hunks
# Edit and resolve manually, then:
git add <resolved-file>
git merge --continue          # or git rebase --continue / git cherry-pick --continue
# Abort: git merge --abort / git rebase --abort / git cherry-pick --abort
# Note: rebase commands are for feature branches only — never on protected branches.
```

### Collaborative decision flow

1. Report to the human: conflicted file list + what each side means per hunk;
2. Independent features on both sides → suggest keeping both;
3. Same line changed both sides → merge semantics (not a binary pick);
4. When unsure → ask the human, never guess.

### Special cases

- **Binary conflicts** (images, archives): cannot text-merge. Ask the human
  which side to keep (`git checkout --ours/--theirs` only on explicit instruction);
- **stash pop conflicts**: `git add` after resolving, no commit needed,
  then `git stash drop` manually;

---

## 2. Cherry-pick & Revert

**Safety rule (from git-workflow.md): never cherry-pick directly onto a
protected branch and push — work on a temp branch and follow the normal flow.**

```bash
git cherry-pick -x <commit-hash>    # -x records source in message for traceability
git cherry-pick A..B                # batch (excludes A, includes B)
git cherry-pick -n <hash>           # --no-commit: stage only, combine multiple into one commit
# On conflict: resolve → git add → git cherry-pick --continue (or --abort)
```

**Decision rule: pushed → `revert`; not pushed → `reset`; single file → `restore --source`.**

| Scenario | Command | Why |
|---|---|---|
| Revert a pushed bad commit | `git revert <hash>` | Doesn't rewrite history, safe |
| Revert a merge commit | `git revert -m 1 <hash>` | `-m 1` keeps the mainline parent |
| Undo a local unpushed commit | `git reset --soft HEAD~1` | Changes stay staged |
| Revert a single file | `git restore --source=<commit> -- <path>` | Precise blast radius |
| Batch revert | `git revert -n A..B && git commit` | Single revert commit |

### ⚠️ Revert-then-merge trap

```text
Scenario: reverted a feature branch's merge → merge the same branch again → changes "vanish"
Cause: git considers those commits already in history (revert ≠ never merged)
Fix: revert the revert commit first, then merge
```

---

## 3. Git Bisect — find the bug-introducing commit

```bash
git bisect start
git bisect bad                    # current HEAD is broken
git bisect good <known-good>      # mark a known-good commit
# Git checks out midpoints; test each and mark good/bad until first bad commit found
git bisect reset                  # finish, return to original branch
```

**Automation**: `git bisect run ./test.sh` — script returns 0=good, non-0=bad, 125=skip.

```bash
git bisect start -- src/          # narrow scope to a path
git bisect skip                   # current commit can't build, skip it
git bisect log                    # review all markings
```

Tip: in automation scripts, return 125 (not 1) when the build fails, to avoid false bad markings.

---

## 4. Git Reflog — disaster recovery

Reflog records every HEAD/branch movement (commit, reset, rebase, checkout…),
even for commits no longer on any branch:

```bash
git reflog                        # operation history
git reflog --date=relative        # with relative timestamps
git reset --hard HEAD@{1}         # back to pre-last-operation state (⚠️ needs human confirmation)
git branch recovery <hash>        # resurrect a deleted branch tip
git show HEAD@{2.hours.ago}       # time expressions
```

| Scenario | Recovery |
|---|---|
| Accidental `git reset --hard` | Find pre-reset hash in reflog → `git reset --hard <hash>` |
| Deleted branch | `git reflog --all \| grep <branch>` → `git branch <name> <hash>` |
| Botched rebase | Find pre-`rebase (start)` state → `git reset --hard HEAD@{N}` |
| Want pre-`amend` commit | `HEAD@{1}` is the pre-amend version |

**Limits**: local-only (never pushed); expires (default 90 days via `gc.reflogExpire`);
fresh clones have no reflog history.

---

## 5. Command Quick Reference

```bash
git fetch origin                                  # sync remote refs (read-only)
git log HEAD..origin/main --oneline               # is remote ahead? (output = yes)
git branch --show-current                         # current branch (check before commit)
git status --short                                # workspace snapshot
git diff HEAD --stat                              # change overview
git stash push -m "WIP: xxx"                      # stash work
git stash pop                                     # restore stash
git restore --staged <file>                       # unstage (keeps changes)
```
