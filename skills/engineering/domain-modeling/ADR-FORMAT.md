# ADR Format

ADRs live in `docs/adr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.

Create the `docs/adr/` directory lazily — only when the first ADR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) — useful when decisions are revisited
- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one.

## When to offer an ADR

All three of these must be true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it — you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Architectural shape.** "Raw stays append-only; all deduplication happens in staging." "Marts are rebuilt from staging rather than updated in place."
- **Grain and modelling decisions.** "The orders mart is one row per order line, not per order." This is the highest-value ADR in a warehouse: the grain is hard to reverse, invisible from the column list, and every downstream model assumes it.
- **Partitioning and clustering choices that are expensive to change.** "Events are partitioned on `event_date`, not ingestion date, because backfills replay by event date."
- **Integration patterns between contexts.** "Modelling reads from marts, never from staging, so features can't outrun a definition change."
- **Technology choices that carry lock-in.** Warehouse, orchestrator, training platform, serving target. Not every library — just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer PII is owned by the ingestion context and never lands in a mart." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "This model is a full rebuild rather than incremental, because the source mutates history." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code or the graph.** "This dataset must stay in `europe-west1` for compliance." "This table is contractually frozen because a partner reads it."
- **Rejected alternatives when the rejection is non-obvious.** If you considered a Vertex AI AutoML model and picked gradient boosting for subtle reasons, record it — otherwise someone will suggest AutoML again in six months.
