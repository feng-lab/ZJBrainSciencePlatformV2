FROM zj-brain-science-platform-base:latest

WORKDIR /code

RUN poetry install --only=alembic --no-interaction --no-cache
