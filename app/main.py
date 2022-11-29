import json
import logging
import logging.handlers
from datetime import date, timedelta, datetime
from http import HTTPStatus
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Query, UploadFile, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.api import user
from app.api.auth import router as auth_router
from app.api.notification import router as notification_router
from app.api.user import router as user_router
from app.config import config
from app.db.database import database
from app.model.request import (
    AddExperimentRequest,
    GetExperimentsByPageRequest,
    AddParadigmRequest,
    DeleteParadigmsRequest,
    AddHumanSubjectRequest,
    UpdateHumanSubjectRequest,
    DeleteHumanSubjectRequest,
    AddDeviceRequest,
    UpdateDeviceRequest,
    DeleteDeviceRequest,
    DisplayEEGRequest,
    AddTaskRequest,
    GoSearchRequest,
)
from app.model.response import (
    Response,
    CODE_FAIL,
    CODE_SESSION_TIMEOUT,
    GetStatisticResponse,
    CODE_SUCCESS,
    GetStatisticWithDataTypeResponse,
    GetStatisticWithSubjectResponse,
    GetStatisticWithServerResponse,
    GetStatisticWithDataResponse,
    GetStatisticWithSickResponse,
    AddExperimentResponse,
    GetExperimentsByPageResponse,
    GetExperimentsByIdResponse,
    AddParadigmResponse,
    GetParadigmsResponse,
    GetParadigmByIdResponse,
    DeleteParadigmsResponse,
    GetDocTypeResponse,
    GetDocByPageResponse,
    DeleteDocResponse,
    AddFileResponse,
    GetHumanSubjectByPageResponse,
    AddHumanSubjectResponse,
    UpdateHumanSubjectResponse,
    DeleteHumanSubjectResponse,
    GetDeviceByPageResponse,
    AddDeviceResponse,
    GetDeviceByIdResponse,
    UpdateDeviceResponse,
    DeleteDeviceResponse,
    DisplayEEGResponse,
    GetFilesResponse,
    GetTaskByPageResponse,
    AddTaskResponse,
    GetTaskByIDResponse,
    GetTaskStepsByIDResponse,
    GetFilterStepResultByIDResponse,
    GetAnalysisStepResultByIDResponse,
    UploadSearchFileResponse,
    GoSearchResponse,
)
from app.model.schema import (
    Experiment,
    Paradigm,
    Human,
    Device,
    EEGData,
    File,
    Task,
    SearchFile,
    SearchResult,
)

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notification_router)

PROJECT_ROOT_PATH = Path(__file__).parent.parent
LOG_ROOT_PATH = PROJECT_ROOT_PATH / "log" / "app"
LOGURU_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS}|{level}|{message}"
logger.add(
    LOG_ROOT_PATH / "access.log",
    format=LOGURU_FORMAT,
    level="INFO",
    rotation=timedelta(days=1),
    backtrace=False,
    diagnose=False,
    enqueue=True,
    colorize=False,
)
logger.add(
    LOG_ROOT_PATH / "error.log",
    format=LOGURU_FORMAT,
    level="ERROR",
    rotation=timedelta(days=1),
    backtrace=True,
    diagnose=True,
    enqueue=True,
    colorize=False,
)

app.state.database = database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_ROOT_PATH / "uvicorn.log", when="D", backupCount=7, encoding="UTF-8"
    )
    uvicorn_logger_handler.setFormatter(
        logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")
    )
    uvicorn_logger.addHandler(uvicorn_logger_handler)

    await user.create_root_user()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.middleware("http")
async def log_access_api(request: Request, call_next: Callable):
    start_time = datetime.now()
    response = await call_next(request)
    rt = datetime.now() - start_time
    access_info = {
        "method": request.method,
        "url": str(request.url),
        "client_address": request.client,
        "rt": int(rt.total_seconds() * 1000),
        "status_code": response.status_code,
    }
    logger.info(json.dumps(access_info))
    return response


@app.exception_handler(HTTPException)
async def handle_http_exception(_request: Request, e: HTTPException):
    return JSONResponse(
        status_code=e.status_code,
        content=Response(code=CODE_FAIL, message=e.detail).dict(),
    )


@app.exception_handler(RequestValidationError)
async def handle_http_exception(_request: Request, e: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=Response(code=CODE_FAIL, message=repr(e)).dict(),
    )


@app.exception_handler(ExpiredSignatureError)
async def handle_expired_token_exception(_request: Request, _e: ExpiredSignatureError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content=Response(code=CODE_SESSION_TIMEOUT, message="session timeout").dict(),
    )


@app.get("/")
async def index():
    if config.DEBUG_MODE:
        return RedirectResponse(url="/docs")
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


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
        search: str | None = Query(title="搜索内容", default=None),
):
    return GetExperimentsByPageResponse(code=CODE_SUCCESS, data=[Experiment()])


@app.get(
    "/api/getExperimentsByPage",
    response_model=GetExperimentsByIdResponse,
    name="获取实验详情",
    description="根据实验编号获取实验详细信息",
)
def get_experiments_by_id(experiment_id: str = Query(title="实验编号")):
    return GetExperimentsByIdResponse(code=CODE_SUCCESS, data=Experiment())


