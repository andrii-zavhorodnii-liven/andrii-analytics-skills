---
name: retrain-proof
description: Make every training run retrain-proof. Use whenever writing or running a script that trains a model (CatBoost/sklearn probe, grid or gate-cell sweep, Vertex AI experiment) — before the first fit call, even for a "quick" scratchpad probe.
---

# Retrain-proof training runs

A run is **retrain-proof** when every follow-up question — precision/recall, a new threshold sweep, a slice decomposition, a calibration check — can be answered from its saved artifacts alone. A metrics-only JSON is not retrain-proof: it forces a data reload and a refit for any metric nobody thought to compute the first time.

## What every training script persists, next to its metrics output

1. **Scored evaluation rows** (parquet): the entity id, timestamp, label, and score, plus whatever value/cost columns the run's business metric is computed from. This is the artifact that makes follow-ups free — typically megabytes, seconds to write.
2. **The trained model file** (e.g. `model.save_model(...)` for CatBoost, `joblib.dump` for sklearn) so new populations can be scored without refitting.
3. **The exact population definition** in the metrics output: filters, gates, split dates, feature list or a pointer to it — enough to reproduce the rows.

For a sweep or grid, this applies per cell — a cached cell whose scores were never saved is a retrain waiting to happen.

Completion criterion: from the output directory alone — no data reload, no refit — a new metric can be computed on the evaluation set. A run that fails this check is unfinished, however good its headline numbers.

## Where artifacts go

Next to the run's metrics output, whatever that location is — a repo `artifacts/` dir, the run's output directory, or the scratchpad for a throwaway probe. Scratchpad runs are the ones that get re-asked about, so they follow the same rule.
