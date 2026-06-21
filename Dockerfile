FROM python:3.13.5-slim-bookworm

ARG UID=10001
ARG GID=10001

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    GEOSERVER_MCP_TRANSPORT=streamable-http \
    GEOSERVER_MCP_HOST=0.0.0.0 \
    GEOSERVER_MCP_PORT=8000

COPY --from=ghcr.io/astral-sh/uv:0.11.17 /uv /uvx /usr/local/bin/

RUN groupadd --gid "${GID}" app \
    && useradd --uid "${UID}" --gid "${GID}" --create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY pyproject.toml uv.lock README.md .python-version ./
COPY src ./src

RUN uv sync --frozen --no-dev

USER app

EXPOSE 8000

CMD ["geoserver-mcp"]
