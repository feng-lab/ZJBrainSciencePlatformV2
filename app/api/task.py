from fastapi import APIRouter, Depends

from app.common.config import config
from app.common.context import ResearcherContext
from app.common.exception import ServiceError
from app.db.crud import task as crud
from app.model import convert
from app.model.response import PagedData, Response, wrap_api_response
from app.model.schema import TaskSourceFileResponse, TaskSourceFileSearch

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
