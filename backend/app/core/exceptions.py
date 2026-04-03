class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str | int):
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            detail=f"{resource} with id '{resource_id}' not found",
        )
        self.resource = resource
        self.resource_id = resource_id


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)
