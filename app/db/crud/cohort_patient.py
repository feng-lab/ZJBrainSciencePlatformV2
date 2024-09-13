from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_pages
from app.db.orm import CohortPatient
from app.model.schema import CohortPatientSearch


def search_cohort_patient(db: Session, search: CohortPatientSearch) -> tuple[int, Sequence[CohortPatient]]:
    base_stmt = select(CohortPatient).select_from(CohortPatient)
    if search.patient_name is not None:
        base_stmt = base_stmt.where(
            CohortPatient.patient_name.icontains(search.patient_name), CohortPatient.domain_id == search.domain_id
        )
    if search.hospital is not None:
        base_stmt = base_stmt.where(
            CohortPatient.hospital.icontains(search.hospital), CohortPatient.domain_id == search.domain_id
        )
    if search.gender is not None:
        base_stmt = base_stmt.where(CohortPatient.gender == search.gender, CohortPatient.domain_id == search.domain_id)
    if search.family_address is not None:
        base_stmt = base_stmt.where(
            CohortPatient.family_address == search.family_address, CohortPatient.domain_id == search.domain_id
        )
    if search.family_address_city is not None:
        base_stmt = base_stmt.where(
            CohortPatient.family_address_city == search.family_address_city, CohortPatient.domain_id == search.domain_id
        )
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
