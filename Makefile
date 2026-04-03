.PHONY: help dev test lint build up down migrate

help: ## 도움말
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# === 개발 ===

dev: ## 개발 서버 실행 (백엔드 + 프론트엔드)
	@echo "Starting backend..."
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev &
	@wait

# === 테스트 ===

test: ## 전체 테스트 (백엔드 + 프론트엔드)
	cd backend && .venv/bin/python -m pytest -v
	cd frontend && npm run test

test-be: ## 백엔드 테스트
	cd backend && .venv/bin/python -m pytest -v

test-fe: ## 프론트엔드 테스트
	cd frontend && npm run test

# === 코드 품질 ===

lint: ## 린트 (ruff)
	cd backend && .venv/bin/ruff check .

format: ## 포맷 (ruff)
	cd backend && .venv/bin/ruff format .

typecheck: ## 타입 체크
	cd backend && .venv/bin/mypy app/
	cd frontend && npx tsc --noEmit

# === 빌드 / 인프라 ===

build: ## Docker 이미지 빌드
	docker compose build

up: ## Docker Compose 시작
	docker compose up -d

down: ## Docker Compose 중지
	docker compose down

# === 데이터베이스 ===

migrate: ## Alembic 마이그레이션 적용
	cd backend && .venv/bin/alembic upgrade head

migrate-gen: ## Alembic 마이그레이션 생성 (message 필요)
	@read -p "Migration message: " msg; \
	cd backend && .venv/bin/alembic revision --autogenerate -m "$$msg"

# === 설치 ===

install: ## 의존성 설치 (백엔드 + 프론트엔드)
	cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
	cd frontend && npm install
