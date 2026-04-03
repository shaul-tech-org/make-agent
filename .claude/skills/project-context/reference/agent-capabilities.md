# 에이전트별 역량 상세

## Coordinator (sonnet)

- **역할**: 모든 요청의 진입점, 분류 + 라우팅
- **스킬**: /request
- **판단 기준**: 키워드 매칭 + 복잡도 판단
- **위임**: 단순 → 직접 에이전트 호출, 복합 → CEO

## CEO (opus)

- **역할**: 전략 수립, 복합 작업 분해, 에이전트 조율
- **스킬**: /decompose, /plane-delegate, /plane-heartbeat
- **핵심**: 절대 직접 코드 작성하지 않음
- **분해 기준**: 독립 실행 가능, 단일 에이전트 할당, 검증 가능

## CTO (opus)

- **역할**: 기술 결정, 아키텍처 리뷰, 코드 품질 판단
- **스킬**: /decompose, /plane-delegate, /plane-heartbeat
- **핵심**: 기술 세부 분해 (개발자 착수 가능 수준)
- **판단 영역**: 기술 스택, 아키텍처 패턴, 성능 최적화

## be-developer (sonnet)

- **역할**: Python/FastAPI 백엔드 구현
- **스킬**: /python-module, /python-feature, /python-test, /plane-heartbeat
- **기술**: Python, FastAPI, SQLAlchemy, pytest, Pydantic
- **구조**: router/service/repository + schemas(requests/responses)

## fe-developer (sonnet)

- **역할**: React/TypeScript 프론트엔드 구현
- **스킬**: /typescript-feature, /plane-heartbeat
- **기술**: TypeScript, React, Vite, CSS/Tailwind
- **구조**: components, hooks, api client

## qa-engineer (sonnet)

- **역할**: 테스트 작성, 코드 구조 검증, 품질 보증
- **스킬**: /python-test, /plane-heartbeat
- **기술**: pytest, Playwright, httpx
- **검증**: 12항목 체크리스트 (레이어, 테스트, 네이밍)

## infra-engineer (sonnet)

- **역할**: Docker, CI/CD, 배포, 인프라 관리
- **스킬**: /plane-heartbeat
- **기술**: Docker, Docker Compose, GitHub Actions, Caddy

## researcher (sonnet)

- **역할**: 기술 리서치, 비교 분석, 트렌드 조사
- **스킬**: /plane-heartbeat
- **산출물**: 리서치 보고서, 기술 비교표, 의사결정 근거
