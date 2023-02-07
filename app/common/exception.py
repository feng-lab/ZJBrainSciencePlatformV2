from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.model.response import CODE_DATABASE_FAIL, CODE_FAIL, CODE_NOT_FOUND


class ServiceError(Exception):
    def __init__(self, status_code: int, code: int, message: str):
        self.status_code: int = status_code
        self.code: int = code
        self.message: str = message

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
