---
paths:
  - "**/*.py"
  - "**/requirements.txt"
  - "**/pyproject.toml"
---

# FastAPI 규칙

## 모듈 기본 구조

모든 모듈은 최소한 다음 레이어를 분리한다:

```
app/modules/{모듈}/
├── router.py              # Controller — HTTP 라우팅만
├── service.py             # Service — 비즈니스 로직
├── repository.py          # Repository — 데이터 접근
├── schemas/
│   ├── __init__.py        # 재export
│   ├── requests.py        # 요청 DTO (CreateRequest, UpdateRequest)
│   └── responses.py       # 응답 DTO (Response)
└── __init__.py
```

- **router.py**: HTTP 요청/응답 처리만. 비즈니스 로직은 service에 위임.
- **service.py**: 비즈니스 규칙 구현. repository를 통해 데이터 접근.
- **repository.py**: 데이터 저장소 접근만. SQL/NoSQL/in-memory 추상화.
- **schemas/requests.py**: 클라이언트 → 서버 요청 스키마.
- **schemas/responses.py**: 서버 → 클라이언트 응답 스키마.

## 복잡도 기반 구조 확장 제안

모듈이나 프로젝트가 아래 기준에 도달하면 구조 확장을 **제안**한다:

### 모듈 레벨

| 기준 | 추가 파일 | 이유 |
|------|----------|------|
| 엔드포인트 5개 이상 | `exceptions.py` | 모듈 전용 예외 분리 (예: `TodoNotFoundException`) |
| 엔드포인트 5개 이상 | `dependencies.py` | FastAPI `Depends()` DI 분리 (service 주입) |
| DB 연동 시 | `models.py` | SQLAlchemy 엔티티 정의 |
| 복잡한 비즈니스 로직 | `validators.py` | 입력값 유효성 검증 로직 분리 |

### 프로젝트 레벨

| 기준 | 추가 구조 | 이유 |
|------|----------|------|
| 모듈 2개 이상 | `app/core/` (exceptions, dependencies, database) | 공통 레이어 도입 |
| DB 연동 시 | `alembic/`, `alembic.ini` | 마이그레이션 관리 |
| 테스트 15개 이상 | `tests/unit/`, `tests/integration/` | 테스트 디렉토리 분리 |
| 환경 분리 필요 | `.env.example` | 환경변수 템플릿 |
| 미들웨어 2개 이상 | `app/middleware/` | 전역 미들웨어 분리 |

> **원칙**: 현재 불필요한 구조는 추가하지 않는다. 기준에 도달했을 때 제안만 하고, 사용자 확인 후 추가한다.

## API 패턴

- Router: `APIRouter(prefix="/api/v1/{모듈}")`
- 의존성 주입: `Depends()`
- 입력 검증: Pydantic BaseModel
- 응답: `JSONResponse` 또는 Pydantic 모델

## DB

- SQLAlchemy 2.0 async (PostgreSQL)
- Alembic 마이그레이션
- Motor (MongoDB async)
- aioredis (Redis async)

## 테스트

- pytest + httpx (AsyncClient)
- pytest-asyncio
- TDD: Red → Green → Refactor
