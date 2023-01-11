from typing import Callable, TypeVar

from app.db.orm import Experiment, User
from app.model.schema import ExperimentInDB, ExperimentResponse, UserInfo

A = TypeVar("A")
B = TypeVar("B")


def list_convert(function: Callable[[A], B], items: list[A] | None) -> list[B]:
    if items is None:
        return []
    return [function(item) for item in items]


def experiment_orm_2_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        main_operator=user_orm_2_info(experiment.main_operator_obj),
        assistants=list_convert(user_orm_2_info, experiment.assistants),
        **ExperimentInDB.from_orm(experiment).dict(exclude={"main_operator"}),
    )


def user_orm_2_info(user: User) -> UserInfo:
    return UserInfo.from_orm(user)
