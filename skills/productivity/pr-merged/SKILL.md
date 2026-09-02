---
name: pr-merged
description: After a PR merges, sync the default branch and delete the merged local branches.
disable-model-invocation: true
---

The user just merged a PR (and typically deleted its remote branch). Bring the local
repo back to a clean baseline while every other session keeps working.

A worktree is **live** when another session may be using it: a parallel agent, a Codex
checkout, a scratchpad the user still has open. A live worktree stays exactly as it is;
the step prints it as **HELD** with a reason and moves on. This worktree is **idle** only
when `git status --porcelain` prints nothing **and** `HEAD` still equals the value
recorded in step 1 — a clean tree whose `HEAD` moved is live. Every other worktree is
live by definition: a clean tree says nothing about the session sitting in it.

1. **Record, then prune.** Capture the state the later steps compare against, then
   prune so a just-deleted remote branch shows as `[gone]`:

   ```bash
   start=$(git rev-parse HEAD)
   default=$(git symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null | sed 's|^origin/||')
   default=${default:-main}
   git fetch --prune
   ```

   Done when `git branch -v` lists the merged branch as `[gone]`.

2. **Sync `$default` without disturbing anyone.** The ref moves; a working tree moves
   only when idle.

   - On `$default` and idle: `git pull --ff-only`.
   - On `$default` and live: print HELD. Git refuses to fetch into a checked-out
     branch, so the ref waits for the user.
   - On any other branch: `git fetch . origin/$default:$default` fast-forwards the ref
     with no working-tree effect and refuses anything but a fast-forward. Then
     `git checkout $default` if this worktree is idle; if live, stay where you are and
     print HELD.

   Done when `git rev-parse $default` equals `git rev-parse origin/$default`, or the
   HELD line explains why it does not.

3. **Delete every `[gone]` branch whose commits are contained in `$default`:**

   ```bash
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ -n "$worktree" ]; then
       echo "HELD $branch — checked out in worktree $worktree"; continue
     fi
     if git merge-base --is-ancestor "$branch" "$default"; then
       git branch -D "$branch"
     else
       echo "HELD $branch — not contained in $default"
     fi
   done
   ```

   Two gates carry the safety. A branch checked out in any worktree is HELD: removing
   the worktree is the user's call, and `git worktree remove <path>` is the one command
   they need. `--is-ancestor` proves `$default` holds the commits before `-D` drops the
   name; `[gone]` alone only says the remote was deleted. A squash or rebase merge fails the
   ancestor test even though its content landed, so it surfaces HELD: run
   `git cherry -v $default $branch`, and a branch showing `-` on every commit is already
   upstream and safe for the user to delete by hand.

   Done when every `[gone]` branch is either deleted or printed as HELD.

4. **Report**: what `$default` gained, which branches were deleted, and each HELD line
   with its reason. Nothing `[gone]`: say so plainly.

Scope: local branches whose remote is gone and whose commits live on in `$default`.
Remote branches, uncommitted work, and every worktree stay exactly as they are.
