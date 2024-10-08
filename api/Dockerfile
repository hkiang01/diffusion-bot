FROM python:3.11 AS builder
WORKDIR /app
ADD pyproject.toml poetry.lock /app/

ARG POETRY_VERSION=1.6.1
RUN pip install poetry==${POETRY_VERSION}
RUN poetry config virtualenvs.in-project true
RUN poetry install

FROM python:3.11
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # resolve libGL.so.1
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY api api

RUN addgroup --gid 1000 app
RUN adduser app --home /app --uid 1000 --gid 1000 --no-create-home --disabled-password
USER 1000

CMD .venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 80
