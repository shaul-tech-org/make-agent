import pytest


# === Communication 코멘트 프로토콜 테스트 ===

class TestComment:
    """에이전트 코멘트 CRUD"""

    @pytest.mark.asyncio
    async def test_create_comment(self, client):
        response = await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer",
            "task_id": "SCAG-7",
            "type": "progress",
            "content": "Todo 모듈 스키마 정의 완료",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["agent"] == "be-developer"
        assert data["type"] == "progress"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_list_comments_by_task(self, client):
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-7",
            "type": "progress", "content": "시작",
        })
        await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-7",
            "type": "completed", "content": "완료",
        })

        response = await client.get("/api/v1/communication/comments?task_id=SCAG-7")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_comment_types(self, client):
        """코멘트 유형: progress, blocker, completed, handoff"""
        for comment_type in ["progress", "completed", "handoff"]:
            response = await client.post("/api/v1/communication/comments", json={
                "agent": "cto", "task_id": "SCAG-10",
                "type": comment_type, "content": f"{comment_type} 테스트",
            })
            assert response.status_code == 201

        # blocker는 escalate_to 필수
        response = await client.post("/api/v1/communication/comments", json={
            "agent": "cto", "task_id": "SCAG-10",
            "type": "blocker", "content": "blocker 테스트",
            "escalate_to": "ceo",
        })
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_blocker_has_escalation(self, client):
        """blocker 코멘트에 에스컬레이션 대상 포함"""
        response = await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-8",
            "type": "blocker",
            "content": "DB 연결 실패",
            "escalate_to": "cto",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["escalate_to"] == "cto"


# === Memory 테스트 ===

class TestMemory:
    """에이전트별 메모리 저장/조회"""

    @pytest.mark.asyncio
    async def test_save_memory(self, client):
        response = await client.post("/api/v1/memory", json={
            "agent": "be-developer",
            "key": "user_module_schema",
            "value": "users 테이블: id, email, password_hash, created_at",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["agent"] == "be-developer"
        assert data["key"] == "user_module_schema"

    @pytest.mark.asyncio
    async def test_get_memory(self, client):
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "arch_decision",
            "value": "모듈러 모놀리스로 결정",
        })

        response = await client.get("/api/v1/memory/cto/arch_decision")
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "모듈러 모놀리스로 결정"

    @pytest.mark.asyncio
    async def test_list_agent_memories(self, client):
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "key1", "value": "val1",
        })
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "key2", "value": "val2",
        })

        response = await client.get("/api/v1/memory/be-developer")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_memory_isolation(self, client):
        """에이전트별 메모리 격리"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "shared_key", "value": "be value",
        })
        await client.post("/api/v1/memory", json={
            "agent": "fe-developer", "key": "shared_key", "value": "fe value",
        })

        be = await client.get("/api/v1/memory/be-developer/shared_key")
        fe = await client.get("/api/v1/memory/fe-developer/shared_key")
        assert be.json()["value"] == "be value"
        assert fe.json()["value"] == "fe value"

    @pytest.mark.asyncio
    async def test_update_memory(self, client):
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "db_choice", "value": "MySQL",
        })
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "db_choice", "value": "PostgreSQL",
        })

        response = await client.get("/api/v1/memory/cto/db_choice")
        assert response.json()["value"] == "PostgreSQL"

    @pytest.mark.asyncio
    async def test_memory_not_found(self, client):
        response = await client.get("/api/v1/memory/unknown/nonexistent")
        assert response.status_code == 404


# === Handoff 테스트 ===

class TestHandoff:
    """에이전트 간 작업 인수인계"""

    @pytest.mark.asyncio
    async def test_create_handoff(self, client):
        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "be-developer",
            "to_agent": "qa-engineer",
            "task_id": "SCAG-9",
            "context": "Todo CRUD API 구현 완료. POST/GET/PUT/DELETE /api/v1/todos",
            "artifacts": ["backend/app/modules/todo/router.py"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["from_agent"] == "be-developer"
        assert data["to_agent"] == "qa-engineer"
        assert len(data["artifacts"]) == 1

    @pytest.mark.asyncio
    async def test_list_handoffs_for_agent(self, client):
        await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "be-developer",
            "task_id": "SCAG-7", "context": "스키마 설계 완료",
            "artifacts": [],
        })

        response = await client.get("/api/v1/communication/handoffs?to_agent=be-developer")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["to_agent"] == "be-developer"

    @pytest.mark.asyncio
    async def test_handoff_chain(self, client):
        """CEO → CTO → be-developer 체인 추적"""
        await client.post("/api/v1/communication/handoff", json={
            "from_agent": "ceo", "to_agent": "cto",
            "task_id": "SCAG-14", "context": "사용자 관리 기술 작업 위임",
            "artifacts": [],
        })
        await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "be-developer",
            "task_id": "SCAG-15", "context": "DB 스키마 작업 할당",
            "artifacts": [],
        })

        response = await client.get("/api/v1/communication/handoffs?task_id=SCAG-14")
        chain_14 = response.json()

        response = await client.get("/api/v1/communication/handoffs?task_id=SCAG-15")
        chain_15 = response.json()

        assert len(chain_14) >= 1
        assert chain_14[0]["from_agent"] == "ceo"
        assert len(chain_15) >= 1
        assert chain_15[0]["from_agent"] == "cto"


# === 개선 1: Handoff + Memory 연계 ===

class TestHandoffMemoryIntegration:
    """handoff 시 from_agent의 관련 메모리 자동 첨부"""

    @pytest.mark.asyncio
    async def test_handoff_includes_memory(self, client):
        """메모리 저장 후 handoff → memory_context 자동 포함"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "user_schema",
            "value": "users: id, email, password_hash",
        })
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "api_pattern",
            "value": "REST /api/v1/users",
        })

        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "be-developer", "to_agent": "qa-engineer",
            "task_id": "SCAG-9", "context": "API 구현 완료",
            "artifacts": ["backend/app/modules/user/router.py"],
        })
        data = response.json()
        assert "memory_context" in data
        assert len(data["memory_context"]) == 2

    @pytest.mark.asyncio
    async def test_handoff_no_memory(self, client):
        """메모리 없는 에이전트의 handoff → memory_context 빈 리스트"""
        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "ceo", "to_agent": "cto",
            "task_id": "SCAG-14", "context": "기술 작업 위임",
            "artifacts": [],
        })
        data = response.json()
        assert data["memory_context"] == []


