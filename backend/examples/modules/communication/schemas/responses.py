from pydantic import BaseModel


class CommentResponse(BaseModel):
    id: int
    agent: str
    task_id: str
    type: str
    content: str
    escalate_to: str | None
    timestamp: str


class MemoryItem(BaseModel):
    key: str
    value: str


class HandoffResponse(BaseModel):
    id: int
    from_agent: str
    to_agent: str
    task_id: str
    context: str
    artifacts: list[str]
    memory_context: list[MemoryItem]
    timestamp: str
