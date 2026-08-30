---
name: ask-andrii
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
disable-model-invocation: true
---

# Ask Andrii

You don't remember every skill, so ask.

A **flow** is a path through the skills. Most paths run along one **main flow**, and two **on-ramps** merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath.

## The main flow: idea → ship

The route most work travels. You have an idea and want it built.

1. **`/grill-with-docs`** — sharpen the idea by interview. Start here when you **have a codebase**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No codebase? Use `/grill-me` — see Standalone. Both run the same `/grilling` primitive; `grill-with-docs` is the one that leaves a paper trail.)
2. **Branch — can you settle every question in conversation?** If a question needs a runnable answer — how the logic sequences, or what the output table actually looks like — detour through a prototype, bridged by **`/handoff`** in both directions (see Crossing sessions):
   - **`/handoff`** out, then open a fresh session against that file,
   - **`/prototype`** to answer the question with throwaway code,
   - **`/handoff`** back what you learned, and reference it from the original idea thread.
3. **Branch — is this a multi-session build?**
   - **Yes** → **`/to-spec`** (turn the thread into a spec), then **`/to-tickets`** to split it into tracer-bullet tickets, each declaring its **blocking edges**. On GitHub the edges become native issue dependencies, so any ticket whose blockers are done can be grabbed — kick off **`/implement`** per ticket, **clearing context between each one**. On a local tracker that's one file per ticket under `.scratch/<feature>/issues/`, worked blockers-first by hand.
   - **No** → **`/implement`** right here, in the same context window.

   Either way, **`/implement`** builds each issue by driving **`/tdd`** internally — one red-green slice at a time — then closes out by running **`/code-review`**, a two-axis review (Standards + Spec) of the diff, before committing. Reach for **`/tdd`** on its own when you just want to build a concrete behaviour test-first without a full spec, and **`/code-review`** on its own whenever you want to review a branch or PR against a fixed point — code, or a skill's own markdown, which it judges against **`/writing-for-agents`**.

### Context hygiene

Keep steps 1–3 in **one unbroken context window** — don't compact or clear until after `/to-tickets` — so the grilling, spec, and tickets all build on the same thinking. Each `/implement` then starts fresh, working from the ticket.

The limit on this is the **smart zone**: the window (~120k tokens on current models) within which the model still reasons sharply. If a session approaches it before `/to-tickets`, don't push on degraded — `/handoff` and continue in a fresh thread.

## On-ramps

A starting situation that generates work, then merges onto the main flow.

- **A stakeholder ask lands and someone wants an estimate** → **`/feasibility-check`**. Before anyone promises anything, it traces the real system the change would plug into, tags each piece ✓ have / ✗ build / ⛔ can't / ⚠ unknown, and returns one verdict with the single check to run first. Its verdict is a route: **feasible** → `/grill-with-docs` and the main flow; **too big or foggy for one session** → `/wayfinder`, seeded by its ⚠ rows; **check first** → `/research-data` or `/research-docs`. It has a light "smell test" mode for small asks — reach for it any time you're about to say "sure, about a week."

- **Bugs and requests piling up** → **`/triage`**. It moves issues through triage roles and produces agent-ready issues, which **`/implement`** later picks up.

  Triage is only for issues **you didn't create** — bug reports, incoming feature requests, anything that arrives raw. Tickets that `/to-tickets` produced are already agent-ready, so **don't triage them**.

- **Something's broken** → **`/diagnosing-bugs`**. For the hard ones: the bug that resists a first glance, the intermittent flake, the regression that crept in between two known-good states. It refuses to theorise until it has a **tight feedback loop** — one command that already goes red on *this* bug — then fixes with a regression test. Its post-mortem hands off to **`/improve-codebase-architecture`** when the real finding is that there's no good seam to lock the bug down.

- **A huge, foggy effort — a new platform area, a warehouse re-grain, a migration off a legacy pipeline, too big for one session** → **`/wayfinder`**, the most cognitively demanding flow here. When the way from here to the destination isn't visible yet, it charts a **shared map** of **decision tickets** on the issue tracker and resolves them one at a time — producing **decisions, not deliverables** — until the fog is pushed back and the way is clear. Where **`/grill-with-docs`** sharpens an idea you can hold in one session, wayfinder is for the idea you can't — and it's slower and denser, so save it for exactly that, never a well-scoped feature.

  When the map clears, **it hands off, it doesn't build**: merge onto the main flow at **`/to-spec`**, which collapses the map's linked decisions into a buildable plan, then `/to-tickets` and `/implement` as usual. Looping the map straight into `/implement` skips that collapse and throws the linked detail away — go straight to `/implement` only when the effort turned out genuinely small.

## Codebase health

Not feature work — upkeep.

- **`/improve-codebase-architecture`** — run whenever you have a spare moment to keep the codebase good for agents to operate in. It surfaces **deepening opportunities**; picking one _generates an idea_ you can take into the main flow at `/grill-with-docs`. It's the survey that finds the candidates; **`/codebase-design`** (below) is the bench you design the chosen one on.

## Vocabulary underneath

Two model-invoked references that run *beneath* the other skills — each the single source of truth for its vocabulary. Reach for them directly when the **words**, not the process, are the problem; or let the skills above pull them in.

- **`/domain-modeling`** — sharpen the project's *domain* language: challenge a fuzzy term, resolve an overloaded word ("account" doing three jobs), record a hard-to-reverse decision as an ADR. It's the active discipline `/grill-with-docs` drives to keep `CONTEXT.md` a clean glossary.
- **`/codebase-design`** — the deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality) for designing a module's *shape*: a lot of behaviour behind a small interface at a clean seam. `/tdd` and `/improve-codebase-architecture` both speak it.

