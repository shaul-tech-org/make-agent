---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/tsconfig.json"
---

# TypeScript 공통 규칙

## 코딩 표준
- strict 모드 필수 (`"strict": true`)
- `any` 사용 금지 (정당한 이유 없이)
- union type 또는 제네릭으로 타입 안전성 확보
- `as` 타입 캐스팅 최소화

## 네이밍
- 변수/함수: camelCase
- 클래스/인터페이스/타입: PascalCase
- 상수: SCREAMING_SNAKE_CASE
- 파일: camelCase.ts 또는 kebab-case.ts (프로젝트 컨벤션 따름)

## 인터페이스 & 타입
- 객체 shape: `interface` 사용
- 유니온/교차: `type` 사용
- API 응답 타입은 별도 파일로 분리
- `Partial<T>`, `Pick<T>`, `Omit<T>` 유틸리티 타입 활용

## 비동기
- async/await 사용 (.then 체인 지양)
- Promise 에러는 try-catch로 처리
- 병렬 가능한 작업은 `Promise.all()` 사용

## 테스트
- Jest 또는 Vitest
- 타입 테스트: `expectTypeOf` 활용
- mock: 인터페이스 기반
