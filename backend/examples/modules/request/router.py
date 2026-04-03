from fastapi import APIRouter

from app.modules.request.schemas.requests import UnifiedRequest
from app.modules.request.schemas.responses import UnifiedResponse
from app.modules.request.service import request_service

router = APIRouter(tags=["request"])


@router.post("/api/v1/request", response_model=UnifiedResponse)
async def handle_request(data: UnifiedRequest):
    return request_service.process(data)
