from pydantic import BaseModel, Field


class Paradigm(BaseModel):
    pass


class Human(BaseModel):
    pass


class Device(BaseModel):
    pass


class EEGData(BaseModel):
    pass


class File(BaseModel):
    pass


class Task(BaseModel):
    class Steps(BaseModel):
        pass

    steps_list: list[Steps] = Field(default_factory=list)


class SearchFile(BaseModel):
    pass


class SearchResult(BaseModel):
    pass
