ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

ARG POETRY_VERSION
ARG PIP_INDEX_OPTION=""
RUN pip install --no-cache-dir ${PIP_INDEX_OPTION} "poetry==${POETRY_VERSION}" && \
    poetry config virtualenvs.create false
