FROM zj-brain-science-platform-base:latest

WORKDIR /code

COPY app /code/app

CMD uvicorn app.main:app --host 0.0.0.0 --port 80
