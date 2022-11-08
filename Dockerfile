FROM python:3.10
WORKDIR /code

# uncomment next line to activate debug mode
# ENV DEBUG_MODE True

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --requirement /code/requirements.txt
COPY ./app /code/app
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]