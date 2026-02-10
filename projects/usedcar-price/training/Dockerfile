FROM python:3.11-slim

WORKDIR /app

# Build deps (helps if wheels aren't available and pip tries to compile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY training/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY data /app/data
COPY training /app/training

CMD ["python", "training/train.py"]
