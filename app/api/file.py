import logging
import os.path
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi import File as FastApiFile
from fastapi import Form, Query, UploadFile
from fastapi.responses import FileResponse as FastApiFileResponse
from sqlalchemy.orm import Session

from app.common.config import config
from app.common.context import Context, human_subject_context, not_logon_context, researcher_context
from app.common.exception import ServiceError
from app.db import common_crud, crud
from app.db.orm import File
from app.model.request import DeleteModelRequest, GetModelsByPageParam, get_models_by_page
from app.model.response import NoneResponse, PagedData, Response, wrap_api_response
from app.model.schema import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["file"])


@router.post("/api/uploadFile", description="上传文件", response_model=Response[int])
@wrap_api_response
def upload_file(
    experiment_id: int = Form(description="实验ID", default=0),
    is_original: bool = Form(description="是否是设备产生的原始文件"),
    file: UploadFile = FastApiFile(),
    ctx: Context = Depends(researcher_context),
) -> int:
    file_index = get_next_index(ctx.db, experiment_id)
    name = file.filename
    extension = name.rsplit(".", 1)[-1].lower()
    store_path = get_os_path(experiment_id, file_index, extension)
    write_file(file, store_path)
    file_size = os.path.getsize(store_path) / 1024 / 1024
    file_dict = {
        "experiment_id": experiment_id,
        "name": name,
        "extension": extension,
        "index": file_index,
        "size": file_size,
        "is_original": is_original,
    }
    file_id = common_crud.insert_row(ctx.db, File, file_dict, commit=True)
    if not file_id:
        raise ServiceError.database_fail("上传文件失败")
    return file_id


@router.get("/api/getFileTypes", description="获取当前实验已有的文件类型", response_model=Response[list[str]])
@wrap_api_response
def get_file_types(
    experiment_id: int = Query(description="实验ID"), ctx: Context = Depends(human_subject_context)
) -> list[str]:
    extensions = crud.get_file_extensions(ctx.db, experiment_id)
    return extensions


@router.get(
    "/api/getFilesByPage", description="分页获取文件列表", response_model=Response[list[FileResponse]]
)
@wrap_api_response
def get_files_by_page(
    experiment_id: int = Query(description="实验ID", default=0),
    name: str = Query(description="文件名，模糊查找", default=""),
    file_type: str = Query(description="文件类型，模糊查找", default=""),
    page_param: GetModelsByPageParam = Depends(get_models_by_page),
    ctx: Context = Depends(human_subject_context),
) -> PagedData[FileResponse]:
    files = crud.search_files(ctx.db, experiment_id, name, file_type, page_param)
    return files


@router.get("/api/downloadFile/{file_id}", description="下载文件")
def download_file(
    file_id: int = Path(description="文件ID"), ctx: Context = Depends(not_logon_context)
) -> FastApiFileResponse:
    file = common_crud.select_row_by_id(ctx.db, File, file_id)
    if file is None:
        raise ServiceError.not_found("未找到文件")

    os_path = get_os_path(file.experiment_id, file.index, file.extension)
    return FastApiFileResponse(path=os_path, filename=file.name)


@router.delete("/api/deleteFile", description="删除文件", response_model=NoneResponse)
@wrap_api_response
def delete_file(request: DeleteModelRequest, ctx: Context = Depends(researcher_context)) -> None:
    file = common_crud.select_row_by_id(ctx.db, File, request.id)
    if file is None:
        return None

    os_path = get_os_path(file.experiment_id, file.index, file.extension)
    try:
        os_path.unlink(missing_ok=False)
    except FileNotFoundError:
        logger.error(f"failed to delete file {os_path}, not found")
    else:
        logger.info(f"deleted file {os_path}")

    success = common_crud.update_row_as_deleted(ctx.db, File, request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除文件失败")


def get_next_index(db: Session, experiment_id: int) -> int:
    last_index = crud.get_file_last_index(db, experiment_id)
    return last_index + 1 if last_index is not None else 1


def get_os_path(experiment_id: int, file_index: int, extension: str) -> Path:
    file_name = f"{file_index}.{extension}" if extension else str(file_index)
    return config.FILE_ROOT / str(experiment_id) / file_name


def write_file(file: UploadFile, store_path: Path) -> None:
    try:
        store_path.parent.mkdir(exist_ok=True)
        with open(store_path, "wb") as f:
            while content := file.file.read(config.FILE_CHUNK_SIZE):
                f.write(content)
    except Exception as e:
        logger.error(f"fail to write file, {store_path=}")
        raise e
    else:
        logger.info(f"write file success, {store_path=}")
    finally:
        file.file.close()
