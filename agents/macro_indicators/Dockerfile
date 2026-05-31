FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir sqlalchemy pandas numpy

COPY . .

CMD ["python", "macro_engine.py"]
