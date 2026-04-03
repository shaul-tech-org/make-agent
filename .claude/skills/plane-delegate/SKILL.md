---
name: plane-delegate
description: "Plane 기반 작업 위임. CEO/CTO가 sub-issue를 생성하고 담당 에이전트에게 할당."
user-invocable: true
argument-hint: "[위임할 작업 설명]"
---

# Plane Delegation

작업을 다른 에이전트에게 위임할 때 사용.

## 필수 전제조건

/project-context를 참조하라 — 에이전트 역량, 스킬 스코프, Plane 워크플로우 포함.

## 위임 절차

### 1. 작업 분석
- 요청을 읽고 필요한 작업 단위로 분해
- 각 단위가 독립적으로 실행/검증 가능한지 확인

### 2. Sub-Issue 생성

```bash
source scripts/plane-api.sh
PROJECT_ID="..."
PARENT_ID="..."
TODO=$(plane_get_state_id "$PROJECT_ID" "Todo")

plane_create_sub_issue "$PROJECT_ID" "$PARENT_ID" \
  "[Task] 작업 제목" \
  "<p><strong>목표:</strong> 무엇을 달성해야 하는지<br/><strong>컨텍스트:</strong> 왜 이 작업이 필요한지<br/><strong>기대 결과:</strong> 완료 기준</p>" \
  "medium" \
  "$TODO"
```

### 3. 코멘트로 컨텍스트 전달

위임 시 반드시 포함:
- **무엇을**: 구체적인 작업 내용
- **왜**: 이 작업이 필요한 이유
- **어떻게**: 접근 방법 제안 (강제는 아님)
- **완료 기준**: 어떤 상태가 되면 완료인지
- **참고**: 관련 파일, 이슈, 문서 링크

### 4. 라우팅 테이블

| 작업 유형 | 담당 | 이유 |
|----------|------|------|
| 백엔드 코드 | be-developer | API, DB, 서버 로직 |
| 프론트엔드 코드 | fe-developer | UI, 컴포넌트, CSS |
| 기술 결정 | cto | 아키텍처, 스택 선택 |
| 테스트/검증 | qa-engineer | 품질, E2E |
| 리서치/조사 | researcher | 분석, 비교, 보고서 |
| 전략/우선순위 | ceo | 비즈니스 판단 |

### 5. 추적

- 위임한 이슈의 진행 상황을 정기적으로 확인
- 블로커 발생 시 코멘트로 도움 또는 재할당
- 완료 시 상위 이슈도 업데이트
