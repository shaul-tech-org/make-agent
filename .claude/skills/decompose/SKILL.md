---
name: decompose
description: "복합 요청을 세부 작업으로 분해한다. 작업 목록 + 의존성 + 에이전트 할당 + Plane sub-issue 생성."
user-invocable: true
argument-hint: "[복합 요청 내용]"
---

# /decompose — 요청 분해

복합 요청을 독립 실행 가능한 세부 작업으로 분해한다.

## 필수 전제조건

/project-context를 참조하라 — 에이전트 역량, 스킬 스코프 포함.

→ *Consult [dependency-patterns](reference/dependency-patterns.md) for dependency analysis rules.*
→ *Consult [sizing-guide](reference/sizing-guide.md) for task sizing criteria.*

## 입력

사용자의 원본 요청 (복합 요청)

## 분해 프로세스

### 1. 목표 파악

요청에서 최종 목표를 추출한다:
- 무엇을 만들어야 하는가?
- 어떤 기술 영역이 필요한가?
- 완료 기준은?

### 2. 작업 분해

목표를 달성하기 위한 작업 단위를 나열한다.
각 작업은:
- **독립 실행 가능** (다른 작업 없이 시작 가능하거나, 선행 작업만 완료되면 시작 가능)
- **단일 에이전트 할당** (한 에이전트가 완료 가능한 크기)
- **검증 가능** (완료 여부를 판단할 수 있는 기준)

### 3. 출력 형식

```markdown
## 분해 결과

### 요청: "{원본 요청}"
### 목표: {최종 목표 한 줄}

| # | 작업 | 담당 | 의존성 | 우선순위 |
|---|------|------|--------|---------|
| 1 | {작업 제목} | {에이전트} | 없음 | high |
| 2 | {작업 제목} | {에이전트} | Task 1 | high |
| 3 | {작업 제목} | {에이전트} | Task 1 | high |
| 4 | {작업 제목} | {에이전트} | Task 2 | medium |
| 5 | {작업 제목} | {에이전트} | Task 3 | medium |
| 6 | {작업 제목} | {에이전트} | Task 4,5 | medium |

### 실행 순서
```
Phase 1 (병렬 없음): Task 1
Phase 2 (병렬): Task 2 // Task 3
Phase 3 (병렬): Task 4 // Task 5
Phase 4: Task 6
```

### 예상 에이전트 호출
- be-developer: Task 1, 2, 3
- fe-developer: Task 4, 5
- qa-engineer: Task 6
```

### 4. 에이전트 매핑

| 작업 키워드 | 에이전트 |
|-----------|---------|
| DB, 스키마, 마이그레이션, 모델 | be-developer |
| API, 엔드포인트, 서비스, 서버 로직 | be-developer |
| UI, 페이지, 컴포넌트, 스타일 | fe-developer |
| 아키텍처, 기술 결정, 설계 | cto |
| 테스트, 검증, QA, E2E | qa-engineer |
| 조사, 리서치, 비교, 분석 | researcher |
| Docker, CI/CD, 배포, 인프라 | infra-engineer |

### 5. 의존성 규칙

- DB/스키마 → API → UI → 테스트 (일반적 순서)
- 설계/기술 결정 → 구현 (설계가 먼저)
- 리서치 → 설계 (조사 후 설계)
- 같은 에이전트의 독립 작업은 병렬 가능
- 다른 에이전트의 독립 작업은 항상 병렬 가능

### 6. Plane 이슈 생성

분해 결과를 Plane sub-issue로 생성:

```bash
source scripts/plane-api.sh

for each task:
  plane_create_sub_issue "$PROJECT_ID" "$PARENT_ISSUE_ID" \
    "[Task] {작업 제목}" \
    "<p><strong>목표:</strong> {작업 목표}<br/><strong>담당:</strong> {에이전트}<br/><strong>의존성:</strong> {선행 작업}<br/><strong>완료 기준:</strong> {어떻게 되면 완료}</p>" \
    "{우선순위}" \
    "$TODO_STATE"
```

### 7. 사용자 확인

작업이 5개 이상이면 분해 결과를 사용자에게 보여주고 확인:
- "이 분해 결과로 진행할까요?"
- 수정/추가/삭제 가능

## 예시

### 입력
"사용자 관리 기능 만들어줘"

### 출력
```
| # | 작업 | 담당 | 의존성 |
|---|------|------|--------|
| 1 | users 테이블 마이그레이션 | be-developer | 없음 |
| 2 | 회원가입 API (POST /api/v1/auth/register) | be-developer | 1 |
| 3 | 로그인 API (POST /api/v1/auth/login) | be-developer | 1 |
| 4 | 프로필 API (GET/PUT /api/v1/users/me) | be-developer | 1 |
| 5 | 회원가입/로그인 페이지 | fe-developer | 2,3 |
| 6 | 프로필 페이지 | fe-developer | 4 |
| 7 | Auth API 테스트 | qa-engineer | 2,3,4 |
| 8 | E2E 테스트 (가입→로그인→프로필) | qa-engineer | 5,6 |

Phase 1: Task 1
Phase 2: Task 2 // 3 // 4
Phase 3: Task 5 // 6
Phase 4: Task 7 // 8
```
