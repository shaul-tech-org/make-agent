from app.modules.memory.repository import memory_repository
from app.modules.memory.schemas.requests import MemorySaveRequest
from app.modules.memory.schemas.responses import MemoryResponse, MemoryStatsResponse


class MemoryService:
    def __init__(self, repository=memory_repository):
        self._repo = repository

    def save(self, data: MemorySaveRequest) -> MemoryResponse:
        return self._repo.save(
            agent=data.agent, key=data.key,
            value=data.value, task_id=data.task_id,
            tier=data.tier,
        )

    def get(self, agent: str, key: str) -> MemoryResponse | None:
        return self._repo.get(agent, key)

    def list_by_agent(
        self, agent: str,
        task_id: str | None = None,
        tier: str | None = None,
    ) -> list[MemoryResponse]:
        return self._repo.list_by_agent(agent, task_id, tier)

    def get_stats(self, agent: str) -> MemoryStatsResponse:
        return self._repo.get_stats(agent)

    def archive_task(self, task_id: str) -> int:
        return self._repo.archive_by_task(task_id)


memory_service = MemoryService()
