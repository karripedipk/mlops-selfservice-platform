# Self-Service MLOps Platform (Local + AWS ECS + Terraform)

This repo is a practical, interview-ready end-to-end MLOps platform project:
- **Golden path** via `mlopsctl` CLI (init/train/register/deploy/monitor)
- **Training pipeline** (Docker) with quality gates
- **Model artifact versioning** in **S3**
- **Promotion pointer** via **SSM Parameter Store** (acts as a simple registry pointer)
- **Serving** on **ECS Fargate** behind an **ALB**
- **Monitoring**: logs/metrics endpoint + drift job that writes reports to S3
- **GitHub Actions**: CI + build/push + deploy

> You can run everything locally first, then deploy to AWS with Terraform.

---

## 0) Prereqs
Local:
- Python 3.11+
- Docker Desktop
- Make (optional)

AWS:
- AWS account + credentials
- Terraform >= 1.5
- An AWS region (default: `us-east-1`)

GitHub:
- Store this repo in GitHub
- Add GitHub Actions secrets (see below)

---

## 1) Quickstart (Local)
### 1.1 Create venv + install CLI
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./platform/cli
```

### 1.2 Start local MLflow (optional, local tracking)
```bash
docker compose -f platform/registry/docker-compose.mlflow.yml up -d
export MLFLOW_TRACKING_URI=http://localhost:5001
```

### 1.3 Train locally (logs to MLflow if set)
```bash
cd projects/usedcar-price
make train-local
```

### 1.4 Serve locally
```bash
cd projects/usedcar-price
make serve-local
# in another terminal:
curl -s http://localhost:8080/health | jq
```

---

## 2) AWS Deploy (Terraform + ECS)
### 2.1 Terraform apply
This Terraform uses your **default VPC** + public subnets.
```bash
cd platform/infra/terraform
terraform init
terraform apply -auto-approve \
  -var="project_name=mlops-demo" \
  -var="aws_region=us-east-1"
```

Terraform outputs:
- `alb_dns_name` (your serving endpoint)
- `artifact_bucket`
- `model_pointer_ssm_param`

### 2.2 Build & push serving image to ECR (once)
```bash
cd ../../..   # repo root
bash scripts/aws_login_ecr.sh us-east-1
bash scripts/build_push_serving.sh us-east-1 mlops-demo
```

### 2.3 Train & publish model to S3 + update SSM pointer
```bash
export AWS_REGION=us-east-1
export PROJECT_NAME=mlops-demo

# Fetch outputs from terraform (recommended)
export ARTIFACT_BUCKET=$(terraform -chdir=platform/infra/terraform output -raw artifact_bucket)
export MODEL_POINTER_PARAM=$(terraform -chdir=platform/infra/terraform output -raw model_pointer_ssm_param)

cd projects/usedcar-price
bash ../../scripts/train_publish.sh
```

### 2.4 Deploy/update ECS service (pulls latest pointer from SSM)
```bash
cd platform/infra/terraform
terraform apply -auto-approve
```

### 2.5 Test endpoint
```bash
ALB=$(terraform output -raw alb_dns_name)
curl -s "http://$ALB/health" | jq
```

---

## 3) GitHub Actions (recommended)
We include workflows:
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml` (manual dispatch)

You can use either:
- **AWS OIDC (preferred)**: configure a GitHub OIDC IAM role
- OR **AWS keys as secrets** (simpler)

### If using AWS keys:
Set repo secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., us-east-1)
- `PROJECT_NAME` (e.g., mlops-demo)

---

## 4) What counts as “Model Registry” here?
To keep this home project lightweight yet realistic:
- **Artifacts are immutable** in S3 under versioned prefixes
- “Promotion” is modeled as an **SSM parameter** that points to the current “prod” model artifact URI.

This matches real platform patterns: immutable artifacts + mutable pointer + audit trails.

---

## 5) Demo script (5 minutes)
1) `mlopsctl init usedcar-price`
2) `mlopsctl train` (logs metrics, packages model)
3) `mlopsctl publish` (uploads to S3 + updates model pointer)
4) `mlopsctl deploy --env prod` (ECS picks latest pointer)
5) Show `/metrics` and drift report written to S3

---

## License
MIT (for your portfolio use).
