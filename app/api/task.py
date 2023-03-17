import json

from fastapi import APIRouter, Depends

from app.api import check_file_exists
from app.common.config import config
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.crud import task as crud
from app.db.orm import Task, TaskStatus, TaskStep, TaskStepType, TaskType
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import TaskCreate, TaskSourceFileResponse, TaskSourceFileSearch

router = APIRouter(tags=["task"])


@router.get(
    "/api/getSourceFilesToCreateTask",
    description="获取创建任务时可用的文件列表",
    response_model=Response[PagedData[TaskSourceFileResponse]],
)
@wrap_api_response
def get_source_files_to_create_task(
    search: TaskSourceFileSearch = Depends(), ctx: ResearcherContext = Depends()
) -> PagedData[TaskSourceFileResponse]:
    if search.extension:
        lower_extension = search.extension.lower()
        if lower_extension not in config.SUPPORTED_TASK_SOURCE_FILE_TYPES:
            raise ServiceError.invalid_request(f"{search.extension}不是支持的文件类型")
        search.extension = lower_extension

    total, file_experiments = crud.search_source_files(ctx.db, search)
    items = convert.map_list(convert.file_experiment_orm_2_task_source_response, file_experiments)
    return PagedData(total=total, items=items)


@router.post("/api/createTask", description="创建任务", response_model=Response[int])
@wrap_api_response
def create_task(create: TaskCreate, ctx: ResearcherContext = Depends()) -> int:
    check_file_exists(ctx.db, create.source_file)

    if all(step.step_type is TaskStepType.preprocess for step in create.steps):
        task_type = TaskType.preprocess
    elif all(step.step_type is TaskStepType.analysis for step in create.steps):
        task_type = TaskType.analysis
    else:
        task_type = TaskType.preprocess_analysis
    task_create_dict = {
        "name": create.name,
        "description": create.description,
        "source_file": create.source_file,
        "type": task_type,
        "status": TaskStatus.wait_start,
        "creator": ctx.user_id,
    }
    task_id = common_crud.insert_row(ctx.db, Task, task_create_dict, commit=(not create.steps))
    if task_id is None:
        raise ServiceError.database_fail("创建任务失败")

    step_dicts = [
        {
            "task_id": task_id,
            "name": step.name,
            "type": step.step_type,
            "parameter": json.dumps(step.parameters),
            "index": i + 1,
            "status": TaskStatus.wait_start,
        }
        for i, step in enumerate(create.steps)
    ]
    success = common_crud.bulk_insert_rows(ctx.db, TaskStep, step_dicts, commit=True)
    if not success:
        raise ServiceError.database_fail("创建任务失败")

    return task_id


@router.delete("/api/deleteTask", description="删除任务", response_model=NoneResponse)
@wrap_api_response
def delete_task(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, TaskStep, where=[TaskStep.task_id == request.id], commit=False
    )
    if not success:
        raise ServiceError.database_fail("删除任务失败")

    success = common_crud.update_row_as_deleted(ctx.db, Task, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除任务失败")
