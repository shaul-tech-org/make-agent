---
name: request
description: "사용자 요청을 Coordinator가 분석하여 적절한 에이전트에게 자동 라우팅. 모든 요청의 진입점."
user-invocable: true
argument-hint: "[요청 내용]"
---

# /request — Coordinator 요청 라우팅

사용자의 모든 요청을 Coordinator가 접수하여 분석 → 라우팅 → 실행 → 보고한다.

## 필수 전제조건

/project-context를 참조하라 — 조직 구조, 에이전트 역량, Plane 워크플로우 포함.

→ *Consult [routing-rules](reference/routing-rules.md) for detailed agent selection criteria.*

## Flow

### 1. 요청 분류

사용자 요청을 분석하여 분류한다:
- **유형**: 구현 / 기술결정 / 리서치 / QA / 전략 / 단순질문
- **복잡도**: 단일 에이전트 / 다수 에이전트 / CEO 조율 필요
- **긴급도**: 즉시 / 계획적

### 2. 라우팅 결정

| 키워드 | 에이전트 |
|--------|---------|
| 만들어, 구현, 수정, 버그, API, DB, 마이그레이션 | be-developer |
| UI, 프론트, 디자인, 컴포넌트, CSS, 레이아웃 | fe-developer |
| 아키텍처, 기술 선택, 리뷰, 스택 | cto |
| 조사, 분석, 비교, 리서치, 트렌드 | researcher |
| 테스트, QA, 검증, 품질 | qa-engineer |
| 계획, 우선순위, 로드맵, 전략 | ceo |
| 풀스택, 복합, 여러 팀 | ceo (분해 후 위임) |
| 설명, 뭐야, 알려줘 (단순) | 직접 응답 (라우팅 생략) |

### 3. 에이전트 호출

```
Agent(
  prompt: "요청: {사용자 요청}\n컨텍스트: {프로젝트 상황}",
  subagent_type: "{선택된 에이전트}",
  model: "{에이전트 모델}"
)
```

### 4. Plane 이슈 연동

복잡한 작업 시:
1. Plane 이슈 생성 (부모)
2. Sub-issue 분해
3. 에이전트별 할당
4. 각 에이전트가 /plane-heartbeat 프로토콜로 실행
5. 완료 시 부모 이슈 업데이트

### 5. 결과 보고

에이전트 실행 결과를 사용자에게 간결하게 보고.
