import json

from fastapi import APIRouter, Depends, Query

from app.api import check_file_exists, check_task_exists
from app.common.config import config
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.crud import task as crud
from app.db.orm import Task, TaskStatus, TaskStep, TaskStepType, TaskType
from app.model import convert
from app.model.field import JsonDict
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response, wrap_api_response
from app.model.schema import (
    TaskBaseInfo,
    TaskCreate,
    TaskInfo,
    TaskSearch,
    TaskSourceFileResponse,
    TaskSourceFileSearch,
    TaskStepInfo,
)

router = APIRouter(tags=["task"])


@router.get(
    "/api/getSourceFilesToCreateTask",
    description="获取创建任务时可用的文件列表",
    response_model=Response[Page[TaskSourceFileResponse]],
)
@wrap_api_response
def get_source_files_to_create_task(
    search: TaskSourceFileSearch = Depends(), ctx: ResearcherContext = Depends()
) -> Page[TaskSourceFileResponse]:
    if search.file_type:
        lower_extension = search.file_type.lower()
        if lower_extension not in config.SUPPORTED_TASK_SOURCE_FILE_TYPES:
            raise ServiceError.invalid_request(f"{search.file_type}不是支持的文件类型")
        search.file_type = lower_extension

    total, file_experiments = crud.search_source_files(ctx.db, search)
    items = convert.map_list(convert.file_experiment_orm_2_task_source_response, file_experiments)
    return Page(total=total, items=items)


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
            "parameter": dump_compact_json(step.parameters),
            "index": i + 1,
            "status": TaskStatus.wait_start,
        }
        for i, step in enumerate(create.steps)
    ]
    success = common_crud.bulk_insert_rows(ctx.db, TaskStep, step_dicts, commit=True)
    if not success:
        raise ServiceError.database_fail("创建任务失败")

    return task_id


def dump_compact_json(obj: JsonDict) -> str:
    return json.dumps(obj, indent=None, separators=(",", ":"))


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


@router.get("/api/getTaskInfo", description="获取任务详情", response_model=Response[TaskInfo])
@wrap_api_response
def get_task_info(task_id: int = Query(ge=0), ctx: HumanSubjectContext = Depends()) -> TaskInfo:
    orm_task = crud.get_task_info_by_id(ctx.db, task_id)
    if orm_task is None:
        raise ServiceError.not_found("任务不存在")

    task_info = convert.task_orm_2_info(orm_task)
    return task_info


@router.get(
    "/api/getTasksByPage", description="分页查找任务", response_model=Response[Page[TaskBaseInfo]]
)
@wrap_api_response
def get_tasks_by_page(
    search: TaskSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[TaskBaseInfo]:
    total, orm_tasks = crud.search_task(ctx.db, search)
    task_base_infos = convert.map_list(convert.task_orm_2_base_info, orm_tasks)
    return Page(total=total, items=task_base_infos)


@router.get(
    "/api/getTaskStepsInfo", description="获取任务步骤详情", response_model=Response[list[TaskStepInfo]]
)
@wrap_api_response
def get_task_steps_info(
    task_id: int = Query(ge=0), ctx: HumanSubjectContext = Depends()
) -> list[TaskStepInfo]:
    check_task_exists(ctx.db, task_id)

    orm_task_steps = crud.get_steps_by_task_id(ctx.db, task_id)
    task_step_infos = convert.map_list(convert.task_step_orm_2_info, orm_task_steps)
    return task_step_infos
