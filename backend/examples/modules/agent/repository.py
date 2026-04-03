"""에이전트 레지스트리 — .claude/agents/ 기반 초기 에이전트 + 동적 추가"""

from app.modules.agent.schemas.responses import AgentResponse

# .claude/agents/ 에 정의된 기본 에이전트
DEFAULT_AGENTS: list[dict] = [
    {"name": "coordinator", "description": "요청 접수 + 라우팅", "model": "sonnet", "skills": ["routing", "classification"]},
    {"name": "ceo", "description": "전략, 복합 분해", "model": "opus", "skills": ["decomposition", "delegation"]},
    {"name": "cto", "description": "기술 결정, 리뷰", "model": "opus", "skills": ["architecture", "code-review"]},
    {"name": "be-developer", "description": "FastAPI 백엔드", "model": "sonnet", "skills": ["python", "fastapi", "postgresql"]},
    {"name": "fe-developer", "description": "React 프론트", "model": "sonnet", "skills": ["typescript", "react", "css"]},
    {"name": "qa-engineer", "description": "테스트, 품질", "model": "sonnet", "skills": ["pytest", "playwright", "e2e"]},
    {"name": "researcher", "description": "리서치, 분석", "model": "sonnet", "skills": ["analysis", "comparison"]},
    {"name": "infra-engineer", "description": "Docker, CI/CD", "model": "sonnet", "skills": ["docker", "github-actions", "kubernetes"]},
]


class AgentRepository:
    def __init__(self):
        self._agents: dict[int, dict] = {}
        self._next_id = 1
        self._load_defaults()

    def _load_defaults(self):
        for agent in DEFAULT_AGENTS:
            self._agents[self._next_id] = {
                "id": self._next_id,
                **agent,
                "status": "active",
                "reject_reason": None,
            }
            self._next_id += 1

    def list_all(self) -> list[AgentResponse]:
        return [AgentResponse(**a) for a in self._agents.values()]

    def find_by_name(self, name: str) -> AgentResponse | None:
        for a in self._agents.values():
            if a["name"] == name:
                return AgentResponse(**a)
        return None

    def create(self, name: str, description: str, model: str, skills: list[str]) -> AgentResponse:
        agent = {
            "id": self._next_id,
            "name": name,
            "description": description,
            "model": model,
            "skills": skills,
            "status": "pending",
            "reject_reason": None,
        }
        self._agents[self._next_id] = agent
        self._next_id += 1
        return AgentResponse(**agent)

    def update_status(self, agent_id: int, status: str, reason: str | None = None) -> AgentResponse | None:
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        agent["status"] = status
        if reason:
            agent["reject_reason"] = reason
        return AgentResponse(**agent)

    def clear(self):
        self._agents.clear()
        self._next_id = 1
        self._load_defaults()


agent_repository = AgentRepository()
