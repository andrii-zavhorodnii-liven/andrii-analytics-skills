# Logic Prototype

A tiny interactive terminal app that lets the user drive a state model by hand. Use this when the question is about **logic, state transitions, or sequencing** — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.

## When this is the right shape

- "I'm not sure this ingestion cursor handles a late-arriving batch followed by a replay."
- "Does this backfill state machine cope with a partition being reprocessed twice?"
- "What should the retry / dead-letter policy actually do when the source API rate-limits mid-page?"
- "Does this slowly-changing-dimension model let me represent a record that changes twice in one day?"
- Anything where the user wants to **press keys and watch state change**.

If the question is "what should the output look like" — wrong branch. Use [SHAPE.md](SHAPE.md).

## Process

### 1. State the question

Before writing code, write down what state model and what question you're prototyping. One paragraph, in the prototype's README or a comment at the top of the file. A logic prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, whether the user is watching now or returning to it AFK.

### 2. Pick the language

Use whatever the host project uses — for most of our repos that's Python under `uv`, run with `uv run <path>`. If the project has no obvious runtime (a Dataform-only repo, say), a standalone `uv run --script` file with inline dependencies is the lightest thing that works.

Match the project's existing conventions for tooling — don't add a new package manager or runtime just for the prototype. Don't reach for a notebook: hidden execution order makes a state prototype impossible to trust.

### 3. Isolate the logic in a portable module

Put the actual logic — the bit that's answering the question — behind a small, pure interface that could be lifted out and dropped into the real codebase later. The TUI around it is throwaway; the logic module shouldn't be.

The right shape depends on the question:

- **A pure reducer** — `reduce(state, event) -> state`. Good when events are discrete and state is a single value.
- **A state machine** — explicit states and transitions. Good when "which actions are even legal right now" is part of the question.
- **A small set of pure functions** over a plain data type. Good when there's no implicit current state — just transformations.
- **A class or module with a clear method surface** when the logic genuinely owns ongoing internal state.

Pick whichever shape best fits the question being asked, *not* whichever is easiest to wire to a TUI. Keep it pure: no I/O, no terminal code, no warehouse client, no `print` for control flow. The TUI imports it and calls into it; nothing flows the other direction.

This is what makes the prototype useful past its own lifetime: when the question's been answered, the validated reducer / machine / function set can be lifted into the real module on its own.

### 4. Build the smallest TUI that exposes the state

Build it as a **lightweight TUI** — on every tick, clear the screen (`print("\033[2J\033[H", end="")` or equivalent) and re-render the whole frame. The user should always see one stable view, not an ever-growing scrollback.

Each frame has two parts, in this order:

1. **Current state**, pretty-printed and diff-friendly (one field per line, or formatted JSON). Use **bold** for field names or section headers and **dim** for less important context (timestamps, IDs, derived values). Native ANSI escape codes are fine — `\x1b[1m` bold, `\x1b[2m` dim, `\x1b[0m` reset. No need to pull in a styling library unless one is already in the project.
2. **Keyboard shortcuts**, listed at the bottom: `[b] arrive batch  [l] late event  [r] replay partition  [t] tick clock  [q] quit`. Bold the key, dim the description, or vice-versa — whatever reads cleanly.

Behaviour:

1. **Initialise state** — a single in-memory object/struct. Render the first frame on start.
2. **Read one keystroke (or one line)** at a time, dispatch to a handler that mutates state.
3. **Re-render** the full frame after every action — don't append, replace.
4. **Loop until quit.**

The whole frame should fit on one screen.

### 5. Make it runnable in one command

Add a target to the project's existing task runner (`Makefile`, `justfile`, `pyproject.toml` scripts). The user should run `make <prototype-name>` or `uv run <prototype-name>` — never need to remember a path.

If the host project has no task runner, just put the command at the top of the prototype's README.

### 6. Hand it over

Give the user the run command. They'll drive it themselves; the interesting moments are when they say "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the _idea_, which is the whole point. If they want new actions added, add them. Prototypes evolve.

### 7. Capture the answer and the prototype

Once the prototype has answered its question, capture the answer, then capture the prototype the way the [SKILL](SKILL.md) describes. The logic-specific mapping: the validated reducer / machine / function set lifts into the real module (the decision, absorbed); the TUI shell rides along to the throwaway branch that keeps the prototype as a primary source.

## Anti-patterns

- **Don't add tests.** A prototype that needs tests is no longer a prototype.
- **Don't wire it to the warehouse.** Use an in-memory store with a few hand-written events. A logic prototype that has to query BigQuery to take a step is slow, costly, and no longer answering a logic question.
- **Don't generalise.** No "what if we wanted to support X later." The prototype answers one question.
- **Don't blur the logic and the TUI together.** If the reducer / state machine references `print`, prompts, or terminal escape codes, it's no longer portable. Keep the TUI as a thin shell over a pure module.
- **Don't ship the TUI shell into production.** The shell is optimised for being driven by hand from a terminal. The logic module behind it is the bit worth keeping.
