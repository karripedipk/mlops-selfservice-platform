from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

try:
    import mlflow
except Exception:
    mlflow = None


ARTIFACTS_DIR = Path("artifacts")
DATA_PATH = Path("data/train.csv")


def compute_baseline(df: pd.DataFrame, feature_cols: list[str]) -> dict:
    baseline = {"generated_at": datetime.now(timezone.utc).isoformat(), "features": {}}
    for c in feature_cols:
        col = df[c].astype(float)
        baseline["features"][c] = {
            "mean": float(col.mean()),
            "std": float(col.std(ddof=0) if col.std(ddof=0) > 0 else 1.0),
            "p05": float(np.percentile(col, 5)),
            "p50": float(np.percentile(col, 50)),
            "p95": float(np.percentile(col, 95)),
        }
    return baseline


def main() -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    feature_cols = ["year", "odometer", "make_encoded", "model_encoded"]
    target_col = "price"

    X = df[feature_cols]
    y = df[target_col]

    pre = ColumnTransformer(
        transformers=[("num", StandardScaler(), feature_cols)],
        remainder="drop",
    )

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    pipe = Pipeline([("pre", pre), ("model", model)])
    pipe.fit(X, y)

    preds = pipe.predict(X)
    rmse = float(mean_squared_error(y, preds, squared=False))

    model_path = ARTIFACTS_DIR / "model.pkl"
    joblib.dump(pipe, model_path)

    baseline = compute_baseline(df, feature_cols)
    baseline_path = ARTIFACTS_DIR / "baseline.json"
    baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")

    metrics = {"rmse_train": rmse}
    (ARTIFACTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "").strip()
    if tracking_uri and mlflow is not None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("usedcar-price")
        with mlflow.start_run(run_name=f"train-{datetime.utcnow().isoformat()}"):
            mlflow.log_params({"model": "RandomForestRegressor", "n_estimators": 300})
            mlflow.log_metrics({"rmse_train": rmse})
            mlflow.log_artifact(str(model_path))
            mlflow.log_artifact(str(baseline_path))
            mlflow.log_artifact(str(ARTIFACTS_DIR / "metrics.json"))

    print(f"Training complete. RMSE(train)={rmse:.3f}")
    print(f"Artifacts written to: {ARTIFACTS_DIR.resolve()}")


if __name__ == "__main__":
    main()
