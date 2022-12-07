FROM zj-brain-science-platform-base:latest

WORKDIR /code

RUN poetry install --with=alembic --no-interaction --no-cache
