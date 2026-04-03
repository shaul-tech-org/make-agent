from pydantic import BaseModel


class CommentCreateRequest(BaseModel):
    agent: str
    task_id: str
    type: str  # progress, blocker, completed, handoff
    content: str
    escalate_to: str | None = None


class HandoffCreateRequest(BaseModel):
    from_agent: str
    to_agent: str
    task_id: str
    context: str
    artifacts: list[str]
