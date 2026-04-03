from pydantic import BaseModel


class TodoCreateRequest(BaseModel):
    title: str
    description: str | None = None


class TodoUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
