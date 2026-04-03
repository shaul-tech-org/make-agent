---
paths:
  - "**/*.tsx"
  - "**/*.ts"
  - "**/package.json"
---

# React 규칙

## 구조
```
src/
├── components/    # 재사용 컴포넌트
├── pages/         # 페이지 컴포넌트
├── hooks/         # 커스텀 훅
├── api/           # API 클라이언트
├── context/       # React Context
├── types/         # TypeScript 타입
└── utils/         # 유틸리티
```

## 패턴
- 함수형 컴포넌트 + Hooks
- Custom Hooks으로 로직 분리
- Props: TypeScript interface 정의
- 상태: useState (로컬) / Context (글로벌) / TanStack Query (서버)

## 테스트
- Vitest + React Testing Library
- 컴포넌트 단위 테스트
