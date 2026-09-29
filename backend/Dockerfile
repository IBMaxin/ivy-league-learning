FROM ghcr.io/astral-sh/uv:0.6 AS uv
FROM python:3.12-slim AS base
# SOC: minimal image, non-root runtime, no secrets baked in
COPY --from=uv /uv /usr/local/bin/uv
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
# uv: copy lockfiles first for layer caching, sync locked pinned deps
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY app ./app
USER appuser
EXPOSE 8000
# Exec form, no shell; docs disabled via env in prod; run via uv venv
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
