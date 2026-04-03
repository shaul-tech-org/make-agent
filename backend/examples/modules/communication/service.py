from app.modules.communication.exceptions import (
    BlockerRequiresEscalateException,
    InvalidCommentTypeException,
)
from app.modules.communication.repository import (
    VALID_COMMENT_TYPES,
    communication_repository,
)
from app.modules.communication.schemas.requests import CommentCreateRequest, HandoffCreateRequest
from app.modules.communication.schemas.responses import CommentResponse, HandoffResponse, MemoryItem
from app.modules.memory.repository import memory_repository


class CommunicationService:
    def __init__(self, repository=communication_repository):
        self._repo = repository

    def create_comment(self, data: CommentCreateRequest) -> CommentResponse:
        if data.type not in VALID_COMMENT_TYPES:
            raise InvalidCommentTypeException(data.type, VALID_COMMENT_TYPES)

        if data.type == "blocker" and not data.escalate_to:
            raise BlockerRequiresEscalateException()

        return self._repo.create_comment(
            agent=data.agent,
            task_id=data.task_id,
            comment_type=data.type,
            content=data.content,
            escalate_to=data.escalate_to,
        )

    def list_comments(self, task_id: str | None = None) -> list[CommentResponse]:
        return self._repo.list_comments(task_id)

    def create_handoff(self, data: HandoffCreateRequest) -> HandoffResponse:
        # P3: hot 메모리만 + task 스코프 필터 (글로벌 + 해당 task)
        memories = memory_repository.list_hot_for_handoff(
            data.from_agent, data.task_id,
        )
        memory_context = [
            MemoryItem(key=m.key, value=m.value) for m in memories
        ]

        return self._repo.create_handoff(
            from_agent=data.from_agent,
            to_agent=data.to_agent,
            task_id=data.task_id,
            context=data.context,
            artifacts=data.artifacts,
            memory_context=memory_context,
        )

    def list_handoffs(
        self, to_agent: str | None = None, task_id: str | None = None,
    ) -> list[HandoffResponse]:
        return self._repo.list_handoffs(to_agent, task_id)


communication_service = CommunicationService()
