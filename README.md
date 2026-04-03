# make-agent

Claude Code의 .claude 설정을 UI를 통해 생성, 설정, 관리하는 웹 애플리케이션.

## 기술 스택

| 항목 | 기술 |
|------|------|
| 백엔드 | Python 3.12 + FastAPI |
| 프론트엔드 | TypeScript + React 19 + Tailwind CSS v4 |
| DB | PostgreSQL 18 + SQLAlchemy 2.0 + Alembic |
| 인프라 | Docker + GitHub Actions |

## 시작하기

### 1. 의존성 설치

```bash
make install
```

### 2. Docker (PostgreSQL)

```bash
docker compose up -d postgres
```

### 3. DB 마이그레이션

```bash
make migrate
```

### 4. 개발 서버

```bash
# 백엔드 (localhost:8000)
cd backend && .venv/bin/uvicorn app.main:app --reload

# 프론트엔드 (localhost:5173)
cd frontend && npm run dev
```

### 5. 테스트

```bash
make test
```

## 프로젝트 구조

```
.claude/              # 에이전트, 스킬, 규칙
backend/
├── app/
│   ├── core/         # 공통 인프라 (DB, 로깅, 에러, 보안, 메트릭)
│   ├── modules/      # 비즈니스 모듈 (자동 라우터 발견)
│   └── config.py
├── alembic/          # DB 마이그레이션
├── tests/
└── examples/         # 참고용 예제 모듈
frontend/
├── src/
│   ├── components/   # React 컴포넌트
│   └── api.ts        # API 클라이언트
└── ...
```

## 새 모듈 만들기

```bash
# Claude Code에서
/python-module user
```

자동 생성: SQLAlchemy 모델 + async CRUD + FastAPI router + Pydantic schemas + 커스텀 예외 + TDD 테스트

## 주요 명령어

```bash
make help       # 전체 명령어 목록
make test       # 테스트 실행
make lint       # 린트
make build      # Docker 빌드
make migrate    # DB 마이그레이션 적용
```

## 에이전트 구조

```
Coordinator (sonnet) → 자동 라우팅
  └── CEO (opus) → 전략, 위임
        ├── CTO (opus) → 기술 결정
        │     ├── be-developer (sonnet)
        │     ├── fe-developer (sonnet)
        │     ├── qa-engineer (sonnet)
        │     └── infra-engineer (sonnet)
        └── researcher (sonnet)
```
