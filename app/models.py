from pydantic import BaseModel

from .database import Base


class Experiment(BaseModel):
    pass


class Paradigm(BaseModel):
    pass


class Human(BaseModel):
    pass


class Device(BaseModel):
    pass


class EEGData(BaseModel):
    pass
