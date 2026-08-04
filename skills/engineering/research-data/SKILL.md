---
name: research-data
description: Investigate what the data actually is before building on it — profile a BigQuery table, sample an API response, establish grain, nulls, cardinality, volume and freshness — and capture the findings as a Markdown file with the queries that produced them. Use when a pipeline, model, metric, or spec decision waits on a fact about real data.
---

# Research Data

Most bad data work is built on an assumption about the data that nobody checked. This skill checks it.

The output is not an opinion. It's **a set of numbers, plus the exact queries that produced them**, so anyone can re-run and get the same answer.

## When this is the right skill

- "What's the grain of this table — is `order_id` actually unique?"
- "How many rows land per day, and how far back does history go?"
- "Is `customer_email` nullable in practice, and how often?"
- "How many distinct values does this dimension have — 12, or 400,000?"
- "Does this source API's response actually contain the field the spec assumes?"
- "Are these two tables joinable on this key, and what's the match rate?"
- "Is this feature available at prediction time, or is it leakage?"

Wrong skill when the question is about what a **tool** does (`/research-docs`) or which **approach** to take (`/research-web`).

## Rules

1. **Never sample without saying you sampled.** State the scope of every number: which table, which partition range, which filters. A count over last week is not a count.
2. **Cost first.** In BigQuery, dry-run before you run: `bq query --dry_run --use_legacy_sql=false '<sql>'`, and report the bytes. Prefer `INFORMATION_SCHEMA`, table metadata, and `TABLESAMPLE` over a full scan. Never run an unbounded scan on a partitioned table without a partition filter.
3. **Read-only.** This skill investigates; it does not create, replace, or delete tables. A scratch table is the one exception, and only in an explicitly scratch dataset with a clearly temporary name.
4. **Show the query.** Every number in the findings carries the SQL (or the Python snippet) that produced it. A number without its query is a rumour.
5. **Distinguish absent from zero.** "No rows matched" and "the column doesn't exist" and "the value is NULL" are three different findings. Don't collapse them.

## Process

### 1. Write the question down

One line, as a question, before touching anything. Data investigation sprawls — the written question is what stops it.

### 2. Find the shape before you find the numbers

Cheap metadata first, so the expensive queries are aimed:

- Schema, partitioning, clustering, row count, size, last modified — `INFORMATION_SCHEMA.COLUMNS`, `INFORMATION_SCHEMA.TABLES`, `INFORMATION_SCHEMA.PARTITIONS`, or `bq show --schema`
- Where it comes from — if it's a Dataform output, read the SQLX definition and its `config` block; the declared `uniqueKey`, `assertions`, and upstream `ref()`s often answer the question outright
- Whether an assertion already covers it — a passing Dataform assertion on uniqueness is stronger evidence than a query you wrote just now

### 3. Profile

Pick only the profiles the question needs:

- **Grain** — is the claimed key unique? `SELECT COUNT(*) AS rows, COUNT(DISTINCT <key>) AS keys FROM ...`. Equal means unique; unequal means the grain is not what was claimed, and the duplicate pattern is the interesting finding.
- **Completeness** — null and empty-string rate per column of interest, as a percentage of rows in a stated window.
- **Cardinality** — distinct counts for dimensions, plus the top values by frequency. This decides whether something is a category or an identifier.
- **Range and outliers** — min, max, and the percentiles that matter for numerics and dates.
- **Volume and freshness** — rows per day over a recent window, plus `MAX(<event_timestamp>)` versus now. A gap in the daily counts is a finding, not noise.
- **Joinability** — match rate in both directions between the two keys, not just one.

For an external source rather than a warehouse table: capture one real response, verbatim, into a scratch file, and report the field set and types found — versus what the spec assumes.

### 4. Write the findings

~~~markdown
# <the question, as a question>

**Answer**: <one or two lines>
**Scope**: <table(s), partition/date range, filters, and when this was run>

## Findings

| Fact | Value | Query |
| ---- | ----- | ----- |
| Rows in window | 4,182,394 | `q1` |
| Distinct order_id | 4,182,394 | `q1` |

## Queries

### q1
```sql
-- ...
```

## Surprises

<what contradicted the assumption we were working from — this is the part people read>

## What this means for us

<the decision this unblocks, and any assertion or test worth adding to lock it in>
~~~

### 5. Lock the finding in

A profile is true on the day it's run. When a finding is something the pipeline must keep being true — a key really is unique, a column really is never null — say so, and propose the **Dataform assertion** (`uniqueKey`, `nonNull`, or a custom assertion) that turns the finding into a standing check. That's how a one-off investigation stops being re-investigated.

Link the findings file from the issue the question came from.
