---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the change follow this repo's documented standards, plus a baseline chosen from what the diff is made of — code or skill markdown?) and Spec (does it match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, a skill's markdown, or asks to "review since X".
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the change conform to this repo's documented standards?
- **Spec** — does the change faithfully implement the originating issue / PRD / spec?

The diff can be code or a skill's own markdown; step 3 picks the baseline from what it holds.

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

Issue tracker convention: **GitHub Issues** via the `gh` CLI when the repo has a git remote; local markdown under `.scratch/<feature>/issues/` when it doesn't.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, etc.) — fetch with `gh issue view <n> --comments` (or read the `.scratch/` file on a remoteless repo).
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how its contents should be written, such as `CODING_STANDARDS.md`, `CONTRIBUTING.md`, or a `CLAUDE.md` carrying repo conventions.

On top of whatever the repo documents, the Standards axis carries a **baseline** — the failure modes that apply even when a repo documents nothing. Which baseline applies follows each changed file, so a diff holding both kinds carries both baselines — each file judged against its own:

- **Code** → read [`code-baselines.md`](code-baselines.md): the Fowler smell baseline and the data baseline, plus the two rules that bind them.
- **Skill markdown** — `SKILL.md` files and their sibling reference files, under a project's `.claude/skills/` or in the skills repo itself → read `~/.claude/skills/writing-great-skills/SKILL.md` and its `GLOSSARY.md`. Its **Failure modes** list is this branch's baseline: premature completion, duplication, sediment, sprawl, no-op, negation. If that path doesn't resolve, find the repo root by resolving an installed skill's symlink (`readlink ~/.claude/skills/code-review`) and read `skills/productivity/writing-great-skills/` there. Judge prose against that skill and nothing else.

### 4. Spawn both sub-agents in parallel

Send a single message with two `Agent` tool calls. Use the `general-purpose` subagent for both.

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus every baseline step 3 selected**, pasted in full; the sub-agent has no other access to them.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline issue you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline items are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong; (d) where the diff defines or changes a metric, analysis query, or stakeholder-facing output, whether it answers the question the spec actually asks — flag a metric that subtly answers a different question (a rate where the spec needs a volume, an average masking a distribution), a likely misread by the output's audience, and survivorship or excluded segments that could change the conclusion. Quote the spec line for each finding; (d) items are judgement calls, tag them as such. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
