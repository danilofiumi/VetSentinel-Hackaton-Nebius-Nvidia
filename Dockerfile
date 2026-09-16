# ── Stage 1: builder ────────────────────────────────────────────────────────
# Has build-time tools. Only the compiled .venv directory is copied forward.
FROM python:3.12-slim AS builder

# System build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_HOME="/opt/poetry"
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app

# Copy only the dependency manifests first — Docker caches this layer and only
# re-runs the poetry install when pyproject.toml or poetry.lock change.
COPY app/py/pyproject.toml app/py/poetry.lock* app/py/poetry.toml* /app/

# Single unified virtualenv at /app/.venv
RUN poetry install --no-root -v


# ── Stage 2: runtime ────────────────────────────────────────────────────────
# Lean image. No build headers.
FROM python:3.12-slim

# Runtime-only native libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Dagu — the workflow scheduler
RUN curl -fsSL https://raw.githubusercontent.com/dagucloud/dagu/main/scripts/installer.sh \
    | bash -s -- --no-prompt --install-dir /usr/local/bin --version v2.12.0

WORKDIR /app

# Copy source code first
COPY . /app

# Copy the pre-compiled virtualenv from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Put the venv first on PATH so `python` and `dagu`-spawned subprocesses
# all see the same interpreter without needing `poetry run`.
ENV PATH="/app/.venv/bin:${PATH}"

# Poetry compatibility shim for Dagu step commands invoking 'poetry run'
RUN echo '#!/bin/sh\nif [ "$1" = "run" ]; then shift; exec "$@"; fi\nexec "$@"' > /usr/local/bin/poetry && \
    chmod +x /usr/local/bin/poetry

# Dagu workspace
ENV DAGU_HOME=/app/.dagu
ENV DAGU_CONFIG=/app/.dagu/config.yaml

RUN mkdir -p ${DAGU_HOME}/dags ${DAGU_HOME}/logs ${DAGU_HOME}/data ${DAGU_HOME}/data/artifacts && \
    chmod +x /app/docker-entrypoint.sh

EXPOSE 8075

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["dagu", "start-all"]


