import pytest


# === CEO Decomposer 테스트 ===

class TestCeoDecomposer:
    """CEO가 복합 요청을 기능 단위로 분해"""

    @pytest.mark.asyncio
    async def test_decompose_user_management(self, client):
        """사용자 관리 → DB + API + UI + 테스트"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["ceo_tasks"]) >= 3
        task_types = {t["type"] for t in data["ceo_tasks"]}
        assert "backend" in task_types
        assert "frontend" in task_types

    @pytest.mark.asyncio
    async def test_decompose_has_dependencies(self, client):
        """CEO 분해 결과에 의존성 정보가 포함"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "게시판 만들어줘",
        })
        data = response.json()
        # 최소 하나의 task는 의존성이 있어야 함
        has_dependency = any(
            len(t["depends_on"]) > 0 for t in data["ceo_tasks"]
        )
        assert has_dependency

    @pytest.mark.asyncio
    async def test_decompose_tasks_have_names(self, client):
        """모든 CEO 작업에 이름이 있는가"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        for task in data["ceo_tasks"]:
            assert "name" in task
            assert "type" in task
            assert len(task["name"]) > 0


# === CTO Decomposer 테스트 ===

class TestCtoDecomposer:
    """CTO가 CEO의 기능 작업을 기술 단위로 분해"""

    @pytest.mark.asyncio
    async def test_technical_tasks_have_agent(self, client):
        """모든 CTO 분해 결과에 담당 에이전트가 있는가"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        for task in data["cto_tasks"]:
            assert "agent" in task
            assert task["agent"] in [
                "be-developer", "fe-developer", "qa-engineer",
                "infra-engineer", "cto",
            ]

    @pytest.mark.asyncio
    async def test_technical_tasks_have_file_paths(self, client):
        """CTO 분해에 구체적 파일 경로가 포함"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        has_path = any("file_path" in t and t["file_path"] for t in data["cto_tasks"])
        assert has_path

    @pytest.mark.asyncio
    async def test_cto_tasks_more_than_ceo(self, client):
        """CTO 분해 결과가 CEO보다 세밀 (task 수 >= CEO)"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        assert len(data["cto_tasks"]) >= len(data["ceo_tasks"])

    @pytest.mark.asyncio
    async def test_backend_tasks_go_to_be_developer(self, client):
        """backend 유형 작업은 be-developer에게"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        be_tasks = [t for t in data["cto_tasks"] if t["agent"] == "be-developer"]
        assert len(be_tasks) >= 1


# === 실행 계획 테스트 ===

class TestExecutionPlan:
    """전체 위임 체인 통합 — 실행 계획"""

    @pytest.mark.asyncio
    async def test_plan_has_phases(self, client):
        """실행 계획에 Phase가 있는가"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        assert "phases" in data
        assert len(data["phases"]) >= 2

    @pytest.mark.asyncio
    async def test_phase_order_db_before_api(self, client):
        """Phase 순서: DB가 API보다 먼저"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        phase_tasks = []
        for phase in data["phases"]:
            phase_tasks.extend(phase["tasks"])

        db_idx = next(
            (i for i, t in enumerate(phase_tasks) if "db" in t.lower() or "스키마" in t.lower() or "마이그레이션" in t.lower()),
            None,
        )
        api_idx = next(
            (i for i, t in enumerate(phase_tasks) if "api" in t.lower() or "엔드포인트" in t.lower()),
            None,
        )
        if db_idx is not None and api_idx is not None:
            assert db_idx < api_idx

    @pytest.mark.asyncio
    async def test_plan_has_agent_summary(self, client):
        """실행 계획에 에이전트별 할당 요약이 있는가"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        data = response.json()
        assert "agent_summary" in data
        assert len(data["agent_summary"]) >= 1

    @pytest.mark.asyncio
    async def test_response_has_all_fields(self, client):
        """응답에 필수 필드가 모두 있는가"""
        response = await client.post("/api/v1/delegation/plan", json={
            "request": "게시판 만들어줘",
        })
        data = response.json()
        assert "request" in data
        assert "ceo_tasks" in data
        assert "cto_tasks" in data
        assert "phases" in data
        assert "agent_summary" in data

    @pytest.mark.asyncio
    async def test_empty_request_validation(self, client):
        """빈 요청 → 422"""
        response = await client.post("/api/v1/delegation/plan", json={})
        assert response.status_code == 422
