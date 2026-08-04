# CONTEXT.md Format

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Grain_: one row per order
_Avoid_: Purchase, transaction

**Order Line**:
A single product-and-quantity within an **Order**. The finest grain we hold order data at.
_Grain_: one row per (order, product)
_Avoid_: Line item, order item

**Active Customer**:
A **Customer** with at least one **Order** in the trailing 90 days, measured on `ordered_at` — not on ingestion time.
_Avoid_: Live customer, engaged customer
```

For terms that name something the warehouse holds, add a `_Grain_` line: what one row is. It's part of what the word means, and it's the fact most often assumed differently by two people using the same term. For a metric term, the definition must state its **window** and the **timestamp** it's measured on — a metric word without those isn't defined yet.

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.

## Single vs multi-context repos

**Single context (most repos):** One `CONTEXT.md` at the repo root.

**Multiple contexts:** A `CONTEXT-MAP.md` at the repo root lists the contexts, where they live, and how they relate to each other:

```md
# Context Map

## Contexts

- [Ingestion](./src/ingestion/CONTEXT.md) — pulls source systems into raw and staging tables
- [Marts](./src/marts/CONTEXT.md) — models staging data into the tables analysts query
- [Modelling](./src/modelling/CONTEXT.md) — builds feature sets and trains predictive models

## Relationships

- **Ingestion → Marts**: Ingestion owns `staging.*`; Marts may only read from staging, never from raw
- **Marts → Modelling**: Modelling builds features from mart tables, never from staging — so a feature can't outrun a definition change
- **Ingestion ↔ Marts**: Shared definition of `customer_id` and the ingestion watermark convention
```

The skill infers which structure applies:

- If `CONTEXT-MAP.md` exists, read it to find contexts
- If only a root `CONTEXT.md` exists, single context
- If neither exists, create a root `CONTEXT.md` lazily when the first term is resolved

When multiple contexts exist, infer which one the current topic relates to. If unclear, ask.
