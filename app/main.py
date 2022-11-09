from fastapi import FastAPI
from objprint import op

from .request import LoginRequest
from .response import (
    GetStatisticResponse,
    GetStatisticWithDataTypeResponse,
    CODE_SUCCESS,
    LoginResponse,
    GetStatisticWithSubjectResponse,
    GetStatisticWithServerResponse,
)

app = FastAPI()


@app.post("/api/login", response_model=LoginResponse, description="用户提交登录表单，进行登录验证")
def login(request: LoginRequest):
    op(request)
    return LoginResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getStatistic",
    response_model=GetStatisticResponse,
    description="获取首页实验、文件、被试、任务四个卡片的统计数据",
)
def get_statistic():
    return GetStatisticResponse(
        code=CODE_SUCCESS,
        data=GetStatisticResponse.Data(experiments=7, files=8, human=7, taskmaster=8),
    )


@app.get(
    "/api/getStatisticWithDataType",
    response_model=GetStatisticWithDataTypeResponse,
    description="获取平台已上传的各类型数据的占比统计",
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


@app.get(
    "/api/getStatisticWithSubject",
    response_model=GetStatisticWithSubjectResponse,
    description="获取平台已记录的被试对象的特性分布统计",
)
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


@app.get(
    "/api/getStatisticWithServer",
    response_model=GetStatisticWithServerResponse,
    description="返回当前计算服务器资源利用率的百分比数值，精确到小数点后两位",
)
def get_statistic_with_server():
    return GetStatisticWithServerResponse(
        code=CODE_SUCCESS,
        data=70.53,
    )
