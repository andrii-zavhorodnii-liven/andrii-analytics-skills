Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools

Both buckets are **promoted**: every skill in them must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`'s `skills` array (the Claude Code plugin ships exactly the promoted set). This repo carries no unpromoted buckets — a skill that isn't ready to ship doesn't land on `main`.

The repo is also its own single-plugin Claude Code marketplace: `.claude-plugin/marketplace.json` lists the one `andrii-analytics-skills` plugin. When bumping the release version, keep `.claude-plugin/plugin.json`'s `version` in sync with `package.json`'s — Claude uses the plugin `version` to decide when installed users see an update. Run `claude plugin validate . --strict` after touching either manifest.

Bump the version by hand in both files, in the same commit — the `@changesets/cli` tooling in `package.json` is inherited from the upstream fork and is unused here. Bump the **minor** for anything installed users should receive: a new skill, or a change to how an existing one behaves. Leave it alone for repo-only edits (this file, an ADR, a `README.md` wording pass). One bump can carry several changes, so a skill can sit unbumped for a while — but "released" means the number moved, and until it does the change reaches nobody. Why a Claude plugin but not (yet) a Codex one lives in [.agents/adr/0002-ship-as-a-claude-code-plugin.md](./.agents/adr/0002-ship-as-a-claude-code-plugin.md).

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, with the skill name linked to its `SKILL.md`. Both bucket `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**.

Every `SKILL.md` is either user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, reachable only by the human) or model-invoked (model- or user-reachable). See [.agents/invocation.md](./.agents/invocation.md).

## The working context these skills target

The skills assume a **data platform**, not a web app. When writing or editing a skill, draw examples from this stack and no other:

- **Warehouse**: BigQuery, with transformations in **Dataform** — SQLX definitions, `config` blocks, assertions, tags, the dependency graph
- **Pipelines**: Python managed with **uv**, deployed as Cloud Run jobs/services
- **ML**: **Vertex AI** — training jobs, pipelines, model registry, endpoints
- **Analytics**: metric definitions, ad-hoc analysis, dashboards, stakeholder-facing reporting

Do not introduce frontend examples (React, CSS, browsers, component trees) or Node/TypeScript tooling examples. When a skill needs a concrete illustration, reach for a BigQuery table, a Dataform model, a Python ingestion job, a Vertex AI training run, or a metric definition.

## Issue tracker

These skills track work in **GitHub Issues** via the `gh` CLI, by convention — no per-repo config file or setup step. A repo with no git remote falls back to local markdown under `.scratch/`. Triage labels are the five canonical role names verbatim. Skills that touch the tracker state the convention inline; `/wayfinder` keeps the heavier per-tracker operations in [trackers.md](./skills/engineering/wayfinder/trackers.md).

## Router

[`ask-andrii`](./skills/engineering/ask-andrii/SKILL.md) is the router that maps every user-reachable skill and how they relate. Whenever you add, rename, remove, or change how a user-reachable skill fits the flows, re-read `ask-andrii`'s `SKILL.md` and update it so the map stays accurate — a new skill it never mentions, or a stale one it still routes to, is a router that lies.

To (re)link every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current; re-run the script after adding, removing, or renaming a skill.
