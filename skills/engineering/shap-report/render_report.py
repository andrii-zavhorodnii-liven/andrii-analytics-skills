"""Render the SHAP side-by-side HTML report from a shap-report.json (see DATA-CONTRACT.md).

    uv run python render_report.py shap-report.json --out report.html [--baseline prev.json]

Targets are strings (roi10, inc11, ...), ordered strictest-last in meta.targets;
baseline comparison optional.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CSS = """
  :root {
    --bg: #0f1115; --panel: #171a21; --text: #e8eaed; --muted: #9aa0a6;
    --border: #2a2f3a; --accent: #6b9fff; --warn: #c9a227;
    --bar-sum: #6b9fff; --bar-strict: #9aa0a6;
    --info-bg: #1a2333; --warn-row: #2a2418; --info-row: #182033;
  }
  * { box-sizing: border-box; }
  body { margin: 0; font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: var(--bg); color: var(--text); }
  main { max-width: 1280px; margin: 0 auto; padding: 24px; }
  h1 { font-size: 22px; font-weight: 600; margin: 0 0 6px; }
  h2 { font-size: 16px; font-weight: 600; margin: 0 0 8px; }
  .muted { color: var(--muted); font-size: 12px; }
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; }
  .stat { background: var(--panel); border: 1px solid var(--border);
          border-radius: 8px; padding: 12px 14px; }
  .stat .v { font-size: 22px; font-weight: 600; }
  .stat .l { color: var(--muted); font-size: 12px; margin-top: 2px; }
  .stat.warn .v { color: var(--warn); }
  .stat.info .v { color: var(--accent); }
  .controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin: 12px 0 16px; }
  select { background: var(--panel); color: var(--text); border: 1px solid var(--border);
           border-radius: 6px; padding: 8px 10px; min-width: 280px; }
  .callout { background: var(--info-bg); border: 1px solid var(--border); border-radius: 8px;
             padding: 12px 14px; margin-bottom: 20px; font-size: 13px; color: var(--muted); }
  .callout strong { color: var(--text); }
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .chart-panel { background: var(--panel); border: 1px solid var(--border);
                 border-radius: 8px; padding: 12px; }
  .chart-scroll { max-height: 70vh; overflow: auto; padding-right: 4px; }
  .bar-row { display: grid; grid-template-columns: 220px 1fr 52px;
             gap: 8px; align-items: center; margin: 2px 0; font-size: 11px; }
  .bar-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
               color: var(--text); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  .bar-track { height: 12px; background: #222733; border-radius: 2px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 2px; }
  .bar-fill.sum { background: var(--bar-sum); }
  .bar-fill.strict { background: var(--bar-strict); }
  .bar-val { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
  table { width: 100%; border-collapse: collapse; font-size: 12px;
          background: var(--panel); border: 1px solid var(--border); border-radius: 8px; }
  th, td { padding: 6px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }
  th { position: sticky; top: 0; background: #1c212b; text-align: right;
       color: var(--muted); font-weight: 600; z-index: 1; }
  th:nth-child(3), td:nth-child(3) { text-align: left; }
  td { text-align: right; font-variant-numeric: tabular-nums; }
  td.feat { text-align: left; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  tr.warn { background: var(--warn-row); }
  tr.info { background: var(--info-row); }
  .table-wrap { max-height: 70vh; overflow: auto; border-radius: 8px; }
  @media (max-width: 960px) {
    .charts { grid-template-columns: 1fr; }
    .stats { grid-template-columns: 1fr 1fr; }
  }
"""

JS = """
function fmtShare(v) { return v === 0 ? "\\u2014" : v.toFixed(2); }
function fmtDelta(v) {
  if (v === null || v === undefined) return "\\u2014";
  return (v > 0 ? "+" : "") + v.toFixed(2);
}

function sortFeatures(rows, key) {
  const copy = rows.slice();
  if (key === "sum") {
    copy.sort((a, b) => b.sum_share - a.sum_share || a.feature.localeCompare(b.feature));
  } else if (key === "strict") {
    copy.sort((a, b) => b.strictest_share - a.strictest_share
                        || a.feature.localeCompare(b.feature));
  } else if (key === "baseline") {
    copy.sort((a, b) => (b.share_delta ?? -1e9) - (a.share_delta ?? -1e9)
                        || a.feature.localeCompare(b.feature));
  } else {
    copy.sort((a, b) => b.used - a.used ||
      Math.max(...b.shares) - Math.max(...a.shares) || a.feature.localeCompare(b.feature));
  }
  return copy;
}

function renderBars(el, rows, valueKey, cls) {
  const max = Math.max(...rows.map(r => r[valueKey]), 0.0001);
  el.innerHTML = rows.map(r => {
    const v = r[valueKey];
    const pct = (v / max) * 100;
    return `<div class="bar-row">
      <div class="bar-label" title="${r.feature}">${r.id}. ${r.feature}</div>
      <div class="bar-track"><div class="bar-fill ${cls}" style="width:${pct}%"></div></div>
      <div class="bar-val">${fmtShare(v)}</div>
    </div>`;
  }).join("");
}

function renderTable(rows) {
  document.getElementById("tbody").innerHTML = rows.map((r, i) => {
    const cls = r.used === 0 ? "warn" : r.used === N_MODELS ? "info" : "";
    const cells = r.shares.map(fmtShare).join("</td><td>");
    const base = HAS_BASELINE
      ? `<td>${fmtShare(r.sum_share_base ?? 0)}</td><td>${fmtDelta(r.share_delta)}</td>` : "";
    return `<tr class="${cls}">
      <td>${i + 1}</td><td>${r.id}</td><td class="feat">${r.feature}</td>
      <td>${r.used}</td><td>${fmtShare(r.sum_share)}</td>
      <td>${cells}</td>${base}
    </tr>`;
  }).join("");
}

function render() {
  const sel = document.getElementById("sortBy");
  const key = sel.value;
  const sorted = sortFeatures(FEATURES, key);
  document.getElementById("chartTitle").textContent =
    `All ${FEATURES.length} features \\u2014 sorted by ${sel.selectedOptions[0].textContent}`;
  renderBars(document.getElementById("chartSum"), sorted, "sum_share", "sum");
  renderBars(document.getElementById("chartStrict"), sorted, "strictest_share", "strict");
  renderTable(sorted);
}

document.getElementById("sortBy").addEventListener("change", render);
render();
"""


def join_baseline(rows: list[dict], baseline_path: Path | None) -> bool:
    if baseline_path is None:
        return False
    base = json.loads(baseline_path.read_text())
    ref = {r["feature"]: r["sum_share"] for r in base["features"]}
    for r in rows:
        s = ref.get(r["feature"])
        r["sum_share_base"] = round(s, 4) if s is not None else None
        r["share_delta"] = round(r["sum_share"] - s, 4) if s is not None else None
    return True


def html(meta: dict, rows: list[dict], has_baseline: bool) -> str:
    targets = meta["targets"]
    n = len(targets)
    strict = targets[-1]
    zero = [r for r in rows if r["used"] == 0]
    alln = [r for r in rows if r["used"] == n]
    trees = " · ".join(f"{k}: {v}" for k, v in meta["trees"].items())
    roi_th = "".join(f"<th>{t}</th>" for t in targets)
    base_th = "<th>Σbase</th><th>Δ</th>" if has_baseline else ""
    base_opt = ('<option value="baseline">Σ share change vs baseline</option>'
                if has_baseline else "")
    if has_baseline:
        deltas = [r for r in rows if r.get("share_delta") is not None]
        n_up = sum(1 for r in deltas if r["share_delta"] > 0)
        base_stat = (f'<div class="stat info"><div class="v">{n_up}/{len(deltas)}</div>'
                     f'<div class="l">Gained Σ share vs baseline</div></div>')
        base_note = ("<br><br><strong>Σbase / Δ</strong> compare each feature's "
                     "Σ share to the baseline report. Share % is within-model, so a "
                     "changed feature list mechanically shifts everyone's share — read "
                     "Δ as where the weight moved, not raw importance change.")
    else:
        base_stat = (f'<div class="stat"><div class="v">{meta["sample_rows"]:,}</div>'
                     f'<div class="l">Shared sample rows</div></div>')
        base_note = ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>SHAP share % by feature × target — {meta['roster_dir']}</title>
<style>{CSS}</style>
</head>
<body>
<main>
  <h1>SHAP share % by feature × target</h1>
  <p class="muted">
    Roster: <code>{meta['roster_dir']}</code> · cut {meta['cut']} · shared holdout
    sample n={meta['sample_rows']:,} · each model column is that feature's % of the
    model's total mean |SHAP| · Sum is Σ of those shares across all {n} targets
  </p>

  <div class="stats">
    <div class="stat"><div class="v">{meta['n_features']}</div><div class="l">Features</div></div>
    <div class="stat warn"><div class="v">{len(zero)}</div>
      <div class="l">Zero in every model</div></div>
    <div class="stat info"><div class="v">{len(alln)}</div>
      <div class="l">Used in all {n}</div></div>
    {base_stat}
  </div>

  <div class="controls">
    <label for="sortBy"><strong>Sort by</strong></label>
    <select id="sortBy">
      <option value="sum">Sum of share % (all models)</option>
      <option value="strict">{strict} share %</option>
      <option value="used">Used in N models</option>
      {base_opt}
    </select>
  </div>

  <div class="callout">
    <strong>How to read.</strong> Share % is within-model. Sum adds those percentages across
    the {n} models (max {n}00%). The selected sort controls both charts and the table.
    Table <strong>#</strong> is the row counter. <strong>ID</strong> is a fixed alphabetical
    feature ID that also prefixes chart labels. Dash = exact zero.{base_note}
  </div>

  <h2 id="chartTitle">All {meta['n_features']} features</h2>
  <p class="muted">Both charts use the same features in the same order. X-axes scale
    independently.</p>
  <div class="charts">
    <div class="chart-panel">
      <h2>Σ share % across all {n} models</h2>
      <p class="muted">Y-axis: feature · X-axis: Σ within-model SHAP share %</p>
      <div class="chart-scroll" id="chartSum"></div>
    </div>
    <div class="chart-panel">
      <h2>{strict} within-model share %</h2>
      <p class="muted">Y-axis: feature · X-axis: {strict} SHAP share %</p>
      <div class="chart-scroll" id="chartStrict"></div>
    </div>
  </div>
  <p class="muted" style="margin-top:-12px;margin-bottom:24px">
    Source: CatBoost ShapValues · shared {meta['sample_rows']:,}-row holdout sample
    ({meta.get('eval_window', 'see meta')}, identical rows for all {n} targets,
    hash-verified) · trees per model: {trees}.
  </p>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th><th>ID</th><th>Feature</th><th>Used</th><th>Sum</th>
          {roi_th}
          {base_th}
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</main>
<script>
const FEATURES = {json.dumps(rows)};
const N_MODELS = {n};
const HAS_BASELINE = {json.dumps(has_baseline)};
{JS}
</script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Render SHAP side-by-side report")
    p.add_argument("src", type=Path, help="shap-report.json (see DATA-CONTRACT.md)")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--baseline", type=Path, default=None,
                   help="previous shap-report.json for Σbase/Δ columns")
    args = p.parse_args()

    payload = json.loads(args.src.read_text())
    meta, rows = payload["meta"], payload["features"]
    has_baseline = join_baseline(rows, args.baseline)
    args.out.write_text(html(meta, rows, has_baseline))
    print(f"Wrote {args.out} ({args.out.stat().st_size:,} bytes, {len(rows)} features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
