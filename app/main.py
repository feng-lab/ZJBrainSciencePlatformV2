from fastapi import FastAPI
from objprint import op

from .request import LoginRequest
from .response import (
    GetStatisticResponse,
    GetStatisticWithDataTypeResponse,
    CODE_SUCCESS,
    LoginResponse,
    GetStatisticWithSubjectResponse,
)

app = FastAPI()


@app.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest):
    op(request)
    return LoginResponse(code=CODE_SUCCESS)


@app.get("/api/getStatistic", response_model=GetStatisticResponse)
def get_statistic():
    return GetStatisticResponse(
        code=CODE_SUCCESS,
        data=GetStatisticResponse.Data(experiments=7, files=8, human=7, taskmaster=8),
    )


@app.get(
    "/api/getStatisticWithDataType", response_model=GetStatisticWithDataTypeResponse
)
def get_statistic_with_data_type():
    return GetStatisticWithDataTypeResponse(
        code=CODE_SUCCESS,
        data=[
            GetStatisticWithDataTypeResponse.Data(name="EEG", value=61.41),
            GetStatisticWithDataTypeResponse.Data(name="spike", value=16.84),
            GetStatisticWithDataTypeResponse.Data(name="EOG", value=10.85),
            GetStatisticWithDataTypeResponse.Data(name="iEEG", value=6.67),
            GetStatisticWithDataTypeResponse.Data(name="MP4", value=15.18),
        ],
    )


@app.get("/api/getStatisticWithSubject", response_model=GetStatisticWithSubjectResponse)
def get_statistic_with_subject():
    return GetStatisticWithSubjectResponse(
        code=CODE_SUCCESS,
        data=[
            GetStatisticWithSubjectResponse.Data(
                type="男性",
                below_30=5,
                between_30_and_60=5,
                over_60=3,
            ),
            GetStatisticWithSubjectResponse.Data(
                type="女性",
                below_30=9,
                between_30_and_60=5,
                over_60=7,
            ),
        ],
    )
