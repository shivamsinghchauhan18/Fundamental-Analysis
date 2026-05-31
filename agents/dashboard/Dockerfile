FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY agents/dashboard/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY shared/ ./shared/
COPY agents/ ./agents/
COPY orchestrator/ ./orchestrator/

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=6 \
  CMD curl -fsS http://127.0.0.1:${PORT:-8000}/api/market-status || exit 1

# Shell-form CMD so $PORT expands at runtime (Render/Railway inject it).
# Falls back to 8000 locally where $PORT is unset.
CMD uvicorn agents.dashboard.app:app --host 0.0.0.0 --port ${PORT:-8000}
