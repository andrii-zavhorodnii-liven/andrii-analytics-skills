# Shape Prototype

A small, real, concrete result the user can point at and say "no, not like that". Use this when the question is about **the shape of an output** — a table's columns and grain, a metric's definition, a feature set, a report's layout — the kind of thing that sounds agreed in prose and turns out not to be the moment anyone sees actual rows.

Prose loses this argument. Twenty real rows win it.

## When this is the right shape

- "What columns should this mart table have, and what's its grain?"
- "Is 'active customer' the definition we mean? Show me the number three ways."
- "What does this feature table look like for a single entity across time?"
- "Should this be one wide table or a fact plus a dimension?"
- "Does this metric move the way we expect over the last 30 days?"

If the question is "does this logic handle the case where X then Y" — wrong branch. Use [LOGIC.md](LOGIC.md).

## Process

### 1. State the question

Before writing anything, write down what output you're prototyping and what question it settles. One paragraph, at the top of the file. A prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, whether the user is watching now or returning to it AFK.

### 2. Bound it hard

Real data, small slice. Pick one:

- A single date partition, or a handful of recent days
- A single entity followed across time — one customer, one account, one campaign
- `TABLESAMPLE SYSTEM (1 PERCENT)` where a random slice is representative enough

Dry-run before you run (`bq query --dry_run --use_legacy_sql=false`) and say what it costs. If the honest slice is too expensive to be a prototype, that's a finding — report it instead of running it anyway.

### 3. Write it as plain SQL or a plain script

Whichever the real thing will be:

- **Headed for the warehouse** → a plain `.sql` file, run with `bq query`. Not a `.sqlx` file, not in the `definitions/` tree — a prototype must not enter the Dataform graph. Keep it flat and readable: CTEs in the order a human reads them, no macros, no `ref()`.
- **Headed for a Python job or a Vertex AI training set** → a plain `.py` script run with `uv run`. Not a notebook — a notebook's output state can't be reviewed in a diff and can't be re-run to the same result.

Either way: one file, no config, no parameters beyond a date at the top.

### 4. Print the result so it can be argued with

The output is the artifact. Make it readable at a glance:

1. **The grain, asserted out loud.** `rows: 4182 / distinct order_id: 4182 → grain is one row per order`. If those two numbers differ, that *is* the finding — lead with it.
2. **The columns**, with types, in the order the real table would have them.
3. **A handful of rows** — ten to twenty, as a fixed-width table. Enough to see the texture, few enough to read.
4. **Anything alarming**: null counts on columns that shouldn't have them, a suspiciously round number, a value out of range.

For a metric question, show the metric **more than one way** — two or three candidate definitions side by side over the same window. The gap between them is the conversation.

### 5. Make it runnable in one command

Add it to whatever task runner the project already has (`Makefile`, `justfile`, `pyproject.toml` scripts). The user should run one command, never remember a path. If there's no task runner, put the command on line one of the file as a comment.

### 6. Hand it over

Give the user the command and the output. The interesting moments are "that column shouldn't be there", "that's not the grain I meant", "why is that number so low" — those are the bugs in the _idea_, which is the whole point. Adjust and re-run; prototypes evolve.

### 7. Capture the answer and the prototype

Once it's answered its question, capture the answer, then capture the prototype the way the [SKILL](SKILL.md) describes. The shape-specific mapping: the agreed columns, grain, and metric definition become the real Dataform definition and its `config` block — including the assertions that lock the grain in — while the throwaway SQL or script rides along to the throwaway branch as a primary source for *why* the shape is what it is.

## Anti-patterns

- **Don't put it in `definitions/`.** A prototype inside the Dataform tree gets compiled, scheduled, and depended on. Keep it out.
- **Don't write to a real dataset.** Print the result; don't materialise it. A scratch dataset with an expiry is the only exception.
- **Don't use a notebook.** Hidden execution order and un-reviewable output are exactly what a prototype can't afford.
- **Don't generalise.** No parameters "in case we want other date ranges later." The prototype answers one question.
- **Don't fabricate rows.** A shape prototype on made-up data proves nothing about the shape of the real thing — the surprises live in the real data.
- **Don't skip the grain check.** It's two lines and it's the single most common thing a shape prototype turns out to have wrong.
