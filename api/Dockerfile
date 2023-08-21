FROM python:3.11 AS builder
WORKDIR /app
ADD pyproject.toml poetry.lock /app/

RUN pip install poetry
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

CMD /app/.venv/bin/python api/main.py
