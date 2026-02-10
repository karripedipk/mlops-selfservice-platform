#!/usr/bin/env bash
set -euo pipefail

REGION="${1:-us-east-1}"
PROJECT_NAME="${2:-mlops-demo}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${PROJECT_NAME}-serving"
TAG="$(git rev-parse --short HEAD)"

docker build -t "${PROJECT_NAME}-serving:${TAG}" -f projects/usedcar-price/serving/Dockerfile projects/usedcar-price
docker tag "${PROJECT_NAME}-serving:${TAG}" "${REPO}:${TAG}"
docker tag "${PROJECT_NAME}-serving:${TAG}" "${REPO}:latest"

aws ecr describe-repositories --repository-names "${PROJECT_NAME}-serving" --region "$REGION" >/dev/null 2>&1 ||   aws ecr create-repository --repository-name "${PROJECT_NAME}-serving" --region "$REGION" >/dev/null

docker push "${REPO}:${TAG}"
docker push "${REPO}:latest"

echo "Pushed: ${REPO}:${TAG} and :latest"
