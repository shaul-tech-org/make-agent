# 거버넌스 — 승인 규칙

## 사용자 확인 필수 사항

| 행동 | 승인 필요 | 방법 |
|------|----------|------|
| 새 에이전트 채용 (hire) | ✅ | AskUserQuestion → approve/reject |
| 프로젝트 방향 변경 | ✅ | AskUserQuestion |
| 파괴적 작업 (DB 삭제, 서비스 중단) | ✅ | AskUserQuestion |
| 프로덕션 배포 | ✅ | 사용자 확인 후 진행 |
| Sub-issue 생성/할당 | ❌ | 자율 진행 |
| 코멘트 작성 | ❌ | 자율 진행 |
| 상태 변경 | ❌ | 자율 진행 |

## 에이전트 채용 (Agent Hire) 프로세스

작업에 적합한 에이전트가 없을 때:

```
1. 필요성 식별 (CEO/CTO가 판단)
   → "이 작업에 ml-engineer가 필요하다"

2. 제안 (propose) — pending 상태
   → 이름, 설명, 모델, 스킬 정의
   → AskUserQuestion으로 승인 요청

3a. 승인 (approve) → active 상태
    → 에이전트 레지스트리에 등록
    → coordinator 라우팅 테이블에 추가
    → 작업 할당 가능

3b. 거절 (reject) → rejected 상태
    → 거절 사유 기록
    → 기존 에이전트로 대체 방안 모색
```

### 제안 시 필수 정보

| 항목 | 설명 | 예시 |
|------|------|------|
| name | 에이전트 식별자 (영문 소문자) | `ml-engineer` |
| description | 역할 설명 | "머신러닝 모델 개발 및 배포" |
| model | LLM 모델 | `sonnet` / `opus` |
| skills | 핵심 스킬 목록 | `["pytorch", "mlops"]` |

### 승인 권한

- **사용자(보드)**: 모든 에이전트 승인/거절 가능
- **CEO**: 제안만 가능, 승인은 사용자에게 요청

## 에스컬레이션 경로

```
Developer → CTO → CEO → 사용자(보드)
```

- Developer가 막히면 → CTO에게 코멘트로 보고
- CTO가 판단 불가 → CEO에게 에스컬레이션
- CEO가 결정 불가 → 사용자에게 AskUserQuestion
- 에이전트 부족 → CEO가 hire 제안 → 사용자 승인
