from typing import Callable, Iterable, TypeVar

from app.db.orm import Device, Experiment, Paradigm
from app.model.schema import (
    DeviceResponse,
    ExperimentInDB,
    ExperimentResponse,
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
