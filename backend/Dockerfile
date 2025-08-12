# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (curl needed for healthcheck; libgomp for faiss)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements (explicit path to avoid picking up root requirements.txt)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only backend source code (not the entire repo)
COPY backend/ ./

# Create non-root user and required dirs before switching
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/data /app/.cache \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "main:app"]

