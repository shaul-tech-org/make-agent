from pydantic import BaseModel


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
