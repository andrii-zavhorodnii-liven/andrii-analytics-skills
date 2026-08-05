# shap-report.json contract

The compute script writes this; `render_report.py` reads it. Shares are percentages
(0–100), rounded to 4 decimals. `targets` are ordered strictest-last; the last one
drives the right-hand bar chart.

```json
{
  "meta": {
    "targets": ["roi10", "roi15", "roi20", "roi25", "roi30", "roi35", "roi40"],
    "sample_rows": 25000,
    "holdout_key_hash": 1234567890,
    "trees": {"roi10": 812, "roi15": 790},
    "cut": "2026-08-05 00:00:00",
    "n_features": 60,
    "roster_dir": "artifacts/roster",
    "eval_window": "2026-07-29 → 08-04"
  },
  "features": [
    {
      "feature": "spend_slope_24h",
      "id": 41,
      "used": 7,
      "shares": [3.1, 2.9, 3.4, 3.0, 2.8, 2.7, 2.5],
      "sum_share": 20.4,
      "strictest_share": 2.5,
      "mean_abs": [0.0123, 0.0119, 0.0131, 0.0118, 0.011, 0.0105, 0.0098]
    }
  ]
}
```

Rules:

- `shares` / `mean_abs` are ordered by `meta.targets`.
- `id` is a fixed **alphabetical** feature ID (1…n), stable across sorts.
- `used` counts models where the share is > 0.
- `features` sorted by `-sum_share`, then feature name.
- `strictest_share` = the last target's share (kept explicit so render needs no lookup).
- `eval_window` is a human-readable description of the holdout dates, shown in the footer.
