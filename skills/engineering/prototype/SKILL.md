---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a logic or state model feels right, or to see the actual shape of an output table, metric, or feature set before committing to it.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a tiny interactive app that pushes the model through cases that are hard to reason about on paper — a terminal TUI by default, or a single shareable HTML file when a non-developer needs to drive it.
- **"What should the output actually look like?"** → [SHAPE.md](SHAPE.md). Produce a small, real, concrete result set — a query result, a metric over a few days, a feature table's first twenty rows — for the user to react to.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default by what's being prototyped: a scheduler, a retry policy, a state machine, an ingestion cursor → logic; a table, a metric, a report, a feature set → shape. State the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype close to where it will actually be used (next to the module, Dataform definition, or job it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production. Never put a prototype where the Dataform graph or a scheduled job will pick it up.
2. **One command to run.** Whatever the project's existing task runner supports — `uv run <path>`, a `Makefile` target, `just <name>`. The user must be able to start it without thinking.
3. **Read-only against real data; no writes to real destinations.** A prototype may read production tables. It must never write to one. If the question genuinely involves a write, target an explicitly scratch dataset with a clearly temporary name (`scratch_<user>__proto_<name>`) and give it an expiry.
4. **No persistence in the logic branch by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on.
5. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
6. **Surface the state.** After every action (logic) or on every run (shape), print the full relevant state or result so the user can see exactly what they're reacting to.
7. **Cost-bound anything that touches BigQuery.** Dry-run first, report the bytes, and keep a partition filter on. A prototype that quietly scans a terabyte has failed regardless of what it proved.
8. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too — the verdict and the question it settled — in the issue or a commit. The main branch keeps only the validated decision.
