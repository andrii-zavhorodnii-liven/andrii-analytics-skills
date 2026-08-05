---
name: shap-report
description: Build the SHAP side-by-side HTML report for the current repo's published model roster (mean|SHAP| share % by feature × target, shared holdout sample).
disable-model-invocation: true
---

# SHAP side-by-side report for the current roster

One HTML page showing every roster feature's mean|SHAP| **share %** in every roster
model, computed on one **side-by-side** row sample — the exact same holdout rows scored
by all models, hash-verified — so columns are comparable across targets. Works in any
repo with the roster convention: `artifacts/roster/<target>*/` dirs each holding
`model.cbm` + `feature_manifest.json` (targets like roi10…roi40 or inc11…inc46).

The pipeline has two halves with a JSON contract between them:

- **Compute** (drifts with the repo — write it fresh each run) → `shap-report.json`
- **Render** (stable — ship as-is) → [render_report.py](render_report.py)

## 1. Resolve the roster and data

Load the **published** models — never retrain for this report.

- Models: `artifacts/roster/*/model.cbm`, features + categorical list from each fit's
  `feature_manifest.json`. Confirm the feature list is identical across all targets; if
  not, stop and ask the user which report they actually want.
- Targets: order strictest-last (ascending threshold); the last one drives the
  right-hand bar chart.
- Data: the repo's current training parquet (ask if ambiguous or stale vs the roster
  timestamps).

Done when: N models loaded, one shared feature list confirmed, parquet located.

## 2. Compute — write a scratch script

Write a disposable script under `.scratch/`, built on the repo's **current** labeling /
eligibility / split modules (a worked example lives in the creo-score-model repo:
`.scratch/feature-reduction-60/shap_60.py` — load `model.cbm` instead of training).
Invariants the script must keep:

- **Shared sample.** Build each target's holdout with the repo's own split code; sort
  canonically by (ID, TIME) with a stable sort; draw ~25 000 positions with a fixed
  seed; hash the (ID, TIME) keys per target and **assert all hashes equal** — abort
  otherwise.
- **SHAP math.** CatBoost `get_feature_importance(pool, type="ShapValues")`; drop the
  last column (base value); `mean(|·|)` per feature; share % = feature / model total × 100.
- **Memory.** Eligible rows only, float32, `del` + `gc.collect()` between targets.

Write `shap-report.json` matching the contract in [DATA-CONTRACT.md](DATA-CONTRACT.md),
plus a CSV of the same rows.

Done when: the JSON validates against the contract, the hash assertion passed, and the
logged per-model Σmean|SHAP| totals are all nonzero.

## 3. Render

```bash
uv run python <this skill's base directory>/render_report.py shap-report.json --out .scratch/shap-report-<date>.html
```

Optionally pass `--baseline <previous shap-report.json>` to add the Σ-baseline and Δ
columns (rank change vs a prior roster or feature list).

Done when: the HTML opens, both bar charts and the table render, the sort selector
reorders all three, and the header stats (features, zero-in-every-model, used-in-all-N)
match the JSON. Tell the user the file path and the top-5 features by Σ share.
