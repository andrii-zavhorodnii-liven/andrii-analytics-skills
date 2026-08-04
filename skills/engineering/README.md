# Engineering

Skills I use daily for data, analytics and platform work — BigQuery + Dataform, Python/uv pipelines on Cloud Run, and Vertex AI.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[ask-andrii](./ask-andrii/SKILL.md)** — Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.
- **[grill-with-docs](./grill-with-docs/SKILL.md)** — Grilling session that also builds your project's domain model, sharpening terminology and updating `CONTEXT.md` and ADRs inline.
- **[triage](./triage/SKILL.md)** — Move issues through a state machine of triage roles.
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)** — Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **[to-spec](./to-spec/SKILL.md)** — Turn the current conversation into a spec and publish it to the issue tracker.
- **[to-tickets](./to-tickets/SKILL.md)** — Break any plan, spec, or conversation into a set of tracer-bullet tickets, each declaring its blocking edges — native issue dependencies on GitHub, text in a local file otherwise.
- **[implement](./implement/SKILL.md)** — Build the work described by a spec or set of tickets, driving `/tdd` at pre-agreed seams and closing out with `/code-review` before committing.
- **[wayfinder](./wayfinder/SKILL.md)** — Plan a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets on the issue tracker, resolved one at a time until the way to the destination is clear.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[prototype](./prototype/SKILL.md)** — Build a throwaway prototype to answer a design question: a runnable terminal app for logic and state, or a small real result set when the question is what the output should look like.
- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **[research-docs](./research-docs/SKILL.md)** — Answer a factual question about a tool, library or API from its primary sources, pinned to a version, as a cited Markdown file. Run as a background agent.
- **[research-data](./research-data/SKILL.md)** — Profile the real data before building on it — grain, nulls, cardinality, volume, freshness, joinability — and capture the numbers with the queries that produced them.
- **[research-web](./research-web/SKILL.md)** — Survey how a problem is usually solved (model families, orchestration options, prior art) and come back with a shortlist and one recommendation for our constraints.
- **[tdd](./tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[domain-modeling](./domain-modeling/SKILL.md)** — Actively build and sharpen a project's domain model — challenge terms, stress-test with scenarios, update `CONTEXT.md` and ADRs inline.
- **[codebase-design](./codebase-design/SKILL.md)** — Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- **[code-review](./code-review/SKILL.md)** — Two-axis review of the diff since a fixed point: **Standards** (repo standards, plus a Fowler smell baseline and a data baseline covering unbounded scans, unenforced grain, non-idempotent writes and leakage) and **Spec** (does it faithfully implement the originating issue?), run as parallel sub-agents.
- **[resolving-merge-conflicts](./resolving-merge-conflicts/SKILL.md)** — Work through an in-progress git merge or rebase conflict hunk by hunk, resolving by intent traced to each side's primary source, then finish the operation — never `--abort`.
- **[to-experiment](./to-experiment/SKILL.md)** — Spin up a sibling `<main>-experiments` repo for throwaway exploration work: a `uv`-managed Python project with plain `.py` scripts, no notebooks.
- **[cloud-run-to-repo](./cloud-run-to-repo/SKILL.md)** — Recover an ad-hoc-deployed Cloud Run service into a git repo — uv-managed, with a repeatable `deploy.sh` that mirrors every live runtime flag.
