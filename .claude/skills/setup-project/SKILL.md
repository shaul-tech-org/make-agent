---
name: setup-project
description: "프로젝트 초기 설정 — CLAUDE.md 생성, 환경 설정, Plane 연동, 기본 구조 검증"
user-invocable: true
---

# /setup-project — 프로젝트 초기 설정

새 프로젝트를 이 스켈레톤으로 시작할 때 **1회 실행**한다.
CLAUDE.md 템플릿을 기반으로 프로젝트 설정을 자동 생성한다.

## Step 1: 프로젝트 정보 수집

사용자에게 다음 정보를 질문한다 (AskUserQuestion):

| 항목 | 예시 | 필수 |
|------|------|------|
| 프로젝트명 | my-awesome-project | ✅ |
| 프로젝트 설명 | 이커머스 주문 관리 시스템 | ✅ |
| Plane 워크스페이스 | tech-org | ✅ |
| Plane 프로젝트 식별자 | SHOP | ✅ |

## Step 2: CLAUDE.md 생성

`.claude/CLAUDE.md.template`을 기반으로 CLAUDE.md를 자동 생성한다:

```
{{PROJECT_NAME}} → 프로젝트명
{{PROJECT_DESCRIPTION}} → 프로젝트 설명
{{PLANE_WORKSPACE}} → Plane 워크스페이스
{{PLANE_PROJECT_ID}} → Plane 프로젝트 식별자
```

생성 후 CLAUDE.md.template은 삭제하지 않는다 (참고용으로 유지).

## Step 3: docker-compose.yml 설정

프로젝트명 기반으로 DB 설정을 업데이트:

```yaml
POSTGRES_DB: {{project_name_snake}}
POSTGRES_USER: {{project_name_snake}}
POSTGRES_PASSWORD: {{project_name_snake}}_dev
```

`backend/app/config.py`의 `database_url` 기본값도 동일하게 업데이트.
`backend/alembic.ini`의 `sqlalchemy.url`도 동일하게 업데이트.

## Step 4: 환경 검증

| 항목 | 확인 방법 | 실패 시 |
|------|----------|---------|
| Python 버전 | `python3 --version` | pyproject.toml 요구사항과 비교 |
| Node 버전 | `node --version` | package.json engines 확인 |
| Docker | `docker compose version` | 설치 안내 |
| pip 의존성 | `.venv/bin/pip install -e ".[dev]"` | 에러 수정 |

## Step 5: Plane 연동 확인

Plane API 연동을 확인한다:

1. `.env`에서 `PLANE_API_KEY` 확인
2. 프로젝트 접근 테스트: `GET /api/v1/workspaces/{workspace}/projects/`
3. 상태 ID 매핑 (Backlog, Todo, In Progress, Done, Cancelled)

## Step 6: Phase 1 이슈 자동 생성

Plane에 Phase 1 이슈를 자동 생성한다:

```
[Phase 1] 인프라 준비
├── [Task] 프로젝트 초기 설정 완료
├── [Task] Docker + CI 기본 구성
├── [Task] 첫 번째 모듈 생성 (/python-module 사용)
└── [Task] TDD 테스트 작성
```

## Step 7: 결과 보고

```
## 프로젝트 설정 완료

| 항목 | 상태 |
|------|------|
| CLAUDE.md 생성 | ✅ |
| docker-compose 설정 | ✅ |
| 환경 검증 | ✅ / ⚠️ {문제} |
| Plane 연동 | ✅ |
| Phase 1 이슈 생성 | ✅ |

다음 단계: `/python-module {module_name}` 으로 첫 번째 모듈을 생성하세요.
```
