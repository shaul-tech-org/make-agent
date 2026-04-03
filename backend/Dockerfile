# === Builder ===
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# === Runtime ===
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

RUN mkdir -p /tmp/make-agent-clones && chown -R app:app /app /tmp/make-agent-clones
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
