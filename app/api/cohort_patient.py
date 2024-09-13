from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from starlette.responses import guess_type
from zjbs_file_client import Client, FileType

import app.db.crud.cohort_patient as crud
from app.api import check_cohort_patient_exists, wrap_api_response
from app.common.config import config
from app.common.context import HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import CohortPatient, CohortPatientFile, CohortPatientFromData
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import (
    CohortPatientInfo,
    CohortPatientSearch,
    CreateCohortPatient,
    PageParm,
    UpdateCohortPatientRequest,
)

router = APIRouter(tags=["cohort_patient"])


@router.post("/api/createCohortPatient", description="队列患者表", response_model=Response[int])
@wrap_api_response
def create_cohort_patient(request: CreateCohortPatient, ctx: ResearcherContext = Depends()) -> int:
    cohort_patient_dict = request.dict()
    cohort_patient_id = common_crud.insert_row(ctx.db, CohortPatient, cohort_patient_dict, commit=False)
    if cohort_patient_id is None:
        raise ServiceError.database_fail()
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post(
            "/create-directory", params={"path": dataset_file_path(cohort_patient_id, "/"), "exists_ok": True}
        )
        if not file_server_response.is_success:
            raise ServiceError.remote_service_error(file_server_response.reason_phrase)

    ctx.db.commit()
    return cohort_patient_id


def dataset_file_path(cohort_patient_id: int, *parts: str) -> PurePosixPath:
    file_path = PurePosixPath(f"/cohort_patient_{cohort_patient_id}")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    return file_path


@router.post("/api/getCohortPatientInfo", description="获取病人信息详情", response_model=Response[CohortPatientInfo])
@wrap_api_response
def get_cohort_patient_info(cohort_patient_id: int, ctx: HumanSubjectContext = Depends()) -> CohortPatientInfo:
    orm_cohort_patient = common_crud.get_row_by_id(ctx.db, CohortPatient, cohort_patient_id)
    if orm_cohort_patient is None:
        raise ServiceError.not_found(Entity.orm_cohort_patient)
    cohort_patient_info = convert.cohort_patient_orm_2_info(orm_cohort_patient)
    return cohort_patient_info


@router.post("/api/getCohortPatientByPage", description="获取病人信息列表", response_model=Response[Page[CohortPatientInfo]])
@wrap_api_response
def get_cohort_patient_by_page(
    search: CohortPatientSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[CohortPatientInfo]:
    print(search.dict())
    total, orm_cohort_patient = crud.search_cohort_patient(ctx.db, search)
    cohort_patient_infos = convert.map_list(convert.cohort_patient_orm_2_info, orm_cohort_patient)
    return Page(total=total, items=cohort_patient_infos)


@router.post("/api/updateCohortPatient", description="更新病人信息", response_model=NoneResponse)
@wrap_api_response
def update_dataset(request: UpdateCohortPatientRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_cohort_patient = common_crud.get_row_by_id(ctx.db, CohortPatient, request.id)
    if orm_cohort_patient is None:
        raise ServiceError.not_found(Entity.orm_cohort_patient)
    orm_cohort_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, CohortPatient, orm_cohort_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteCohortPatient", description="删除病人信息", response_model=NoneResponse)
@wrap_api_response
def delete_dataset(request: DeleteModelRequest, ctx: ResearcherContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, CohortPatient, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.database_fail()


### 其他表单建立
# @router.post("/api/createPatientFormData", description="更新患者表单数据", response_model=Response[int])
# @wrap_api_response
# def create_cohort_patient(request: CreatePatientFormDataRequest, ctx: ResearcherContext = Depends())-> int:
#
#     orm_dataset = common_crud.get_row_by_id(ctx.db, Dataset, request.id)
#
# @router.post("/api/createPatientMemo", description="更新患者备注信息", response_model=Response[int])
# @wrap_api_response
# def create_cohort_patient(request: UpdateModelRequest, ctx: ResearcherContext = Depends())-> None:
#     orm_dataset = common_crud.get_row_by_id(ctx.db, Dataset, request.id)


@router.post("/api/uploadCohortPatientFile", description="上传病人文件", response_model=NoneResponse)
@wrap_api_response
def upload_cohort_patient_file(
    cohort_patient_id: Annotated[int, Form(description="病人ID")],
    directory: Annotated[str, Form(description="目标文件夹路径")],
    file: Annotated[UploadFile, File(description="文件")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_cohort_patient_exists(ctx.db, cohort_patient_id)
    directory_path = dataset_file_path(cohort_patient_id, directory)
    with Client(config.FILE_SERVER_URL) as client:
        client.upload(str(directory_path), file.file, file.filename, mkdir=True, allow_overwrite=True)
        file_format = file.filename.split(".")[-1].lower()
    success = common_crud.insert_row(
        ctx.db,
        CohortPatientFile,
        {
            "patient_id": cohort_patient_id,
            "other_path": str(directory_path),
            "file_size": float(file.size),
            "file_format": str(file_format),
        },
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteCohortPatientFile", description="删除病人文件", response_model=NoneResponse)
@wrap_api_response
def delete_cohort_patient_file(
    cohort_patient_id: Annotated[int, Body(description="病人ID")],
    path: Annotated[str, Body(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> None:
    check_cohort_patient_exists(ctx.db, cohort_patient_id)
    path = dataset_file_path(cohort_patient_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        client.delete(str(path))

    success = common_crud.update_row_as_deleted(
        ctx.db,
        CohortPatientFile,
        where=[CohortPatientFile.patient_id == cohort_patient_id, CohortPatientFile.other_path == path],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()
