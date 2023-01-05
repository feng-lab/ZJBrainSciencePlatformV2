FROM python:3.11

WORKDIR /code
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /code/

RUN poetry install --with=alembic --no-interaction --no-cache
