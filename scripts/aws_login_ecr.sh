#!/usr/bin/env bash
set -euo pipefail

REGION="${1:-us-east-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
echo "Logged into ECR: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
