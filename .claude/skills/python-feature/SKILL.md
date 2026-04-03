---
name: python-feature
description: "Python 기능 개발. 모듈 구조, 타입 힌팅, 테스트 포함."
user-invocable: true
argument-hint: "[기능 설명]"
---

# Python Feature Development

## 필수 전제조건

/project-context를 참조하라 — 공통 원칙, TDD 규칙 포함.
/plane-heartbeat Step 1~3을 완료했는가? 이슈 없이 작업을 시작하지 마라.

> **CRITICAL**: 새 모듈이 필요하면 /python-module을 먼저 실행하라.

## 다음 단계

구현 완료 후 → /python-test로 테스트 작성 → qa-engineer 검증

## 워크플로우

1. 요구사항 확인
2. TDD — pytest fixture 기반
3. 구현 — 타입 힌팅 필수
4. `ruff check` + `pytest` 통과

## 구조
```
src/
  __init__.py
  main.py
  config.py
  services/
  models/
tests/
  conftest.py
  test_*.py
```
