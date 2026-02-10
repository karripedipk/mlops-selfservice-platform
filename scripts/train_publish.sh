#!/usr/bin/env bash
set -euo pipefail

# Expected env:
#   AWS_REGION
#   PROJECT_NAME
#   ARTIFACT_BUCKET (terraform output)
#   MODEL_POINTER_PARAM (terraform output)
# Optional:
#   MLFLOW_TRACKING_URI

: "${AWS_REGION:?Need AWS_REGION}"
: "${PROJECT_NAME:?Need PROJECT_NAME}"
: "${ARTIFACT_BUCKET:?Need ARTIFACT_BUCKET}"
: "${MODEL_POINTER_PARAM:?Need MODEL_POINTER_PARAM}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJ_DIR="${ROOT_DIR}/projects/usedcar-price"

# Train locally (docker), artifacts to projects/usedcar-price/artifacts
pushd "${PROJ_DIR}" >/dev/null
make train-local
popd >/dev/null

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
PREFIX="models/usedcar-price/${RUN_ID}"

aws s3 cp "${PROJ_DIR}/artifacts/model.pkl" "s3://${ARTIFACT_BUCKET}/${PREFIX}/model.pkl" --region "${AWS_REGION}"
aws s3 cp "${PROJ_DIR}/artifacts/baseline.json" "s3://${ARTIFACT_BUCKET}/${PREFIX}/baseline.json" --region "${AWS_REGION}"
aws s3 cp "${PROJ_DIR}/artifacts/metrics.json" "s3://${ARTIFACT_BUCKET}/${PREFIX}/metrics.json" --region "${AWS_REGION}"

MODEL_URI="s3://${ARTIFACT_BUCKET}/${PREFIX}/model.pkl"
aws ssm put-parameter --name "${MODEL_POINTER_PARAM}" --type "String" --value "${MODEL_URI}" --overwrite --region "${AWS_REGION}"

echo "Published model to: ${MODEL_URI}"
echo "Updated model pointer: ${MODEL_POINTER_PARAM}"
