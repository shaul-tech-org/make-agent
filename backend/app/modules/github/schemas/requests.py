from pydantic import BaseModel, Field


class GitHubLoadRequest(BaseModel):
    url: str = Field(max_length=500)
    token: str | None = None
