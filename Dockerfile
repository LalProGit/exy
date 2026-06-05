# syntax=docker/dockerfile:1.4

FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src

RUN apt-get update && \
    playwright install chromium --with-deps && \
    chown -R appuser:appgroup /opt/playwright && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY script/start.sh /app/start.sh

RUN chown -R appuser:appgroup /app && \
    chmod +x /app/start.sh

USER appuser

EXPOSE 8000

CMD ["/app/start.sh"]