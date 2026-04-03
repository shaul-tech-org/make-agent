from datetime import datetime, timezone

from app.modules.communication.schemas.responses import CommentResponse, HandoffResponse, MemoryItem

VALID_COMMENT_TYPES = {"progress", "blocker", "completed", "handoff"}


class CommunicationRepository:
    def __init__(self):
        self._comments: list[dict] = []
        self._handoffs: list[dict] = []
        self._next_comment_id = 1
        self._next_handoff_id = 1

    def create_comment(
        self, agent: str, task_id: str, comment_type: str,
        content: str, escalate_to: str | None,
    ) -> CommentResponse:
        comment = {
            "id": self._next_comment_id,
            "agent": agent,
            "task_id": task_id,
            "type": comment_type,
            "content": content,
            "escalate_to": escalate_to,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._comments.append(comment)
        self._next_comment_id += 1
        return CommentResponse(**comment)

    def list_comments(self, task_id: str | None = None) -> list[CommentResponse]:
        filtered = self._comments
        if task_id:
            filtered = [c for c in filtered if c["task_id"] == task_id]
        return [CommentResponse(**c) for c in filtered]

    def create_handoff(
        self, from_agent: str, to_agent: str, task_id: str,
        context: str, artifacts: list[str],
        memory_context: list[MemoryItem],
    ) -> HandoffResponse:
        handoff = {
            "id": self._next_handoff_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_id": task_id,
            "context": context,
            "artifacts": artifacts,
            "memory_context": [m.model_dump() for m in memory_context],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._handoffs.append(handoff)
        self._next_handoff_id += 1
        return HandoffResponse(**handoff)

    def list_handoffs(
        self, to_agent: str | None = None, task_id: str | None = None,
    ) -> list[HandoffResponse]:
        filtered = self._handoffs
        if to_agent:
            filtered = [h for h in filtered if h["to_agent"] == to_agent]
        if task_id:
            filtered = [h for h in filtered if h["task_id"] == task_id]
        return [HandoffResponse(**h) for h in filtered]

    def clear(self):
        self._comments.clear()
        self._handoffs.clear()
        self._next_comment_id = 1
        self._next_handoff_id = 1


communication_repository = CommunicationRepository()
