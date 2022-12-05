import importlib
import inspect
from types import ModuleType
from typing import TypeVar, Callable, Any, Type

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
T = TypeVar("T")


def modify_model_field_by_type(model: Model, field_type: Type[T], map_func: Callable[[T], T]):
    if model is None:
        return None

    old_dict = model.dict()
    new_dict = {
        field_name: map_func(field_value) if isinstance(field_value, field_type) else field_value
        for field_name, field_value in old_dict.items()
    }
    return model.construct(**new_dict)


def get_module_defined_members(
    module: str | ModuleType, filter_func: Callable[[str, Any], bool] | None = None
) -> list[(str, Any)]:
    if isinstance(module, str):
        module = importlib.import_module(module)
    return [
        member
        for member in inspect.getmembers(module)
        if inspect.getmodule(member[1]) == module and (filter_func is None or filter_func(member[0], member[1]))
    ]


TargetModel = TypeVar("TargetModel", bound=BaseModel)


def convert_models(models: list[Model], target_type: type[TargetModel]) -> list[TargetModel]:
    return [target_type(**model.dict()) for model in models]
