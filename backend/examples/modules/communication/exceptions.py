from app.core.exceptions import ValidationException


class InvalidCommentTypeException(ValidationException):
    def __init__(self, comment_type: str, allowed: set[str]):
        super().__init__(
            message=f"Invalid comment type: '{comment_type}'. Allowed: {allowed}",
        )


class BlockerRequiresEscalateException(ValidationException):
    def __init__(self):
        super().__init__(message="blocker comment requires 'escalate_to' field")
