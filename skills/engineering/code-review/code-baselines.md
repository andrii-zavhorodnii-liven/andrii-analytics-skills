# Code baselines

The two baselines the Standards axis carries on the **code branch** of `SKILL.md` step 3. Neither applies to skill markdown — that branch reaches for `writing-for-agents` instead.

Two rules bind both:

- **The repo overrides.** A documented repo standard always wins; where it endorses something a baseline would flag, suppress it.
- **Always a judgement call.** Each item is a labelled heuristic ("possible Feature Envy"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

## Smell baseline

A fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Each reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

## Data baseline

The failure modes that are cheap to introduce here and expensive to discover in production.

- **Unbounded scan** — a query over a partitioned table with no partition filter, or a `SELECT *` on a wide table. → add the filter; select the columns you need.
- **Unenforced grain** — a new or changed output table whose grain isn't guaranteed by a `uniqueKey` or an assertion. → add the assertion; a grain in a comment isn't a grain.
- **Silent full refresh** — an incremental model changed in a way that quietly forces or breaks a full rebuild. → make the intent explicit and say what it costs.
- **Non-idempotent write** — a load path where re-running a partition duplicates or loses rows. → make the write replace or merge on a key.
- **Hidden clock dependency** — `CURRENT_DATE()` / `datetime.now()` inside logic, so the same input produces different output tomorrow. → pass the date in as a parameter.
- **Leakage** — a feature or label computed from information not available at prediction time. → recompute it as of the prediction timestamp.
- **Hardcoded identifiers** — a project, dataset, or bucket name inline instead of resolved from config or `workflow_settings.yaml`. → move it to config.
- **Fan-out join** — a join whose other side isn't unique on the join key, silently duplicating rows before an aggregate. → verify or enforce uniqueness on that side; `DISTINCT` after the fact masks it, it doesn't fix it.
- **Silent population filter** — a `WHERE` clause or join condition that quietly drops a segment the metric claims to cover (an inner join standing in for a left join, a status filter excluding edge states). → make the exclusion explicit and intended, or widen the join.
- **NULL-blind aggregate** — a ratio or aggregate whose numerator and denominator treat NULLs differently, or where `COUNT(col)` vs `COUNT(*)` changes the answer. → decide what a NULL means here and encode it.
- **Temporal boundary error** — an off-by-one date range, an incomplete trailing period presented as complete, or a window mixing event time with ingestion time. → pin the boundary semantics and exclude or label the partial edge.
