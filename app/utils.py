from datetime import timezone, datetime, timedelta
from typing import TypeVar

from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)

CST_TIMEZONE = timezone(timedelta(hours=8), "中国标准时间")


def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


# 将数据库中取出的无时区datetime对象转换为CST时区对象
def convert_timezone_to_cst(model: Model) -> Model:
    new_dict = {
        name: value.replace(tzinfo=timezone.utc).astimezone(CST_TIMEZONE)
        if isinstance(value, datetime) and value.tzinfo is None
        else value
        for name, value in model.dict().items()
    }
    return model.construct(**new_dict)


def list_convert_timezone_to_cst(models: list[Model]) -> list[Model]:
    return [convert_timezone_to_cst(model) for model in models]
