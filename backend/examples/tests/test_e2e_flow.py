"""Phase 6 개선: 연속 흐름 E2E 테스트

각 step의 결과가 다음 step의 입력으로 이어지는 진정한 E2E.
"""

import pytest


class TestComplexRequestFlow:
    """시나리오: "사용자 관리 기능 만들어줘" 전체 파이프라인

    하나의 연속 흐름으로 검증:
    요청 → 분류 → 분해 → 핸드오프 체인 → 작업 → 코멘트 → 메모리 → 아카이브
    """

    @pytest.mark.asyncio
    async def test_full_pipeline(self, client):
        # ── Step 1: 통합 /request ──
        route = await client.post("/api/v1/request", json={
            "request": "사용자 관리 기능 만들어줘",
        })
        assert route.status_code == 200
        route_data = route.json()
        assert route_data["complexity"] == "complex"
        assert route_data["agent"] == "ceo"

        plan = route_data["delegation_plan"]
        ceo_tasks = plan["ceo_tasks"]
        cto_tasks = plan["cto_tasks"]
        phases = plan["phases"]
        agent_summary = plan["agent_summary"]

        assert len(ceo_tasks) >= 3
        assert len(cto_tasks) >= len(ceo_tasks)
        assert len(phases) >= 2
        assert len(agent_summary) >= 1

        # ── Step 2: CEO 메모리 저장 + CEO→CTO 핸드오프 ──
        # CEO가 분해 결과를 메모리에 기록
        task_names = ", ".join(t["name"] for t in ceo_tasks)
        await client.post("/api/v1/memory", json={
            "agent": "ceo", "key": "decomposition",
            "value": f"{len(ceo_tasks)}개 작업: {task_names}",
            "task_id": "FLOW-1",
        })

        # CEO → CTO 핸드오프 (메모리 자동 첨부)
        handoff_1 = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "ceo", "to_agent": "cto",
            "task_id": "FLOW-1",
            "context": f"사용자 관리 — {len(ceo_tasks)}개 기능 작업 기술 분해 위임",
            "artifacts": [],
        })
        h1 = handoff_1.json()
        assert h1["to_agent"] == "cto"
        assert len(h1["memory_context"]) >= 1
        assert any("decomposition" in m["key"] for m in h1["memory_context"])

        # CEO 진행 코멘트
        await client.post("/api/v1/communication/comments", json={
            "agent": "ceo", "task_id": "FLOW-1",
            "type": "progress",
            "content": f"CTO에게 기술 분해 위임 완료. {len(ceo_tasks)}개 작업.",
        })

        # ── Step 3: CTO 기술 결정 + CTO→Developer 핸드오프 ──
        # CTO가 plan의 cto_tasks에서 be-developer 작업 추출
        be_tasks = [t for t in cto_tasks if t["agent"] == "be-developer"]
        assert len(be_tasks) >= 1

        # CTO 기술 결정 메모리
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "tech_decision",
            "value": "FastAPI + PostgreSQL + Alembic. 모듈: app/modules/user/",
            "task_id": "FLOW-2",
        })

        # CTO → be-developer 핸드오프
        first_be_task = be_tasks[0]
        handoff_2 = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "be-developer",
            "task_id": "FLOW-2",
            "context": first_be_task["name"],
            "artifacts": [first_be_task["file_path"]] if first_be_task.get("file_path") else [],
        })
        h2 = handoff_2.json()
        assert h2["to_agent"] == "be-developer"
        assert len(h2["memory_context"]) >= 1

        # ── Step 4: be-developer 작업 (코멘트 + 메모리) ──
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "FLOW-2",
            "type": "progress", "content": "DB 마이그레이션 시작",
        })

        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "schema",
            "value": "users: id, email(unique), password_hash, created_at",
            "task_id": "FLOW-2",
        })

        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "FLOW-2",
            "type": "completed", "content": "DB 마이그레이션 + API 구현 완료",
        })

        # ── Step 5: be-developer → qa-engineer 핸드오프 ──
        # QA를 위한 메모리를 FLOW-3 스코프로 저장
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "api_endpoints",
            "value": "POST/GET/PUT/DELETE /api/v1/users",
            "task_id": "FLOW-3",
        })

        handoff_3 = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "be-developer", "to_agent": "qa-engineer",
            "task_id": "FLOW-3",
            "context": "User API 구현 완료 — 테스트 요청",
            "artifacts": [
                "backend/app/modules/user/router.py",
                "backend/app/modules/user/service.py",
            ],
        })
        h3 = handoff_3.json()
        assert h3["to_agent"] == "qa-engineer"
        assert len(h3["artifacts"]) == 2
        # FLOW-3 스코프 hot 메모리만 첨부 (FLOW-2 메모리는 제외)
        assert len(h3["memory_context"]) >= 1
        assert any(m["key"] == "api_endpoints" for m in h3["memory_context"])

        # ── Step 6: qa-engineer 검증 ──
        await client.post("/api/v1/communication/comments", json={
            "agent": "qa-engineer", "task_id": "FLOW-3",
            "type": "progress", "content": "User API 테스트 시작",
        })
        await client.post("/api/v1/communication/comments", json={
            "agent": "qa-engineer", "task_id": "FLOW-3",
            "type": "completed", "content": "8개 테스트 통과. LGTM.",
        })

        # ── Step 7: 완료 검증 — 전체 이력 정합성 ──

        # 핸드오프 체인: CEO→CTO→be-developer→qa-engineer
        all_handoffs_1 = await client.get("/api/v1/communication/handoffs?task_id=FLOW-1")
        all_handoffs_2 = await client.get("/api/v1/communication/handoffs?task_id=FLOW-2")
        all_handoffs_3 = await client.get("/api/v1/communication/handoffs?task_id=FLOW-3")
        assert len(all_handoffs_1.json()) == 1  # CEO→CTO
        assert len(all_handoffs_2.json()) == 1  # CTO→be-dev
        assert len(all_handoffs_3.json()) == 1  # be-dev→qa

        # 코멘트 이력
        flow2_comments = await client.get("/api/v1/communication/comments?task_id=FLOW-2")
        assert len(flow2_comments.json()) == 2  # progress + completed

        # 메모리 확인
        ceo_mem = await client.get("/api/v1/memory/ceo?task_id=FLOW-1")
        assert len(ceo_mem.json()) == 1

        be_mem = await client.get("/api/v1/memory/be-developer?task_id=FLOW-2")
        assert len(be_mem.json()) == 1

        # ── Step 8: 아카이브 ──
        archive_1 = await client.post("/api/v1/memory/archive?task_id=FLOW-1")
        archive_2 = await client.post("/api/v1/memory/archive?task_id=FLOW-2")
        assert archive_1.json()["archived"] >= 1
        assert archive_2.json()["archived"] >= 1

        # 아카이브 후 조회 시 빈 결과
        ceo_mem_after = await client.get("/api/v1/memory/ceo?task_id=FLOW-1")
        assert len(ceo_mem_after.json()) == 0


