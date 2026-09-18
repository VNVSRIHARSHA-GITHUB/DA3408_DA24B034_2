# --- Stage 1: build ---
FROM python:3.10 AS builder
WORKDIR /build
COPY Q2/requirements-cache.txt requirements.txt
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# --- Stage 2: minimal runtime ---
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /build/deps /usr/local/lib/python3.10/site-packages
COPY Q2/app_with_cache.py app.py
COPY app/model.joblib model.joblib

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]