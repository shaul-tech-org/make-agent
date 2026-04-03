from collections import defaultdict

from app.modules.delegation.decomposer import (
    CeoDecomposer,
    CtoDecomposer,
    TemplateCeoDecomposer,
    TemplateCtoDecomposer,
)
from app.modules.delegation.exceptions import EmptyDelegationRequestException
from app.modules.delegation.schemas.requests import DelegationRequest
from app.modules.delegation.schemas.responses import (
    AgentSummary,
    CtoTask,
    DelegationPlanResponse,
    Phase,
)


class DelegationService:
    """CEO→CTO 위임 체인 서비스

    Decomposer를 주입받아 분해한다.
    기본값: Template 기반 (향후 LLM 기반으로 교체 가능)
    """

    def __init__(
        self,
        ceo_decomposer: CeoDecomposer | None = None,
        cto_decomposer: CtoDecomposer | None = None,
    ):
        self._ceo = ceo_decomposer or TemplateCeoDecomposer()
        self._cto = cto_decomposer or TemplateCtoDecomposer()

    def create_plan(self, data: DelegationRequest) -> DelegationPlanResponse:
        if not data.request or not data.request.strip():
            raise EmptyDelegationRequestException()

        # Step 1: CEO 분해
        ceo_tasks = self._ceo.decompose(data.request)

        # Step 2: CTO 분해
        cto_tasks = self._cto.decompose(ceo_tasks, data.request)

        # Step 3: 실행 계획
        phases = self._build_phases(cto_tasks)

        # Step 4: 에이전트 요약
        agent_summary = self._build_agent_summary(cto_tasks)

        return DelegationPlanResponse(
            request=data.request,
            ceo_tasks=ceo_tasks,
            cto_tasks=cto_tasks,
            phases=phases,
            agent_summary=agent_summary,
        )

    def _build_phases(self, cto_tasks: list[CtoTask]) -> list[Phase]:
        remaining = {t.id: t for t in cto_tasks}
        completed: set[int] = set()
        phases: list[Phase] = []
        phase_num = 1

        while remaining:
            ready = [
                t for t in remaining.values()
                if all(dep in completed for dep in t.depends_on)
            ]
            if not ready:
                ready = list(remaining.values())

            phase_tasks = [t.name for t in ready]
            phases.append(Phase(
                phase=phase_num,
                tasks=phase_tasks,
                parallel=len(ready) > 1,
            ))

            for t in ready:
                completed.add(t.id)
                del remaining[t.id]
            phase_num += 1

        return phases

    def _build_agent_summary(self, cto_tasks: list[CtoTask]) -> list[AgentSummary]:
        by_agent: dict[str, list[int]] = defaultdict(list)
        for t in cto_tasks:
            by_agent[t.agent].append(t.id)

        return [
            AgentSummary(agent=agent, task_count=len(ids), task_ids=ids)
            for agent, ids in sorted(by_agent.items())
        ]


delegation_service = DelegationService()
