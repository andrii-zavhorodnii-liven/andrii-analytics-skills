---
name: check-result-before-reporting
description: Check a measured result before you report or act on it — an A/B lift, a metric moving week over week, a model's AUC after a retrain, a query's cost or runtime saving. Use before a number goes into a report, a PR, a decision, or a stakeholder message, or when the user asks "is this real?" or "is this significant?".
---

# Check result before reporting

A result is **checked** when you can say what it measured, what bounds it, and that the gap beats the noise. Until then it is a draft, not a finding.

A quick ballpark the user asked for needs only question 1; say it is a single unchecked number.

## Before you measure

1. **Write the claim you would ship**, in the words you would ship it: "variant B lifts checkout conversion by 1.8 pp over 14 days, all markets". The questions below test that sentence.
2. **Name the decision threshold**: the smallest effect that would change what someone does.
3. **Name the noise floor**: how much this number moves when nothing changed — the day-to-day spread of the metric over the last few weeks, the seed-to-seed spread of a retrain, the run-to-run spread of a query's slot time. If the noise floor is bigger than the threshold, say so before running anything.

## The questions

1. **Did it happen?** The work ran on what you think it ran on. The partition filter and date range applied (row counts per side). The join neither fanned out nor dropped rows (counts before and after, key uniqueness). The variant reached users (exposure counts per arm). The model was scored on the holdout, not the training rows. The query read data instead of the cache (`cacheHit` in the job statistics). Nothing failed quietly: count failed Cloud Run job attempts, rows `SAFE_CAST` turned to NULL, rejected or skipped inserts — a run that half-failed still prints a number.
2. **Is it beyond the noise?** Compare the gap to the noise floor, on the right unit.
   - A/B: a confidence interval on the randomisation unit (user, not event), and a sample-ratio-mismatch check.
   - Retrain: at least 3 seeds, or a bootstrap interval over the holdout, on the same split for both models.
   - Week over week: against the same weekdays in earlier weeks.
   A gap inside the spread is **no measurable difference**.
3. **Why not double?** Name what bounds the number. For a lift, the share of users the change could reach: a change on a screen 20% of users see cannot move total conversion by more than that share allows. For a model gain, the features or rows that changed. For cost or speed, the stage that dominates (bytes processed, slot-milliseconds, the slowest step). If you can't say why it isn't twice as big, you don't know what you measured.
4. **What carries it?** Decompose the number by its main slices — market, platform, new vs returning, model segment. If one slice carries the whole effect, the claim is about that slice.
5. **What else could it be measuring?** Rule out each with evidence: a tracking or logging change, a late-arriving partition, a definition change in an upstream Dataform model, seasonality or a holiday, a mix shift between segments (Simpson's paradox), leakage (a feature computed after the label time), populations of different shape on the two sides.
6. **Does it matter?** Put it in the units the decision uses. Absolute next to relative (+20% of a 0.5% rate is 0.1 pp). Share of the total revenue, users, or cost. End to end: a staging model that runs 40% faster saves nothing if another step dominates the pipeline's runtime.

## Report

- Lead with the verdict: **real**, **no measurable difference**, or **inconclusive**.
- Then the number with its unit, the comparison, the interval and how it was computed, the sample size, and the slice that carries it. For example: "Variant B +1.8 pp conversion (95% CI 0.6 to 3.0), 41k users per arm, no sample-ratio mismatch; 80% of the lift comes from new iOS users."
- Call it inconclusive when question 1 or 2 could not be checked, or the effect could not be decomposed. Name the gap.
- Keep the queries behind each answer next to the number — in the analysis file, the notebook, or the PR — so anyone can rerun them.

Done when every question has a query or run behind its answer, or is marked unchecked with the reason.