# === 개선 2: 코멘트 템플릿 검증 ===

class TestCommentTemplate:
    """코멘트 유형별 구조화 형식 검증"""

    @pytest.mark.asyncio
    async def test_invalid_comment_type(self, client):
        """허용되지 않은 코멘트 유형 → 422"""
        response = await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-7",
            "type": "invalid_type", "content": "테스트",
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_blocker_requires_escalate_to(self, client):
        """blocker 유형에 escalate_to 미포함 → 422"""
        response = await client.post("/api/v1/communication/comments", json={
            "agent": "be-developer", "task_id": "SCAG-7",
            "type": "blocker", "content": "DB 연결 실패",
        })
        assert response.status_code == 422


# === 개선 3: Memory 스코프 ===

class TestMemoryScope:
    """task_id 기반 메모리 스코프"""

    @pytest.mark.asyncio
    async def test_save_scoped_memory(self, client):
        """task_id 스코프 메모리 저장"""
        response = await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "progress",
            "value": "50% 완료", "task_id": "SCAG-7",
        })
        assert response.status_code == 201
        assert response.json()["task_id"] == "SCAG-7"

    @pytest.mark.asyncio
    async def test_list_scoped_memories(self, client):
        """특정 task의 메모리만 조회"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "key1",
            "value": "task7 메모리", "task_id": "SCAG-7",
        })
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "key2",
            "value": "task8 메모리", "task_id": "SCAG-8",
        })
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "key3",
            "value": "글로벌 메모리",
        })

        response = await client.get("/api/v1/memory/be-developer?task_id=SCAG-7")
        data = response.json()
        assert len(data) == 1
        assert data[0]["task_id"] == "SCAG-7"

    @pytest.mark.asyncio
    async def test_archive_task_memories(self, client):
        """task 메모리 아카이브 → 조회 시 제외"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "done_key",
            "value": "완료된 작업", "task_id": "SCAG-7",
        })

        response = await client.post("/api/v1/memory/archive?task_id=SCAG-7")
        assert response.status_code == 200

        response = await client.get("/api/v1/memory/be-developer")
        data = response.json()
        active = [m for m in data if m.get("task_id") == "SCAG-7"]
        assert len(active) == 0
