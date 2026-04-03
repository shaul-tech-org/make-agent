# 조직도 — 명령 체계

## 계층 구조

```
사용자 (보드)
  └── Coordinator (sonnet) — 모든 요청 접수 + 자동 라우팅
        └── CEO (opus) — 전략, 복합 작업 분해
              ├── CTO (opus) — 기술 결정, 리뷰
              │     ├── be-developer (sonnet) — Python/FastAPI 백엔드
              │     ├── fe-developer (sonnet) — React/TypeScript 프론트
              │     ├── qa-engineer (sonnet) — 테스트, 품질
              │     └── infra-engineer (sonnet) — Docker, CI/CD
              └── researcher (sonnet) — 리서치, 분석
```

## 보고 라인 (reportsTo)

| 에이전트 | 상급자 | 역할 |
|---------|--------|------|
| coordinator | 사용자 | 요청 접수, 라우팅 |
| ceo | coordinator | 전략, 위임, 조율 |
| cto | ceo | 기술 결정, 리뷰 |
| be-developer | cto | Python/FastAPI 구현 |
| fe-developer | cto | React/TypeScript 구현 |
| qa-engineer | cto | 테스트, 품질 |
| infra-engineer | cto | Docker, CI/CD, 배포 |
| researcher | ceo | 리서치, 분석 |

## 원칙

- Coordinator: 모든 요청의 진입점, 라우팅만
- CEO/CTO: 위임만, 직접 구현 금지
- Developer/QA/Researcher/Infra: 직접 실행
- 불명확한 작업은 항상 상위로 에스컬레이션
