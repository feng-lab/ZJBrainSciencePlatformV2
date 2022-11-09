from datetime import date

from fastapi import FastAPI, Query
from objprint import op

from .request import *
from .response import *
from .models import *

app = FastAPI()


@app.post(
    "/api/login", response_model=LoginResponse, name="登录", description="用户提交登录表单，进行登录验证"
)
def login(request: LoginRequest):
    op(request)
    return LoginResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getStatistic",
    response_model=GetStatisticResponse,
    name="获取统计信息",
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
    name="获取平台数据量按类型的统计数据",
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
    name="获取被试分布的统计数据",
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
    name="获取计算服务器水位",
    description="返回当前计算服务器资源利用率的百分比数值，精确到小数点后两位",
)
def get_statistic_with_server():
    return GetStatisticWithServerResponse(
        code=CODE_SUCCESS,
        data=70.53,
    )


@app.get(
    "/api/getStatisticWithData",
    response_model=GetStatisticWithDataResponse,
    name="获取平台上传数据量增长趋势的统计结果",
    description="获取一定周期内平台上传数据量的按天统计结果，默认周期为一周",
)
def get_statistic_with_data(
    start: date = Query(title="周期起始日期，YYYY-MM-DD"),
    end: date = Query(title="周期截止日期，YYYY-MM-DD"),
):
    op((start, end))
    return GetStatisticWithDataResponse(
        code=CODE_SUCCESS,
        data=[
            [1370131200000, 0.7695],
            [1370217600000, 0.7648],
            [1370304000000, 0.7645],
            [1370390400000, 0.7638],
            [1370476800000, 0.7549],
        ],
    )


@app.get(
    "/api/getStatisticWithSick",
    response_model=GetStatisticWithSickResponse,
    name="获取疾病种类的统计结果",
    description="获取各种疾病的分布统计",
)
def get_statistic_with_sick():
    return GetStatisticWithSickResponse(
        code=CODE_SUCCESS,
        data=[
            GetStatisticWithSickResponse.Data(
                sick="癫痫", part1=107, part2=133, part3=93
            ),
            GetStatisticWithSickResponse.Data(
                sick="睡眠障碍", part1=31, part2=156, part3=14
            ),
            GetStatisticWithSickResponse.Data(sick="老年痴呆", part1=5, part2=92, part3=14),
            GetStatisticWithSickResponse.Data(sick="中风", part1=23, part2=48, part3=32),
            GetStatisticWithSickResponse.Data(sick="其他", part1=2, part2=6, part3=34),
        ],
    )


@app.post(
    "/api/addExperiments",
    response_model=AddExperimentResponse,
    name="新增实验",
    description="新增实验，提交实验表单",
)
def add_experiments(request: AddExperimentRequest):
    op(request)
    return AddExperimentResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getExperimentsByPage",
    response_model=GetExperimentsByPageResponse,
    name="获取实验列表",
    description="根据筛选、排序等条件得到实验列表并分页返回",
)
def get_experiments_by_page(
    sort_by: GetExperimentsByPageRequest.SortBy = Query(title="排序依据"),
    sort_order: GetExperimentsByPageRequest.SortOrder = Query(title="排序顺序"),
    offset: int = Query(title="分页起始位置", default=0),
    limit: int = Query(title="分页大小", default=10),
    search: Optional[str] = Query(title="搜索内容", default=None),
):
    op((sort_by, sort_order, offset, limit, search))
    return GetExperimentsByPageResponse(code=CODE_SUCCESS, data=[Experiment()])


@app.get(
    "/api/getExperimentsByPage",
    response_model=GetExperimentsByIdResponse,
    name="获取实验详情",
    description="根据实验编号获取实验详细信息",
)
def get_experiments_by_id(experiment_id: str = Query(title="实验编号")):
    op(experiment_id)
    return GetExperimentsByIdResponse(code=CODE_SUCCESS, data=Experiment())
