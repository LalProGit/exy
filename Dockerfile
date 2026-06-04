# syntax=docker/dockerfile:1

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Pro-Tip: Pulling uv directly from Astral's image is faster than pip installing it
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy only dependency metadata first for optimal layer caching
COPY pyproject.toml uv.lock ./

# Create virtual environment and install runtime dependencies
RUN uv sync --frozen --no-dev

# Copy application source
COPY src ./src

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

# Create a non-root user and group for security
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

# Copy virtual environment and app code from the builder stage
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src

# Transfer ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Expose the API port
EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]