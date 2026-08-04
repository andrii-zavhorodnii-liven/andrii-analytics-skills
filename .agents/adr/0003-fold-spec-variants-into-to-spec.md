# Fold `pipeline-spec` and `ml-modeling-spec` into `to-spec`

The old `andrii-skills` plugin carried two spec skills this fork never ported: `pipeline-spec` (seven-field spec block for ingestion work) and `ml-modeling-spec` (seven-field spec block for predictive models). The open question was whether they come across as separate front-doors or fold into `to-spec`.

**Decision: fold.** `to-spec`'s Implementation Decisions checklist already carried most of the pipeline fields (grain, source contracts, backfill/idempotency, freshness); the fold added the missing decision items rather than the skills' interview machinery:

- Done signal for a scheduled or backfilled load
- Cost ceiling per run
- The full ML block: target with units and horizon, training population, time-based split policy, prediction-time feature check, baseline-before-training, metric-before-evaluation

What was deliberately dropped: the "spec already, or figure it out together?" opening and the `open:` field protocol. That machinery belongs to the grilling flow — in this repo the interview is `/grill-with-docs` (or `/grill-me`), and `/to-spec` is pure synthesis afterwards. Two spec front-doors per domain would have duplicated that flow and given the router two more near-synonyms to disambiguate.

Consequence: a pipeline or model spec is reached the same way as any other spec — grill first, then `/to-spec` — and the domain-specific rigor lives in one checklist instead of three skills.
