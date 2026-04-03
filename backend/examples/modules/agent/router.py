from fastapi import APIRouter

from app.modules.agent.exceptions import AgentAlreadyExistsException, AgentNotFoundException
from app.modules.agent.schemas.requests import AgentProposeRequest, AgentRejectRequest
from app.modules.agent.schemas.responses import AgentResponse
from app.modules.agent.service import agent_service

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents():
    return agent_service.list_all()


@router.post("/propose", status_code=201, response_model=AgentResponse)
async def propose_agent(data: AgentProposeRequest):
    result = agent_service.propose(data)
    if result is None:
        raise AgentAlreadyExistsException(data.name)
    return result


@router.post("/{agent_id}/approve", response_model=AgentResponse)
async def approve_agent(agent_id: int):
    result = agent_service.approve(agent_id)
    if result is None:
        raise AgentNotFoundException(agent_id)
    return result


@router.post("/{agent_id}/reject", response_model=AgentResponse)
async def reject_agent(agent_id: int, data: AgentRejectRequest):
    result = agent_service.reject(agent_id, data)
    if result is None:
        raise AgentNotFoundException(agent_id)
    return result
