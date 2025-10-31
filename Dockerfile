FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl git build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pipx && \
    pipx install poetry

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8009

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8009"]