from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

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
