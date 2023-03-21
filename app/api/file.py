import logging
import os.path
from pathlib import Path
from typing import BinaryIO

from fastapi import APIRouter, Depends
from fastapi import File as FastApiFile
from fastapi import Form, Query, UploadFile
from fastapi.responses import FileResponse as FastApiFileResponse

from app.common.config import config
from app.common.context import HumanSubjectContext, NotLogonContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.crud import file as crud
from app.db.orm import File
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response, wrap_api_response
from app.model.schema import FileResponse, FileSearch

logger = logging.getLogger(__name__)

router = APIRouter(tags=["file"])


@router.post("/api/uploadFile", description="上传文件", response_model=Response[int])
@wrap_api_response
def upload_file(
    experiment_id: int = Form(description="实验ID", default=0),
    is_original: bool = Form(description="是否是设备产生的原始文件"),
    file: UploadFile = FastApiFile(),
    ctx: ResearcherContext = Depends(),
) -> int:
    database_error = ServiceError.database_fail("上传文件失败")

    name = file.filename
    extension = name.rsplit(".", 1)[-1].lower()
    file_dict = {
        "experiment_id": experiment_id,
        "name": name,
        "extension": extension,
        "size": -1.0,
        "is_original": is_original,
    }
    file_id = common_crud.insert_row(ctx.db, File, file_dict, commit=False)
    if file_id is None:
        raise database_error

    store_path = get_os_path(experiment_id, file_id, extension)
    write_file(file.file, store_path)

    file_size = os.path.getsize(store_path) / 1024 / 1024
    update_size_success = common_crud.update_row(
        ctx.db, File, {"size": file_size}, id=file_id, commit=True
    )
    if not update_size_success:
        raise database_error

    return file_id


@router.get("/api/getFileTypes", description="获取当前实验已有的文件类型", response_model=Response[list[str]])
@wrap_api_response
def get_file_types(
    experiment_id: int = Query(description="实验ID"), ctx: HumanSubjectContext = Depends()
) -> list[str]:
    extensions = crud.get_file_extensions(ctx.db, experiment_id)
    return list(extensions)


@router.get(
    "/api/getFilesByPage", description="分页获取文件列表", response_model=Response[list[FileResponse]]
)
@wrap_api_response
def get_files_by_page(
    search: FileSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[FileResponse]:
    total, files = crud.search_files(ctx.db, search)
    file_responses = convert.map_list(convert.file_orm_2_response, files)
    return Page(total=total, items=file_responses)


@router.get("/api/downloadFile/{file_id}", description="下载文件")
def download_file(
    file_id: int = Path(description="文件ID"), ctx: NotLogonContext = Depends()
) -> FastApiFileResponse:
    file = common_crud.get_row_by_id(ctx.db, File, file_id)
    if file is None:
        raise ServiceError.not_found("未找到文件")

    os_path = get_os_path(file.experiment_id, file_id, file.extension)
    return FastApiFileResponse(path=os_path, filename=file.name)


@router.delete("/api/deleteFile", description="删除文件", response_model=NoneResponse)
@wrap_api_response
def delete_file(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    file = common_crud.get_row_by_id(ctx.db, File, request.id)
    if file is None:
        return None

    os_path = get_os_path(file.experiment_id, file.id, file.extension)
    delete_os_file(os_path)

    success = common_crud.update_row_as_deleted(ctx.db, File, id=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail("删除文件失败")


def get_os_path(experiment_id: int, file_id: int, extension: str) -> Path:
    file_name = f"{file_id}.{extension}" if extension else str(file_id)
    return config.FILE_ROOT / str(experiment_id) / file_name


def write_file(file: BinaryIO, store_path: Path) -> None:
    try:
        store_path.parent.mkdir(exist_ok=True)
        with open(store_path, "wb") as f:
            while content := file.read(config.FILE_CHUNK_SIZE):
                f.write(content)
    except Exception as e:
        logger.error(f"fail to write file, {store_path=}")
        raise e
    else:
        logger.info(f"write file success, {store_path=}")
    finally:
        file.close()


def delete_os_file(path: Path) -> None:
    try:
        path.unlink(missing_ok=False)
    except FileNotFoundError:
        logger.error(f"failed to delete file {path}, not found")
    else:
        logger.info(f"deleted file {path}")
