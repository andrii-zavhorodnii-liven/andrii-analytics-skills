---
name: shap-report
description: Build a SHAP HTML report for the CatBoost model(s) published in the current repo — mean|SHAP| share % by feature × model, on one shared holdout sample so columns are comparable. Use when the user asks for SHAP, feature importance, or which features drive a trained model, especially after a retrain or a feature-list change. Only when the working directory is a git repo holding at least one saved `.cbm` model — never outside a repo, and never for a model that isn't saved in it.
---

# SHAP side-by-side report for the repo's published models

One HTML page showing every feature's mean|SHAP| **share %** in every published model,
computed on one **side-by-side** row sample — the exact same holdout rows scored by all
models, hash-verified — so columns are comparable across targets. With one model it is
the same page with one column.

The pipeline has two halves with a JSON contract between them:

- **Compute** (drifts with the repo — write it fresh each run) → `shap-report.json`
- **Render** (stable — ship as-is) → [render_report.py](render_report.py)

## 0. Gate — is there a repo with a model?

- `git rev-parse --show-toplevel` must succeed. If it fails, stop: tell the user this
  report runs inside the repo that owns the model.
- At least one CatBoost model file must exist in it:
  `git ls-files '*.cbm'`, plus `find . -name '*.cbm' -not -path './.venv/*'` for
  untracked artifacts. None found → stop and say so. Don't train one to have something
  to report on.

Done when: repo root known, at least one `.cbm` path listed.

## 1. Resolve the models and data

Load the **published** models — never retrain for this report. The repo is in one of
two layouts:

- **Roster** — `artifacts/roster/<target>*/` dirs, each with `model.cbm` +
  `feature_manifest.json` (targets like roi10…roi40 or inc11…inc46). Features and the
  categorical list come from each manifest.
- **Models only** — `.cbm` files anywhere else, no roster dirs, maybe no manifest. One
  model is the common case: use it. Several → show the list and ask which ones form the
  set. Features: the manifest if one sits next to the model, else read them off the
  model itself (`model.feature_names_`; categoricals from
  `model.get_cat_feature_indices()`). Target name: the model's dir or file stem.

Then, either layout:

- Confirm the feature list is identical across all models; if not, stop and ask the
  user which report they actually want.
- Targets: order strictest-last (ascending threshold); the last one drives the
  right-hand bar chart. One model → one target.
- Data: the repo's current training parquet (ask if ambiguous or stale vs the model
  timestamps). SHAP needs real rows — if the repo has no data the model can score, ask
  the user where it lives; never fabricate or sample synthetic rows.

Done when: N ≥ 1 models loaded, one shared feature list confirmed, data located.

## 2. Compute — write a scratch script

Write a disposable script under `.scratch/`, built on the repo's **current** labeling /
eligibility / split modules (a worked example lives in the creo-score-model repo:
`.scratch/feature-reduction-60/shap_60.py` — load `model.cbm` instead of training).
If the repo has no split code, ask the user which rows count as holdout (e.g. a date
cut) rather than guessing. Invariants the script must keep:

- **Shared sample.** Build each target's holdout with the repo's own split code; sort
  canonically by (ID, TIME) with a stable sort; draw ~25 000 positions with a fixed
  seed; hash the (ID, TIME) keys per target and **assert all hashes equal** — abort
  otherwise. With one model the assertion is trivial; still record the hash.
- **SHAP math.** CatBoost `get_feature_importance(pool, type="ShapValues")`; drop the
  last column (base value); `mean(|·|)` per feature; share % = feature / model total × 100.
- **Memory.** Eligible rows only, float32, `del` + `gc.collect()` between targets.

Write `shap-report.json` matching the contract in [DATA-CONTRACT.md](DATA-CONTRACT.md),
plus a CSV of the same rows. In the models-only layout, set `meta.roster_dir` to the
model's directory.

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
