from typing import Callable, Type, TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)
T = TypeVar("T")


def modify_model_field_by_type(model: Model, field_type: Type[T], map_func: Callable[[T], T]):
    if model is None:
        return None
    field_schemas: dict[str, dict[str, str]] = model.schema(by_alias=False)["properties"]
    for field_name in field_schemas.keys():
        field_value = getattr(model, field_name)
        if isinstance(field_value, field_type):
            setattr(model, field_name, map_func(field_value))
        if isinstance(field_value, BaseModel):
            modify_model_field_by_type(field_value, field_type, map_func)
    return model
