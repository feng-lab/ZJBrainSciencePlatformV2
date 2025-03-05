from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from starlette.responses import guess_type
from zjbs_file_client import Client, FileType

import app.db.crud.cohort_patient as crud
from app.api import check_cohort_patient_exists, check_cohort_patient_form_data, wrap_api_response
from app.common.config import config
from app.common.context import AdministratorContext, HumanSubjectContext, ResearcherContext
from app.common.exception import ServiceError
from app.common.localization import Entity
from app.db import common_crud
from app.db.orm import (
    CohortPatient,
    CohortPatientCTherapyDetail,
    CohortPatientFile,
    CohortPatientFromData,
    CohortPatientMemo,
    User,
)
from app.external.province import city
from app.model import convert
from app.model.request import DeleteModelRequest
from app.model.response import NoneResponse, Page, Response
from app.model.schema import (
    CohortPatientIdSearch,
    CohortPatientInfo,
    CohortPatientSearch,
    CreateCohortPatient,
    CreatePatientCTherapyDetailRequest,
    CreatePatientFormDataRequest,
    CreatePatientMemoRequest,
    PatientCTherapyDetail,
    PatientCTherapyDetailInfo,
    PatientFormDataInfo,
    PatientMemoInfo,
    UpdateCohortPatientRequest,
    UpdatePatientFormDataRequest,
)

router = APIRouter(tags=["cohort_patient"])


@router.post("/api/createCohortPatient", description="队列患者表", response_model=Response[int])
@wrap_api_response
def create_cohort_patient(request: CreateCohortPatient, ctx: ResearcherContext = Depends()) -> int:
    cohort_patient_dict = request.dict()
    exists = common_crud.exists_row(
        ctx.db, CohortPatient, where=[CohortPatient.identity_id == request.identity_id]
    )
    if exists:
        raise ServiceError.database_fail()

    cohort_patient_id = common_crud.insert_row(ctx.db, CohortPatient, cohort_patient_dict, commit=False)
    if cohort_patient_id is None:
        raise ServiceError.database_fail()
    ctx.db.commit()
    return cohort_patient_id


def dataset_file_path(cohort_patient_id: int, *parts: str) -> PurePosixPath:
    file_path = PurePosixPath(f"/cohort_patient_{cohort_patient_id}")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    return file_path


def patient_file_path(cohort_patient_id: int | None, type:str,*parts: str) -> str:
    file_path =PurePosixPath(config.PATIENT_FILE_DIR,type,f"cohort_patient_{cohort_patient_id}")
    for part in parts:
        file_path = file_path / part.lstrip("/")
    if part.endswith("/"):
        file_path = file_path.as_posix() + "/"
    return file_path







@router.post("/api/getCohortPatientInfo", description="获取病人信息详情", response_model=Response[CohortPatientInfo])
@wrap_api_response
def get_cohort_patient_info(cohort_patient_id: int, ctx: HumanSubjectContext = Depends()) -> CohortPatientInfo:
    orm_cohort_patient = common_crud.get_row_by_id(ctx.db, CohortPatient, cohort_patient_id)

    if orm_cohort_patient is None:
        raise ServiceError.not_found(Entity.cohort_patient)
    cohort_patient_info = convert.cohort_patient_orm_2_info(orm_cohort_patient)

    orm_user = common_crud.get_row_by_id(ctx.db, User, ctx.user_id)
    print("user_id,patient",ctx.user_id,cohort_patient_id)
    user_accesss = crud.check_dataset_access(ctx.db,ctx.user_id,cohort_patient_info.domain_id)
    print(orm_user.access_level != 1000 or not user_accesss)
    #domain id
    if orm_user.access_level != 1000 and not user_accesss:
        cohort_patient_info.identity_id = None
        cohort_patient_info.family_address_street = None
        cohort_patient_info.phone_number = None
        cohort_patient_info.family_address = None
    return cohort_patient_info