@app.post(
    "/api/addParadigms",
    response_model=AddParadigmResponse,
    name="新增实验范式",
    description="新增实验相关的范式描述",
)
def add_paradigm(request: AddParadigmRequest):
    return AddParadigmResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getParadigms",
    response_model=GetParadigmsResponse,
    name="获取实验范式",
    description="根据实验编号获取实验相关的所有范式描述",
)
def get_paradigms(experiment_id: str = Query(title="实验编号")):
    return GetParadigmsResponse(code=CODE_SUCCESS, data=[Paradigm()])


@app.get(
    "/api/getParadigmById",
    response_model=GetParadigmByIdResponse,
    name="获取具体实验范式详情",
    description="根据实验范式ID获取单条实验范式的详情",
)
def get_paradigm_by_id(
        experiment_id: str = Query(title="实验编号"),
        paradigm_id: str = Query(alias="id", title="实验范式id"),
):
    return GetParadigmByIdResponse(code=CODE_SUCCESS, data=Paradigm())


@app.delete(
    "/api/deleteParadigms",
    response_model=DeleteParadigmsResponse,
    name="删除实验范式",
    description="删除指定的实验范式",
)
def delete_paradigms(request: DeleteParadigmsRequest):
    return DeleteParadigmsResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getDocType",
    response_model=GetDocTypeResponse,
    name="获取平台可筛选的文件格式",
    description="获取平台支持的或者已上传的文件格式后缀列表",
)
def get_doc_type():
    return GetDocTypeResponse(code=CODE_SUCCESS, data=["MP4", "BDF", "EEG"])


@app.get(
    "/api/getDocByPage",
    response_model=GetDocByPageResponse,
    name="获取文件列表",
    description="根据文件格式，分页获取文件列表，默认获取所有文件的前30个",
)
def get_doc_by_page(
        experiment_id: str = Query(title="实验编号"),
        doc_type: str = Query(title="文档格式"),
        offset: int = Query(title="分页起始位置", default=0),
        limit: int = Query(title="分页大小", default=30),
):
    return GetDocByPageResponse(
        code=CODE_SUCCESS,
        data=[
            GetDocByPageResponse.Data(file_id=1, name="file1", url="http://example.com")
        ],
    )


@app.delete(
    "/api/deleteDoc",
    response_model=DeleteDocResponse,
    name="删除文件",
    description="删除上传的数据文件",
)
def delete_doc(
        experiment_id: str = Query(title="实验编号"),
        file_id: int = Query(title="文件ID"),
):
    return DeleteDocResponse(code=CODE_SUCCESS)


@app.post(
    "/api/addFile",
    response_model=AddFileResponse,
    name="批量上传文件",
    description="从用户本地上传文件到服务端",
)
def delete_doc(files: list[UploadFile]):
    return AddFileResponse(
        code=CODE_SUCCESS,
        data=[AddFileResponse.Data(name="file1", url="http://example.com")],
    )


@app.get(
    "/api/getHumanSubjectByPage",
    response_model=GetHumanSubjectByPageResponse,
    name="获取人类被试列表",
    description="分页获取人类被试列表，默认每页返回10个元素",
)
def get_human_subject_by_page(
        experiment_id: str = Query(title="实验编号"),
        offset: int = Query(title="分页起始位置", default=0),
        limit: int = Query(title="分页大小", default=10),
):
    return GetHumanSubjectByPageResponse(code=CODE_SUCCESS, data=[Human()])


@app.post(
    "/api/addHumanSubject",
    response_model=AddHumanSubjectResponse,
    name="新增人类被试",
    description="新增一条人类被试记录",
)
def add_human_subject(request: AddHumanSubjectRequest):
    return AddHumanSubjectResponse(code=CODE_SUCCESS)


@app.post(
    "/api/updateHumanSubject",
    response_model=UpdateHumanSubjectResponse,
    name="编辑人类被试",
    description="更新某一个人类被试的信息",
)
def update_human_subject(request: UpdateHumanSubjectRequest):
    return UpdateHumanSubjectResponse(code=CODE_SUCCESS)


@app.delete(
    "/api/deleteHumanSubject",
    response_model=DeleteHumanSubjectResponse,
    name="删除人类被试",
    description="删除某个实验下的某个人类被试",
)
def delete_human_subject(request: DeleteHumanSubjectRequest):
    return DeleteHumanSubjectResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getDeviceByPage",
    response_model=GetDeviceByPageResponse,
    name="获取设备列表",
    description="分页获取设备列表，默认每页返回10个元素",
)
def get_device_by_page(
        experiment_id: str = Query(title="实验编号"),
        offset: int = Query(title="分页起始位置", default=0),
        limit: int = Query(title="分页大小", default=10),
):
    return GetDeviceByPageResponse(code=CODE_SUCCESS, data=[Device()])


@app.post(
    "/api/addDevice",
    response_model=AddDeviceResponse,
    name="新增设备",
    description="新增实验设备",
)
def add_device(request: AddDeviceRequest):
    return AddDeviceResponse(code=CODE_SUCCESS)


