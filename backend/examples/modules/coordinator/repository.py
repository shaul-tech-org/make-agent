"""Coordinator 라우팅 테이블 — .claude/agents/coordinator.md 기반

키워드에 가중치를 부여하여 동점 문제를 해결한다.
가중치: 해당 에이전트의 핵심 키워드일수록 높음 (1~3)
"""


# 키워드 → (가중치) 매핑
# 가중치: 3=핵심, 2=주요, 1=보조
AGENT_KEYWORDS: dict[str, list[tuple[str, int]]] = {
    "be-developer": [
        ("api", 2), ("db", 3), ("서버", 3), ("백엔드", 3),
        ("마이그레이션", 3), ("fastapi", 3), ("엔드포인트", 3),
        ("모델", 1), ("스키마", 1), ("쿼리", 2),
    ],
    "fe-developer": [
        ("ui", 3), ("프론트", 3), ("디자인", 2), ("컴포넌트", 3),
        ("css", 3), ("react", 3), ("페이지", 2), ("버튼", 2),
        ("스타일", 2), ("레이아웃", 2),
    ],
    "cto": [
        ("아키텍처", 3), ("기술 선택", 3), ("리뷰", 2), ("스택", 2),
        ("설계", 2),
    ],
    "researcher": [
        ("조사", 3), ("분석", 2), ("비교", 3), ("리서치", 3),
        ("트렌드", 2),
    ],
    "qa-engineer": [
        ("테스트", 3), ("qa", 3), ("검증", 3), ("품질", 2),
        ("e2e", 3),
    ],
    "infra-engineer": [
        ("docker", 3), ("ci", 2), ("배포", 3), ("인프라", 3),
        ("cd", 2), ("쿠버네티스", 3),
    ],
    "ceo": [
        ("계획", 3), ("우선순위", 3), ("로드맵", 3), ("전략", 3),
    ],
}

# 복합 요청 키워드
COMPLEX_KEYWORDS: list[str] = [
    "기능 만들어", "전부", "시스템 구축", "프로젝트 셋업",
    "처음부터", "풀스택", "관리 기능",
]

# 질문 키워드
QUESTION_KEYWORDS: list[str] = [
    "뭐야", "뭔가요", "알려줘", "설명해", "어떻게 되",
    "무엇", "진행 상황", "현재 상태", "왜 그런",
]

# 카테고리 매핑
CATEGORY_MAP: dict[str, str] = {
    "be-developer": "implementation",
    "fe-developer": "implementation",
    "cto": "tech-decision",
    "researcher": "research",
    "qa-engineer": "test",
    "infra-engineer": "infra",
    "ceo": "strategy",
}


def get_agent_keywords() -> dict[str, list[tuple[str, int]]]:
    return AGENT_KEYWORDS


def get_complex_keywords() -> list[str]:
    return COMPLEX_KEYWORDS


def get_question_keywords() -> list[str]:
    return QUESTION_KEYWORDS


def get_category_map() -> dict[str, str]:
    return CATEGORY_MAP
