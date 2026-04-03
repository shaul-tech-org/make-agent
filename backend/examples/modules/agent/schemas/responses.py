from pydantic import BaseModel


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    model: str
    skills: list[str]
    status: str  # active, pending, rejected
    reject_reason: str | None = None
