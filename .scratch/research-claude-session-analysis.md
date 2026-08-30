# What can analyze Claude Code JSONL transcripts across sessions to improve CLAUDE.md/skills/memories?

**Recommendation**: Use the two first-party built-ins first — `/insights` (multi-session, 30-day, local analysis with friction-point findings) plus the shipped `fewer-permission-prompts` skill (transcript scan → settings.json allowlist) — and add **claude-reflect** (BayramAnnakov, plugin-marketplace install, 1.4k stars) as the piece that actually writes learnings into CLAUDE.md/skills. If claude-reflect's hook-based capture feels heavy, fall back to a ~100-line custom skill in your own plugin repo.

## Our constraints
- Claude Code CLI + VSCode on macOS; user ships a personal skills repo as a Claude Code plugin.
- Must be installable as a skill/plugin or simple CLI; no hosted SaaS / no data upload.
- Multi-session analysis is the differentiator: recurring friction, permission prompts, repeated corrections.
- Output should be actionable edits: CLAUDE.md, SKILL.md files, persistent memories.

## Shortlist

### 1. `/insights` — built into Claude Code (first-party)
- **Good at**: exactly the multi-session goal — analyzes ~/.claude/ session logs from the last 30 days locally, produces an HTML report (`~/.claude/usage-data/report.html`) with work-pattern categories, friction points, and workflow/feature suggestions. Zero install, no data leaves the machine.
- **Costs**: report-shaped, not edit-shaped — it suggests, but doesn't write CLAUDE.md/skill diffs.
- **Evidence**: https://www.mindstudio.ai/blog/claude-code-insights-command-workflow-audit , https://adventuresinclaude.ai/posts/2026-02-20-insights-report/ (2026-02), https://angelo-lima.fr/en/claude-code-insights-command/

### 2. `fewer-permission-prompts` — first-party skill (already installed)
- **Good at**: scans transcripts for common read-only Bash/MCP calls and writes a prioritized allowlist into `.claude/settings.json`. Multi-session by design, output is an actual config edit.
- **Costs**: narrow scope (permissions only).

### 3. **claude-reflect** (BayramAnnakov) — community plugin
- **Good at**: hooks capture corrections ("no, use X", "actually…") live; `/reflect` reviews and syncs approved learnings to global/project CLAUDE.md, skill files, and AGENTS.md; `/reflect --scan-history` analyzes past sessions and `/reflect-skills` mines session patterns for automation ideas. Install: `claude plugin install claude-reflect@claude-reflect-marketplace`. Human review before anything is written.
- **Costs**: installs hooks (runs in every session); Python scripts; third-party code editing your CLAUDE.md.
- **Evidence**: https://github.com/BayramAnnakov/claude-reflect (1.4k stars, v2.6.0, active as of 2026-08-15).

### 4. **claude-improve** (TerenceBristol) — single markdown command
- **Good at**: one `improve.md` in `~/.claude/commands/`; `/improve` reads last 5 sessions, detects feedback patterns, edits CLAUDE.md/skills/agents plus learnings files. No dependencies, no hooks.
- **Costs**: only 5 sessions deep; 26 stars — a one-off, not established.
- **Evidence**: https://github.com/TerenceBristol/claude-improve (2026-08-15).

### 5. Viewers / quantitative analyzers (adjacent)
- https://github.com/kmizzi/claude-code-sessions — cross-project session browser, SQLite FTS5 search; manual pattern-finding, no edit suggestions.
- https://github.com/lucemia/claude-session-analyzer — quantitative metrics over JSONL logs.
- https://github.com/daaain/claude-code-log , https://github.com/kiliman/claude-transcript — JSONL → HTML/Markdown converters; useful plumbing for a custom skill.

### 6. Boring baseline — custom skill in this plugin repo
- **Good at**: full control, fits repo conventions. SKILL.md + small script globbing `~/.claude/projects/**/*.jsonl`, extracting user corrections / tool denials across N sessions, drafting CLAUDE.md/memory edits for review.
- **Costs**: you maintain it; re-derives heuristics claude-reflect already has.
- **Feasibility**: https://fazm.ai/blog/claude-code-previous-sessions-jsonl-transcripts , https://alexop.dev/posts/building-conversation-search-skill-claude-code/

## Consensus vs. opinion
- **Consensus**: `/insights` is the recognized first stop (many independent 2026 write-ups); claude-reflect is the community leader for "sync learnings into CLAUDE.md"; the JSONL format under `~/.claude/projects/` is well-documented.
- **One-off**: claude-improve and various retrospective gists/skills are individual experiments — fine as reading, weak as dependencies.

## What would change this
- claude-reflect's always-on hooks conflict with your setup / feel invasive → claude-improve or the custom skill.
- Pain is mostly permission prompts → `fewer-permission-prompts` alone may cover it.
- Anthropic extends `/insights` to emit CLAUDE.md edits directly → third-party layer unnecessary.
- You want the logic version-controlled in your own plugin → custom skill wins.

## Next step
Run `/insights` today (zero install), run `fewer-permission-prompts` once, then trial claude-reflect for two weeks before building anything custom.
