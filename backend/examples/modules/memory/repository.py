from datetime import datetime, timezone

from app.modules.memory.schemas.responses import MemoryResponse, MemoryStatsResponse

# 에이전트별 hot 메모리 budget (문자 수 기준, ~토큰 근사)
HOT_BUDGET_CHARS = 10_000


class MemoryRepository:
    def __init__(self):
        # (agent, key) → {value, task_id, tier, archived, updated_at}
        self._store: dict[tuple[str, str], dict] = {}

    def save(
        self, agent: str, key: str, value: str,
        task_id: str | None = None, tier: str = "hot",
    ) -> MemoryResponse:
        store_key = (agent, key)
        self._store[store_key] = {
            "agent": agent,
            "key": key,
            "value": value,
            "task_id": task_id,
            "tier": tier,
            "archived": False,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return MemoryResponse(**self._store[store_key])

    def get(self, agent: str, key: str) -> MemoryResponse | None:
        entry = self._store.get((agent, key))
        if not entry or entry["archived"]:
            return None
        return MemoryResponse(**entry)

    def list_by_agent(
        self, agent: str,
        task_id: str | None = None,
        tier: str | None = None,
    ) -> list[MemoryResponse]:
        results = []
        for (a, _), entry in self._store.items():
            if a != agent or entry["archived"]:
                continue
            if task_id is not None and entry.get("task_id") != task_id:
                continue
            # tier 미지정 → hot만 반환 (기본 동작)
            if tier is None and entry.get("tier", "hot") != "hot":
                continue
            if tier is not None and entry.get("tier", "hot") != tier:
                continue
            results.append(MemoryResponse(**entry))
        return results

    def list_hot_for_handoff(
        self, agent: str, task_id: str | None = None,
    ) -> list[MemoryResponse]:
        """handoff용: hot 메모리만 (글로벌 + task 스코프)"""
        results = []
        for (a, _), entry in self._store.items():
            if a != agent or entry["archived"]:
                continue
            if entry.get("tier", "hot") != "hot":
                continue
            # 글로벌(task_id 없음) 또는 해당 task_id
            entry_task = entry.get("task_id")
            if entry_task is None or entry_task == task_id:
                results.append(MemoryResponse(**entry))
        return results

    def get_stats(self, agent: str) -> MemoryStatsResponse:
        hot_count = 0
        hot_chars = 0
        warm_count = 0
        cold_count = 0

        for (a, _), entry in self._store.items():
            if a != agent or entry["archived"]:
                continue
            t = entry.get("tier", "hot")
            if t == "hot":
                hot_count += 1
                hot_chars += len(entry["value"])
            elif t == "warm":
                warm_count += 1
            elif t == "cold":
                cold_count += 1

        budget_pct = max(0.0, (1.0 - hot_chars / HOT_BUDGET_CHARS) * 100)
        return MemoryStatsResponse(
            agent=agent,
            hot_count=hot_count,
            hot_chars=hot_chars,
            warm_count=warm_count,
            cold_count=cold_count,
            budget_remaining_pct=round(budget_pct, 1),
        )

    def archive_by_task(self, task_id: str) -> int:
        count = 0
        for entry in self._store.values():
            if entry.get("task_id") == task_id and not entry["archived"]:
                entry["archived"] = True
                count += 1
        return count

    def clear(self):
        self._store.clear()


memory_repository = MemoryRepository()
