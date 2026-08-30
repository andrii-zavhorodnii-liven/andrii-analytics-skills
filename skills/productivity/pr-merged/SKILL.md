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
   fall back to `main`), then `git checkout <default> && git pull`. If the working
   tree has uncommitted changes that block the checkout, stop and tell the user —
   never stash or discard on their behalf.
3. **Delete every local branch marked `[gone]`**, removing an associated worktree
   first when one exists:

   ```bash
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ -n "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       git worktree remove --force "$worktree"
     fi
     git branch -D "$branch"
   done
   ```

4. **Report** in one or two sentences: what the default branch pulled in, and which
   branches/worktrees were deleted. If nothing was `[gone]`, say so plainly.

Scope guard: this skill only deletes local branches whose remote is gone. It never
deletes remote branches, never force-pushes, and never touches uncommitted work.
