---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

Issue tracker convention: **GitHub Issues** via the `gh` CLI when the repo has a git remote; local markdown under `.scratch/<feature>/issues/` when it doesn't.

The goal is the entire spec implemented on a single **integration branch**, with every ticket closed.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets: relevant codebase files, the Dataform graph around the models being touched, or external documentation. Ensure the exploration subagent can save files: it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch. If the user asks for a PR, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main can't open one), referencing the spec and tickets.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - calls the Skill tool with "tdd" to build the ticket;
   - runs the repo's fast checks (lint, type checks, the test file it touched, `dataform compile` after a model edit), and never runs a pipeline against a production destination: a dev dataset or the repo's dev workspace only;
   - merges the integration branch tip into its own branch before reporting done.

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**. Two tickets can each compile alone and break the graph together (a renamed model one side still `ref()`s), so the merger runs `dataform compile` and the test suite on the merged result before reporting.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with "code-review" on the integration branch. Fix all issues raised by the code review in a single **implementer subagent**.

8. Close each ticket (`gh issue close <n> --comment "..."`, or `Status: done` in the `.scratch/` file) naming the integration branch and commit, which acceptance criteria are covered, and anything deliberately left out. Don't wait for a PR to merge: committed and verified is done. If a draft PR exists, mark it ready for review. Report the integration branch.

9. Clean up all **implementer subagent** worktrees.
