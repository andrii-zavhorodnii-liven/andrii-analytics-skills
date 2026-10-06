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
- **[implement-spec](./implement-spec/SKILL.md)** — Build a whole spec's tickets in one run: implementer subagents work the ready frontier of the task graph in parallel, each in its own worktree, merged onto one integration branch and closed out with `/code-review`.
- **[retro](./retro/SKILL.md)** — Look back at a coding session and suggest changes to the agent's environment, not the code: navigation pointers, automated checks, coding standards, steering files, data access.
- **[wayfinder](./wayfinder/SKILL.md)** — Plan a huge chunk of work — more than one agent session can hold — as a shared map of decision tickets on the issue tracker, resolved one at a time until the way to the destination is clear.
- **[consolidating-work](./consolidating-work/SKILL.md)** — Pull a sprawl of parallel worktrees and branches back to a reviewable state: secure every uncommitted change first, reap the branches a descendant already contains, then settle each surviving tip as a PR to `main`.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[prototype](./prototype/SKILL.md)** — Build a throwaway prototype to answer a design question: an interactive app for logic and state (terminal TUI, or a shareable HTML file for non-developers), or a small real result set when the question is what the output should look like.
- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **[research-docs](./research-docs/SKILL.md)** — Answer a factual question about a tool, library or API from its primary sources, pinned to a version, as a cited Markdown file. Run as a background agent.
- **[research-data](./research-data/SKILL.md)** — Profile the real data before building on it — grain, nulls, cardinality, volume, freshness, joinability — and capture the numbers with the queries that produced them.
- **[research-web](./research-web/SKILL.md)** — Survey how a problem is usually solved (model families, orchestration options, prior art) and come back with a shortlist and one recommendation for our constraints.
- **[tdd](./tdd/SKILL.md)** — Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[pr](./pr/SKILL.md)** — The shape of a PR body: the smallest visual that shows the change (a Dataform graph or schema diff), before/after evidence that it works, and a one-way/two-way door call with its blast radius.
- **[domain-modeling](./domain-modeling/SKILL.md)** — Actively build and sharpen a project's domain model — challenge terms, stress-test with scenarios, update `CONTEXT.md` and ADRs inline.
- **[codebase-design](./codebase-design/SKILL.md)** — Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- **[code-review](./code-review/SKILL.md)** — Two-axis review of the diff since a fixed point: **Standards** (repo standards, plus a baseline chosen from what the diff is made of — Fowler smells and data failure modes for code, `writing-for-agents`'s failure modes for skill markdown) and **Spec** (does it faithfully implement the originating issue?), run as parallel sub-agents.
- **[retrain-proof](./retrain-proof/SKILL.md)** — Make every training run retrain-proof: persist the scored evaluation rows, the model file, and the population definition next to the metrics output, so any follow-up metric is computable without a refit.
- **[cloud-run-to-repo](./cloud-run-to-repo/SKILL.md)** — Recover an ad-hoc-deployed Cloud Run service into a git repo — uv-managed, with a repeatable `deploy.sh` that mirrors every live runtime flag.
- **[feasibility-check](./feasibility-check/SKILL.md)** — Pressure-test whether an ask is feasible, and at what cost, before promising an estimate: trace the real system, tag each piece have/build/can't/unknown, one verdict plus the single check to run first.
- **[present-analysis](./present-analysis/SKILL.md)** — Turn a finished analysis into a layered stakeholder report: takeaways anchored on the stakeholder question, every takeaway backed by a chart.
- **[shap-report](./shap-report/SKILL.md)** — SHAP HTML report for the CatBoost model(s) published in the current repo — a roster of targets or a single model: mean|SHAP| share % by feature × model, on one hash-verified shared holdout sample. Fires only inside a repo that holds a `.cbm` model.
