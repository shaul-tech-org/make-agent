from app.modules.agent.repository import agent_repository
from app.modules.agent.schemas.requests import AgentProposeRequest, AgentRejectRequest
from app.modules.agent.schemas.responses import AgentResponse


class AgentService:
    def __init__(self, repository=agent_repository):
        self._repo = repository

    def list_all(self) -> list[AgentResponse]:
        return self._repo.list_all()

    def propose(self, data: AgentProposeRequest) -> AgentResponse | None:
        existing = self._repo.find_by_name(data.name)
        if existing:
            return None  # duplicate
        return self._repo.create(
            name=data.name,
            description=data.description,
            model=data.model,
            skills=data.skills,
        )

    def approve(self, agent_id: int) -> AgentResponse | None:
        return self._repo.update_status(agent_id, "active")

    def reject(self, agent_id: int, data: AgentRejectRequest) -> AgentResponse | None:
        return self._repo.update_status(agent_id, "rejected", data.reason)


agent_service = AgentService()
