---
name: blast-radius
description: Find what a change breaks beyond its diff — downstream Dataform models, dashboards, scheduled queries, Python jobs, Vertex AI features — and prove the one fact it is safe because of by running a query or a compile. Use for "what could this break", "blast radius of X", or before renaming, retyping, or dropping a column, or changing a table's grain, partitioning, or a shared contract.
---

# Blast radius

Listing direct dependents is one grep. The job is the breakage grep doesn't show.

## How sure

For each fact the change's safety rests on, get it as far down this ladder as is cheap, and say where it stopped:

1. **Said so.** Worthless on its own.
2. **Pointed at it.** A real `file:line`, or a query result.
3. **Walked it.** You traced the failure step by step and showed it can't happen.
4. **Ran it.** A query, `dataform compile`, or a test against the real code or data that fails loud if you are wrong.
5. **Reproduced it.** A real run in a dev dataset or staging.

## Steps

1. **Read the change.** What it does differently, including what the diff doesn't spell out: a cast that changes NULL handling, a dedup that changes the row count, a timestamp that moves timezone.
2. **Find the one fact it is safe because of.** Most risky-looking changes are safe because of one fact — "no consumer reads `user_country`", "the grain stays one row per `order_id`", "every caller passes `as_of`". If it holds, most risks clear at once. Spend your time here.
3. **Look where grep stops.**
   - **The Dataform graph**: every dependent in the compiled graph, plus a text search of `definitions/` for the table name — assertions and operations that name it in raw SQL instead of `ref()` are missing from the graph.
   - **Consumers outside the repo**: `INFORMATION_SCHEMA.JOBS` over the last 30–90 days, filtered on `referenced_tables` — scheduled queries, dashboard connectors, service accounts. Group by `user_email`. It lists only jobs run in the project you query; readers in other projects need `INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION`, or one query per consumer project.
   - **Views** that reference it: `INFORMATION_SCHEMA.VIEWS`, searching `view_definition`.
   - **Python jobs** that read it by name, rely on `SELECT *` column order, or assume a dtype.
   - **Vertex AI**: a feature the model was trained on, the serving query that builds its input, an endpoint's request schema.
   - **History**: incremental models that need a full refresh, and old partitions that keep the old meaning.
   - **Grain and meaning**: downstream `SUM` and `COUNT` that assume the old uniqueness or the old definition.
4. **Rate each risk.** A real chance and a real cost. Cite a `file:line` or the query; a search that finds nothing is an answer — show it.
5. **Prove the one fact.** Run the query, compile, or test that settles it, and paste the command and its output, secrets redacted.

Done when every place in step 3 is reported — a risk, cleared, or searched with nothing found — and the one fact reaches rung 4 or is marked **unproven** with the reason.

## Hand back

- **What it does** — including the part that isn't obvious.
- **The one fact it is safe because of** — its rung, and the proof or "unproven".
- **Risks** — how each breaks, where, how likely and how bad, and how to check.
- **Cleared** — what you checked and why it is fine.
- **Before you merge** — the cheapest check that catches the real risk, ideally a Dataform assertion that keeps catching it.
