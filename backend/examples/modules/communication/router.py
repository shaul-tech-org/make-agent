from fastapi import APIRouter

from app.modules.communication.schemas.requests import CommentCreateRequest, HandoffCreateRequest
from app.modules.communication.schemas.responses import CommentResponse, HandoffResponse
from app.modules.communication.service import communication_service

router = APIRouter(prefix="/api/v1/communication", tags=["communication"])


@router.post("/comments", status_code=201, response_model=CommentResponse)
async def create_comment(data: CommentCreateRequest):
    return communication_service.create_comment(data)


@router.get("/comments", response_model=list[CommentResponse])
async def list_comments(task_id: str | None = None):
    return communication_service.list_comments(task_id)


@router.post("/handoff", status_code=201, response_model=HandoffResponse)
async def create_handoff(data: HandoffCreateRequest):
    return communication_service.create_handoff(data)


@router.get("/handoffs", response_model=list[HandoffResponse])
async def list_handoffs(to_agent: str | None = None, task_id: str | None = None):
    return communication_service.list_handoffs(to_agent, task_id)
