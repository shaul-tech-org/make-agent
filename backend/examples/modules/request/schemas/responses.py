from pydantic import BaseModel

from app.modules.delegation.schemas.responses import DelegationPlanResponse


class ContextInfo(BaseModel):
    agent: str
    hot_count: int
    hot_chars: int
    budget_remaining_pct: float


class UnifiedResponse(BaseModel):
    request: str
    category: str
    complexity: str
    agent: str
    delegation_plan: DelegationPlanResponse | None
    context_info: ContextInfo | None = None
