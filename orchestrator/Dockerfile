FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY orchestrator/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY shared/ ./shared/
COPY agents/ ./agents/
COPY orchestrator/ ./orchestrator/

CMD ["python", "-u", "orchestrator/orchestrator.py"]
