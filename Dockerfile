FROM python:3.13-alpine AS builder

# Install Poetry
ARG POETRY_VERSION=2.1

ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PYTHON_PACKAGE=fishsense_data_processing_spider
# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Reproduce environment
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --without dev && rm -rf ${POETRY_CACHE_DIR}

COPY README.md /app/README.md
COPY smartfin_data_api /app/smartfin_data_api
RUN poetry install --only main

# COPY from builder
FROM python:3.13-alpine AS runtime

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV E4ESF_DOCKER=true

RUN mkdir -p /e4esf/config /e4esf/logs /e4esf/data /e4esf/cache
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/smartfin_data_api /app/smartfin_data_api
COPY ./sql /app/sql

ENTRYPOINT ["sf_api"]
