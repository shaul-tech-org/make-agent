from fastapi import APIRouter

from app.modules.coordinator.schemas.requests import RouteRequest
from app.modules.coordinator.schemas.responses import RouteResponse
from app.modules.coordinator.service import coordinator_service

router = APIRouter(prefix="/api/v1/coordinator", tags=["coordinator"])


@router.post("/route", response_model=RouteResponse)
async def route_request(data: RouteRequest):
    return coordinator_service.route(data)
