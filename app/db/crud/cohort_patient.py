from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import common_crud
from app.db.crud import query_pages
from app.db.orm import CohortPatient, CohortPatientCTherapyDetail, CohortPatientFromData, CohortPatientMemo
from app.model.schema import CohortPatientIdSearch, CohortPatientSearch


def search_cohort_patient(db: Session, search: CohortPatientSearch) -> tuple[int, Sequence[CohortPatient]]:
    base_stmt = select(CohortPatient).select_from(CohortPatient).where(CohortPatient.domain_id == search.domain_id)
    if search.patient_name is not None:
        base_stmt = base_stmt.where(CohortPatient.patient_name.icontains(search.patient_name))
    if search.hospital is not None:
        base_stmt = base_stmt.where(CohortPatient.hospital.icontains(search.hospital))
    if search.gender is not None:
        base_stmt = base_stmt.where(CohortPatient.gender == search.gender)
    if search.family_address is not None:
        base_stmt = base_stmt.where(CohortPatient.family_address == search.family_address)
    if search.family_address_city is not None:
        base_stmt = base_stmt.where(CohortPatient.family_address_city == search.family_address_city)
    if search.family_address_street is not None:
        base_stmt = base_stmt.where(
            CohortPatient.family_address_street == search.family_address_street,
            CohortPatient.domain_id == search.domain_id,
        )
    if search.birth_start is not None:
        base_stmt = base_stmt.where(CohortPatient.date_birth >= search.birth_start)
    if search.birth_end is not None:
        base_stmt = base_stmt.where(CohortPatient.date_birth <= search.birth_end)
    if not search.include_deleted:
        base_stmt = base_stmt.where(CohortPatient.is_deleted == False)
    return query_pages(db, base_stmt, search.offset, search.limit)


def search_patient_form_data(db: Session, search: CohortPatientIdSearch) -> tuple[int, Sequence[CohortPatientFromData]]:
    base_stmt = select(CohortPatientFromData).select_from(CohortPatientFromData)
    if search.patient_id is not None:
        base_stmt = base_stmt.where(CohortPatientFromData.patient_id == search.patient_id)
    return query_pages(db, base_stmt, search.offset, search.limit)


def search_patient_memo(db: Session, search: CohortPatientIdSearch) -> tuple[int, Sequence[CohortPatientMemo]]:
    base_stmt = select(CohortPatientMemo).select_from(CohortPatientMemo)
    if search.patient_id is not None:
        base_stmt = base_stmt.where(CohortPatientMemo.patient_id == search.patient_id)
    return query_pages(db, base_stmt, search.offset, search.limit)


def search_patient_therapy_detail(
    db: Session, search: CohortPatientIdSearch
) -> tuple[int, Sequence[CohortPatientCTherapyDetail]]:
    base_stmt = select(CohortPatientCTherapyDetail).select_from(CohortPatientCTherapyDetail)
    if search.patient_id is not None:
        base_stmt = base_stmt.where(CohortPatientCTherapyDetail.patient_id == search.patient_id)
    return query_pages(db, base_stmt, search.offset, search.limit)


def update_patient_memo(patient_id: int, new_memos: set[str], db: Session) -> bool:
    old_memos = set(
        db.execute(
            select(CohortPatientMemo.memo).where(
                CohortPatientMemo.patient_id == patient_id, CohortPatientMemo.is_deleted == False
            )
        )
        .scalars()
        .all()
    )
    delete_success = common_crud.bulk_delete_rows(
        db,
        CohortPatientMemo,
        [CohortPatientMemo.patient_id == patient_id, CohortPatientMemo.memo.in_(old_memos - new_memos)],
        commit=False,
    )
    insert_success = common_crud.bulk_insert_rows(
        db,
        CohortPatientMemo,
        [{"patient_id": patient_id, "memo": memo} for memo in new_memos - old_memos],
        commit=False,
    )

    return delete_success and insert_success


def update_patient_c_therapy_detail(patient_id: int, new_c_therapy_details: list, db: Session) -> bool:
    new_memos = set([a.dict()["c_index"] for a in new_c_therapy_details])
    print(new_memos)
    old_memos = set(
        db.execute(
            select(CohortPatientCTherapyDetail.c_index).where(
                CohortPatientCTherapyDetail.patient_id == patient_id, CohortPatientCTherapyDetail.is_deleted == False
            )
        )
        .scalars()
        .all()
    )
    print(old_memos)
    delete_success = common_crud.bulk_delete_rows(
        db,
        CohortPatientCTherapyDetail,
        [CohortPatientCTherapyDetail.patient_id == patient_id, CohortPatientCTherapyDetail.c_index.in_(old_memos)],
        commit=False,
    )
    temp_dict = [
        {"patient_id": patient_id, **a.dict()}
        for a in new_c_therapy_details
        if a.dict()["c_index"] not in (old_memos - new_memos)
    ]
    insert_success = common_crud.bulk_insert_rows(db, CohortPatientCTherapyDetail, temp_dict, commit=False)
    return delete_success and insert_success
