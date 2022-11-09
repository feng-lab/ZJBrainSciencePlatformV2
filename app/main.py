from fastapi import FastAPI
from objprint import op

from .request import LoginRequest
from .response import Response, response_success, GetStatisticResponse, GetStatisticWithDataTypeResponse

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


@app.get("/api/getStatisticWithDataType", response_model=Response[list[GetStatisticWithDataTypeResponse]])
def get_statistic_with_data_type():
    return response_success(
        data=[
            GetStatisticWithDataTypeResponse(name="EEG", value=61.41),
            GetStatisticWithDataTypeResponse(name="spike", value=16.84),
            GetStatisticWithDataTypeResponse(name="EOG", value=10.85),
            GetStatisticWithDataTypeResponse(name="iEEG", value=6.67),
            GetStatisticWithDataTypeResponse(name="MP4", value=15.18),
        ]
    )
