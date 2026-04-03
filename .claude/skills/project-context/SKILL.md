---
name: project-context
description: "프로젝트 컨텍스트 및 공통 원칙. 모든 에이전트 작업의 기반 스킬."
---

# 프로젝트 컨텍스트 — 기반 스킬

모든 에이전트가 작업 수행 전 참조하는 공통 컨텍스트와 원칙.

## 조직 구조

→ *Consult [org-chart](reference/org-chart.md) for the full hierarchy and reporting lines.*

```
사용자 (보드)
  └── Coordinator (sonnet) — 모든 요청 접수 + 자동 라우팅
        └── CEO (opus) — 전략, 복합 작업 분해
              ├── CTO (opus) — 기술 결정, 리뷰
              │     ├── be-developer (sonnet)
              │     ├── fe-developer (sonnet)
              │     ├── qa-engineer (sonnet)
              │     └── infra-engineer (sonnet)
              └── researcher (sonnet)
```

## 에이전트 역량

→ *Consult [agent-capabilities](reference/agent-capabilities.md) for detailed skill sets per agent.*

| 에이전트 | 핵심 역량 | 위임 가능 |
|---------|----------|----------|
| coordinator | 분류, 라우팅 | 자동 |
| ceo | 전략, 분해, 조율 | ✅ |
| cto | 기술 결정, 리뷰 | ✅ |
| be-developer | Python/FastAPI | ❌ |
| fe-developer | React/TypeScript | ❌ |
| qa-engineer | 테스트, 검증 | ❌ |
| infra-engineer | Docker, CI/CD | ❌ |
| researcher | 리서치, 분석 | ❌ |

## Plane 워크플로우

→ *Consult [plane-workflow](reference/plane-workflow.md) for API usage and state management.*

1. 모든 작업은 Plane 이슈로 추적
2. 작업 시작 → In Progress 상태 변경 + 시작 코멘트
3. 작업 완료 → Done 상태 변경 + 완료 코멘트
4. 블로커 발생 → 즉시 코멘트 + 상급자 에스컬레이션

## 공통 원칙

### DO (모든 에이전트 공통)

**DO**: 작업 시작 전 Plane 이슈를 확인하거나 생성한다
**DO**: 작업 상태를 실시간으로 업데이트한다 (In Progress → Done/Blocked)
**DO**: 블로커 발생 시 즉시 상급자에게 코멘트로 보고한다
**DO**: 모든 행동을 Plane 코멘트에 기록한다 (추적 가능성)
**DO**: TDD로 테스트를 먼저 작성한다 (Red → Green → Refactor)
**DO**: 레이어를 분리한다 (router/service/repository + schemas)

### DON'T (모든 에이전트 공통)

**DON'T**: 이슈 없이 작업을 시작한다
**DON'T**: CEO/CTO가 직접 코드를 작성한다 (위임만)
**DON'T**: 이슈 상태를 업데이트하지 않고 방치한다
**DON'T**: 블로커를 보고하지 않고 혼자 해결하려 한다
**DON'T**: 테스트 없이 커밋한다
**DON'T**: 다른 에이전트의 체크아웃된 작업을 수정한다

## 스킬 파이프라인

### 단순 요청
```
/request → coordinator 라우팅 → /plane-heartbeat → 작업 수행 → 결과 보고
```

### 복합 요청
```
/request → coordinator → CEO → /decompose → /plane-delegate
    → 각 에이전트: /plane-heartbeat → 작업 수행 → 결과 보고
    → CEO: 결과 수집 → 종합 보고
```

### Python 기능 개발
```
/plane-heartbeat → /python-module (신규 모듈 시) → /python-feature → /python-test → QA 검증
```

### TypeScript 기능 개발
```
/plane-heartbeat → /typescript-feature → QA 검증
```

## 에이전트별 스킬 스코프

| 스킬 | coordinator | ceo | cto | be-dev | fe-dev | qa | infra | researcher |
|------|:-----------:|:---:|:---:|:------:|:------:|:--:|:-----:|:----------:|
| /request | ● | - | - | - | - | - | - | - |
| /decompose | - | ● | ● | - | - | - | - | - |
| /plane-heartbeat | ● | ● | ● | ● | ● | ● | ● | ● |
| /plane-delegate | - | ● | ● | - | - | - | - | - |
| /python-module | - | - | - | ● | - | - | - | - |
| /python-feature | - | - | - | ● | - | - | - | - |
| /python-test | - | - | - | ● | - | ● | - | - |
| /typescript-feature | - | - | - | - | ● | - | - | - |
| /setup-project | ● | ● | - | - | - | - | - | - |
