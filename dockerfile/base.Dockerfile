FROM python:3.11

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-interaction --no-cache
