FROM python:3.12.7-slim AS base

ENV TZ="Europe/Moscow"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gcc build-essential libpq-dev python3-dev cron && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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
    pip cache purge

FROM base_with_req AS final

WORKDIR /app

COPY /src ./src

RUN touch /var/log/cron.log && chmod 0666 /var/log/cron.log

RUN printenv > /etc/environment && \
    echo "0 20 * * * . /etc/environment && cd /app && /usr/local/bin/python3 -m src.services.parsers >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job && \
    chmod 0644 /etc/cron.d/my-cron-job && \
    crontab /etc/cron.d/my-cron-job

CMD printenv | grep -v "no_proxy" >> /etc/environment && cron -f