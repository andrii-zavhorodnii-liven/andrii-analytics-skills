---
name: pr-merged
description: After a PR merges, sync the default branch and delete the merged local branches.
disable-model-invocation: true
---

The user just merged a PR (and typically deleted its remote branch). Bring the local
repo back to a clean baseline:

1. **Prune first**: `git fetch --prune` — without it a just-deleted remote branch does
   not yet show as `[gone]` locally.
2. **Return to the default branch and pull the merge**: detect it with
   `git symbolic-ref refs/remotes/origin/HEAD --short` (strip the `origin/` prefix;
   fall back to `main`), then `git checkout <default> && git pull`. If uncommitted
   changes block the checkout or the pull, leave them as they are (no stash, no
   discard), note what blocked it for the report, and go on to step 3 — branch
   cleanup does not need the pull.
3. **Delete every local branch marked `[gone]`**, removing an associated worktree
   first when one exists. A plain `git worktree remove` refuses a worktree with
   uncommitted work; that branch is skipped and named in the report:

   ```bash
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ -n "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       git worktree remove "$worktree" || { echo "skipped $branch: $worktree has uncommitted work"; continue; }
     fi
     git branch -D "$branch"
   done
   ```

4. **Report** in one or two sentences: what the default branch pulled in, and which
   branches/worktrees were deleted, and anything blocked or skipped with its reason.
   If nothing was `[gone]`, say so plainly.

Scope guard: this skill only deletes local branches whose remote is gone. It never
deletes remote branches, never force-pushes, and never touches uncommitted work.
