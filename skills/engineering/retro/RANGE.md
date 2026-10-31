# Range mode

A retro over every session on this machine in a date range, across all projects. A week of raw logs runs to hundreds of MB, so each session is shrunk to a **digest** and subagents read the digests in batches. The payoff over a single-session retro is **recurrence**: a problem that hits five sessions outranks a one-off.

## Steps

1. **Digest.** Run the script against the user's range (`today`, `Nd` such as `7d`, or a `YYYY-MM-DD` start date), writing into the scratchpad:

   ```bash
   python3 <this skill's folder>/scripts/digest-sessions.py <range> <scratchpad>/retro-digests > <scratchpad>/retro-index.tsv
   ```

   The script keeps only entries inside the window and groups worktrees under their repo. The index has one row per session; its header line names the columns, and the script's docstring defines them. Done when the index exists and has at least one row. With zero rows, tell the user the range is empty and stop.

2. **Plan and ask.** Pack digests into **batches** of at most 150 KB each (a larger digest is a batch on its own). Show the user: session count, sessions per repo, total KB, and the number of subagents. Then ask with `AskUserQuestion`, offering: run all batches; run only the N sessions with the most tool errors (the `tool_errors` column; denials are the user's or a guardrail's call, not the agent struggling); cancel. Every run asks, even when the user approved one before. Dispatch only after the user picks a run option.

3. **Fan out.** Dispatch one subagent per batch, all in a single message. Each prompt carries:
   - the digest paths in its batch;
   - the path to this skill's `SKILL.md`, to read step 3's categories from;
   - the digest format: `USER:`, `AGENT:`, `CALL <tool>:`, `ERROR:` (a failed call), `DENIED:` (a blocked call) and `SYSTEM:` (a harness event) lines, clipped. The header names the raw `log:`, which the subagent can `grep` to confirm a finding the digest leaves unclear;
   - the return shape, one entry per finding: category, what went wrong, session id and project, one quoted evidence line, and the fix (which file, check, or access to add).

   Done when every batch has returned.

4. **Merge.** Collapse findings that share a root cause into one, listing every session and project it hit. Rank by sessions hit, then severity. Tag each fix with where it lands: a named repo, or the user's global `~/.claude/CLAUDE.md` / settings when it spans projects. Then present as in `SKILL.md` step 4.