@router.post("/api/getCohortPatientByPage", description="获取病人信息列表", response_model=Response[Page[CohortPatientInfo]])
@wrap_api_response
def get_cohort_patient_by_page(
    search: CohortPatientSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[CohortPatientInfo]:
    total, orm_cohort_patient = crud.search_cohort_patient(ctx.db, search)
    cohort_patient_infos = convert.map_list(convert.cohort_patient_orm_2_info, orm_cohort_patient)
    return Page(total=total, items=cohort_patient_infos)


@router.post("/api/updateCohortPatient", description="更新病人信息", response_model=NoneResponse)
@wrap_api_response
def update_dataset(request: UpdateCohortPatientRequest, ctx: ResearcherContext = Depends()) -> None:
    orm_cohort_patient = common_crud.get_row_by_id(ctx.db, CohortPatient, request.id)
    if orm_cohort_patient is None:
        raise ServiceError.not_found(Entity.cohort_patient)
    orm_cohort_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(ctx.db, CohortPatient, orm_cohort_dict, id_=request.id, commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.delete("/api/deleteCohortPatient", description="删除病人信息", response_model=NoneResponse)
@wrap_api_response
def delete_cohort_patient(request: DeleteModelRequest, ctx: AdministratorContext = Depends()) -> None:
    delete_patient_success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, CohortPatient, ids=[request.id], commit=True
    )
    delete_patient_from_data_success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, CohortPatientFromData, where=[CohortPatientFromData.patient_id == request.id], commit=True
    )
    delete_patient_c_therapy_detail_success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, CohortPatientCTherapyDetail, where=[CohortPatientCTherapyDetail.patient_id == request.id], commit=True
    )
    delete_patient_memo_success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, CohortPatientMemo, where=[CohortPatientMemo.patient_id == request.id], commit=True
    )
    if not (
        delete_patient_success
        and delete_patient_from_data_success
        and delete_patient_c_therapy_detail_success
        and delete_patient_memo_success
    ):
        raise ServiceError.database_fail()


@router.get("/api/getProvinceCity", description="获取省市信息", response_model=Response[dict])
@wrap_api_response
def get_province_city() -> dict:
    return city


@router.post("/api/createPatientFormData", description="创建患者表单数据", response_model=Response[int])
@wrap_api_response
def create_patient_form_data(request: CreatePatientFormDataRequest, ctx: ResearcherContext = Depends()) -> int:
    check_cohort_patient_exists(ctx.db, request.patient_id)
    exists = common_crud.exists_row(
        ctx.db, CohortPatientFromData, where=[CohortPatientFromData.patient_id == request.patient_id]
    )
    if exists:
        raise ServiceError.database_fail()

    patient_form_data_dict = request.dict()
    patient_form_data_id = common_crud.insert_row(ctx.db, CohortPatientFromData, patient_form_data_dict, commit=False)
    if patient_form_data_id is None:
        raise ServiceError.database_fail()
    ctx.db.commit()
    return patient_form_data_id


@router.post("/api/updatePatientFormData", description="更新患者表单数据", response_model=NoneResponse)
@wrap_api_response
def update_patient_form_data(request: UpdatePatientFormDataRequest, ctx: ResearcherContext = Depends()) -> None:
    check_cohort_patient_exists(ctx.db, request.patient_id)
    exists = common_crud.exists_row(
        ctx.db, CohortPatientFromData, where=[CohortPatientFromData.patient_id == request.patient_id]
    )
    if not exists:
        patient_form_data_dict = request.dict()
        patient_form_data_id = common_crud.insert_row(
            ctx.db, CohortPatientFromData, patient_form_data_dict, commit=False
        )
        if patient_form_data_id is None:
            raise ServiceError.database_fail()
        ctx.db.commit()
        return patient_form_data_id

    patient_memo_dict = request.dict(exclude_unset=True)
    success = common_crud.update_row(
        ctx.db,
        CohortPatientFromData,
        patient_memo_dict,
        where=[CohortPatientFromData.patient_id == request.patient_id, CohortPatientFromData.is_deleted == False],
        commit=True,
    )
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/getPatientFormDataInfo", description="获取患者表单数据详情", response_model=Response[PatientFormDataInfo])
@wrap_api_response
def get_patient_form_data_info(patient_id: int, ctx: HumanSubjectContext = Depends()) -> PatientFormDataInfo:
    check_cohort_patient_exists(ctx.db, patient_id)
    orm_patient_form_data = common_crud.get_row(
        ctx.db, CohortPatientFromData, CohortPatientFromData.patient_id == patient_id
    )
    if orm_patient_form_data is None:
        return None
    patient_form_data_info = convert.patient_form_data_orm_2_info(orm_patient_form_data)
    return patient_form_data_info


