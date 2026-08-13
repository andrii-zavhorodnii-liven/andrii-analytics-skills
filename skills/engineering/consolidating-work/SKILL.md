---
name: consolidating-work
description: Pull a sprawl of parallel worktrees and branches back to a reviewable state — secure what's live, reap what's spent, one PR per tip.
disable-model-invocation: true
---

Parallel ticket work leaves two kinds of sprawl, and they answer to different tests.

A **worktree** holds state no commit graph can see: uncommitted edits, untracked files, a stash, a detached `HEAD` with no branch at all. A **branch** is committed history, so it can be judged by **containment** — every one of its commits already sitting in a descendant, which makes deleting it lossless. Only the **tips**, the branches no descendant contains, carry work nobody else holds.

Containment is blind to everything in the first paragraph. A branch can be provably spent while its worktree holds an afternoon of uncommitted work, so securing the worktrees is what earns the right to reap the branches. The passes run in that order, always.

1. **Inventory both axes.** Walk `git worktree list --porcelain` for every worktree, its branch (or `detached`), and its `git status --porcelain` count; walk `git branch` for every branch, including those with no worktree at all. Clear stale metadata with `git worktree prune` — a worktree whose directory was deleted by hand still occupies the list. Run `git stash list` once for the whole repo, not per worktree: `refs/stash` is shared, so every worktree reports the same entries, and an entry's `WIP on <branch>` line is the only clue which one it came from. Done when every path on disk and every name in `git branch` appears exactly once, and every branch is either matched to a worktree or named as having none.

2. **Secure everything live.** Every uncommitted edit, untracked file and stash entry is work no later step can see, so it gets resolved now — each kind has its own move:

   - **Uncommitted edits and untracked files.** Commit them where they stand (`git add -A && git commit`) on whatever branch the worktree already has. That commit puts the branch strictly ahead of everything that held it, so step 3 labels it a **tip** instead of *contained* — which is the right answer, and is the whole reason this pass runs first. If the changes are a mess the user should look at, hand over the file list instead and hold that worktree back from the rest of the run.
   - **Stash entries.** Restore each one in the worktree its `WIP on <branch>` line points at, then commit it like any other edit — or leave the entry and name it as held back. Never `git stash drop`: the point of this step is that nothing is thrown away here.
   - **A detached `HEAD` carrying commits.** `git switch -c <name>` at that `HEAD` before anything else touches the worktree. Removing the worktree first leaves the commits unreachable and reachable only by `git reflog`.

   Done when every surviving worktree reports a clean `git status`, the stash list is empty or every remaining entry is named, and anything unresolved is named as deliberately held back.

3. **Map containment.** For every branch, test it against every other: `git merge-base --is-ancestor <branch> <other>` succeeds when `<other>` already holds every commit of `<branch>`. This is the test that matters — `git branch --merged main` reaps nothing while a whole stack sits unlanded, and reads as "nothing to clean up" when most of the stack is spent. Containment only counts when `<other>` is strictly ahead: two names on the same commit are each an ancestor of the other, so labelling both *contained* would delete the work outright — compare `git rev-parse` on the pair, keep one name, and let it be the descendant that holds the rest. Done when every branch is labelled *contained* (naming the descendant that holds it) or a **tip**.

4. **Show the plan and get a yes.** The branches to reap, each with the descendant that makes it safe; the tips to keep, each with its commit count ahead of `main`; anything held back by step 2. Deleting a branch is the one move here the working tree cannot give back, so it waits on the user's word. Done when the user has said yes to a named list of branches — approval of something adjacent, a partial answer, or silence is not a yes, and the list you act on in step 5 is the one they saw.

5. **Reap the spent.** Where a branch has a worktree, `git worktree remove <path>` first — a branch checked out somewhere cannot be deleted. Then `git branch -D <branch>` either way. `-D` is warranted only because step 3 proved a descendant holds the commits; `-d` measures containment against the branch's upstream, or against wherever `HEAD` sits when it has no upstream — neither is the descendant step 3 found, so it refuses a branch that never reached `main`. Done when every name on step 4's list is gone from both `git worktree list` and `git branch`, and nothing off that list moved.

6. **Settle each tip.** Per tip, the user picks: open a PR to `main`, or abandon the work and delete the branch. Run the repo's checks before a PR goes up — a tip that sat while `main` moved is where a stale `ref()` or an out-of-date `uv.lock` surfaces. Tips grown from one stack share the commits beneath them, so their PRs overlap: land them in stack order, rebasing the rest onto `main` as each one lands. Done when `git worktree list` holds only the main checkout and whatever step 2 held back, and `git branch` holds `main` plus exactly the surviving tips, each with an open PR in `gh pr list` — anything else still standing gets named, with why. On a repo with no git remote there is nothing to open a PR against: the choice per tip is keep or abandon, and a kept tip is settled once the closing summary names it and its commit count ahead of `main`.
