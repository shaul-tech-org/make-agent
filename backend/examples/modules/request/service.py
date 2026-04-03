from app.modules.coordinator.schemas.requests import RouteRequest
from app.modules.coordinator.service import coordinator_service
from app.modules.delegation.schemas.requests import DelegationRequest
from app.modules.delegation.service import delegation_service
from app.modules.memory.repository import memory_repository
from app.modules.request.exceptions import EmptyUnifiedRequestException
from app.modules.request.schemas.requests import UnifiedRequest
from app.modules.request.schemas.responses import ContextInfo, UnifiedResponse


class RequestService:
    """통합 요청 처리 — Coordinator + Delegation + Context 연결"""

    def process(self, data: UnifiedRequest) -> UnifiedResponse:
        if not data.request or not data.request.strip():
            raise EmptyUnifiedRequestException()

        # Step 1: Coordinator 분류
        route_result = coordinator_service.route(RouteRequest(request=data.request))

        # Step 2: complex이면 delegation
        delegation_plan = None
        if route_result.complexity == "complex":
            delegation_plan = delegation_service.create_plan(
                DelegationRequest(request=data.request)
            )

        # Step 3: 라우팅된 에이전트의 context 상태 조회
        context_info = None
        if route_result.agent not in ("direct",):
            stats = memory_repository.get_stats(route_result.agent)
            context_info = ContextInfo(
                agent=stats.agent,
                hot_count=stats.hot_count,
                hot_chars=stats.hot_chars,
                budget_remaining_pct=stats.budget_remaining_pct,
            )

        return UnifiedResponse(
            request=data.request,
            category=route_result.category,
            complexity=route_result.complexity,
            agent=route_result.agent,
            delegation_plan=delegation_plan,
            context_info=context_info,
        )


request_service = RequestService()
