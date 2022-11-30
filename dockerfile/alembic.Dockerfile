FROM python:3.11
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./requirements.alembic.txt /code/requirements.alembic.txt
COPY ./alembic.ini /code/alembic.ini

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --requirement /code/requirements.txt && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir --requirement /code/requirements.alembic.txt

CMD ["alembic", "upgrade", "head"]