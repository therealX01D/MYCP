# ---- build stage ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached unless pyproject/lock change)
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Then install the project itself
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# ---- runtime stage ----
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 app \
    && mkdir /data \
    && chown app:app /data

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    MYCP_DB_PATH=/data/mycp.db \
    MYCP_HOST=0.0.0.0 \
    MYCP_PORT=8080

USER app
VOLUME ["/data"]
EXPOSE 8080

CMD ["mycp", "run"]