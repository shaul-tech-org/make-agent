from pydantic import BaseModel


class MemoryResponse(BaseModel):
    agent: str
    key: str
    value: str
    task_id: str | None = None
    tier: str = "hot"
    archived: bool = False
    updated_at: str


class MemoryStatsResponse(BaseModel):
    agent: str
    hot_count: int
    hot_chars: int
    warm_count: int
    cold_count: int
    budget_remaining_pct: float
