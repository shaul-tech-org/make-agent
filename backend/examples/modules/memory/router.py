from fastapi import APIRouter

from app.modules.memory.exceptions import MemoryNotFoundException
from app.modules.memory.schemas.requests import MemorySaveRequest
from app.modules.memory.schemas.responses import MemoryResponse, MemoryStatsResponse
from app.modules.memory.service import memory_service

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.post("", status_code=201, response_model=MemoryResponse)
async def save_memory(data: MemorySaveRequest):
    return memory_service.save(data)


@router.get("/{agent}/stats", response_model=MemoryStatsResponse)
async def get_agent_stats(agent: str):
    return memory_service.get_stats(agent)


@router.get("/{agent}", response_model=list[MemoryResponse])
async def list_agent_memories(
    agent: str,
    task_id: str | None = None,
    tier: str | None = None,
):
    return memory_service.list_by_agent(agent, task_id, tier)


@router.get("/{agent}/{key}", response_model=MemoryResponse)
async def get_memory(agent: str, key: str):
    result = memory_service.get(agent, key)
    if not result:
        raise MemoryNotFoundException(agent, key)
    return result


@router.post("/archive", status_code=200)
async def archive_task_memories(task_id: str):
    count = memory_service.archive_task(task_id)
    return {"archived": count, "task_id": task_id}
