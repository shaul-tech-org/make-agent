from app.core.exceptions import ValidationException


class EmptyRequestException(ValidationException):
    def __init__(self):
        super().__init__(message="Request text must not be empty")
