from pydantic import BaseModel


class MemorySaveRequest(BaseModel):
    agent: str
    key: str
    value: str
    task_id: str | None = None
    tier: str = "hot"  # hot, warm, cold
