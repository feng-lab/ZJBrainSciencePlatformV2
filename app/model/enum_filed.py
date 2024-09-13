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


class PatientDiagnose(StrEnum):
    de_no_AML = "de_no_AML"
    sAML = "sAML"
    Ph_ALL = "Ph+ALL（PH+融合基因）"
    Ph_B_ALL = "Ph-B-ALL（PH-融合基因）"
    T_ALL = "T-ALL"
    ETP_ALL = "ETP-ALL"
    Ph_MPAL = "Ph+MPAL"
    MLL_MPAL = "MLL+MPAL"
    B_Myeloid_MPAL = "B-Myeloid_MPAL"
    T_Myeloid_MPAL = "T-Myeloid_MPAL"
    BPDCN = "BPDCN"


class GeneFusion(StrEnum):
    no_test = "未测"
    partial_test = "部分检测"
    other = "融合基因套餐"


class GeneMutation(StrEnum):
    no_test = "未测"
    partial_test = "部分检测"
    other = "NGS"


class CEffects(StrEnum):
    CR_CRi = "CR/CRi"
    PR = "PR"
    NR = "NR"
