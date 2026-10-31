#!/usr/bin/env python3
"""Shrink Claude Code session logs into short digests a subagent can read.

Usage: digest-sessions.py SINCE OUT_DIR
  SINCE: today | Nd (last N days, e.g. 7d) | YYYY-MM-DD

Reads every top-level session log under ~/.claude/projects (subagent logs and
throwaway /private/tmp scratchpad projects are skipped), keeps what the user
typed, the agent's text, each tool call, every tool error and every denial, and
drops big tool outputs. Only entries inside the window are kept, so an old
session resumed today brings only today's turns. Sessions with no tool calls
and branch-naming side-calls are skipped.

Writes one <session-id>.md per session into OUT_DIR and prints a TSV index:
digest path, repo, start time, user turns, tool calls, tool errors, denials,
digest KB, title.
- user turns: what the user typed or invoked (slash commands count); harness
  events (task notifications, system reminders, command output) do not.
- tool errors: tool calls that failed. denials: calls blocked by a permission
  prompt, the auto-mode classifier, a hook, or worktree isolation.
- repo: the main checkout a session's folder belongs to, so worktrees of one
  repo group together.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
TEXT_CAP = 600   # chars kept per user/agent message
INPUT_CAP = 200  # chars kept per tool-call input
ERROR_CAP = 400  # chars kept per tool error
HELPER_PROMPT = "USER: Generate a short git branch name"  # Claude Code side-call, not real work
SYSTEM_TAGS = ("<task-notification>", "<system-reminder>", "<ci-monitor-event>",  # harness events, not user input
               "<local-command-stdout>", "<local-command-stderr>", "<bash-stdout>", "<bash-stderr>")
DENIAL = re.compile(
    r"^(Permission to use .* has been denied|Permission for this action was denied"
    r"|The user doesn't want to proceed|\S+ hook error: Refused|This session is isolated in the worktree)"
)


def parse_since(arg):
    now = datetime.now().astimezone()
    if arg == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if m := re.fullmatch(r"(\d+)d", arg):
        return now - timedelta(days=int(m[1]))
    return datetime.fromisoformat(arg).astimezone()


def clip(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n] + " …"


def user_line(text):
    """(line, is_turn): a slash command reads as `/name args`; harness events are SYSTEM, not turns."""
    s = text.lstrip()
    if s.startswith("<command-"):
        name = re.search(r"<command-name>(.*?)</command-name>", s, re.S)
        args = re.search(r"<command-args>(.*?)</command-args>", s, re.S)
        s = " ".join(x[1].strip() for x in (name, args) if x) or s
    if s.startswith(SYSTEM_TAGS):
        return f"SYSTEM: {clip(s, 120)}", False
    return f"USER: {clip(s, TEXT_CAP)}", True


def git_repo(folder):
    r = subprocess.run(["git", "-C", str(folder), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True)
    common = Path(r.stdout.strip())
    return str(common.parent) if r.returncode == 0 and common.name == ".git" else None


def resolve_repos(cwds):
    """Map each cwd to its main checkout via git's common dir. A deleted worktree is tried from its
    nearest existing parent; failing that, matched by that parent's name to a repo found for another
    session (an orca workspace folder `.../workspaces/<repo>/` names its repo); else the cwd minus any
    .claude/worktrees suffix."""
    found, parents = {}, {}
    for cwd in cwds:
        here = Path(cwd)
        while not here.exists() and here != here.parent:
            here = here.parent
        found[cwd], parents[cwd] = git_repo(here), here
    by_name = {Path(r).name: r for r in found.values() if r}
    return {cwd: found[cwd] or by_name.get(parents[cwd].name) or re.sub(r"/\.claude/worktrees/.*", "", cwd)
            for cwd in cwds}


def digest(path, since):
    lines, title, cwd, start = [], "", "", None
    turns = calls = errors = denials = 0
    for raw in path.open(errors="replace"):
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        t = d.get("type")
        if t == "ai-title":
            title = d.get("aiTitle") or title
        if t not in ("user", "assistant") or d.get("isMeta"):
            continue
        ts = d.get("timestamp")
        if not ts or datetime.fromisoformat(ts.replace("Z", "+00:00")) < since:
            continue
        cwd = cwd or d.get("cwd", "")
        start = start or ts
        content = d["message"].get("content")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for b in content or []:
            bt = b.get("type")
            if bt == "text" and t == "user":
                line, is_turn = user_line(b["text"])
                turns += is_turn
                lines.append(line)
            elif bt == "text":
                lines.append(f"AGENT: {clip(b['text'], TEXT_CAP)}")
            elif bt == "tool_use":
                calls += 1
                lines.append(f"CALL {b.get('name')}: {clip(json.dumps(b.get('input')), INPUT_CAP)}")
            elif bt == "tool_result" and b.get("is_error"):
                body = clip(b.get("content"), ERROR_CAP)
                if DENIAL.match(body):
                    denials += 1
                    lines.append(f"DENIED: {body}")
                else:
                    errors += 1
                    lines.append(f"ERROR: {body}")
    return dict(lines=lines, title=title, cwd=cwd, start=start,
                turns=turns, calls=calls, errors=errors, denials=denials)


def main():
    since, out = parse_since(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    sessions = []
    for path in sorted(PROJECTS.glob("*/*.jsonl")):
        if path.parent.name.startswith("-private-tmp-"):
            continue
        if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < since:
            continue
        s = digest(path, since)
        if s["turns"] == 0 or s["calls"] == 0 or s["lines"][0].startswith(HELPER_PROMPT):
            continue
        sessions.append((path, s))

    repos = resolve_repos({s["cwd"] for _, s in sessions})
    print("digest\trepo\tstart\tuser_turns\ttool_calls\ttool_errors\tdenials\tkb\ttitle")
    written = set()
    for path, s in sessions:
        repo = repos[s["cwd"]]
        name, n = path.stem, 2
        while name in written:  # one session id can log under two project folders
            name, n = f"{path.stem}-{n}", n + 1
        written.add(name)
        dest = out / f"{name}.md"
        header = f"# {s['title'] or path.stem}\nrepo: {repo}\nfolder: {s['cwd']}\nlog: {path}\n\n"
        dest.write_text(header + "\n".join(s["lines"]) + "\n")
        kb = -(-dest.stat().st_size // 1024)  # round up
        print(f"{dest}\t{repo}\t{s['start']}\t{s['turns']}\t{s['calls']}\t{s['errors']}\t{s['denials']}\t{kb}\t{s['title']}")


if __name__ == "__main__":
    main()