class TestAgentHireFlow:
    """시나리오: 작업 중 에이전트 부족 → 채용 → 활용 연속 흐름"""

    @pytest.mark.asyncio
    async def test_hire_and_use(self, client):
        # ── 블로커: ML 전문가 부재 ──
        await client.post("/api/v1/communication/comments", json={
            "agent": "cto", "task_id": "HIRE-1",
            "type": "blocker",
            "content": "추천 시스템 구현에 ML 전문가 필요",
            "escalate_to": "ceo",
        })

        # ── CEO 제안 ──
        propose = await client.post("/api/v1/agents/propose", json={
            "name": "ml-engineer",
            "description": "추천 시스템 ML 모델 개발",
            "model": "sonnet",
            "skills": ["pytorch", "recommendation"],
        })
        agent_id = propose.json()["id"]
        assert propose.json()["status"] == "pending"

        # ── 사용자 승인 ──
        approve = await client.post(f"/api/v1/agents/{agent_id}/approve")
        assert approve.json()["status"] == "active"

        # ── 승인 후 에이전트 목록에 포함 확인 ──
        agents = await client.get("/api/v1/agents")
        names = {a["name"] for a in agents.json()}
        assert "ml-engineer" in names

        # ── CTO→ml-engineer 핸드오프 ──
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "ml_requirements",
            "value": "collaborative filtering, user-item matrix",
            "task_id": "HIRE-2",
        })

        handoff = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "ml-engineer",
            "task_id": "HIRE-2",
            "context": "추천 시스템 ML 모델 개발",
            "artifacts": [],
        })
        assert handoff.json()["to_agent"] == "ml-engineer"
        assert len(handoff.json()["memory_context"]) >= 1

        # ── ml-engineer 작업 ──
        await client.post("/api/v1/communication/comments", json={
            "agent": "ml-engineer", "task_id": "HIRE-2",
            "type": "completed",
            "content": "추천 모델 학습 완료. AUC 0.87",
        })

        # ── 블로커 해제 기록 ──
        await client.post("/api/v1/communication/comments", json={
            "agent": "ceo", "task_id": "HIRE-1",
            "type": "progress",
            "content": "ml-engineer 채용+작업 완료. 블로커 해제.",
        })

        # 전체 이력 검증
        hire1 = await client.get("/api/v1/communication/comments?task_id=HIRE-1")
        assert len(hire1.json()) == 2  # blocker + progress
