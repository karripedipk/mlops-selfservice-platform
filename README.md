# Self-Service MLOps Platform (Local + AWS ECS + Terraform)

# Self-Service MLOps Platform (Local → AWS ECS via Terraform)

I’m building a practical, end-to-end **MLOps platform** that enables internal data science teams to reliably take models from development to production with strong defaults, automated promotion, and operational visibility.

This repo is intentionally **platform-first**:
- Opinionated **golden paths** for common workflows (80/20)
- Self-service tooling to remove manual steps and reduce friction
- Secure, scalable deployment patterns on AWS
- Monitoring + drift detection to keep models reliable after release

---

## What I’m Building

### 1) Golden Path Developer Experience (DX)
I’m creating a small CLI (`mlopsctl`) and a standard project template so a data scientist can:

- scaffold a new ML project
- run training in a consistent, containerized way
- package and publish model artifacts immutably
- promote a model to “prod” with a controlled pointer update
- deploy a serving endpoint on ECS with repeatable infrastructure

This is meant to feel like an internal platform: simple for users, strict where it matters.

### 2) Model Lifecycle (End-to-End)
**Train → Validate → Register/Promote → Deploy → Observe**

- **Training pipeline** runs in Docker and produces:
  - `model.pkl`
  - `metrics.json`
  - `baseline.json` (for drift monitoring)
- **Artifacts** are stored immutably in **S3** under versioned paths
- A **production model pointer** is stored in **SSM Parameter Store** (a lightweight “registry pointer”)
- **Serving** runs on **ECS Fargate** behind an **Application Load Balancer**
- **Monitoring** includes:
  - `/health` endpoint for readiness
  - `/metrics` endpoint for basic service health
  - drift job that compares current feature distributions to baseline and writes an HTML report

### 3) Infrastructure as Code (IaC)
All AWS resources are created with **Terraform**:
- S3 bucket for artifacts
- ECR repository for serving image
- ECS cluster + task definition + service (Fargate)
- ALB + target group + listener
- IAM roles/policies for least-privilege access
- CloudWatch logs

---

## Architecture (Simplified)

**Local**
- Train (Docker) → artifacts in `projects/usedcar-price/artifacts/`
- Optional: MLflow local tracking (Docker Compose)
- Serve locally (FastAPI container)

**AWS**
- Model artifacts: **S3**
- Prod model pointer: **SSM Parameter Store**
- Serving: **ECS Fargate** + **ALB**
- Logs: **CloudWatch Logs**

Key design choice:
> Artifacts are immutable; “promotion” is a pointer update.  
> This matches how real platforms separate reproducible artifacts from deploy-time selection.

---

## Repo Layout

```text
platform/
  cli/                      # mlopsctl (golden path)
  registry/                 # local MLflow (optional)
  infra/terraform/          # AWS IaC for ECS + ALB + S3 + IAM
  templates/ml-project/     # project template for DS teams

projects/
  usedcar-price/
    training/               # training container + code
    serving/                # FastAPI serving container + code
    monitoring/             # drift job (HTML report)
    data/                   # small sample data for local runs

.github/workflows/
  ci.yml                    # lint + tests
  deploy.yml                # manual terraform deploy

---

## License
MIT (for your portfolio use).
