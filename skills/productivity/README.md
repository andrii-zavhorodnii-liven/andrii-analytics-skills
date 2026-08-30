# Productivity

General workflow tools, not code-specific.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[grill-me](./grill-me/SKILL.md)** — Get relentlessly interviewed about a plan or design until every branch of the decision tree is resolved.
- **[handoff](./handoff/SKILL.md)** — Compact the current conversation into a handoff document so another agent can continue the work.
- **[pr-merged](./pr-merged/SKILL.md)** — After a PR merges, sync the default branch and delete the merged local branches.
- **[teach](./teach/SKILL.md)** — Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- **[wait-what](./wait-what/SKILL.md)** — Stop and re-pitch the last message in plain language when it didn't land.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[grilling](./grilling/SKILL.md)** — Interview the user relentlessly about a plan, decision, or idea, a round of frontier questions at a time, until every branch of the design tree is resolved.
- **[writing-for-agents](./writing-for-agents/SKILL.md)** — Reference for writing any document an agent consumes — skills, `AGENTS.md`/`CLAUDE.md`, docs reached by pointers: the levers that make each one predictable.
