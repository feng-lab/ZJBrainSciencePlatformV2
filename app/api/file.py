import logging
import os.path
from os import PathLike
from pathlib import Path
from typing import IO
from zipfile import ZipFile

from fastapi import APIRouter, Depends
from fastapi import File as FastApiFile
from fastapi import Form, Query, UploadFile
from fastapi.responses import FileResponse as FastApiFileResponse
from sqlalchemy.orm import Session

from app.common.config import config
from app.common.context import HumanSubjectContext, NotLogonContext, ResearcherContext
from app.common.exception import ServiceError
from app.db import common_crud
from app.db.crud import file as crud
from app.db.orm import StorageFile, VirtualFile
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
    virtual_file_id, file_type, os_storage_path = save_file(
        ctx.db, file, experiment_id, is_original
    )
    if file_type == "zip" and is_nev_zip_file(os_storage_path):
        handle_nev_zip_file(ctx.db, os_storage_path, experiment_id, virtual_file_id)
    return virtual_file_id


def save_file(
    db: Session, file: UploadFile, experiment_id: int, is_original: bool
) -> tuple[int, str, Path]:
    # 插入VirtualFile行
    name = file.filename
    file_type = get_filename_extension(name)
    virtual_file_dict = {
        "experiment_id": experiment_id,
        "name": name,
        "file_type": file_type,
        "is_original": is_original,
        "size": -1.0,
    }
    virtual_file_id = common_crud.insert_row(db, VirtualFile, virtual_file_dict, commit=False)
    if virtual_file_id is None:
        raise ServiceError.database_fail("上传文件失败")

    # 插入StorageFile行
    storage_path = f"{experiment_id}/{virtual_file_id}{'.' + file_type if file_type else ''}"
    storage_file_dict = {
        "virtual_file_id": virtual_file_id,
        "name": name,
        "size": -1.0,
        "storage_path": storage_path,
    }
    storage_file_id = common_crud.insert_row(db, StorageFile, storage_file_dict, commit=False)
    if storage_file_id is None:
        raise ServiceError.database_fail("上传文件失败")

    # 写入文件
    os_storage_path = config.FILE_ROOT / storage_path
    write_file(file.file, os_storage_path)

    # 更新size字段
    file_size = get_file_size(os_storage_path)
    if not common_crud.update_row(
        db, VirtualFile, {"size": file_size}, id=virtual_file_id, commit=False
    ):
        raise ServiceError.database_fail("上传文件失败")
    if not common_crud.update_row(
        db, StorageFile, {"size": file_size}, id=storage_file_id, commit=True
    ):
        raise ServiceError.database_fail("上传文件失败")

    return virtual_file_id, file_type, os_storage_path


def is_nev_zip_file(path: Path) -> bool:
    nev_extensions = {"nev", "ccf", "ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7", "ns8", "ns9"}
    with ZipFile(path, mode="r") as zip_file:
        extensions = set()
        for filename in zip_file.namelist():
            if filename.endswith("/"):
                continue
            file_extension = get_filename_extension(filename)
            if file_extension in extensions or file_extension not in nev_extensions:
                return False
            extensions.add(file_extension)
        return True


def handle_nev_zip_file(
    db: Session, zip_file_path: Path, experiment_id: int, virtual_file_id: int
) -> None:
    # 更新file_type
    if not common_crud.update_row(
        db, VirtualFile, {"file_type": "nev"}, id=virtual_file_id, commit=False
    ):
        raise ServiceError.database_fail("上传文件失败")

    # 创建文件夹
    nev_dir = config.FILE_ROOT / str(experiment_id) / str(virtual_file_id)
    nev_dir.mkdir()

    # 解压缩zip文件
    storage_file_dicts = []
    with ZipFile(zip_file_path, mode="r") as zip_file:
        for filename, file_info in zip_file.NameToInfo.items():
            file_extension = get_filename_extension(filename)
            if not file_extension:
                continue
            output_file_name = f"{virtual_file_id}.{file_extension}"
            output_file_path = nev_dir / output_file_name
            with zip_file.open(file_info, mode="r") as zipped_file:
                write_file(zipped_file, output_file_path)
            storage_file_dicts.append(
                {
                    "virtual_file_id": virtual_file_id,
                    "name": output_file_name,
                    "size": get_file_size(output_file_path),
                    "storage_path": f"{experiment_id}/{virtual_file_id}/{output_file_name}",
                }
            )

    # 插入StorageFile行
    if not common_crud.bulk_insert_rows(db, StorageFile, storage_file_dicts, commit=True):
        raise ServiceError.database_fail("上传文件失败")


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
    file_responses = convert.map_list(convert.virtual_file_orm_2_response, files)
    return Page(total=total, items=file_responses)


@router.get("/api/downloadFile/{file_id}", description="下载文件")
def download_file(
    file_id: int = Path(description="文件ID"), ctx: NotLogonContext = Depends()
) -> FastApiFileResponse:
    filename, db_storage_path = crud.get_file_download_info(ctx.db, file_id)
    if filename is None:
        raise ServiceError.not_found("未找到文件")
    os_storage_path = config.FILE_ROOT / db_storage_path
    return FastApiFileResponse(path=os_storage_path, filename=filename)


@router.delete("/api/deleteFile", description="删除文件", response_model=NoneResponse)
@wrap_api_response
def delete_file(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    file_paths = crud.get_db_storage_paths(ctx.db, request.id)
    if not common_crud.update_row_as_deleted(ctx.db, VirtualFile, id=request.id, commit=False):
        raise ServiceError.database_fail("删除文件失败")
    if not common_crud.update_row_as_deleted(
        ctx.db, StorageFile, where=[StorageFile.virtual_file_id == request.id], commit=True
    ):
        raise ServiceError.database_fail("删除文件失败")
    for file_path in file_paths:
        delete_os_file(config.FILE_ROOT / file_path)


def get_filename_extension(filename: str) -> str:
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
        return parts[1]
    return ""


def get_file_size(path: PathLike) -> float:
    return os.path.getsize(path) / 1024 / 1024


def get_os_path(experiment_id: int, file_id: int, extension: str) -> Path:
    file_name = f"{file_id}.{extension}" if extension else str(file_id)
    return config.FILE_ROOT / str(experiment_id) / file_name


def write_file(file: IO[bytes], store_path: Path) -> None:
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
