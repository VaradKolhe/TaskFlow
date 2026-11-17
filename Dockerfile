FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TASKFLOW_DB_PATH=/data/taskflow.db

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /data && chown appuser:appuser /data

COPY --chown=appuser:appuser app.py database.py task_logic.py ./
COPY --chown=appuser:appuser scripts/healthcheck.py ./scripts/healthcheck.py

USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python scripts/healthcheck.py || exit 1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
