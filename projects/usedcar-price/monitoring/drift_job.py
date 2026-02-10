from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from jinja2 import Template
from scipy.stats import ks_2samp


HTML_TEMPLATE = Template(
    """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Drift Report</title></head>
<body>
<h2>Drift Report</h2>
<p><b>Overall drift detected:</b> {{ overall }}</p>
<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Feature</th><th>KS p-value</th><th>Drift</th></tr>
{% for row in rows %}
<tr><td>{{ row.feature }}</td><td>{{ "%.6f"|format(row.pvalue) }}</td><td>{{ row.drift }}</td></tr>
{% endfor %}
</table>
</body>
</html>"""
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, help="Path to baseline.json")
    ap.add_argument("--current", required=True, help="Path to current.csv (must include feature cols)")
    ap.add_argument("--out", required=True, help="Output HTML report path")
    ap.add_argument("--alpha", type=float, default=0.05, help="KS test alpha")
    args = ap.parse_args()

    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    df = pd.read_csv(args.current)

    rows = []
    overall = False
    for feature, stats in baseline["features"].items():
        if feature not in df.columns:
            continue
        cur = df[feature].astype(float).values
        # generate a synthetic baseline sample from mean/std as approximation
        base = np.random.normal(loc=stats["mean"], scale=max(stats["std"], 1e-6), size=min(len(cur) * 5, 5000))
        res = ks_2samp(base, cur)
        drift = bool(res.pvalue < args.alpha)
        overall = overall or drift
        rows.append({"feature": feature, "pvalue": float(res.pvalue), "drift": drift})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(HTML_TEMPLATE.render(rows=rows, overall=overall), encoding="utf-8")
    print(f"Wrote drift report: {out.resolve()}")


if __name__ == "__main__":
    main()
