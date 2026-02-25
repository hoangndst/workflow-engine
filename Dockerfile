## Build stage: use uv to create the virtual environment
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS uv

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings.
# Expecting uv.lock + pyproject.toml to be present in the build context.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it.
# Installing separately from its dependencies allows optimal layer caching.
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


## Final stage: slim Python image for runtime
FROM python:3.13-slim-bookworm

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    DATABASE_URL=sqlite:///./dashmessaging.db

# System deps (if needed later, e.g. for Postgres client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from uv stage
COPY --from=uv --chown=root:root /app/.venv /app/.venv

# Copy project files
COPY --chown=root:root . /app

# Create a non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Expose FastAPI port
EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]