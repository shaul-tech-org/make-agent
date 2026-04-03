from app.core.exceptions import AppException, NotFoundException, ValidationException


class InvalidGitHubUrlException(ValidationException):
    def __init__(self, url: str):
        super().__init__(message=f"Invalid GitHub URL: '{url}'. Expected: https://github.com/owner/repo")


class NoProjectLoadedException(NotFoundException):
    def __init__(self):
        super().__init__(resource="Project", resource_id="none")
        self.message = "No project loaded"
        self.detail = "Load a GitHub project first via POST /api/v1/github/load"


class GitHubApiException(AppException):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message=message, status_code=status_code)
