---
name: retro
description: "Conduct a retrospective on a coding session."
disable-model-invocation: true
---

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** to improve future runs.

## Steps

1. Call the Skill tool with "writing-for-agents" for the writing style guide.

2. Read the primary sources for the session the user specifies. This may mean searching through session logs on this machine. If the user doesn't specify a session, default to the current one.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files, such as a Dataform model and the Python job that writes its source table? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? `ruff`, `mypy`, `pytest`, `dataform compile`, a SQL linter, a Dataform assertion? Read the repo's own check commands first (`pyproject.toml`, a `Makefile`, the pre-commit config, the CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook and no CI job running its lint, typecheck, test or `dataform compile`) is itself a finding: an unchecked repo is a standing missed opportunity, not a neutral default. _Use when_ the agent made a mistake an automated check could have caught, or the repo has no guardrail at all.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned function, a hardcoded project or dataset name, a file-location rule, a model missing its `uniqueKey` assertion) gets a deterministic check, full stop: a custom lint rule, a new pre-commit hook, a Dataform assertion, or a new CI job, whichever the repo's existing guardrail makes cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style", whether a metric is defined in the right layer, anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md or CLAUDE.md file is particularly large, in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? A full-table scan where a partition filter or `LIMIT` would do, a `SELECT *` dumped into context, a CLI or MCP that returns far more than it needs to? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Read-only BigQuery access to a dev dataset, `INFORMATION_SCHEMA` for table metadata, Cloud Logging for Cloud Run job runs, Vertex AI job logs. _Use when_ a crucial piece of information was not available to the agent.

4. Present these candidates to the user, in order of severity.

## Reference

### Implementation vs Review

All work goes through two stages: implementation and review. The implementation agent has the most **context pressure**. It is responsible for exploration, writing code, and debugging failures.

The review agent has the least context pressure: it receives a diff, so no exploration is needed. It often does not need to write code or debug.

This means the review agent should be responsible for imposing coding standards, not the implementation agent.

### Files

You have access to several files in the repo:

- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. Use them incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: read during review (by `code-review`), not implementation. Add **navigation pointers** to docs folders if the standards file gets more than 1,000 lines long.
- Docs: reference files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into the agent's context window), or for user-invoked commands. Follow the advice in the `writing-for-agents` skill.
