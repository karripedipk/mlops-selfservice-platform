# 🚀 Self-Service MLOps Platform
Local Development → AWS ECS (Terraform) Deployment

I built this end-to-end MLOps platform to demonstrate how internal ML teams can reliably move from experimentation to production using standardized workflows, immutable artifacts, and infrastructure-as-code.

This project is intentionally platform-first — not just model training.

------------------------------------------------------------

🎯 PLATFORM GOALS

- Enable self-service ML development
- Standardize training & deployment workflows
- Ensure runtime consistency between training and serving
- Promote models safely using immutable artifacts
- Provide production observability and drift detection
- Use Infrastructure-as-Code for reproducibility

------------------------------------------------------------

🧱 HIGH-LEVEL ARCHITECTURE

Local Data (CSV / S3)
        ↓
Training Container (Dockerized ML)
        ↓
Model Artifacts
 - model.pkl
 - baseline.json
 - metrics.json
        ↓
S3 Versioned Artifact Storage
        ↓
SSM Parameter Store (Production Model Pointer)
        ↓
ECS Fargate FastAPI Inference Service
        ↓
Application Load Balancer
 - /health
 - /predict
 - /metrics

Side Systems:
- CloudWatch Logs (observability)
- Drift Monitoring Job (KS test + HTML report)

------------------------------------------------------------

🏗 ARCHITECTURE COMPONENTS

Training Layer
- Dockerized training pipeline
- Scikit-learn model (RandomForest)
- Generates model.pkl, baseline.json, metrics.json
- Optional MLflow tracking

Artifact Management
- Immutable artifacts stored in S3
- Timestamped versioned paths
- Production model selected via SSM Parameter pointer
- Promotion = updating pointer, not overwriting artifact

Serving Layer
- FastAPI inference service
- Containerized deployment
- Runs on ECS Fargate
- Endpoints: /health, /predict, /metrics

Infrastructure as Code (Terraform)
- S3 bucket
- ECS cluster + service
- ECR repository
- IAM roles
- Application Load Balancer
- CloudWatch logs
- SSM model pointer

Monitoring & Drift
- Baseline feature statistics saved at training
- KS-test drift detection
- HTML drift report
- Production logs in CloudWatch

------------------------------------------------------------

📦 GOLDEN PATH (SELF-SERVICE WORKFLOW)

mlopsctl init project-name
mlopsctl train
mlopsctl publish
mlopsctl deploy --env prod

This enforces consistency and reduces operational risk.

------------------------------------------------------------

⚙️ LOCAL SETUP

1) Create virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -e ./platform/cli

2) Optional: Start MLflow
docker compose -f platform/registry/docker-compose.mlflow.yml up -d
export MLFLOW_TRACKING_URI=http://localhost:5001

3) Train locally
cd projects/usedcar-price
make train-local

Artifacts generated in:
projects/usedcar-price/artifacts/

4) Run inference locally
make serve-local

Test:
curl http://localhost:8080/health

curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"year":2019,"odometer":25000,"make_encoded":9,"model_encoded":42}'

------------------------------------------------------------

☁️ AWS DEPLOYMENT

1) Provision infrastructure
cd platform/infra/terraform
terraform init
terraform apply -auto-approve \
  -var="project_name=mlops-demo" \
  -var="aws_region=us-east-1"

2) Build & push serving image
bash scripts/aws_login_ecr.sh us-east-1
bash scripts/build_push_serving.sh us-east-1 mlops-demo

3) Publish model + update prod pointer
export AWS_REGION=us-east-1
export PROJECT_NAME=mlops-demo
export ARTIFACT_BUCKET=$(terraform output -raw artifact_bucket)
export MODEL_POINTER_PARAM=$(terraform output -raw model_pointer_ssm_param)

bash scripts/train_publish.sh

4) Test live endpoint
ALB=$(terraform output -raw alb_dns_name)
curl http://$ALB/health

------------------------------------------------------------

🧠 DESIGN PRINCIPLES

- Immutable artifacts, mutable promotion pointer
- Separation of training and serving environments
- Reproducible container builds
- Declarative infrastructure
- Observability-first mindset
- Platform abstraction over manual workflows

------------------------------------------------------------

🔎 WHAT THIS DEMONSTRATES

- Scalable ML platform engineering
- Self-service tooling design
- Automated promotion workflows
- Runtime dependency alignment
- Infrastructure-as-Code best practices
- Production-ready ML deployment on AWS
- Drift monitoring integration

------------------------------------------------------------

🚀 PLATFORM MATURITY ROADMAP

- Automated evaluation gates in CI
- Canary / blue-green deployment
- Rollback via pointer reset
- Model approval workflow
- Scheduled drift job via EventBridge
- FinOps cost monitoring
- Feature store integration