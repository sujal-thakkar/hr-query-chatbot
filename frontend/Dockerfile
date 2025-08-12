# frontend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy frontend requirements (assumes build context is repo root)
COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only frontend application code (avoid copying entire repo)
COPY frontend/ ./

# Create non-root user and prepare .streamlit before switching
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/.streamlit \
    && chown -R app:app /app

USER app


EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

