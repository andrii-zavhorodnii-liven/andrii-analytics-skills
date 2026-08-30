---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-one-row-per-order-line-grain.md
│       └── 0002-partition-marts-by-event-date.md
├── definitions/                       ← Dataform SQLX
└── pipelines/                         ← Python ingestion jobs
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← platform-wide decisions
├── src/
│   ├── ingestion/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── marts/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the Subscription? Those are different things."

Data work has its own recurring fuzz, and it's worth hunting deliberately:

- **Metric words that hide a definition** — "active", "churned", "revenue", "session". Every one of these is a decision about a window and a filter. Pin it: active over what period, measured on what event?
- **Entity words that hide a grain** — "an order", "a customer", "an event". Ask what one row *is*. A term whose grain nobody can state is the term that will produce a fan-out join later.
- **Time words that hide which timestamp** — "the order date" is usually three different columns: when it happened, when the source recorded it, when we ingested it. Name which one the term means, and say so in the glossary.

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your model is grouped by `customer_id` alone, but you just said a customer can hold several subscriptions — which is right?"

For data work, the code includes the **data**. When a claim about the domain is checkable in the warehouse, check it rather than debating it — a `COUNT(*)` versus `COUNT(DISTINCT key)` settles a grain question in seconds. Reach for `/research-data` when the check is bigger than a one-liner. A glossary term contradicted by the rows is the most valuable contradiction you can find.

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

That boundary is easy to lose here: a term's **grain** and **which timestamp it means** belong in the glossary, because they're part of what the word means. Its table name, partitioning, and clustering do not — those are implementation, and they go in an ADR or the spec.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
