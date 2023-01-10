from app.model.response import CODE_DATABASE_FAIL


class ServiceError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    @staticmethod
    def database_fail(message: str):
        return ServiceError(code=CODE_DATABASE_FAIL, message=message)
