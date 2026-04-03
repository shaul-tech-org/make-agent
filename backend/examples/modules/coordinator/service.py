from app.modules.coordinator.classifier import Classifier, KeywordClassifier
from app.modules.coordinator.exceptions import EmptyRequestException
from app.modules.coordinator.schemas.requests import RouteRequest
from app.modules.coordinator.schemas.responses import RouteResponse


class CoordinatorService:
    """Coordinator 라우팅 서비스

    Classifier를 주입받아 요청을 분류한다.
    기본값: KeywordClassifier (향후 LLMClassifier로 교체 가능)
    """

    def __init__(self, classifier: Classifier | None = None):
        self._classifier = classifier or KeywordClassifier()

    def route(self, data: RouteRequest) -> RouteResponse:
        if not data.request or not data.request.strip():
            raise EmptyRequestException()

        result = self._classifier.classify(data.request)
        return RouteResponse(
            request=data.request,
            category=result.category,
            complexity=result.complexity,
            agent=result.agent,
        )


coordinator_service = CoordinatorService()
