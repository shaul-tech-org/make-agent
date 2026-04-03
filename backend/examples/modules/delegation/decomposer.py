"""Decomposer 인터페이스 — 템플릿/LLM 교체 가능

Classifier와 동일한 패턴:
- Protocol로 인터페이스 정의
- TemplateDecomposer: 현재 구현 (키워드+템플릿 기반)
- 향후 LLMDecomposer로 교체 가능
"""

from typing import Protocol

from app.modules.delegation.repository import get_ceo_template, get_cto_decompose_map
from app.modules.delegation.schemas.responses import CeoTask, CtoTask

from collections import defaultdict


class CeoDecomposer(Protocol):
    """CEO 분해 인터페이스"""
    def decompose(self, request_text: str) -> list[CeoTask]: ...


class CtoDecomposer(Protocol):
    """CTO 분해 인터페이스"""
    def decompose(self, ceo_tasks: list[CeoTask], request_text: str) -> list[CtoTask]: ...


class TemplateCeoDecomposer:
    """템플릿 기반 CEO 분해기"""

    def decompose(self, request_text: str) -> list[CeoTask]:
        template = get_ceo_template(request_text)
        return [
            CeoTask(
                id=i,
                name=item["name"],
                type=item["type"],
                depends_on=item["depends_on"],
            )
            for i, item in enumerate(template, start=1)
        ]


class TemplateCtoDecomposer:
    """템플릿 기반 CTO 분해기"""

    def __init__(self):
        self._cto_map = get_cto_decompose_map()

    def decompose(self, ceo_tasks: list[CeoTask], request_text: str) -> list[CtoTask]:
        module_name = self._extract_module_name(request_text)
        cto_tasks: list[CtoTask] = []
        cto_id = 1

        for ceo_task in ceo_tasks:
            decompose_key = self._get_decompose_key(ceo_task)
            sub_tasks = self._cto_map.get(decompose_key, [])

            if not sub_tasks:
                cto_tasks.append(CtoTask(
                    id=cto_id,
                    ceo_task_id=ceo_task.id,
                    name=ceo_task.name,
                    agent=self._default_agent(ceo_task.type),
                    file_path=None,
                    test_criteria=None,
                    depends_on=[],
                ))
                cto_id += 1
                continue

            for sub in sub_tasks:
                file_path = sub["file_path"].format(
                    module=module_name,
                    Page=module_name.capitalize(),
                ) if sub.get("file_path") else None

                cto_tasks.append(CtoTask(
                    id=cto_id,
                    ceo_task_id=ceo_task.id,
                    name=f"{ceo_task.name} — {sub['name_suffix']}",
                    agent=sub["agent"],
                    file_path=file_path,
                    test_criteria=sub.get("test_criteria"),
                    depends_on=[],
                ))
                cto_id += 1

        self._propagate_dependencies(ceo_tasks, cto_tasks)
        return cto_tasks

    def _get_decompose_key(self, ceo_task: CeoTask) -> str:
        name_lower = ceo_task.name.lower()
        if ceo_task.type == "backend":
            if any(kw in name_lower for kw in ["db", "스키마", "테이블", "마이그레이션"]):
                return "backend_db"
            return "backend_api"
        return ceo_task.type

    def _default_agent(self, task_type: str) -> str:
        return {
            "backend": "be-developer",
            "frontend": "fe-developer",
            "test": "qa-engineer",
            "infra": "infra-engineer",
        }.get(task_type, "be-developer")

    def _extract_module_name(self, request_text: str) -> str:
        text = request_text.lower()
        if "사용자" in text or "유저" in text or "회원" in text:
            return "user"
        if "게시" in text or "포스트" in text:
            return "post"
        return "feature"

    def _propagate_dependencies(
        self, ceo_tasks: list[CeoTask], cto_tasks: list[CtoTask]
    ):
        ceo_to_cto: dict[int, list[int]] = defaultdict(list)
        for ct in cto_tasks:
            ceo_to_cto[ct.ceo_task_id].append(ct.id)

        for ct in cto_tasks:
            ceo_task = next((c for c in ceo_tasks if c.id == ct.ceo_task_id), None)
            if not ceo_task:
                continue
            for dep_ceo_id in ceo_task.depends_on:
                dep_cto_ids = ceo_to_cto.get(dep_ceo_id, [])
                if dep_cto_ids:
                    ct.depends_on.append(max(dep_cto_ids))
