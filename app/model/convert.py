from typing import Any, Callable, Iterable, TypeVar

from app.db import OrmModel
from app.db.orm import Device, Experiment, HumanSubject, Paradigm
from app.model.schema import (
    DeviceResponse,
    ExperimentInDB,
    ExperimentResponse,
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


def paradigm_orm_2_response(paradigm: Paradigm) -> ParadigmResponse:
    return ParadigmResponse(
        creator=UserInfo.from_orm(paradigm.creator_obj),
        images=map_list(lambda orm_file: orm_file.id, paradigm.files),
        **ParadigmInDB.from_orm(paradigm).dict(exclude={"creator"}),
    )


def device_orm_2_response(device: Device) -> DeviceResponse:
    return DeviceResponse.from_orm(device)


def human_subject_orm_2_response(human_subject: HumanSubject) -> HumanSubjectResponse:
    return HumanSubjectResponse(
        username=human_subject.user.username,
        staff_id=human_subject.user.staff_id,
        **orm_2_dict(human_subject),
    )
