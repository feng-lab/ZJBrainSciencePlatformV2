from fastapi import FastAPI
from objprint import op

from .request import LoginRequest
from .response import Response, response_success, GetStatisticResponse

app = FastAPI()


@app.post("/api/login", response_model=Response[None])
def login(request: LoginRequest):
    op(request)
    return response_success("login success")


@app.get("/api/getStatistic", response_model=Response[GetStatisticResponse])
def get_statistic():
    return response_success(
        data=GetStatisticResponse(experiments=1, files=2, human=3, taskmaster=4)
    )
