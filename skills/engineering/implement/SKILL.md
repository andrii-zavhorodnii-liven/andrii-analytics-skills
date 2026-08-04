---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run the fast checks regularly and the slow ones once at the end:

- **Regularly** — lint and type checks (`uv run ruff check`, `uv run mypy` or whatever the repo uses), plus the single test file you're working in. For warehouse changes, `dataform compile` after every model edit; a graph that doesn't compile is the cheapest failure to catch and the most annoying to discover late.
- **Once at the end** — the full test suite, and `dataform run --dry-run` (or the repo's equivalent) so you see the full set of actions and assertions the change implies before anything executes for real.

Never run a pipeline against a production destination to check your work. Use a dev/scratch dataset or the repo's dev workspace. If a ticket can only be verified against production, stop and say so rather than doing it quietly.

Once done, use /code-review to review the work.

Commit your work to the current branch.
