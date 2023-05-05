ARG BASE_IMAGE_TAG
FROM ${BASE_IMAGE_TAG}

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN poetry install --only=main --only=alembic --no-interaction --no-cache

COPY alembic.ini /code/
COPY alembic /code/alembic
COPY app /code/app
COPY config /code/config

CMD /bin/bash -c "uvicorn app.main:app --host 0.0.0.0 --port 80 |& tee -a /log/stdout_stderr.log"
