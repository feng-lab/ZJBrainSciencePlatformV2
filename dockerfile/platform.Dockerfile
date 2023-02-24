ARG BASE_IMAGE_TAG
FROM ${BASE_IMAGE_TAG}

WORKDIR /code

COPY platform/poetry.lock platform/pyproject.toml /code/
RUN poetry install --with=alembic --no-interaction --no-cache

COPY platform/alembic.ini /code/
COPY platform/alembic /code/alembic
COPY platform/app /code/app

CMD /bin/bash -c "uvicorn app.main:app --host 0.0.0.0 --port 80 |& tee -a /root/log/ZJBrainSciencePlatform/app/stdout_stderr.log"
