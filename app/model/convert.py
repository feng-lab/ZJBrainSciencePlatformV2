import json
from typing import Any, Callable, Iterable, Sequence, TypeVar

from app.common.config import config
from app.db import OrmModel
from app.db.crud.device import SearchDeviceRow
from app.db.orm import (
    Atlas,
    AtlasBehavioralDomain,
    AtlasParadigmClass,
    AtlasRegion,
    AtlasRegionLink,
    Dataset,
    Device,
    Experiment,
    HumanSubject,
    Notification,
    Paradigm,
    Task,
    TaskStep,
    User,
    VirtualFile,
)
from app.model.field import LongVarchar
from app.model.schema import (
    AtlasBehavioralDomainTreeInfo,
    AtlasBehavioralDomainTreeNode,
    AtlasInfo,
    AtlasParadigmClassTreeInfo,
    AtlasParadigmClassTreeNode,
    AtlasRegionInfo,
    AtlasRegionLinkInfo,
    AtlasRegionTreeInfo,
    AtlasRegionTreeNode,
    DatasetInfo,
    DeviceInfo,
    DeviceInfoWithIndex,
    ExperimentResponse,
    ExperimentSimpleResponse,
    FileResponse,
    HumanSubjectResponse,
    NotificationResponse,
    ParadigmInDB,
    ParadigmResponse,
    TaskBaseInfo,
    TaskInfo,
    TaskSourceFileResponse,
    TaskStepInfo,
    UserInfo,
    UserResponse,
)

A = TypeVar("A")
B = TypeVar("B")


def map_list(function: Callable[[A], B], items: Iterable[A] | None) -> list[B]:
    if items is None:
        return []
    return [function(item) for item in items]


# noinspection PyTypeChecker
def orm_2_dict(orm: OrmModel, *, include: set[str] | None = None, exclude: set[str] | None = None) -> dict[str, Any]:
    return {
        column.name: getattr(orm, column.name)
        for column in orm.__table__.columns
        if ((not include) or (column.name in include)) and ((not exclude) or (column.name not in exclude))
    }


def experiment_orm_2_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        main_operator=user_orm_2_info(experiment.main_operator_obj),
        assistants=map_list(user_orm_2_info, experiment.assistants),
        tags=map_list(lambda tag: tag.tag, experiment.tags),
        **orm_2_dict(experiment, exclude={"main_operator"}),
    )


def experiment_orm_2_simple_response(experiment: Experiment) -> ExperimentSimpleResponse:
    return ExperimentSimpleResponse(tags=map_list(lambda tag: tag.tag, experiment.tags), **orm_2_dict(experiment))


def paradigm_orm_2_response(paradigm: Paradigm) -> ParadigmResponse:
    return ParadigmResponse(
        creator=UserInfo.from_orm(paradigm.creator_obj),
        images=map_list(lambda orm_file: orm_file.id, paradigm.exist_virtual_files),
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
        username=human_subject.user.username, staff_id=human_subject.user.staff_id, **orm_2_dict(human_subject)
    )


def virtual_file_orm_2_response(virtual_file: VirtualFile) -> FileResponse:
    response = FileResponse.from_orm(virtual_file)
    if virtual_file.file_type in config.IMAGE_FILE_EXTENSIONS:
        response.url = f"/api/downloadFile/{virtual_file.id}"
    return response


def file_experiment_orm_2_task_source_response(
    file_experiment: tuple[VirtualFile, Experiment]
) -> TaskSourceFileResponse:
    file, experiment = file_experiment
    return TaskSourceFileResponse(
        id=file.id,
        name=file.name,
        file_type=file.file_type,
        experiment_id=file.experiment_id,
        experiment_name=experiment.name,
    )


def user_orm_2_info(user: User) -> UserInfo:
    return UserInfo(id=user.id, username=user.username, staff_id=user.staff_id)


def user_orm_2_response(user: User) -> UserResponse:
    return UserResponse(
        **orm_2_dict(
            user,
            include={
                "id",
                "gmt_create",
                "gmt_modified",
                "is_deleted",
                "last_login_time",
                "last_logout_time",
                "username",
                "staff_id",
                "access_level",
            },
        )
    )