@app.get(
    "/api/getDeviceById",
    response_model=GetDeviceByIdResponse,
    name="获取设备详情",
    description="根据设备ID获取设备详情",
)
def get_device_by_id(
        experiment_id: str = Query(title="实验编号"),
        equipment_id: str = Query(title="设备编号"),
):
    return GetDeviceByIdResponse(code=CODE_SUCCESS, data=Device())


@app.post(
    "/api/updateDevice",
    response_model=UpdateDeviceResponse,
    name="编辑设备",
    description="更新设备信息",
)
def update_device(request: UpdateDeviceRequest):
    return UpdateDeviceResponse(code=CODE_SUCCESS)


@app.delete(
    "/api/deleteDevice",
    response_model=DeleteDeviceResponse,
    name="删除设备",
    description="删除某个实验下的某个设备",
)
def delete_device(request: DeleteDeviceRequest):
    return DeleteDeviceResponse(code=CODE_SUCCESS)


@app.post(
    "/api/data/displayEEG",
    response_model=DisplayEEGResponse,
    name="查看EEG数据",
    description="查看EEG数据文件指定段",
)
def display_eeg(request: DisplayEEGRequest):
    return DisplayEEGResponse(code=CODE_SUCCESS, data=EEGData())


@app.get(
    "/api/getFiles",
    response_model=GetFilesResponse,
    name="获取任务可用目标文件列表",
    description="新建任务时获取任务可用的目标数据文件列表",
)
def get_files():
    return GetFilesResponse(code=CODE_SUCCESS, data=[File()])


@app.get(
    "/api/getTaskByPage",
    response_model=GetTaskByPageResponse,
    name="获取任务列表",
    description="分页获取任务列表，支持按任务名称、开始时间、类型、状态过滤",
)
def get_task_by_page(
        offset: int = Query(title="分页起始位置", default=0),
        limit: int = Query(title="分页大小", default=20),
        task_name: str | None = Query(title="任务名称", default=None),
        start_time: str | None = Query(title="开始时间", default=None),
        task_type: str | None = Query(title="任务类型", default=None),
        status: str | None = Query(title="任务状态", default=None),
):
    return GetTaskByPageResponse(code=CODE_SUCCESS, data=[Task()])


@app.post(
    "/api/addTask",
    response_model=AddTaskResponse,
    name="新增任务",
    description="新增任务",
)
def add_task(request: AddTaskRequest):
    return AddTaskResponse(code=CODE_SUCCESS, data=[Task()])


@app.get(
    "/api/getTaskByID",
    response_model=GetTaskByIDResponse,
    name="获取任务详细信息",
    description="获取指定任务的相关信息，包括基础信息和步骤执行信息",
)
def get_task_by_id(task_id: str = Query(title="任务ID")):
    return GetTaskByIDResponse(code=CODE_SUCCESS, data=Task())


@app.get(
    "/api/getTaskStepsByID",
    response_model=GetTaskStepsByIDResponse,
    name="获取任务流程的步骤信息",
    description="获取指定任务的相关信息，包括基础信息和步骤执行信息",
)
def get_task_steps_by_id(task_id: str = Query(title="任务ID")):
    return GetTaskStepsByIDResponse(code=CODE_SUCCESS, data=[Task.Steps()])


@app.get(
    "/api/getFilterStepResultByID",
    response_model=GetFilterStepResultByIDResponse,
    name="获取滤波类型步骤的执行结果",
    description="页面点击滤波类型步骤后，获取对应步骤的执行结果，即波形图数据",
)
def get_filter_step_result_by_id(
        task_id: str = Query(title="任务ID"),
        operation_id: str = Query(title="操作步骤ID"),
):
    return GetFilterStepResultByIDResponse(
        code=CODE_SUCCESS,
        data=[
            [1370131200000, 0.7695],
            [1370217600000, 0.7648],
            [1370304000000, 0.7645],
        ],
    )


@app.get(
    "/api/getAnalysisStepResultByID",
    response_model=GetAnalysisStepResultByIDResponse,
    name="获取分析类型步骤的执行结果",
    description="页面点击分析步骤后，获取分析步骤的执行结果，即生成的png图片路径",
)
def get_analysis_step_result_by_id(
        task_id: str = Query(title="任务ID"),
        operation_id: str = Query(title="操作步骤ID"),
):
    return GetAnalysisStepResultByIDResponse(
        code=CODE_SUCCESS,
        data="http://xxx.xxx/result_img.png",
    )


@app.post(
    "/api/search/uploadSearchFile",
    response_model=UploadSearchFileResponse,
    name="上传待检索文件",
    description="将本地EEG数据上传至服务端并解析返回波形图数据",
)
def upload_search_file(file: UploadFile):
    return UploadSearchFileResponse(code=CODE_SUCCESS, data=SearchFile())


@app.post(
    "/api/search/goSearch",
    response_model=GoSearchResponse,
    name="搜索信号",
    description="根据选择的待检索信号，由服务端检索并返回相似的信号数组",
)
def go_search(request: GoSearchRequest):
    return GoSearchResponse(code=CODE_SUCCESS, data=[SearchResult()])
