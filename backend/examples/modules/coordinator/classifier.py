"""Classifier 인터페이스 + KeywordClassifier 구현

향후 LLMClassifier로 교체 가능한 구조.
"""

from typing import Protocol

from app.modules.coordinator.repository import (
    get_agent_keywords,
    get_category_map,
    get_complex_keywords,
    get_question_keywords,
)

# 행위 오버라이드: 대상과 무관하게 행위가 에이전트를 결정하는 키워드
# 예: "API 배포" → 대상은 API(be-developer)지만, 행위는 배포(infra-engineer)
ACTION_OVERRIDES: dict[str, str] = {
    "배포": "infra-engineer",
    "테스트": "qa-engineer",
    "검증": "qa-engineer",
    "e2e": "qa-engineer",
    "조사": "researcher",
    "비교": "researcher",
    "리서치": "researcher",
}


class ClassifyResult:
    """분류 결과"""
    def __init__(self, category: str, complexity: str, agent: str):
        self.category = category
        self.complexity = complexity
        self.agent = agent


class Classifier(Protocol):
    """Classifier 인터페이스 — 키워드/LLM 교체 가능"""

    def classify(self, text: str) -> ClassifyResult:
        """요청 텍스트를 분류하여 category, complexity, agent를 결정"""
        ...


class KeywordClassifier:
    """키워드 기반 분류기

    2단계 분류:
      Step 1: category 결정 (유형 분류)
      Step 2: complexity 판단 (단순/복합/질문)
      → agent 결정
    """

    def __init__(self):
        self._agent_keywords = get_agent_keywords()
        self._complex_keywords = get_complex_keywords()
        self._question_keywords = get_question_keywords()
        self._category_map = get_category_map()

    def classify(self, text: str) -> ClassifyResult:
        text_lower = text.lower()

        # Step 1: 질문 판별 (최우선)
        if self._is_question(text_lower):
            return ClassifyResult(
                category="question",
                complexity="question",
                agent="direct",
            )

        # Step 2: 복합 판별
        if self._is_complex(text_lower):
            return ClassifyResult(
                category="complex",
                complexity="complex",
                agent="ceo",
            )

        # Step 3: 행위 오버라이드 체크 → 에이전트 매칭
        agent = self._check_action_override(text_lower) or self._match_agent(text_lower)
        category = self._category_map.get(agent, "unknown")

        return ClassifyResult(
            category=category,
            complexity="simple",
            agent=agent,
        )

    def _is_question(self, text: str) -> bool:
        """질문 키워드 포함 + 구현성 키워드 미포함"""
        has_question = any(kw in text for kw in self._question_keywords)
        if not has_question:
            return False

        # 구현성 키워드가 있으면 질문이 아님
        action_keywords = ["만들어", "구현", "작성", "추가", "수정", "삭제", "배포"]
        has_action = any(kw in text for kw in action_keywords)
        return not has_action

    def _is_complex(self, text: str) -> bool:
        """복합 키워드 또는 3개 이상 에이전트 영역 매칭"""
        if any(kw in text for kw in self._complex_keywords):
            return True

        matched_agents = set()
        for agent, keywords in self._agent_keywords.items():
            if any(kw in text for kw, _ in keywords):
                matched_agents.add(agent)
        return len(matched_agents) >= 3

    def _check_action_override(self, text: str) -> str | None:
        """행위 키워드 오버라이드 — 대상보다 행위가 에이전트를 결정"""
        for keyword, agent in ACTION_OVERRIDES.items():
            if keyword in text:
                return agent
        return None

    def _match_agent(self, text: str) -> str:
        """가중치 기반 에이전트 매칭

        각 에이전트의 키워드 매칭 점수를 가중치 합산으로 계산.
        동점 시 더 구체적인(키워드 수가 적은) 에이전트 우선.
        """
        scores: dict[str, float] = {}
        for agent, keywords in self._agent_keywords.items():
            score = sum(weight for kw, weight in keywords if kw in text)
            if score > 0:
                scores[agent] = score

        if not scores:
            return "ceo"

        max_score = max(scores.values())
        tied = [a for a, s in scores.items() if s == max_score]

        if len(tied) == 1:
            return tied[0]

        # 동점: 키워드 수가 적은(더 전문적인) 에이전트 우선
        return min(tied, key=lambda a: len(self._agent_keywords[a]))
