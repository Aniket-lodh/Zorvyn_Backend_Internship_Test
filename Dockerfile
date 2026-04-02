FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .

RUN uv sync --frozen || uv pip install -r pyproject.toml
COPY . .

EXPOSE 10000

ENV PYTHONPATH=/app

CMD ["/bin/bash", "-c", "uv run alembic upgrade head && uv run task seed && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