@router.delete("/api/deletePatientFormData", description="删除患者表单数据", response_model=NoneResponse)
@wrap_api_response
def delete_patient_form_data(request: DeleteModelRequest, ctx: AdministratorContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(ctx.db, CohortPatientFromData, ids=[request.id], commit=True)
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/createPatientCTherapyDetail", description="创建队列患者C治疗信息表", response_model=Response[int])
@wrap_api_response
def create_patient_c_therapy_detail(
    request: CreatePatientCTherapyDetailRequest, ctx: ResearcherContext = Depends()
) -> int:
    check_cohort_patient_exists(ctx.db, request.patient_id)
    patient_c_therapy_detail_dict = request.dict()
    patient_therapy_detail_id = common_crud.insert_row(
        ctx.db, CohortPatientCTherapyDetail, patient_c_therapy_detail_dict, commit=False
    )
    if patient_therapy_detail_id is None:
        raise ServiceError.database_fail()
    ctx.db.commit()
    return patient_therapy_detail_id


@router.post(
    "/api/getPatientCTherapyDetailByPage",
    description="获取患者C治疗信息列表",
    response_model=Response[Page[PatientCTherapyDetailInfo]],
)
@wrap_api_response
def get_patient_c_therapy_detail_by_page(
    search: CohortPatientIdSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[PatientCTherapyDetailInfo]:
    total, orm_patient_c_therapy_detail = crud.search_patient_therapy_detail(ctx.db, search)
    patient_c_therapy_detail_infos = convert.map_list(
        convert.patient_c_therapy_detail_2_info, orm_patient_c_therapy_detail
    )
    return Page(total=total, items=patient_c_therapy_detail_infos)


@router.post(
    "/api/getPatientCTherapyDetailInfo", description="获取患者C治疗信息", response_model=Response[PatientCTherapyDetailInfo]
)
@wrap_api_response
def get_patient_c_therapy_detail_info(
    patient_c_therapy_detail_id: int, ctx: HumanSubjectContext = Depends()
) -> PatientCTherapyDetailInfo:
    orm_patient_c_therapy_detail = common_crud.get_row_by_id(
        ctx.db, CohortPatientCTherapyDetail, patient_c_therapy_detail_id
    )
    if orm_patient_c_therapy_detail is None:
        raise ServiceError.not_found(Entity.patient_c_therapy_detail)
    patient_c_therapy_detail_info = convert.patient_c_therapy_detail_2_info(orm_patient_c_therapy_detail)
    return patient_c_therapy_detail_info


@router.post("/api/updatePatientCTherapyDetail", description="更新患者C治疗信息", response_model=NoneResponse)
@wrap_api_response
def update_patient_c_therapy_detail(
    patient_id: int, request: list[PatientCTherapyDetail], ctx: ResearcherContext = Depends()
) -> None:
    check_cohort_patient_exists(ctx.db, patient_id)
    success = crud.update_patient_c_therapy_detail(patient_id, request, ctx.db)
    if not success:
        raise ServiceError.database_fail()
    ctx.db.commit()


@router.delete("/api/deletePatientCTherapyDetail", description="删除患者患者C治疗信息", response_model=NoneResponse)
@wrap_api_response
def delete_patient_c_therapy_detail(request: DeleteModelRequest, ctx: AdministratorContext = Depends()) -> None:
    success = common_crud.bulk_update_rows_as_deleted(
        ctx.db, CohortPatientCTherapyDetail, ids=[request.id], commit=True
    )
    if not success:
        raise ServiceError.database_fail()


@router.post("/api/createPatientMemo", description="创建患者备注信息", response_model=Response[int])
@wrap_api_response
def create_patient_memo(request: CreatePatientMemoRequest, ctx: ResearcherContext = Depends()) -> int:
    check_cohort_patient_exists(ctx.db, request.patient_id)
    patient_memo_dict = request.dict()
    patient_memo_id = common_crud.insert_row(ctx.db, CohortPatientMemo, patient_memo_dict, commit=False)
    if patient_memo_id is None:
        raise ServiceError.database_fail()
    ctx.db.commit()
    return patient_memo_id


@router.post("/api/getPatientMemoByPage", description="获取患者备注列表", response_model=Response[Page[PatientMemoInfo]])
@wrap_api_response
def get_patient_memo_by_page(
    search: CohortPatientIdSearch = Depends(), ctx: HumanSubjectContext = Depends()
) -> Page[PatientMemoInfo]:
    total, orm_patient_memo = crud.search_patient_memo(ctx.db, search)
    patient_memo_infos = convert.map_list(convert.patient_memo_orm_2_info, orm_patient_memo)
    return Page(total=total, items=patient_memo_infos)


@router.post("/api/updatePatientMemo", description="更新患者表单备注", response_model=NoneResponse)
@wrap_api_response
def update_patient_memo(request: list[str], patient_id: int, ctx: ResearcherContext = Depends()) -> None:
    check_cohort_patient_exists(ctx.db, patient_id)
    success = crud.update_patient_memo(patient_id, set(request), ctx.db)
    if not success:
        raise ServiceError.database_fail()
    ctx.db.commit()


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


@router.get("/api/downloadCohortPatientFile", description="下载病人文件")
def download_cohort_patient_file(
    cohort_patient_id: Annotated[int, Query(description="数据集ID")],
    path: Annotated[str, Query(description="文件路径")],
    ctx: ResearcherContext = Depends(),
) -> StreamingResponse:
    check_cohort_patient_exists(ctx.db, cohort_patient_id)
    file_path = dataset_file_path(cohort_patient_id, path)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post("/download-file", params={"path": str(file_path)})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        return StreamingResponse(
            file_server_response.iter_bytes(1024),
            headers={
                "Content-Disposition": f'attachment; filename="{quote(file_path.name)}"',
                "Content-Type": guess_type(file_path.name)[0] or "text/plain",
            },
        )


@router.get("/api/listCohortPatientFiles", description="获取病人文件列表", response_model=Response[list[dict[str, int]]])
@wrap_api_response
def list_cohort_patient_files(
    cohort_patient_id: Annotated[int, Query(description="数据集ID")],
    directory: Annotated[str, Query(description="文件夹路径")],
    file_type: Annotated[str, Query(description="文件夹路径")] = None,
    ctx: HumanSubjectContext = Depends(),
) -> list[dict[str, int]]:
    check_cohort_patient_exists(ctx.db, cohort_patient_id)
    directory_path = dataset_file_path(cohort_patient_id, directory)
    with Client(config.FILE_SERVER_URL) as client:
        file_server_response = client.inner.post("/list-directory", params={"directory": str(directory_path)})
        if file_server_response.status_code != 200:
            raise ServiceError.remote_service_error(file_server_response.text)
        files = file_server_response.json()
        if file_type is None:
            return [{"counts": len(files)}, files]
        else:
            filtered_files = [f for f in files if f.get("name").endswith(f".{file_type}")]
            return [{"counts": len(filtered_files)}, filtered_files]


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
