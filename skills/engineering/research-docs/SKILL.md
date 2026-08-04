---
name: research-docs
description: Investigate a factual question about a tool, library, or API against its primary sources and capture the findings as a cited Markdown file. Use when a decision waits on what BigQuery, Dataform, Vertex AI, a Python library, or a third-party API actually does — not on what our data says (use research-data), and not on which approach is best (use research-web).
---

# Research Docs

Answer a **factual** question — "what does this tool actually do?" — from the sources that own the answer.

Spin up a **background agent** to do the reading, so you keep working while it reads.

## When this is the right skill

- "Does Dataform support an incremental table with a `uniqueKey` and a partition filter at the same time?"
- "What's the actual quota on BigQuery streaming inserts per table per second?"
- "Which Vertex AI Pipelines component versions work with the SDK we pin?"
- "Does this vendor's API paginate by cursor or by offset, and what's the rate limit?"
- "Is this `polars` behaviour documented, or an accident of the version we have?"

Wrong skill when:

- The question is about **our own data** — grain, nulls, cardinality, volume, freshness. Use `/research-data`.
- The question is **"which approach should we take?"** — model choice, tool comparison, prior art. Use `/research-web`.

## The agent's job

1. **Investigate against primary sources** — official documentation, the library's own source, the API's reference and changelog, the RFC or spec, first-party release notes. Not a secondary write-up of them, not a blog post restating them, not a StackOverflow answer. Follow every claim back to the source that owns it.
2. **Pin the version.** A fact about a tool is only a fact at a version. Record which BigQuery API version, which Dataform core version, which package release the finding applies to — and where this repo pins it (`pyproject.toml`, `uv.lock`, `workflow_settings.yaml`).
3. **Read the source when the docs are vague.** For a Python dependency, the installed package under `.venv/` is a primary source, and usually more honest than the docs. Prefer it over guessing.
4. **Write the findings to a single Markdown file**, citing each claim's source with a link, and a version per above.
5. **Say what it couldn't establish.** An undocumented behaviour recorded as undocumented is a useful finding. A guess presented as a fact is a liability — it will get built on.
6. **Save it where the repo already keeps such notes**; match the existing convention, and if there is none, put it somewhere sensible and say where.

## Findings file shape

```markdown
# <the question, as a question>

**Answer**: <what the answer is, in one or two lines>
**Applies to**: <tool + version, and where we pin it>

## Findings

- <claim> — [source](url)

## Not established

- <what stayed open, and why — undocumented, source unreadable, needs an experiment>

## What this means for us

<the decision this unblocks, in a line or two>
```

## Capture it

Link the findings file from the issue the question came from. A finding nobody can locate again gets re-researched.
