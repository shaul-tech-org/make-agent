"""분해 템플릿 — 요청 유형별 분해 패턴

CEO: 기능 단위 분해 템플릿
CTO: 기술 단위 분해 + 에이전트 할당 템플릿
"""

# CEO 분해 템플릿: 키워드 → 기능 작업 목록
CEO_DECOMPOSE_TEMPLATES: dict[str, list[dict]] = {
    "사용자 관리": [
        {"name": "DB 스키마 설계 (users 테이블)", "type": "backend", "depends_on": []},
        {"name": "회원가입/로그인 API 구현", "type": "backend", "depends_on": [1]},
        {"name": "프로필 API 구현", "type": "backend", "depends_on": [1]},
        {"name": "로그인/회원가입 UI 페이지", "type": "frontend", "depends_on": [2]},
        {"name": "프로필 UI 페이지", "type": "frontend", "depends_on": [3]},
        {"name": "테스트", "type": "test", "depends_on": [2, 3]},
    ],
    "게시판": [
        {"name": "DB 스키마 설계 (posts 테이블)", "type": "backend", "depends_on": []},
        {"name": "게시글 CRUD API 구현", "type": "backend", "depends_on": [1]},
        {"name": "게시글 목록/상세 UI 페이지", "type": "frontend", "depends_on": [2]},
        {"name": "게시글 작성/수정 UI 페이지", "type": "frontend", "depends_on": [2]},
        {"name": "테스트", "type": "test", "depends_on": [2]},
    ],
    "default": [
        {"name": "요구사항 분석 + DB 설계", "type": "backend", "depends_on": []},
        {"name": "API 구현", "type": "backend", "depends_on": [1]},
        {"name": "UI 구현", "type": "frontend", "depends_on": [2]},
        {"name": "테스트", "type": "test", "depends_on": [2, 3]},
    ],
}

# CTO 기술 분해: CEO task type → 세부 기술 작업
CTO_DECOMPOSE_MAP: dict[str, list[dict]] = {
    "backend_db": [
        {
            "name_suffix": "Alembic 마이그레이션 작성",
            "agent": "be-developer",
            "file_path": "backend/app/modules/{module}/models.py",
            "test_criteria": "마이그레이션 up/down 테스트",
        },
    ],
    "backend_api": [
        {
            "name_suffix": "엔드포인트 구현",
            "agent": "be-developer",
            "file_path": "backend/app/modules/{module}/router.py",
            "test_criteria": "pytest 성공/실패 케이스 각 1개 이상",
        },
        {
            "name_suffix": "서비스 로직 구현",
            "agent": "be-developer",
            "file_path": "backend/app/modules/{module}/service.py",
            "test_criteria": "비즈니스 로직 단위 테스트",
        },
    ],
    "frontend": [
        {
            "name_suffix": "React 컴포넌트 구현",
            "agent": "fe-developer",
            "file_path": "frontend/src/pages/{Page}.tsx",
            "test_criteria": "렌더링 + 인터랙션 테스트",
        },
    ],
    "test": [
        {
            "name_suffix": "통합 테스트 작성",
            "agent": "qa-engineer",
            "file_path": "backend/tests/test_{module}.py",
            "test_criteria": "전체 CRUD 흐름 E2E 테스트",
        },
    ],
}


def get_ceo_template(request_text: str) -> list[dict]:
    """요청 텍스트에서 키워드 매칭으로 CEO 분해 템플릿 반환"""
    text = request_text.lower()
    for keyword, template in CEO_DECOMPOSE_TEMPLATES.items():
        if keyword == "default":
            continue
        if keyword in text:
            return template
    return CEO_DECOMPOSE_TEMPLATES["default"]


def get_cto_decompose_map() -> dict[str, list[dict]]:
    return CTO_DECOMPOSE_MAP
