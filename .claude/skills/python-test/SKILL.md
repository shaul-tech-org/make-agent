---
name: python-test
description: "Python 테스트 작성 및 실행. pytest, fixture, mock 포함."
user-invocable: true
argument-hint: "[테스트 대상 모듈/기능]"
---

# Python Test

## 필수 전제조건

/project-context를 참조하라 — TDD 원칙, 레이어 분리 규칙 포함.

> **CRITICAL**: 테스트 대상 코드가 존재하는지 먼저 확인하라. 없으면 /python-feature 먼저 실행.

## 실행
```bash
pytest                          # 전체
pytest tests/test_service.py    # 특정 파일
pytest -k "test_create"         # 특정 테스트
pytest --cov=src                # 커버리지
```

## 패턴
- pytest fixture 기반 setup
- conftest.py에 공유 fixture
- mock: pytest-mock 또는 unittest.mock
- 파라미터화: @pytest.mark.parametrize
