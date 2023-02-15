from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.crud import query_paged_data
from app.db.orm import Device, Experiment, ExperimentDevice
from app.model.schema import PageParm


def filter_experiment_devices_to_add(
    db: Session, experiment_id: int, device_ids: list[int]
) -> Sequence[int]:
    stmt = (select(Device.id).where(Device.id.in_(device_ids))).except_(
        select(Device.id)
        .join(Device.experiments)
        .where(
            Experiment.id == experiment_id,
            Experiment.is_deleted == False,
            Device.is_deleted == False,
        )
    )
    device_ids = db.execute(stmt).scalars().all()
    return device_ids


def get_last_index(db: Session, experiment_id: int) -> int | None:
    stmt = (
        select(ExperimentDevice.index)
        .join(Experiment, Experiment.id == ExperimentDevice.experiment_id)
        .join(Device, ExperimentDevice.device_id == Device.id)
        .where(
            Experiment.id == experiment_id,
            Experiment.is_deleted == False,
            Device.is_deleted == False,
        )
        .order_by(ExperimentDevice.index.desc())
        .limit(1)
    )
    last_index = db.execute(stmt).scalar()
    return last_index


def search_devices(
    db: Session, experiment_id: int, page_param: PageParm
) -> (int, Sequence[Device]):
    base_stmt = (
        select(Device)
        .join(Experiment, Experiment.id == Device.experiment_id)
        .where(Experiment.is_deleted == False, Device.experiment_id == experiment_id)
    )
    if not page_param.include_deleted:
        base_stmt = base_stmt.where(Device.is_deleted == False)

    return query_paged_data(db, base_stmt, page_param.offset, page_param.limit)
