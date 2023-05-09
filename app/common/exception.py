from typing import Any, Sequence

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.common.localization import Entity, translate_entity
from app.model.response import ResponseCode


class ServiceError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: int,
        message_id: str,
        format_args: Sequence[Any] | None = None,
    ):
        self.status_code: int = status_code
        self.code: int = code
        self.message_id: str = message_id
        self.format_args: Sequence[Any] = [] if format_args is None else format_args

    @staticmethod
    def not_found(entity: Entity):
        entity_value = translate_entity(entity)
        return ServiceError(
            status_code=HTTP_200_OK,
            code=ResponseCode.PARAMS_ERROR,
            message_id="not found",
            format_args=(entity_value,),
        )

    @staticmethod
    def page_not_found(url: str) -> "ServiceError":
        return ServiceError(
            status_code=HTTP_404_NOT_FOUND,
            code=ResponseCode.PARAMS_ERROR,
            message_id="page not found",
            format_args=(url,),
        )

    @staticmethod
    def not_supported_file_type(file_type: str) -> "ServiceError":
        return ServiceError(
            status_code=HTTP_400_BAD_REQUEST,
            code=ResponseCode.PARAMS_ERROR,
            message_id="file type not supported",
            format_args=(file_type,),
        )

    @staticmethod
    def params_error(message: str) -> "ServiceError":
        return ServiceError(
            status_code=HTTP_400_BAD_REQUEST,
            code=ResponseCode.PARAMS_ERROR,
            message_id="params error",
            format_args=(message,),
        )

    @staticmethod
    def not_login() -> "ServiceError":
        return ServiceError(
            status_code=HTTP_401_UNAUTHORIZED,
            code=ResponseCode.UNAUTHORIZED,
            message_id="not login",
        )

    @staticmethod
    def wrong_password() -> "ServiceError":
        return ServiceError(
            status_code=HTTP_401_UNAUTHORIZED,
            code=ResponseCode.UNAUTHORIZED,
            message_id="wrong password",
        )

    @staticmethod
    def no_enough_access_level() -> "ServiceError":
        return ServiceError(
            status_code=HTTP_401_UNAUTHORIZED,
            code=ResponseCode.UNAUTHORIZED,
            message_id="no enough access level",
        )

    @staticmethod
    def session_timeout() -> "ServiceError":
        return ServiceError(
            status_code=HTTP_401_UNAUTHORIZED,
            code=ResponseCode.UNAUTHORIZED,
            message_id="session timeout",
        )

    @staticmethod
    def remote_service_error(message: str) -> "ServiceError":
        return ServiceError(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=ResponseCode.SERVER_ERROR,
            message_id="remote service error",
            format_args=(message,),
        )

    @staticmethod
    def database_fail():
        return ServiceError(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=ResponseCode.SERVER_ERROR,
            message_id="database fail",
        )
