"""Phase 6: 전체 시나리오 E2E 테스트

3가지 시나리오로 전체 파이프라인을 검증한다.
"""

import pytest


class TestScenario1_ComplexRequest:
    """시나리오 1: 복합 요청 전체 파이프라인

    "사용자 관리 기능 만들어줘"
    → Coordinator(complex) → CEO 분해 → CTO 분해
    → 개발자 작업 시뮬레이션 (코멘트 + 메모리 + 핸드오프)
    → 작업 완료 → 메모리 아카이브
    """

    @pytest.mark.asyncio
    async def test_step1_request_classified_as_complex(self, client):
        """Step 1: 통합 /request → complex + delegation plan"""
        response = await client.post("/api/v1/request", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["complexity"] == "complex"
        assert data["agent"] == "ceo"
        assert data["delegation_plan"] is not None
        # delegation plan 기본 검증
        plan = data["delegation_plan"]
        assert len(plan["ceo_tasks"]) >= 3
        assert len(plan["cto_tasks"]) >= len(plan["ceo_tasks"])
        assert len(plan["phases"]) >= 2
        return data

    @pytest.mark.asyncio
    async def test_step2_ceo_to_cto_handoff(self, client):
        """Step 2: CEO → CTO 핸드오프 + CEO 메모리 저장"""
        # CEO 메모리에 분해 결과 저장
        await client.post("/api/v1/memory", json={
            "agent": "ceo", "key": "decomposition_result",
            "value": "6개 기능 작업으로 분해 완료", "task_id": "SCAG-14",
        })

        # CEO → CTO 핸드오프
        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "ceo", "to_agent": "cto",
            "task_id": "SCAG-14",
            "context": "사용자 관리 기능 — 기술 분해 위임",
            "artifacts": [],
        })
        data = response.json()
        assert data["from_agent"] == "ceo"
        assert data["to_agent"] == "cto"
        # CEO 메모리가 자동 첨부
        assert len(data["memory_context"]) >= 1
        assert any(m["key"] == "decomposition_result" for m in data["memory_context"])

    @pytest.mark.asyncio
    async def test_step3_cto_assigns_and_handoffs_to_developer(self, client):
        """Step 3: CTO → be-developer 핸드오프 + 기술 명세"""
        # CTO 메모리에 기술 결정 저장
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "tech_stack",
            "value": "FastAPI + PostgreSQL + Alembic", "task_id": "SCAG-15",
        })

        # CTO → be-developer 핸드오프
        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "be-developer",
            "task_id": "SCAG-15",
            "context": "users 테이블 마이그레이션 작성",
            "artifacts": ["backend/app/modules/user/models.py"],
        })
        data = response.json()
        assert data["to_agent"] == "be-developer"
        assert len(data["artifacts"]) == 1
        assert len(data["memory_context"]) >= 1

    @pytest.mark.asyncio
    async def test_step4_developer_works_with_comments(self, client):
        """Step 4: be-developer 작업 + progress 코멘트"""
        # 작업 시작
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-15",
            "type": "progress", "content": "users 테이블 마이그레이션 시작",
        })

        # 메모리에 작업 컨텍스트 저장
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "schema_defined",
            "value": "users: id(PK), email(unique), password_hash, created_at",
            "task_id": "SCAG-15",
        })

        # 완료 코멘트
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-15",
            "type": "completed", "content": "users 테이블 마이그레이션 완료",
        })

        # 코멘트 이력 확인
        response = await client.get("/api/v1/communication/comments?task_id=SCAG-15")
        comments = response.json()
        assert len(comments) == 2
        assert comments[0]["type"] == "progress"
        assert comments[1]["type"] == "completed"

    @pytest.mark.asyncio
    async def test_step5_developer_to_qa_handoff(self, client):
        """Step 5: be-developer → qa-engineer 핸드오프"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "api_endpoints",
            "value": "POST/GET/PUT/DELETE /api/v1/users", "task_id": "SCAG-16",
        })

        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "be-developer", "to_agent": "qa-engineer",
            "task_id": "SCAG-16",
            "context": "User CRUD API 구현 완료 — 테스트 요청",
            "artifacts": [
                "backend/app/modules/user/router.py",
                "backend/app/modules/user/service.py",
            ],
        })
        data = response.json()
        assert data["to_agent"] == "qa-engineer"
        assert len(data["artifacts"]) == 2
        assert len(data["memory_context"]) >= 1

    @pytest.mark.asyncio
    async def test_step6_archive_completed_task(self, client):
        """Step 6: 작업 완료 → 메모리 아카이브"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "done_work",
            "value": "마이그레이션 완료", "task_id": "SCAG-15",
        })

        response = await client.post("/api/v1/memory/archive?task_id=SCAG-15")
        assert response.status_code == 200
        assert response.json()["archived"] >= 1

        # 아카이브 후 조회 시 제외
        response = await client.get("/api/v1/memory/be-developer?task_id=SCAG-15")
        assert len(response.json()) == 0


