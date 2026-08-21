# Wayfinding operations, per tracker

How the map, its child tickets, blocking, and frontier queries are physically expressed. **GitHub Issues** is the default; **local markdown** is the fallback for a repo with no git remote.

## GitHub Issues (default)

Drive everything with the `gh` CLI — it infers the repo from `git remote` when run inside a clone.

- **Map**: a single issue labelled `wayfinder:map`, holding the Destination / Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`).
- **Blocking**: GitHub's **native issue dependencies** — the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only — the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me` — the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then append a context pointer (gist + link) to the map's Decisions-so-far. Whether to also `gh issue close <n>` follows the fact-vs-judgment rule in SKILL.md's "Record the resolution": close a verifiable fact; a judgment stays open and assigned with its comment starting `Pending verdict:` — the human closes it to ratify. (Its children stay blocked either way: the dependency gate counts open blockers, and its assignee keeps it off the frontier.)

## Local markdown (no remote)

- **Map**: `.scratch/<effort>/map.md` — the Destination / Notes / Decisions-so-far / Fog body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`pending-verdict`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved` — `pending-verdict` does not unblock.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`. Status follows the fact-vs-judgment rule in SKILL.md's "Record the resolution": a verifiable fact gets `Status: resolved`; a judgment gets `Status: pending-verdict`, and the human sets it to `resolved` to ratify.
