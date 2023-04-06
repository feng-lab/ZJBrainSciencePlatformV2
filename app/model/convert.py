import json
from typing import Any, Callable, Iterable, TypeVar

from app.common.config import config
from app.db import OrmModel
from app.db.crud.device import SearchDeviceRow
from app.db.orm import Device, Experiment, File, HumanSubject, Paradigm, Task, TaskStep, User
from app.model.schema import (
    DeviceInfo,
    DeviceInfoWithIndex,
    ExperimentResponse,
    ExperimentSimpleResponse,
    FileResponse,
    HumanSubjectResponse,
    ParadigmInDB,
    ParadigmResponse,
    TaskBaseInfo,
    TaskInfo,
    TaskSourceFileResponse,
    TaskStepInfo,
    UserInfo,
)

A = TypeVar("A")
B = TypeVar("B")


def map_list(function: Callable[[A], B], items: Iterable[A] | None) -> list[B]:
    if items is None:
        return []
    return [function(item) for item in items]


# noinspection PyTypeChecker
def orm_2_dict(orm: OrmModel, exclude: set[str] | None = None) -> dict[str, Any]:
    return {
        column.name: getattr(orm, column.name)
        for column in orm.__table__.columns
        if exclude is None or column.name not in exclude
    }


def experiment_orm_2_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        main_operator=user_orm_2_info(experiment.main_operator_obj),
        assistants=map_list(user_orm_2_info, experiment.assistants),
        tags=map_list(lambda tag: tag.tag, experiment.tags),
        **orm_2_dict(experiment, exclude={"main_operator"}),
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


def file_orm_2_response(file: File) -> FileResponse:
    response = FileResponse.from_orm(file)
    if file.extension in config.IMAGE_FILE_EXTENSIONS:
        response.url = f"/api/downloadFile/{file.id}"
    return response


def file_experiment_orm_2_task_source_response(
    file_experiment: tuple[File, Experiment]
) -> TaskSourceFileResponse:
    file, experiment = file_experiment
    return TaskSourceFileResponse(
        id=file.id,
        name=file.name,
        extension=file.extension,
        experiment_id=file.experiment_id,
        experiment_name=experiment.name,
    )


def user_orm_2_info(user: User) -> UserInfo:
    return UserInfo(id=user.id, username=user.username, staff_id=user.staff_id)


def task_step_orm_2_info(task_step: TaskStep) -> TaskStepInfo:
    return TaskStepInfo(
        task_id=task_step.task_id,
        name=task_step.name,
        step_type=task_step.type,
        parameters=json.loads(task_step.parameter),
        index=task_step.index,
        status=task_step.status,
        start_at=task_step.start_at,
        end_at=task_step.end_at,
    )


def task_orm_2_info(task: Task) -> TaskInfo:
    steps = map_list(task_step_orm_2_info, task.steps)
    steps.sort(key=lambda step_info: step_info.index)
    return TaskInfo(
        name=task.name,
        description=task.description,
        source_file=task.source_file,
        type=task.type,
        status=task.status,
        start_at=task.start_at,
        end_at=task.end_at,
        creator=user_orm_2_info(task.creator_obj),
        steps=steps,
    )


def task_orm_2_base_info(task: Task) -> TaskBaseInfo:
    return TaskBaseInfo(
        name=task.name,
        description=task.description,
        source_file=task.source_file,
        type=task.type,
        status=task.status,
        start_at=task.start_at,
        end_at=task.end_at,
        creator=user_orm_2_info(task.creator_obj),
    )
