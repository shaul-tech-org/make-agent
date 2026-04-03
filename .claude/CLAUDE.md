# make-agent

Claude Code의 .claude 설정을 UI를 통해 생성하고, 설정, 관리할 수 있는 웹 애플리케이션.
**모든 요청은 Coordinator를 경유하여 적절한 에이전트에게 자동 라우팅된다.**

## 기술 스택

| 항목 | 기술 |
|------|------|
| 백엔드 | Python + FastAPI |
| 프론트엔드 | TypeScript + React |
| DB | PostgreSQL 18, Redis 8 |
| 인프라 | Docker + GitHub Actions |
| 아키텍처 | 모듈러 모놀리스 |

## 요청 Flow

```
사용자 요청
    ↓
[1] Coordinator: 분류 + 복잡도 판단
    ↓
    ├── 단순 (1개 에이전트) → 바로 에이전트 호출 → 결과 보고
    │
    ├── 복합 (다수 에이전트) → CEO에게 위임
    │     ↓
    │   [2] CEO: 큰 단위 분해 (기능별)
    │     ↓
    │     ├── 기술 작업 → CTO에게 위임
    │     │     ↓
    │     │   [3] CTO: 기술 세부 분해 (개발자 착수 가능 수준)
    │     │     ↓
    │     │   [4] 개발자/QA/인프라 호출 (의존성 순서, 병렬)
    │     │     ↓
    │     │   결과 수집 → CEO에게 보고
    │     │
    │     ├── 리서치 → researcher 직접 호출
    │     └── 전략 → CEO가 직접 판단
    │     ↓
    │   결과 종합 → 사용자 보고
    │
    └── 단순 질문 → 직접 응답
```

## 조직도

```
사용자 (보드)
  └── Coordinator (sonnet) — 자동 라우팅
        └── CEO (opus) — 전략, 위임
              ├── CTO (opus) — 기술 결정, 리뷰
              │     ├── be-developer (sonnet) — Python/FastAPI
              │     ├── fe-developer (sonnet) — React/TypeScript
              │     ├── qa-engineer (sonnet) — 테스트
              │     └── infra-engineer (sonnet) — Docker/CI
              └── researcher (sonnet) — 리서치
```

## 에이전트

| 에이전트 | Model | 역할 | 위임 |
|---------|-------|------|------|
| coordinator | sonnet | 요청 접수 + 라우팅 | 자동 |
| ceo | opus | 전략, 복합 분해 | ✅ |
| cto | opus | 기술 결정, 리뷰 | ✅ |
| be-developer | sonnet | FastAPI 백엔드 | ❌ |
| fe-developer | sonnet | React 프론트 | ❌ |
| qa-engineer | sonnet | 테스트, 품질 | ❌ |
| researcher | sonnet | 리서치, 분석 | ❌ |
| infra-engineer | sonnet | Docker, CI/CD | ❌ |

## 스킬

| 스킬 | 유형 | 설명 |
|------|------|------|
| /project-context | 기반 | 프로젝트 컨텍스트 + 공통 원칙 (모든 스킬의 기반) |
| /setup-project | 설정 | 프로젝트 초기 설정 + 컨텍스트 수집 |
| /request | 명령 | Coordinator 자동 라우팅 |
| /decompose | 명령 | 복합 요청 분해 + 의존성 분석 |
| /plane-heartbeat | 명령 | Plane 기반 Heartbeat 프로토콜 |
| /plane-delegate | 명령 | 작업 위임 (sub-issue + 할당) |
| /python-feature | 명령 | Python 기능 개발 |
| /python-module | 명령 | FastAPI 모듈 scaffold 생성 |
| /python-test | 명령 | Python 테스트 |
| /typescript-feature | 명령 | TypeScript 기능 개발 |

### 스킬 파이프라인

모든 명령 스킬은 `/project-context` 기반 스킬을 전제조건으로 참조한다.

```
/project-context (기반)
    ↑ MANDATORY PREPARATION
    │
    ├── /request → /decompose → /plane-delegate
    ├── /plane-heartbeat
    ├── /python-module → /python-feature → /python-test
    └── /typescript-feature
```

## 규칙

| 디렉토리 | 내용 | 로딩 |
|---------|------|------|
| rules/common/ | Heartbeat, 위임 | `**/*.py`, `**/*.ts` |
| rules/governance/ | 조직도, 승인 | 항상 |
| rules/communication/ | 코멘트 프로토콜 | `**/*.py`, `**/*.ts` |
| rules/backend/python/ | Python, FastAPI | `**/*.py` |
| rules/frontend/typescript/ | TypeScript, React | `**/*.ts` |
| rules/infra/ | Docker, CI | Dockerfile 등 |
| rules/architecture/ | 모듈러 모놀리스 | 아키텍처 관련 |
