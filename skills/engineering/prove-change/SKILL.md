---
name: prove-change
description: Prove a change to a Dataform model, Python pipeline, or training job produces the right data — build it from main and from the branch into dev datasets and diff the outputs, or check it against the spec, in a fresh subagent that never saw your reasoning. Use after any such change before saying it is done, closing a ticket, or opening a PR; when asked "does this actually work?" or "prove it"; or to check a refactor or a migration (scheduled query → Dataform, legacy job → new job) changed nothing it shouldn't.
---

# Prove change

**Proof** means you watched the changed code produce output and compared that output with an **answer key** the builder did not write. A clean `dataform compile`, passing tests and a green dry run are not proof: they show the code runs, not that the data is right.

## Answer keys

A ladder, best first. Use the highest rung that fits each output:

1. **The old version.** The same code on main (the merge-base), or the old system a migration replaces. Run both on the same inputs and diff.
2. **A snapshot.** A saved known-good output — a table copy, committed expected rows — taken from a version the user trusts. It shows "same as before", not "correct".
3. **An independent check.** A test or assertion at the public seam, written by someone other than the agent making this change.
4. **The spec.** Acceptance criteria from the issue or PR, written before the code.
5. **Nothing.** The checker decides what right means. The best verdict this allows is UNPROVEN.

The answer key belongs to the user. When the output and the key disagree, fix the code; changing a snapshot, the spec or the allowed-differences list is the user's call, and until they make it the verdict is BROKEN.

## Verdicts

- **PROVED** — every output compared with its answer key and matched.
- **BROKEN** — an output differs from its key, a break-it probe failed, or a question for the user is still open.
- **BLOCKED** — the check itself could not run: compile failure, auth error, an empty output, a missing table. A check that could not run is never a pass.
- **UNPROVEN** — everything ran and matched, but at least one output had only rung 5.
- **NO OUTPUT** — the change reaches no output (tests or docs only), so there is nothing to prove.

## Steps

### 1. Scope

```bash
BASE=$(git merge-base HEAD origin/main)
git diff --name-only "$BASE"              # committed + uncommitted
git ls-files --others --exclude-standard  # new files
```

Map each changed file to the outputs it reaches: the Dataform tables it defines plus their dependents in the compiled graph, the table or file a Python job writes, a training job's model and metrics. For consumers outside the repo, call the Skill tool with "blast-radius". When nothing is reached, the verdict is NO OUTPUT: report it and stop.

Done when every changed file maps to its outputs, or to "reaches nothing".

### 2. Sort each output and pick its key

- **Existing output the change touched** → the old version (rung 1): main's code. The expected differences come from the spec; every other difference is BROKEN.
- **New output that copies an existing one** (a Dataform model replacing a scheduled query, a `_v2` table) → parity with the original (rung 1). If this change also edited the original, add the spec: both sides can be wrong the same way and still match.
- **New output that copies nothing** → the spec (rung 4). Find it in the PR body and the issue it closes (`gh pr view --json body,closingIssuesReferences`), issue numbers in the commit messages, or a spec file under `.scratch/` or `docs/`. The request that asked for the change says what was built, not what right looks like. No spec → ask the user; none exists → rung 5.
- **Training job** → the comparison is a metric, not rows: call the Skill tool with "check-result-before-reporting" for that output.

Rung-1 outputs get a **base side** and a **branch side**; every other output gets a branch side only. Write the allowed differences down before you build: run timestamps, surrogate ids, and the behaviour the change is meant to alter. Keep the list short; every entry hides a diff.

Done when every output from step 1 has its key, its sides, and the allowed differences written down.

### 3. Build into dev

