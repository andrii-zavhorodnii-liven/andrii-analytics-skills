---
name: to-spec
description: Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-analytics-skills` if not.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a growth analyst, I want signup source available on the daily active users table, so that I can attribute activation without joining three tables by hand
</user-story-example>

The actor is whoever consumes the output — an analyst, a stakeholder reading a dashboard, a downstream model, a served ML endpoint. "As a developer, I want…" is almost always a sign the story has been written from the implementation inwards.

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules, models, or jobs that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Output schema, **grain**, partitioning and clustering — state the grain explicitly; it's the single most common thing a spec leaves implicit and an implementation gets wrong
- Source contracts: which fields are relied on, what happens when one goes missing or null
- Backfill and idempotency: whether a re-run replaces, appends, or merges, and what a replay of a past partition does
- Freshness and scheduling expectations
- For a model: the target definition, the train/test split policy, and which features are available at prediction time

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (a state machine, a table schema with its grain, a metric's SQL definition), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested, and at which seams
- Which guarantees become **Dataform assertions** rather than Python tests — grain, uniqueness, non-null, referential checks. A guarantee the spec states and nothing enforces will quietly stop being true.
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
