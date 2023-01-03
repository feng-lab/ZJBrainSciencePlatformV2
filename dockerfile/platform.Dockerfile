FROM zj-brain-science-platform-base:latest

WORKDIR /code

COPY app /code/app

CMD /bin/bash -c "uvicorn app.main:app --host 0.0.0.0 --port 80 |& tee -a /root/log/ZJBrainSciencePlatform/app/stdout_stderr.log"
