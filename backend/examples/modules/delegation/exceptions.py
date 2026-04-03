from app.core.exceptions import ValidationException


class EmptyDelegationRequestException(ValidationException):
    def __init__(self):
        super().__init__(message="Delegation request text must not be empty")
