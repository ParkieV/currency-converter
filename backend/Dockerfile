FROM python:3.12.7-slim AS base

ENV TZ="Europe/Moscow"

RUN apt-get update && apt-get install -y --no-install-recommends curl wget gcc build-essential libpq-dev python3-dev

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

FROM base AS base_with_req

WORKDIR /app

COPY pyproject.toml .

RUN poetry lock --no-cache && \
    poetry install --no-cache && \
    poetry cache clear pypi --all && \
    poetry cache clear virtualenvs --all && \
    pip cache purge && \
    find / -type f -name '*.py[cod]' -delete && \
    find / -type f -name '*.whl' -delete

FROM base_with_req

COPY /src ./src

CMD ["sh", "-c", "python -m uvicorn src.main:app --host $BACKEND_HOST --port $BACKEND_PORT"]