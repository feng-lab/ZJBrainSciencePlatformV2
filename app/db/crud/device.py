from typing import Sequence

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session

from app.db.orm import Device, Experiment, ExperimentDevice
from app.model.schema import DeviceSearch


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


SearchDeviceRow = Row[tuple[int, str, str, str] | tuple[int, str, str, str, int]]


def search_devices(db: Session, search: DeviceSearch) -> tuple[int, Sequence[SearchDeviceRow]]:
    base_stmt = select(Device.id, Device.brand, Device.name, Device.purpose).select_from(Device)
    if search.experiment_id is not None:
        base_stmt = (
            base_stmt.add_columns(ExperimentDevice.index)
            .join(ExperimentDevice, Device.id == ExperimentDevice.device_id)
            .join(Experiment, ExperimentDevice.experiment_id == Experiment.id)
            .where(Experiment.id == search.experiment_id, Experiment.is_deleted == False)
        )
    if search.brand:
        base_stmt = base_stmt.where(Device.brand.icontains(search.brand))
    if search.name:
        base_stmt = base_stmt.where(Device.name.icontains(search.name))
    if not search.include_deleted:
        base_stmt = base_stmt.where(Device.is_deleted == False)

    rows = db.execute(base_stmt.offset(search.offset).limit(search.limit)).all()
    total = db.execute(base_stmt.with_only_columns(func.count())).scalar()
    return total, rows