## Crossing sessions

At every **phase boundary** — grilling done, implementation done, QA done — you pick one of five moves:

- **Continue** — stay put. Costs nothing, loses nothing.
- **`/clear`** (built-in) — empty the window, when nothing here matters to what's next.
- **`/handoff`** — writes a portable markdown file. Narrow: only for a **new harness**, a **new directory**, a **colleague**, or forking a side task **mid-phase** (e.g. into a `/prototype` session). What it buys is portability.
- **Subagent** — send a tightly-scoped task to its own window and get a report back.
- **`/compact`** (built-in) — compresses this context and seeds a fresh session with it. The **default**, at the bottom of the tree rather than the first reach.

Read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) for the ordered tree: the five questions, the reasoning behind each branch, and why the primary-source cost makes **Continue** the one to rule out first. Make the decision **at** a boundary; mid-phase, continue or split the rest into subagents.

## Standalone

Off the main flow entirely.

- **`/grill-me`** — the same relentless interview as `/grill-with-docs`, but for when you have **no codebase**. Stateless: it saves nothing locally, builds no `CONTEXT.md`. Reach for it to sharpen any plan or design that doesn't live in a repo.
- **`/prototype`** — a small, throwaway artifact that answers one design question. Two shapes: **logic**, an interactive app you drive by hand when the question is about sequencing or state (a terminal TUI, or a shareable HTML file for non-developers), and **shape**, a small real result set when the question is what the output should look like. Throwaway from day one — keep the answer, delete the code. It's the detour in step 2 of the main flow, but reach for it any time a design question is hard to settle on paper. Twenty real rows end an argument prose can circle for an hour.
- **The three research skills** — delegate reading and profiling legwork to a **background agent**, and keep working while it runs. Each leaves a findings file to take *into* the main flow at `/grill-with-docs`; research feeds the thinking, it doesn't replace it. Pick by what kind of question you have:
  - **`/research-docs`** — a fact about a **tool**. Does Dataform support this? What's the quota? What does the SDK actually do? Answered from primary sources, pinned to a version.
  - **`/research-data`** — a fact about **our data**. What's the grain? How null is this column? Do these two tables join? Answered in numbers, with the queries attached. Reach for this one first when a plan rests on an assumption nobody has checked — it's the cheapest way to find out you were about to build the wrong thing.
  - **`/research-web`** — **which approach** to take. Model family, orchestration option, prior art. Ends in one recommendation for our constraints, not a survey.
- **`/resolving-merge-conflicts`** — resolve an in-progress git merge or rebase conflict from primary sources (commits, PRs, original issues) rather than guessing. Model-invoked when a merge is already underway; reach for it by name when you're staring at conflict markers.
- **`/consolidating-work`** — the housekeeping pass after a run of parallel tickets, when worktrees and branches have piled up. Two axes, in one fixed order: a **worktree** holds state no commit graph can see (uncommitted edits, untracked files, a stash, a detached `HEAD`), so those get secured first; only then are branches reaped by **containment** — every commit already sitting in a descendant, which makes deletion lossless. `--merged main` is the wrong test here: it reaps nothing while a whole stack sits unlanded. Deletion always waits on your yes. It never folds tips together — several features in one PR stays your call.
- **`/cloud-run-to-repo`** — adopt a Cloud Run service that was deployed ad-hoc (console, lost working copy) into a proper git repo: recover the exact deployed source, set up uv, and write a `deploy.sh` that mirrors every live runtime flag. It never redeploys — that stays your call.
- **`/present-analysis`** — the delivery step when an analysis is *finished*: turn its scripts, result tables, and charts into a layered stakeholder report — takeaways anchored on the stakeholder question, every takeaway backed by a chart, recommendations in plain business language. It communicates existing findings; it never computes new ones — the analysis itself comes from the main flow or `/research-data`/`/prototype`.
- **`/shap-report`** — one HTML page of SHAP share % by feature × target for the repo's *published* model roster (`artifacts/roster/*/model.cbm`), computed on one hash-verified shared holdout sample. Reach for it after a retrain or feature-list change to see where the importance mass sits and moved; it never retrains.
- **`/retrain-proof`** — the persistence discipline for any script that trains a model, sweep cells included: scored evaluation rows, the model file, and the population definition saved next to the metrics, so follow-up metrics never force a refit. Model-invoked before the first fit call; scratchpad probes follow the same rule.
- **`/pr-merged`** — the tidy-up after a PR lands: fetch with prune, return to the default branch and pull the merge, delete every local branch whose remote is gone (worktrees included). It never touches remote branches or uncommitted work. For one merged PR; a pile-up of parallel worktrees is `/consolidating-work`'s job.
- **`/teach`** — learn a concept over multiple sessions, using the current directory as a stateful workspace.
- **`/wait-what`** — when the agent's last message didn't land, stop and have it re-pitched: context first, plain language, the project's own terms.
- **`/writing-for-agents`** — reference for writing any document an agent consumes: skills, `AGENTS.md`/`CLAUDE.md`, docs reached by pointers.

## Conventions underneath

No per-repo setup step. The skills that touch an issue tracker all follow one convention: **GitHub Issues** via the `gh` CLI when the repo has a git remote, local markdown under `.scratch/` when it doesn't, and triage labels equal to the canonical role names verbatim.
