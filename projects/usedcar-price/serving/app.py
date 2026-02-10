from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import boto3
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    year: int = Field(..., ge=1980, le=2035)
    odometer: float = Field(..., ge=0)
    make_encoded: int = Field(..., ge=0)
    model_encoded: int = Field(..., ge=0)


@dataclass
class ModelBundle:
    model: Any
    baseline: dict


def download_s3_uri(uri: str, out_path: Path) -> None:
    # uri format: s3://bucket/key
    assert uri.startswith("s3://")
    _, _, rest = uri.partition("s3://")
    bucket, _, key = rest.partition("/")
    s3 = boto3.client("s3")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(out_path))


def get_model_uri_from_ssm(param_name: str) -> str:
    ssm = boto3.client("ssm")
    resp = ssm.get_parameter(Name=param_name)
    return resp["Parameter"]["Value"]


def load_bundle() -> ModelBundle:
    local_model_path = os.getenv("MODEL_LOCAL_PATH", "").strip()
    s3_model_uri = os.getenv("MODEL_S3_URI", "").strip()
    ssm_param = os.getenv("MODEL_POINTER_PARAM", "").strip()

    model_path = Path("/tmp/model.pkl")
    baseline_path = Path("/tmp/baseline.json")

    if local_model_path:
        model_path = Path(local_model_path)
        baseline_path = model_path.parent / "baseline.json"
    else:
        if not s3_model_uri and ssm_param:
            s3_model_uri = get_model_uri_from_ssm(ssm_param)

        if not s3_model_uri:
            raise RuntimeError("No model source configured. Set MODEL_LOCAL_PATH or MODEL_S3_URI or MODEL_POINTER_PARAM.")

        # baseline expected adjacent with same prefix
        # model uri: s3://bucket/prefix/model.pkl
        base_uri = s3_model_uri.rsplit("/", 1)[0]
        baseline_uri = base_uri + "/baseline.json"

        download_s3_uri(s3_model_uri, model_path)
        download_s3_uri(baseline_uri, baseline_path)

    model = joblib.load(model_path)
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    return ModelBundle(model=model, baseline=baseline)


app = FastAPI(title="Used Car Price Model Server", version="0.1.0")
bundle: ModelBundle | None = None


@app.on_event("startup")
def _startup() -> None:
    global bundle
    bundle = load_bundle()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": bundle is not None}


@app.post("/predict")
def predict(req: PredictRequest) -> dict:
    assert bundle is not None
    df = pd.DataFrame([req.model_dump()])
    yhat = float(bundle.model.predict(df)[0])
    return {"prediction": yhat}


@app.get("/metrics")
def metrics() -> str:
    # Minimal Prometheus-ish metrics
    return "model_server_up 1\n"
