from fastapi import APIRouter

from app.modules.delegation.schemas.requests import DelegationRequest
from app.modules.delegation.schemas.responses import DelegationPlanResponse
from app.modules.delegation.service import delegation_service

router = APIRouter(prefix="/api/v1/delegation", tags=["delegation"])


@router.post("/plan", response_model=DelegationPlanResponse)
async def create_delegation_plan(data: DelegationRequest):
    return delegation_service.create_plan(data)