class TestScenario2_SimpleRequest:
    """시나리오 2: 단순 요청 단축 경로

    "로그인 API 만들어줘"
    → Coordinator(simple, be-developer) → 바로 작업 → 코멘트 → 완료
    """

    @pytest.mark.asyncio
    async def test_simple_flow(self, client):
        """단순 요청 전체 플로우"""
        # Step 1: 라우팅
        route = await client.post("/api/v1/request", json={
            "request": "로그인 API 만들어줘",
        })
        data = route.json()
        assert data["complexity"] == "simple"
        assert data["agent"] == "be-developer"
        assert data["delegation_plan"] is None

        # Step 2: 작업 시작 코멘트
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-25",
            "type": "progress", "content": "로그인 API 구현 시작",
        })

        # Step 3: 메모리 저장
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "auth_method",
            "value": "JWT Bearer Token", "task_id": "SCAG-25",
        })

        # Step 4: 완료
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-25",
            "type": "completed", "content": "POST /api/v1/auth/login 구현 완료",
        })

        # 검증: 코멘트 2개, 메모리 1개
        comments = await client.get("/api/v1/communication/comments?task_id=SCAG-25")
        assert len(comments.json()) == 2

        memory = await client.get("/api/v1/memory/be-developer?task_id=SCAG-25")
        assert len(memory.json()) == 1


class TestScenario3_AgentHire:
    """시나리오 3: Agent Hire 포함

    작업 중 ML 전문가 필요 → propose → approve → 라우팅에 사용
    """

    @pytest.mark.asyncio
    async def test_hire_flow(self, client):
        """에이전트 부족 → 제안 → 승인 → 활용"""
        # Step 1: 기존 에이전트 확인
        agents = await client.get("/api/v1/agents")
        initial_count = len(agents.json())

        # Step 2: 블로커 발생 — ML 전문가 필요
        await client.post("/api/v1/communication/comments", json={
            "agent": "cto", "task_id": "SCAG-30",
            "type": "blocker",
            "content": "추천 시스템에 ML 모델 필요. 현재 ML 전문가 에이전트 없음.",
            "escalate_to": "ceo",
        })

        # Step 3: CEO가 새 에이전트 제안
        propose = await client.post("/api/v1/agents/propose", json={
            "name": "ml-engineer",
            "description": "머신러닝 모델 개발 (추천 시스템, 분류기)",
            "model": "sonnet",
            "skills": ["pytorch", "scikit-learn", "recommendation"],
        })
        assert propose.status_code == 201
        agent_id = propose.json()["id"]
        assert propose.json()["status"] == "pending"

        # Step 4: 사용자 승인
        approve = await client.post(f"/api/v1/agents/{agent_id}/approve")
        assert approve.json()["status"] == "active"

        # Step 5: 승인 후 에이전트 수 증가
        agents = await client.get("/api/v1/agents")
        assert len(agents.json()) == initial_count + 1

        # Step 6: 승인 기록 코멘트
        await client.post("/api/v1/communication/comments", json={
            "agent": "ceo", "task_id": "SCAG-30",
            "type": "progress",
            "content": "ml-engineer 채용 승인. 추천 시스템 작업 할당 가능.",
        })

        # Step 7: CTO → ml-engineer 핸드오프
        handoff = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "ml-engineer",
            "task_id": "SCAG-31",
            "context": "추천 시스템 ML 모델 개발",
            "artifacts": [],
        })
        assert handoff.json()["to_agent"] == "ml-engineer"


class TestScenario4_BlockerEscalation:
    """시나리오 4: 블로커 에스컬레이션 체인

    Developer → CTO → CEO → 사용자
    """

    @pytest.mark.asyncio
    async def test_escalation_chain(self, client):
        """블로커 에스컬레이션: Developer → CTO → CEO"""
        # Developer 블로커
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-40",
            "type": "blocker",
            "content": "외부 API 인증 키 필요. 환경변수 설정 요청.",
            "escalate_to": "cto",
        })

        # CTO가 해결 불가 → CEO에게 에스컬레이션
        await client.post("/api/v1/communication/comments", json={
            "agent": "cto", "task_id": "SCAG-40",
            "type": "blocker",
            "content": "외부 API 계약 미체결. 비즈니스 결정 필요.",
            "escalate_to": "ceo",
        })

        # CEO가 사용자에게 보고
        await client.post("/api/v1/communication/comments", json={
            "agent": "ceo", "task_id": "SCAG-40",
            "type": "blocker",
            "content": "외부 API 제공업체와 계약 필요. 사용자 승인 요청.",
            "escalate_to": "user",
        })

        # 전체 코멘트 이력 확인
        response = await client.get("/api/v1/communication/comments?task_id=SCAG-40")
        comments = response.json()
        assert len(comments) == 3
        assert comments[0]["agent"] == "be-developer"
        assert comments[0]["escalate_to"] == "cto"
        assert comments[1]["agent"] == "cto"
        assert comments[1]["escalate_to"] == "ceo"
        assert comments[2]["agent"] == "ceo"
        assert comments[2]["escalate_to"] == "user"
