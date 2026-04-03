# 조직도 상세

## 계층 구조

```
사용자 (보드) — 최종 의사결정권
  └── Coordinator (sonnet) — 진입점
        └── CEO (opus) — 전략 + 위임
              ├── CTO (opus) — 기술 결정
              │     ├── be-developer (sonnet) — 백엔드
              │     ├── fe-developer (sonnet) — 프론트
              │     ├── qa-engineer (sonnet) — 품질
              │     └── infra-engineer (sonnet) — 인프라
              └── researcher (sonnet) — 리서치
```

## 보고 라인

| 에이전트 | 상급자 | 에스컬레이션 대상 |
|---------|--------|-----------------|
| coordinator | 사용자 | 사용자 |
| ceo | coordinator | 사용자 |
| cto | ceo | ceo |
| be-developer | cto | cto |
| fe-developer | cto | cto |
| qa-engineer | cto | cto |
| infra-engineer | cto | cto |
| researcher | ceo | ceo |

## 에스컬레이션 경로

```
Developer → CTO → CEO → 사용자(보드)
```

## 원칙

- Coordinator: 라우팅만, 구현 금지
- CEO/CTO: 위임만, 직접 구현 금지
- Developer/QA/Researcher/Infra: 직접 실행
- 에이전트 부족 시: CEO가 hire 제안 → 사용자 승인
