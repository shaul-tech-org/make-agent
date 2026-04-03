import pytest


# === 통합 API 테스트 ===

class TestUnifiedRequest:
    """POST /api/v1/request → 자동 라우팅 + 분해"""

    @pytest.mark.asyncio
    async def test_simple_request_routes_to_agent(self, client):
        """단순 요청 → 에이전트 직접 라우팅 (delegation 없음)"""
        response = await client.post("/api/v1/request", json={
            "request": "로그인 API 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "be-developer"
        assert data["delegation_plan"] is None

    @pytest.mark.asyncio
    async def test_complex_request_triggers_delegation(self, client):
        """복합 요청 → CEO 위임 + delegation plan 포함"""
        response = await client.post("/api/v1/request", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "complex"
        assert data["agent"] == "ceo"
        assert data["delegation_plan"] is not None
        assert len(data["delegation_plan"]["ceo_tasks"]) >= 3

    @pytest.mark.asyncio
    async def test_question_direct_response(self, client):
        """질문 → 직접 응답 (delegation 없음)"""
        response = await client.post("/api/v1/request", json={
            "request": "이 에러가 뭐야?",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "question"
        assert data["agent"] == "direct"
        assert data["delegation_plan"] is None


# === Agent Hire 테스트 ===

class TestAgentHire:
    """에이전트 추가 (승인 기반)"""

    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        """현재 에이전트 목록 조회"""
        response = await client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 7
        names = {a["name"] for a in data}
        assert "be-developer" in names
        assert "ceo" in names

    @pytest.mark.asyncio
    async def test_propose_new_agent(self, client):
        """신규 에이전트 제안 → pending 상태"""
        response = await client.post("/api/v1/agents/propose", json={
            "name": "ml-engineer",
            "description": "머신러닝 모델 개발 및 배포",
            "model": "sonnet",
            "skills": ["pytorch", "tensorflow", "mlops"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ml-engineer"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_approve_agent(self, client):
        """에이전트 승인 → active 상태"""
        # 먼저 제안
        propose = await client.post("/api/v1/agents/propose", json={
            "name": "data-engineer",
            "description": "데이터 파이프라인 구축",
            "model": "sonnet",
            "skills": ["spark", "airflow", "etl"],
        })
        agent_id = propose.json()["id"]

        # 승인
        response = await client.post(f"/api/v1/agents/{agent_id}/approve")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_reject_agent(self, client):
        """에이전트 거절 → rejected 상태"""
        propose = await client.post("/api/v1/agents/propose", json={
            "name": "temp-worker",
            "description": "임시 작업자",
            "model": "haiku",
            "skills": [],
        })
        agent_id = propose.json()["id"]

        response = await client.post(f"/api/v1/agents/{agent_id}/reject", json={
            "reason": "역할이 불명확",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_approved_agent_appears_in_list(self, client):
        """승인된 에이전트가 목록에 active로 표시"""
        propose = await client.post("/api/v1/agents/propose", json={
            "name": "security-engineer",
            "description": "보안 감사 및 취약점 분석",
            "model": "sonnet",
            "skills": ["pentest", "owasp", "security-audit"],
        })
        agent_id = propose.json()["id"]
        await client.post(f"/api/v1/agents/{agent_id}/approve")

        response = await client.get("/api/v1/agents")
        agents = response.json()
        sec = next(a for a in agents if a["name"] == "security-engineer")
        assert sec["status"] == "active"

    @pytest.mark.asyncio
    async def test_duplicate_agent_name_rejected(self, client):
        """중복 에이전트명 → 409"""
        response = await client.post("/api/v1/agents/propose", json={
            "name": "be-developer",
            "description": "중복 테스트",
            "model": "sonnet",
            "skills": [],
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_propose_validation(self, client):
        """빈 제안 → 422"""
        response = await client.post("/api/v1/agents/propose", json={})
        assert response.status_code == 422
