# Skills For Data Work

Agent skills for doing real data science, data engineering and analytics with a coding agent — not vibe coding.

Forked from [mattpocock/skills](https://github.com/mattpocock/skills) and adapted end to end for a data platform: BigQuery with transformations in **Dataform**, Python pipelines managed with **uv** and deployed to **Cloud Run**, and modelling on **Vertex AI**. Every example in every skill speaks that stack — tables, grain, partitions, assertions, feature sets — rather than components and routes.

These skills are deliberately small, easy to adapt, and composable. They work with any model. Hack around with them.

## Installation

<details>
<summary><strong>Claude Code</strong></summary>

This repo is its own marketplace, so add it, then install:

```bash
/plugin marketplace add andrii-zavhorodnii-liven/andrii-analytics-skills
/plugin install andrii-analytics-skills
```

</details>

<details>
<summary><strong>Codex, and other agents</strong></summary>

Symlink every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`):

```bash
git clone https://github.com/andrii-zavhorodnii-liven/andrii-analytics-skills
cd andrii-analytics-skills
scripts/link-skills.sh
```

Each entry is a symlink into the clone, so `git pull` keeps installed skills current.

</details>

### No per-repo setup

The skills follow conventions instead of per-repo config:

- The **issue tracker** is GitHub Issues via the `gh` CLI (repo inferred from `git remote`); repos with no remote fall back to local markdown under `.scratch/`
- The **triage labels** are the five canonical role names verbatim: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`
- **`CONTEXT.md` and `docs/adr/`** live at the repo root, created lazily by `/domain-modeling` when terms or decisions actually get resolved

## Why these skills exist

Agents fail in a handful of recognisable ways. Each group of skills fixes one.

### #1: The agent didn't build what I meant

> "No-one knows exactly what they want"
>
> David Thomas & Andrew Hunt, _The Pragmatic Programmer_

The most common failure in software is misalignment, and it's no different with an agent. The fix is a **grilling session** — the agent interviews *you*, one question at a time, until every branch of the decision tree is resolved.

- [`/grill-me`](./skills/productivity/grill-me/SKILL.md) — for anything without a codebase
- [`/grill-with-docs`](./skills/engineering/grill-with-docs/SKILL.md) — same interview, but it writes what it learns into `CONTEXT.md` and ADRs as it goes

Use one of these *every* time you're about to make a change.

### #2: Nobody checked what the data actually is

This is the failure mode specific to data work, and it's the reason for the biggest change in this fork. Most bad pipelines, wrong metrics and leaky models are built on an assumption about the data that nobody verified: the key wasn't unique, the column was null 40% of the time, the timestamp meant ingestion rather than the event.

[`/research-data`](./skills/engineering/research-data/SKILL.md) checks it — grain, nulls, cardinality, volume, freshness, joinability — and reports **numbers with the queries attached**, so anyone can re-run them. Its best output is often a **Dataform assertion** that turns a one-off finding into a standing guarantee.

It has two siblings, split out so each answers one kind of question well:

- [`/research-docs`](./skills/engineering/research-docs/SKILL.md) — a fact about a **tool**: what Dataform supports, what the quota is, what the SDK actually does. Primary sources only, pinned to a version.
- [`/research-web`](./skills/engineering/research-web/SKILL.md) — **which approach** to take: model family, orchestration option, prior art. Ends in one recommendation for your constraints, not "it depends".

When prose can't settle a question, [`/prototype`](./skills/engineering/prototype/SKILL.md) makes something concrete to react to — a terminal app you drive by hand for logic questions, or twenty real rows when the argument is about what the output should look like.

### #3: The agent is way too verbose

> With a ubiquitous language, conversations among developers and expressions of the code are all derived from the same domain model.
>
> Eric Evans, _Domain-Driven Design_

An agent dropped into a project has to guess the jargon, so it uses twenty words where one would do. The fix is a shared glossary — `CONTEXT.md` — that decodes the project's language.

[`/domain-modeling`](./skills/engineering/domain-modeling/SKILL.md) builds it, and it hunts the fuzz that's specific to analytics:

- **Metric words that hide a definition** — "active", "churned", "revenue", "session". Each is a decision about a window and a filter.
- **Entity words that hide a grain** — ask what one row *is*. A term whose grain nobody can state is the term that produces a fan-out join later.
- **Time words that hide which timestamp** — "the order date" is usually three columns: when it happened, when the source recorded it, when we ingested it.

Beyond less waffle, a shared language means models and columns get named consistently, the codebase is easier for an agent to navigate, and the agent spends fewer tokens thinking.

### #4: The code doesn't work

> "Always take small, deliberate steps. The rate of feedback is your speed limit."
>
> David Thomas & Andrew Hunt, _The Pragmatic Programmer_

Without feedback on how its code actually runs, an agent is flying blind.

[`/tdd`](./skills/engineering/tdd/SKILL.md) runs a red-green loop with guidance on what makes a test worth keeping — and, for data work, on the division of labour: `pytest` covers the Python you wrote, **Dataform assertions** cover the SQL the warehouse runs, and neither substitutes for the other. Fixtures are hand-written rows committed to the repo; a test whose expected value is "whatever production returns today" means nothing tomorrow.

[`/diagnosing-bugs`](./skills/engineering/diagnosing-bugs/SKILL.md) refuses to theorise until it has a **tight feedback loop** — one command that already goes red on *this* bug. For a data bug that's usually a single bounded query whose result set *is* the symptom.

### #5: We built a ball of mud

> "The best modules are deep. They allow a lot of functionality to be accessed through a simple interface."
>
> John Ousterhout, _A Philosophy of Software Design_

Agents accelerate coding, so they accelerate entropy too. [`/improve-codebase-architecture`](./skills/engineering/improve-codebase-architecture/SKILL.md) surveys for **deepening opportunities** and presents them as a visual report — including the shapes a data platform actually produces: transformation logic tangled with I/O, a shallow Dataform model that renames three columns, consumers reaching past a mart to read staging directly, one metric defined in four places.

Run it every few days.

### #6: The work is too big to hold in one session

[`/wayfinder`](./skills/engineering/wayfinder/SKILL.md) is for the effort where the *route* isn't visible yet — a warehouse re-grain, a migration off a legacy pipeline, a new platform area. It charts a **shared map** of decision tickets on the issue tracker and resolves them one at a time, producing **decisions, not deliverables**, until the way is clear. Then it hands off to the main flow.

It's the densest thing here. Save it for genuine fog; a well-scoped feature doesn't need it.

## Reference

These split on one axis — who can invoke them. **User-invoked** skills are reachable only when you type them (e.g. `/grill-me`); their job is to orchestrate. **Model-invoked** skills can be invoked by you _or_ reached for automatically by the agent when the task fits; they hold the reusable discipline. A user-invoked skill may invoke model-invoked skills, but never another user-invoked one.

Lost? [`/ask-andrii`](./skills/engineering/ask-andrii/SKILL.md) routes you to the right one.

### Engineering

Daily data, analytics and platform work.

**User-invoked**

- **[ask-andrii](./skills/engineering/ask-andrii/SKILL.md)** — Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.
- **[grill-with-docs](./skills/engineering/grill-with-docs/SKILL.md)** — Grilling session that also builds your project's domain model, sharpening terminology and updating `CONTEXT.md` and ADRs inline.
- **[triage](./skills/engineering/triage/SKILL.md)** — Move issues through a state machine of triage roles, ending in an agent-ready brief.
- **[to-spec](./skills/engineering/to-spec/SKILL.md)** — Turn the current conversation into a spec and publish it to the issue tracker. No interview — just synthesis of what you've already discussed.
- **[to-tickets](./skills/engineering/to-tickets/SKILL.md)** — Break any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges — native issue dependencies on GitHub, text in a local file otherwise.
- **[implement](./skills/engineering/implement/SKILL.md)** — Build the work described by a spec or set of tickets, driving `/tdd` at pre-agreed seams and closing out with `/code-review` before committing.
- **[improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/SKILL.md)** — Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **[wayfinder](./skills/engineering/wayfinder/SKILL.md)** — Plan a huge chunk of work, more than one agent session can hold, as a shared map of decision tickets on the issue tracker — resolved one at a time until the way to the destination is clear.
- **[present-analysis](./skills/engineering/present-analysis/SKILL.md)** — Turn a finished analysis into a layered stakeholder report: takeaways anchored on the stakeholder question, every takeaway backed by a chart, recommendations in plain business language.

**Model-invoked**

- **[research-docs](./skills/engineering/research-docs/SKILL.md)** — Answer a factual question about a tool, library or API from its primary sources, pinned to a version. Run as a background agent.
- **[research-data](./skills/engineering/research-data/SKILL.md)** — Profile the real data before building on it — grain, nulls, cardinality, volume, freshness, joinability — and capture the numbers with the queries that produced them.
- **[research-web](./skills/engineering/research-web/SKILL.md)** — Survey how a problem is usually solved and come back with a shortlist and one recommendation for our constraints.
- **[prototype](./skills/engineering/prototype/SKILL.md)** — Build a throwaway prototype to answer a design question: a runnable terminal app for logic and state, or a small real result set when the question is what the output should look like.
- **[tdd](./skills/engineering/tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop, one vertical slice at a time. Splits duties between `pytest` and Dataform assertions.
- **[diagnosing-bugs](./skills/engineering/diagnosing-bugs/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **[code-review](./skills/engineering/code-review/SKILL.md)** — Two-axis review of the diff since a fixed point: **Standards** (repo standards, plus a Fowler smell baseline and a data baseline covering unbounded scans, unenforced grain, non-idempotent writes and leakage) and **Spec** (does it faithfully implement the originating issue?), run as parallel sub-agents.
- **[domain-modeling](./skills/engineering/domain-modeling/SKILL.md)** — Actively build and sharpen a project's domain model — challenge terms, pin down grain and which timestamp a word means, update `CONTEXT.md` and ADRs inline.
- **[codebase-design](./skills/engineering/codebase-design/SKILL.md)** — Shared discipline and vocabulary for designing deep modules: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface.
- **[resolving-merge-conflicts](./skills/engineering/resolving-merge-conflicts/SKILL.md)** — Work through an in-progress git merge or rebase conflict hunk by hunk, resolving by intent traced to each side's primary source, then finish the operation — never `--abort`.
- **[cloud-run-to-repo](./skills/engineering/cloud-run-to-repo/SKILL.md)** — Recover an ad-hoc-deployed Cloud Run service into a git repo — uv-managed, with a repeatable `deploy.sh` that mirrors every live runtime flag.

### Productivity

General workflow tools, not code-specific.

**User-invoked**

- **[grill-me](./skills/productivity/grill-me/SKILL.md)** — Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved.
- **[handoff](./skills/productivity/handoff/SKILL.md)** — Compact the current conversation into a handoff document so another agent can continue the work.
- **[teach](./skills/productivity/teach/SKILL.md)** — Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- **[writing-great-skills](./skills/productivity/writing-great-skills/SKILL.md)** — Reference for writing and editing skills well: the vocabulary and principles that make a skill predictable.

**Model-invoked**

- **[grilling](./skills/productivity/grilling/SKILL.md)** — Interview the user relentlessly about a plan, decision, or idea until every branch of the decision tree is resolved. The reusable loop behind `grill-me` and `grill-with-docs`.

## Credits

Original skills by [Matt Pocock](https://github.com/mattpocock) ([aihero.dev](https://www.aihero.dev)), MIT licensed. This fork keeps his structure and much of his prose, re-aimed at data work.
