from enum import StrEnum


class TaskStepType(StrEnum):
    preprocess = "preprocess"
    analysis = "analysis"


class TaskStatus(StrEnum):
    wait_start = "wait_start"
    running = "running"
    done = "done"
    error = "error"
    cancelled = "cancelled"


class TaskType(StrEnum):
    preprocess = "preprocess"
    analysis = "analysis"
    preprocess_analysis = "preprocess_analysis"


class Gender(StrEnum):
    male = "male"
    female = "female"


class MaritalStatus(StrEnum):
    unmarried = "unmarried"
    married = "married"


class ABOBloodType(StrEnum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"


class NotificationStatus(StrEnum):
    unread = "unread"
    read = "read"


class NotificationType(StrEnum):
    task_step_status = "task_step_status"


class ExperimentType(StrEnum):
    other = "other"
    SSVEP = "SSVEP"
    MI = "MI"
    neuron = "neuron"


class GetExperimentsByPageSortBy(StrEnum):
    START_TIME = "start_time"
    TYPE = "type"


class GetExperimentsByPageSortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"