1. **Check access, not presence.** For every credential and target the run needs, make one cheap real call first (`bq ls <dev_dataset>`, `gcloud auth print-access-token`). A variable that is set but empty, or an expired token, should surface now, not forty minutes in.
2. **Pick a suffix per side** — `base_<short sha>`, `branch_<short sha>` — and a `--vars` date window if the repo has one. Both sides use the same window.
3. **Clone the inputs.** A schema suffix rewrites every `ref()` to a Dataform table, including upstream tables this run won't build; declarations keep their real names. Per side, list them from the compiled graph:
   ```bash
   dataform compile --json --schema-suffix <suffix>
   ```
   Before anything is written, create every suffixed dataset this side will use — the schemas of the actions you will run and of the tables you will clone — with a one-day expiry, so whatever cleanup misses deletes itself:
   ```bash
   bq mk --dataset --default_table_expiration 86400 p:core_<suffix>
   ```
   Then take the `dependencyTargets` of the actions you will run, minus the targets those actions build and minus declarations, and clone each real table into its suffixed dataset: ``CREATE TABLE `p.core_<suffix>.up` CLONE `p.core.up` ``. BigQuery can't clone a view, a materialized view or an external table; for those, create a view over the real one instead: ``CREATE VIEW `p.core_<suffix>.v` AS SELECT * FROM `p.core.v` ``. Both sides point at the same real objects, so they read identical inputs.
4. **Build each side:**
   - **Dataform** — the base side from a worktree (`git worktree add <scratch>/base "$BASE"`), the branch side from the checkout: `dataform run --actions <changed> --include-dependents --schema-suffix <suffix> --vars <window>`. `.df-credentials.json` is gitignored, so the worktree has none: on the base side add `--credentials <checkout>/.df-credentials.json`.
   - **Python job** — `uv run` with its output pointed at the side's dev dataset.
   - **Old system outside the repo** (a scheduled query a migration replaces) — get its SQL (`bq show --transfer_config <config>`) and run it into the base dataset over the window, passing the values a scheduled run would get as parameters (`--parameter=run_date:DATE:<date>`). A plain `SELECT` takes `bq query --use_legacy_sql=false --destination_table <project>:<dataset>_base_<sha>.<table> < old.sql`. A query that writes its own table (`INSERT`, `MERGE`, `CREATE`, a multi-statement script) names its target inside the SQL: rewrite that target to the base dataset and run it without `--destination_table`. A comparison with the live production table mixes a different run time and different inputs into the diff.

   A production destination is never a target here.
5. **Print identity** for each side: project, dataset, commit.

Done when every side step 2 asked for exists, each with its row count printed.

### 4. Compare in a fresh checker

The builder sees what it meant to build. Hand steps 4 and 5 to a fresh subagent (Agent tool, `general-purpose`) with only: the outputs and their dev table names per side, how each was sorted, its answer key, the allowed differences, and the name of this skill. Leave out your plan and your reasoning. If you can't start a subagent, compare yourself and write `Checker: same agent (not independent)` in the report.

The checker runs, per output:

- **Every side has rows**, and a row you know exists is present. An empty diff between two empty tables proves nothing; zero rows from an assertion on an empty or wrong partition proves nothing. Either is BLOCKED.
- **Row count and key uniqueness** on each side.
- **Against the old version** (rung 1 only): schema diff from `INFORMATION_SCHEMA.COLUMNS`; `EXCEPT DISTINCT` in both directions on the shared columns, minus the allowed differences, with 20 sample rows from each direction; totals of the key metrics by the main slices (date, market, platform).
- **Against the spec**: one query per acceptance criterion.

Done when every output has a result for each check that applies to it, with the query behind it.

### 5. Try to break it

After the comparison passes, the checker runs one probe that matches the change: an incremental model run twice (row count stable?), a late-arriving day, a NULL or duplicate key in the source, an empty source partition. Done when the probe ran and its result is in the report; a failed probe is BROKEN.

### 6. If it is BROKEN

The findings — failing check, the key it was compared with, the evidence — go back to the builder, who fixes the code as the Answer keys section says. Rebuild the branch side and rerun steps 4–5 in a fresh checker. Stop after 3 rounds and report what is still BROKEN. BLOCKED is not a fix-loop case: report it.

### 7. Report and clean up

```
<PROVED | BROKEN | BLOCKED | UNPROVEN | NO OUTPUT>: <what was proved, one line>
Couldn't prove: <each output, why, and what would cover it — "nothing" only if every output has a passing check>
Evidence: <row counts per side, diff sizes, key totals, the probe, the queries>
Answer keys: <each output → its key and rung>
Checker: fresh subagent | same agent (not independent)
```

"Couldn't prove" comes first, even on PROVED: a pass that hides what it skipped reads as full coverage. Put the queries next to the results — in the PR, or the ticket's closing comment.

Then drop the suffixed datasets this run created (by their suffix, nothing else) and remove the base worktree.
