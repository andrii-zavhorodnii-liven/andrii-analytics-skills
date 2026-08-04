---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

   Two hunk shapes here need extra care, because a plausible-looking resolution can be silently wrong:

   - **SQL both sides edited.** Two branches adding columns to the same `SELECT` merge cleanly and read fine — while a join one side added has changed the grain. After resolving a `.sqlx` or `.sql` hunk, re-check what one output row is; don't trust that keeping both sides preserved it.
   - **A lockfile or a compiled artifact.** Never hand-merge `uv.lock`. Take one side, then regenerate it (`uv lock`) so it matches the merged `pyproject.toml`.

4. Discover the project's **automated checks** and run them — typically lint and type checks, then tests, then format. Where the repo has a Dataform graph, `dataform compile` belongs first: a conflict resolved into a broken `ref()` or a duplicated declaration fails there and nowhere else. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
