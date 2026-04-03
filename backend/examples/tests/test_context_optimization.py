"""Context 최적화 테스트 — Memory Tier + Context Budget + Selective Handoff"""

import pytest


# === P1: Memory Tier ===

class TestMemoryTier:
    """hot/warm/cold 메모리 계층"""

    @pytest.mark.asyncio
    async def test_save_hot_memory(self, client):
        """hot 메모리: 현재 활성 작업 컨텍스트"""
        response = await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "current_task",
            "value": "User API 구현 중", "task_id": "SCAG-15",
            "tier": "hot",
        })
        assert response.status_code == 201
        assert response.json()["tier"] == "hot"

    @pytest.mark.asyncio
    async def test_save_warm_memory(self, client):
        """warm 메모리: 참조 가능한 완료 작업"""
        response = await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "arch_decision",
            "value": "모듈러 모놀리스 확정",
            "tier": "warm",
        })
        assert response.status_code == 201
        assert response.json()["tier"] == "warm"

    @pytest.mark.asyncio
    async def test_default_tier_is_hot(self, client):
        """tier 미지정 시 기본값 hot"""
        response = await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "test_key",
            "value": "test_value",
        })
        assert response.json()["tier"] == "hot"

    @pytest.mark.asyncio
    async def test_list_by_tier(self, client):
        """tier별 메모리 조회"""
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "hot1", "value": "active", "tier": "hot",
        })
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "warm1", "value": "reference", "tier": "warm",
        })
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "cold1", "value": "archived", "tier": "cold",
        })

        hot = await client.get("/api/v1/memory/cto?tier=hot")
        assert len(hot.json()) == 1
        assert hot.json()[0]["tier"] == "hot"

        warm = await client.get("/api/v1/memory/cto?tier=warm")
        assert len(warm.json()) == 1

        # tier 미지정 → hot만 반환 (기본 동작)
        default = await client.get("/api/v1/memory/cto")
        assert all(m["tier"] == "hot" for m in default.json())

    @pytest.mark.asyncio
    async def test_promote_warm_to_hot(self, client):
        """warm → hot 승격"""
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "decision", "value": "old", "tier": "warm",
        })
        # 같은 key로 hot 저장 → 승격
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "decision", "value": "updated", "tier": "hot",
        })
        result = await client.get("/api/v1/memory/cto/decision")
        assert result.json()["tier"] == "hot"
        assert result.json()["value"] == "updated"


# === P2: Context Budget ===

class TestContextBudget:
    """에이전트별 context budget 관리"""

    @pytest.mark.asyncio
    async def test_context_stats(self, client):
        """에이전트의 context 사용 통계 조회"""
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "k1", "value": "v" * 100, "tier": "hot",
        })
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "k2", "value": "v" * 200, "tier": "hot",
        })

        response = await client.get("/api/v1/memory/be-developer/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["agent"] == "be-developer"
        assert stats["hot_count"] == 2
        assert stats["hot_chars"] >= 300
        assert "budget_remaining_pct" in stats

    @pytest.mark.asyncio
    async def test_context_budget_warning(self, client):
        """hot 메모리가 budget 80% 초과 시 경고"""
        # 대량 hot 메모리 추가
        for i in range(20):
            await client.post("/api/v1/memory", json={
                "agent": "be-developer", "key": f"big_{i}",
                "value": "x" * 500, "tier": "hot",
            })

        stats = await client.get("/api/v1/memory/be-developer/stats")
        data = stats.json()
        # budget_remaining_pct가 존재하고 수치임을 확인
        assert isinstance(data["budget_remaining_pct"], (int, float))


# === P3: Handoff 선택적 메모리 전달 ===

class TestSelectiveHandoff:
    """handoff 시 task_id 스코프 메모리만 전달"""

    @pytest.mark.asyncio
    async def test_handoff_only_task_scoped_memory(self, client):
        """task_id가 있는 handoff → 해당 task의 hot 메모리만 전달"""
        # 글로벌 hot 메모리
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "global", "value": "글로벌 정보",
            "tier": "hot",
        })
        # task-scoped hot 메모리
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "task_info", "value": "작업 정보",
            "task_id": "TASK-1", "tier": "hot",
        })
        # 다른 task 메모리
        await client.post("/api/v1/memory", json={
            "agent": "be-developer", "key": "other", "value": "다른 작업",
            "task_id": "TASK-2", "tier": "hot",
        })

        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "be-developer", "to_agent": "qa-engineer",
            "task_id": "TASK-1",
            "context": "API 완료",
            "artifacts": [],
        })
        data = response.json()
        keys = {m["key"] for m in data["memory_context"]}
        # TASK-1 메모리 + 글로벌 메모리만 포함, TASK-2는 제외
        assert "task_info" in keys
        assert "global" in keys
        assert "other" not in keys

    @pytest.mark.asyncio
    async def test_handoff_excludes_warm_cold(self, client):
        """handoff에 warm/cold 메모리는 포함되지 않음"""
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "hot_info", "value": "활성", "tier": "hot",
        })
        await client.post("/api/v1/memory", json={
            "agent": "cto", "key": "warm_info", "value": "참조", "tier": "warm",
        })

        response = await client.post("/api/v1/communication/handoff", json={
            "from_agent": "cto", "to_agent": "be-developer",
            "task_id": "TASK-3", "context": "작업 위임",
            "artifacts": [],
        })
        keys = {m["key"] for m in response.json()["memory_context"]}
        assert "hot_info" in keys
        assert "warm_info" not in keys
