---
name: typescript-feature
description: "TypeScript 기능 개발. 컴포넌트, 타입 안전성, 테스트 포함."
user-invocable: true
argument-hint: "[기능 설명]"
---

# TypeScript Feature Development

## 필수 전제조건

/project-context를 참조하라 — 공통 원칙, TDD 규칙 포함.
/plane-heartbeat Step 1~3을 완료했는가? 이슈 없이 작업을 시작하지 마라.

## 다음 단계

구현 완료 후 → qa-engineer 검증 요청

## 워크플로우

1. 요구사항 확인
2. 타입 정의 먼저 (interface/type)
3. TDD — Jest 또는 Vitest
4. 구현 — strict 모드 필수
5. `tsc --noEmit` + 테스트 통과

## 규칙
- `any` 사용 금지
- async/await 사용 (.then 지양)
- 유틸리티 타입 활용: Partial, Pick, Omit
