.PHONY: train-local serve-local drift-local

train-local:
	docker build -t usedcar-train:local -f training/Dockerfile .
	docker run --rm -e MLFLOW_TRACKING_URI=$${MLFLOW_TRACKING_URI:-} \
	  -v $$(pwd)/artifacts:/app/artifacts \
	  usedcar-train:local

serve-local:
	docker build -t usedcar-serve:local -f serving/Dockerfile .
	docker run --rm -p 8080:8080 \
	  -e MODEL_LOCAL_PATH=/app/model/model.pkl \
	  -v $$(pwd)/artifacts:/app/model \
	  usedcar-serve:local

drift-local:
	python monitoring/drift_job.py --baseline artifacts/baseline.json --current data/current.csv --out artifacts/drift_report.html
