from typing import Any, Callable, Iterable, TypeVar

from app.db import OrmModel
from app.db.crud.device import SearchDeviceRow
from app.db.orm import Device, Experiment, HumanSubject, Paradigm
from app.model.schema import (
    DeviceInfo,
    DeviceInfoWithIndex,
    ExperimentInDB,
    ExperimentResponse,
    ExperimentSimpleResponse,
    HumanSubjectResponse,
    ParadigmInDB,
    ParadigmResponse,
    UserInfo,
)

A = TypeVar("A")
B = TypeVar("B")


def map_list(function: Callable[[A], B], items: Iterable[A] | None) -> list[B]:
    if items is None:
        return []
    return [function(item) for item in items]


# noinspection PyTypeChecker
def orm_2_dict(orm: OrmModel) -> dict[str, Any]:
    return {column.name: getattr(orm, column.name) for column in orm.__table__.columns}


def experiment_orm_2_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        main_operator=UserInfo.from_orm(experiment.main_operator_obj),
        assistants=map_list(UserInfo.from_orm, experiment.assistants),
        **ExperimentInDB.from_orm(experiment).dict(exclude={"main_operator"}),
    )


def experiment_orm_2_simple_response(experiment: Experiment) -> ExperimentSimpleResponse:
    return ExperimentSimpleResponse.from_orm(experiment)


def paradigm_orm_2_response(paradigm: Paradigm) -> ParadigmResponse:
    return ParadigmResponse(
        creator=UserInfo.from_orm(paradigm.creator_obj),
        images=map_list(lambda orm_file: orm_file.id, paradigm.files),
        **ParadigmInDB.from_orm(paradigm).dict(exclude={"creator"}),
    )


def device_orm_2_info(device: Device) -> DeviceInfo:
    return DeviceInfo.from_orm(device)


def device_search_row_2_info_with_index(row: SearchDeviceRow) -> DeviceInfoWithIndex:
    device = DeviceInfoWithIndex(id=row.id, brand=row.brand, name=row.name, purpose=row.purpose)
    if len(row) > 4:
        device.index = row[4]
    return device


def human_subject_orm_2_response(human_subject: HumanSubject) -> HumanSubjectResponse:
    return HumanSubjectResponse(
        username=human_subject.user.username,
        staff_id=human_subject.user.staff_id,
        **orm_2_dict(human_subject),
    )
