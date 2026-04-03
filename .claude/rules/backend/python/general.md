---
paths:
  - "**/*.py"
  - "**/requirements.txt"
  - "**/pyproject.toml"
---

# Python 공통 규칙

## 코딩 표준
- PEP 8 준수 (black 또는 ruff 포맷터)
- Type hints 필수 (파라미터, 반환 타입)
- docstring: Google 스타일 또는 NumPy 스타일
- f-string 사용 (.format() 금지)

## 네이밍
- 함수/변수: snake_case
- 클래스: PascalCase
- 상수: SCREAMING_SNAKE_CASE
- 비공개: _underscore_prefix

## 구조
- 패키지: __init__.py
- 진입점: if __name__ == "__main__"
- 설정: .env + python-dotenv 또는 pydantic-settings
- 의존성: requirements.txt 또는 pyproject.toml

## 에러 핸들링
- 구체적 예외 catch (bare except 금지)
- 커스텀 예외 클래스 정의
- 로깅: logging 모듈 사용 (print 디버깅 금지)

## 테스트
- pytest 사용
- fixture 기반 setup
- mock: unittest.mock 또는 pytest-mock
- 커버리지: pytest-cov

## 보안
- 사용자 입력 검증 (pydantic 권장)
- SQL: ORM 또는 parameterized query
- secrets: 환경변수 사용 (하드코딩 금지)
- subprocess: shell=True 금지
