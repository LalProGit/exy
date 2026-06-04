# syntax=docker/dockerfile:1.4

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-slim-bookworm AS builder

# UV_COMPILE_BYTECODE precompiles Python to .pyc files for faster startup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Pull uv directly from Astral's official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency metadata first for optimal layer caching
COPY pyproject.toml uv.lock ./

# Mount the uv cache securely so rebuilds take milliseconds instead of minutes
# Install the heavy dependencies without installing your custom code yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy your actual source code
COPY src ./src

# Sync again to install your actual application package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Create a non-root user and group for strict security
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

# Copy the compiled virtual environment and app code from the builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src

# CRITICAL: Install Playwright system dependencies as root, install the Chromium binary 
# to a global path, and grant ownership to the non-root user. 
# We clean up apt caches immediately after to save disk space on your 4GB VPS.
RUN apt-get update && \
    playwright install chromium --with-deps && \
    chown -R appuser:appgroup /opt/playwright && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Transfer ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the secure user boundary
USER appuser

EXPOSE 8000

# Start Uvicorn with proxy headers enabled for VPS networking
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]