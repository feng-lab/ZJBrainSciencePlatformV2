from typing import Any, Sequence

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.model.response import (
    CODE_DATABASE_FAIL,
    CODE_FAIL,
    CODE_NOT_FOUND,
    CODE_REMOTE_SERVICE_ERROR,
    ResponseCode,
)


class ServiceError(Exception):
    def __init__(
        self, *, status_code: int, code: int, message_id: str, format_args: Sequence[Any] = None
    ):
        self.status_code: int = status_code
        self.code: int = code
        self.message_id: str = message_id
        self.format_args: Sequence[Any] = format_args

    @staticmethod
    def database_fail(message: str):
        return ServiceError(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, code=CODE_DATABASE_FAIL, message=message
        )

    @staticmethod
    def invalid_request(message: str):
        return ServiceError(status_code=HTTP_400_BAD_REQUEST, code=CODE_FAIL, message=message)

    @staticmethod
    def not_found(message: str):
        return ServiceError(status_code=HTTP_200_OK, code=CODE_NOT_FOUND, message=message)

    @staticmethod
    def remote_service_error(message: str):
        return ServiceError(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code=CODE_REMOTE_SERVICE_ERROR,
            message=message,
        )

    @staticmethod
    def page_not_found(url: str) -> "ServiceError":
        return ServiceError(
            status_code=HTTP_404_NOT_FOUND,
            code=CODE_NOT_FOUND,
            message_id="page not found",
            format_args=(url,),
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
