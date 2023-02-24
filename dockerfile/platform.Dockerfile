ARG BASE_IMAGE_TAG
FROM ${BASE_IMAGE_TAG}

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN poetry install --with=alembic --no-interaction --no-cache

COPY alembic.ini /code/
COPY alembic /code/alembic
COPY app /code/app

CMD /bin/bash -c "uvicorn app.main:app --host 0.0.0.0 --port 80 |& tee -a /root/log/ZJBrainSciencePlatform/app/stdout_stderr.log"