def notification_orm_2_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        **orm_2_dict(notification, exclude={"creator_user"}), creator_name=notification.creator_user.username
    )


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


def atlas_orm_2_info(atlas: Atlas) -> AtlasInfo:
    return AtlasInfo(
        id=atlas.id,
        is_deleted=atlas.is_deleted,
        gmt_create=atlas.gmt_create,
        gmt_modified=atlas.gmt_modified,
        name=atlas.name,
        url=atlas.url,
        title=atlas.title,
        whole_segment_id=atlas.whole_segment_id,
    )


def atlas_region_orm_2_info(atlas_region: AtlasRegion) -> AtlasRegionInfo:
    return AtlasRegionInfo(
        id=atlas_region.id,
        is_deleted=atlas_region.is_deleted,
        gmt_create=atlas_region.gmt_create,
        gmt_modified=atlas_region.gmt_modified,
        region_id=atlas_region.region_id,
        atlas_id=atlas_region.atlas_id,
        parent_id=atlas_region.parent_id,
        description=atlas_region.description,
        acronym=atlas_region.acronym,
        label=atlas_region.label,
        lobe=atlas_region.lobe,
        gyrus=atlas_region.gyrus,
    )


def atlas_region_orm_2_tree_node(atlas_region: AtlasRegion) -> AtlasRegionTreeNode:
    return AtlasRegionTreeNode(
        id=atlas_region.id,
        parent_id=atlas_region.parent_id,
        region_id=atlas_region.region_id,
        label=atlas_region.label,
        children=[],
    )


def atlas_region_tree_node_2_info(atlas_region: AtlasRegionTreeNode) -> AtlasRegionTreeInfo:
    return AtlasRegionTreeInfo(
        region_id=atlas_region.region_id,
        label=atlas_region.label,
        children=map_list(atlas_region_tree_node_2_info, atlas_region.children),
    )


def atlas_region_link_orm_2_info(link: AtlasRegionLink) -> AtlasRegionLinkInfo:
    return AtlasRegionLinkInfo(
        id=link.id,
        is_deleted=link.is_deleted,
        gmt_create=link.gmt_create,
        gmt_modified=link.gmt_modified,
        atlas_id=link.atlas_id,
        link_id=link.link_id,
        region1=link.region1,
        region2=link.region2,
        value=link.value,
        opposite_value=link.opposite_value,
    )


def atlas_behavioral_domain_orm_2_tree_node(domain: AtlasBehavioralDomain) -> AtlasBehavioralDomainTreeNode:
    return AtlasBehavioralDomainTreeNode(
        id=domain.id,
        parent_id=domain.parent_id,
        name=domain.name,
        value=domain.value,
        label=domain.label,
        description=domain.description,
        children=[],
    )


def atlas_behavioral_domain_tree_node_2_info(domain: AtlasBehavioralDomainTreeNode) -> AtlasBehavioralDomainTreeInfo:
    return AtlasBehavioralDomainTreeInfo(
        name=domain.name,
        value=domain.value,
        label=domain.label,
        description=domain.description,
        children=map_list(atlas_behavioral_domain_tree_node_2_info, domain.children),
    )


def atlas_region_associated_model_2_dict(models: Sequence) -> dict[LongVarchar, float]:
    return {model.key: model.value for model in models}


def atlas_paradigm_class_orm_2_tree_node(paradigm_class: AtlasParadigmClass) -> AtlasParadigmClassTreeNode:
    return AtlasParadigmClassTreeNode(
        parent_id=paradigm_class.parent_id,
        id=paradigm_class.id,
        name=paradigm_class.name,
        value=paradigm_class.value,
        label=paradigm_class.label,
        description=paradigm_class.description,
        children=[],
    )


def atlas_paradigm_class_tree_node_2_info(paradigm_class: AtlasParadigmClassTreeNode) -> AtlasParadigmClassTreeInfo:
    return AtlasParadigmClassTreeInfo(
        name=paradigm_class.name,
        value=paradigm_class.value,
        label=paradigm_class.label,
        description=paradigm_class.description,
        children=map_list(atlas_paradigm_class_tree_node_2_info, paradigm_class.children),
    )


def dataset_orm_2_info(dataset: Dataset) -> DatasetInfo:
    return DatasetInfo.from_orm(dataset)
