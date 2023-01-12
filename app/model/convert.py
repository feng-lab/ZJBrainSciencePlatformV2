from typing import Callable, TypeVar

from app.db.orm import Experiment
from app.model.schema import ExperimentInDB, ExperimentResponse, UserInfo

A = TypeVar("A")
B = TypeVar("B")


def list_(function: Callable[[A], B], items: list[A] | None) -> list[B]:
    if items is None:
        return []
    return [function(item) for item in items]


def experiment_orm_2_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        main_operator=UserInfo.from_orm(experiment.main_operator_obj),
        assistants=list_(UserInfo.from_orm, experiment.assistants),
        **ExperimentInDB.from_orm(experiment).dict(exclude={"main_operator"}),
    )
