FROM python:3.10.6-slim-bullseye
WORKDIR /app
COPY . .
RUN apt update && apt install -y --fix-missing espeak-ng
RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
