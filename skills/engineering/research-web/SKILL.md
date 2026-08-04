---
name: research-web
description: Survey the open web for how a problem is usually solved — model families and architectures, tool and vendor choices, prior art, benchmarks, known pitfalls — and come back with a shortlist and a recommendation for our context. Use when the question is "which approach should we take?" rather than a fact about a tool (research-docs) or about our data (research-data).
---

# Research Web

Answer a **judgement** question: "what's the sensible approach here, and why?"

This is deliberately not primary-source research. There is no document that owns the answer to "which model should I use for churn prediction on 200k rows of tabular data" — the answer lives in practitioner consensus, benchmarks, and other people's post-mortems. The job is to gather that, weigh it, and land on a recommendation.

Spin up a **background agent** to do the survey, so you keep working while it reads.

## When this is the right skill

- "What model family fits this problem — gradient boosting, a linear baseline, or something on Vertex AI's AutoML?"
- "How do teams usually handle late-arriving events in an incremental warehouse table?"
- "Is there an established approach to backfilling a slowly-changing dimension we should copy rather than invent?"
- "What are the known failure modes of this vendor's API at our volume?"
- "Which orchestration option — Dataform tags, Cloud Scheduler, Vertex AI Pipelines — do people actually use for this shape of job?"

Wrong skill when the question has an authoritative answer in a tool's docs (`/research-docs`) or in our warehouse (`/research-data`).

## Ground it in our context first

A recommendation that ignores the constraints is worthless. Before searching, write down what's fixed:

- **Stack**: BigQuery + Dataform, Python managed with `uv`, Cloud Run, Vertex AI. An answer requiring a platform we don't run is not an answer — say so explicitly rather than recommending it.
- **Scale**: rows, columns, partitions, daily volume. Advice tuned for billions of rows is often wrong at millions, and vice versa.
- **Constraints that decide it**: latency (batch vs. near-real-time), cost ceiling, interpretability requirements, who maintains it, whether it must be reproducible from a Dataform graph.

If any of these are unknown and would flip the recommendation, say which — don't silently assume one.

## The agent's job

1. **Gather from several independent angles**, not one search. Practitioner write-ups, benchmark results, vendor documentation (read as an interested party, not a neutral one), and post-mortems of what went wrong.
2. **Separate consensus from a single loud opinion.** "Three unrelated sources converge on X" and "one heavily-upvoted blog post says X" carry different weight. Report which one you have.
3. **Date everything.** In ML and cloud tooling especially, a confident 2021 recommendation is often actively wrong now. Note the date of each source and discount stale ones.
4. **Name the trade-off, not just the winner.** Every option that made the shortlist gets what it's good at, what it costs, and what it rules out.
5. **Establish a baseline.** For any modelling question, the shortlist must include the boring option — logistic regression, a moving average, a rules-based cut. If nothing is measured against a baseline, "the model works" is unfalsifiable.
6. **Recommend one.** A survey that ends in "it depends" hasn't done the job. Pick one for *our* constraints, and say what would change your mind.

## Findings file shape

```markdown
# <the question, as a question>

**Recommendation**: <the one option, in a line> — <the single strongest reason>

## Our constraints

<stack, scale, and the constraints that actually decide this>

## Shortlist

### <option> — recommended
- Good at: ...
- Costs: ...
- Rules out: ...
- Evidence: [source](url) (<date>), [source](url) (<date>)

### <option> — rejected
- Rejected because: ...

## Consensus vs. opinion

<where sources agree, where a single source is carrying a claim on its own>

## What would change this

<the finding that would flip the recommendation — often something /research-data can settle>

## Next step

<the smallest experiment that would confirm this before we commit>
```

## Hand off to the cheaper skill when you can

The best outcome of a web survey is often "this hinges on a fact about our data" — at which point stop, and let `/research-data` settle it. Guessing at our own numbers from the internet is the failure mode this skill has to avoid.

Link the findings file from the issue the question came from.
