FROM python:3.11

WORKDIR /code
COPY poetry.lock pyproject.toml alembic.ini /code/

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --with=main --with=alembic --no-interaction --no-cache

CMD alembic current
