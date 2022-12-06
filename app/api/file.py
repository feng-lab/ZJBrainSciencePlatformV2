import logging
import os.path
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi import File as FastApiFile
from fastapi import Form, UploadFile

from app.api.auth import get_current_user_as_researcher
from app.config import config
from app.db import crud
from app.model.db_model import File, User
from app.model.response import Response, UploadFileData, wrap_api_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/uploadFile", description="上传文件", response_model=Response[UploadFileData])
@wrap_api_response
async def upload_file(
    experiment_id: int = Form(description="实验ID"),
    path: str = Form(description="文件路径"),
    is_original: bool = Form(description="是否是设备产生的原始文件"),
    file: UploadFile = FastApiFile(),
    _user: User = Depends(get_current_user_as_researcher()),
) -> UploadFileData:
    file_index = await get_next_index(experiment_id)
    extension = path.rsplit(".", 1)[-1]
    store_path = get_real_store_path(experiment_id, file_index, extension)
    write_file(file, store_path)
    file_size = os.path.getsize(store_path) / 1024 / 1024
    db_file = File(
        experiment_id=experiment_id,
        path=path,
        extension=extension,
        index=file_index,
        size=file_size,
        is_original=is_original,
    )
    db_file = await crud.create_model(db_file)
    return UploadFileData(id=db_file.id, index=file_index, path=path)


async def get_next_index(experiment_id: int) -> int:
    last_index_file = await crud.get_last_index_file(experiment_id)
    return last_index_file.index + 1 if last_index_file is not None else 1


def get_real_store_path(experiment_id: int, file_index: int, extension: str) -> Path:
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
