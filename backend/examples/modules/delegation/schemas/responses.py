from pydantic import BaseModel


class CeoTask(BaseModel):
    id: int
    name: str
    type: str
    depends_on: list[int]


class CtoTask(BaseModel):
    id: int
    ceo_task_id: int
    name: str
    agent: str
    file_path: str | None
    test_criteria: str | None
    depends_on: list[int]


class Phase(BaseModel):
    phase: int
    tasks: list[str]
    parallel: bool


class AgentSummary(BaseModel):
    agent: str
    task_count: int
    task_ids: list[int]


class DelegationPlanResponse(BaseModel):
    request: str
    ceo_tasks: list[CeoTask]
    cto_tasks: list[CtoTask]
    phases: list[Phase]
    agent_summary: list[AgentSummary]
