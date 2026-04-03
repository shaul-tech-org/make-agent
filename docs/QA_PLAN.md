# QA 계획서: make-agent

## 1. 테스트 전략

### 테스트 피라미드

```
         ╱╲
        ╱ E2E ╲          Playwright (브라우저)
       ╱────────╲         5~10개 핵심 시나리오
      ╱ 통합 테스트 ╲      httpx AsyncClient
     ╱──────────────╲     모듈 간 상호작용
    ╱   단위 테스트    ╲    pytest + vitest
   ╱────────────────────╲  파서, 검증기, 컴포넌트
```

| 레벨 | 도구 | 대상 | 목표 커버리지 |
|------|------|------|-------------|
| 단위 (백엔드) | pytest + pytest-asyncio | 파서, 검증기, 서비스 | 80% |
| 단위 (프론트) | vitest + testing-library | 컴포넌트, hooks | 70% |
| 통합 | httpx AsyncClient | API 엔드포인트 | 전체 API |
| E2E | Playwright (post-MVP) | 핵심 유저 플로우 | 5~10 시나리오 |

### TDD 원칙
- 모든 기능은 **테스트 먼저** 작성 (RED → GREEN → REFACTOR)
- PR 시 테스트 없는 코드는 머지 불가
- CI에서 전체 테스트 통과 필수

## 2. 테스트 케이스 — 백엔드

### TC-1: 프로젝트 로딩 (FR-1)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-1.1 | 유효한 .claude 디렉토리 로딩 | 실제 .claude 경로 | 200, 프로젝트 데이터 반환 | P0 |
| TC-1.2 | .claude 없는 경로 | /tmp/empty | 400, 에러 메시지 | P0 |
| TC-1.3 | 존재하지 않는 경로 | /nonexistent | 400, 에러 메시지 | P0 |
| TC-1.4 | CLAUDE.md만 있는 최소 프로젝트 | CLAUDE.md만 | 200, 부분 데이터 | P0 |
| TC-1.5 | 깨진 YAML frontmatter | 잘못된 YAML | 200, 경고 포함 | P1 |
| TC-1.6 | 잘못된 JSON settings | 깨진 JSON | 200, 경고 포함 | P1 |

### TC-2: 에이전트 파싱/CRUD (FR-2)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-2.1 | 에이전트 목록 조회 | GET /agents | 200, 에이전트 배열 | P0 |
| TC-2.2 | 에이전트 상세 조회 | GET /agents/ceo | 200, frontmatter + body | P0 |
| TC-2.3 | 없는 에이전트 조회 | GET /agents/nonexistent | 404 | P0 |
| TC-2.4 | 에이전트 생성 | POST /agents {name, description, model, body} | 201, 파일 생성됨 | P0 |
| TC-2.5 | 필수 필드 누락 생성 | POST /agents {name만} | 422 | P0 |
| TC-2.6 | 중복 이름 생성 | POST /agents {기존 이름} | 409 | P0 |
| TC-2.7 | 에이전트 수정 | PUT /agents/ceo {description 변경} | 200, 파일 업데이트됨 | P0 |
| TC-2.8 | 에이전트 삭제 | DELETE /agents/ceo | 204, 파일 삭제됨 | P1 |
| TC-2.9 | frontmatter 파싱 정확성 | name, description, model, memory | 모든 필드 정확히 파싱 | P0 |
| TC-2.10 | 마크다운 body 보존 | 편집 후 저장 | frontmatter 외 내용 보존 | P0 |

### TC-3: 스킬 파싱/CRUD (FR-3)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-3.1 | 스킬 목록 조회 | GET /skills | 200, 스킬 배열 | P0 |
| TC-3.2 | 스킬 상세 조회 | GET /skills/decompose | 200, frontmatter + body + references | P0 |
| TC-3.3 | user-invocable 필터 | GET /skills?invocable=true | user-invocable만 반환 | P0 |
| TC-3.4 | 스킬 생성 | POST /skills {name, description, body} | 201, 디렉토리 + SKILL.md 생성 | P0 |
| TC-3.5 | 스킬 수정 | PUT /skills/decompose | 200, SKILL.md 업데이트 | P0 |
| TC-3.6 | reference 목록 조회 | GET /skills/decompose/references | 200, 파일명 배열 | P1 |
| TC-3.7 | reference 추가 | POST /skills/decompose/references | 201, 파일 생성 | P1 |
| TC-3.8 | argument-hint 파싱 | frontmatter에 argument-hint | 정확히 파싱 | P0 |

### TC-4: 규칙 파싱/CRUD (FR-4)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-4.1 | 규칙 목록 (카테고리별) | GET /rules | 200, 카테고리 그룹핑 | P0 |
| TC-4.2 | 규칙 상세 조회 | GET /rules/backend/python/general | 200, paths + body | P0 |
| TC-4.3 | 규칙 생성 | POST /rules {category, name, paths, body} | 201, 파일 생성 | P0 |
| TC-4.4 | 규칙 수정 | PUT /rules/backend/python/general | 200, 파일 업데이트 | P0 |
| TC-4.5 | glob 패턴 테스트 | POST /rules/test-glob {pattern, base_path} | 200, 매칭 파일 목록 | P1 |
| TC-4.6 | paths 없는 규칙 (항상 로드) | frontmatter에 paths 없음 | always_loaded: true | P0 |
| TC-4.7 | 새 카테고리 생성 | POST /rules {새 카테고리명} | 201, 디렉토리 생성 | P1 |

### TC-5: 설정 관리 (FR-5)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-5.1 | settings.json 조회 | GET /settings | 200, permissions 포함 | P0 |
| TC-5.2 | settings.json 수정 | PUT /settings {permissions 변경} | 200, 파일 업데이트 | P0 |
| TC-5.3 | CLAUDE.md 조회 | GET /claude-md | 200, content 문자열 | P0 |
| TC-5.4 | CLAUDE.md 수정 | PUT /claude-md {content} | 200, 파일 업데이트 | P0 |
| TC-5.5 | settings 없을 때 | settings.json 없는 프로젝트 | 200, 기본값 반환 | P0 |

### TC-6: 검증 (FR-6)

| ID | 테스트 | 입력 | 기대 결과 | 우선순위 |
|----|--------|------|----------|---------|
| TC-6.1 | 유효한 프로젝트 검증 | POST /validate | 200, errors: [] | P1 |
| TC-6.2 | 에이전트 필수 필드 누락 | name 없는 에이전트 | errors에 포함 | P1 |
| TC-6.3 | 스킬 필수 필드 누락 | description 없는 스킬 | errors에 포함 | P1 |
| TC-6.4 | 깨진 참조 감지 | 없는 reference 파일 참조 | warnings에 포함 | P1 |
| TC-6.5 | 잘못된 glob 패턴 | paths에 유효하지 않은 패턴 | errors에 포함 | P1 |
| TC-6.6 | settings.json 스키마 오류 | 잘못된 타입 | errors에 포함 | P1 |

## 3. 테스트 케이스 — 프론트엔드

### TC-FE-1: 컴포넌트 단위 테스트

| ID | 컴포넌트 | 테스트 | 우선순위 |
|----|----------|--------|---------|
| TC-FE-1.1 | AgentList | 에이전트 목록 렌더링 | P0 |
| TC-FE-1.2 | AgentList | 빈 목록 시 EmptyState 표시 | P0 |
| TC-FE-1.3 | AgentForm | frontmatter 폼 필드 렌더링 | P0 |
| TC-FE-1.4 | AgentForm | 필수 필드 검증 | P0 |
| TC-FE-1.5 | SkillList | 스킬 목록 + invocable 뱃지 | P0 |
| TC-FE-1.6 | RuleTree | 카테고리별 트리 렌더링 | P0 |
| TC-FE-1.7 | MarkdownEditor | 마크다운 입력 + 프리뷰 | P0 |
| TC-FE-1.8 | SettingsEditor | 권한 토글 렌더링 | P0 |
| TC-FE-1.9 | GlobTester | 패턴 입력 + 결과 표시 | P1 |
| TC-FE-1.10 | ValidationPanel | 에러/경고 목록 표시 | P1 |

### TC-FE-2: 인터랙션 테스트

| ID | 시나리오 | 테스트 | 우선순위 |
|----|----------|--------|---------|
| TC-FE-2.1 | 에이전트 생성 | 폼 입력 → 저장 → 목록 반영 | P0 |
| TC-FE-2.2 | 에이전트 편집 | 선택 → 폼 수정 → 저장 | P0 |
| TC-FE-2.3 | 스킬 생성 | 폼 입력 → 저장 → 목록 반영 | P0 |
| TC-FE-2.4 | 규칙 편집 | 카테고리 선택 → 규칙 선택 → 수정 → 저장 | P0 |
| TC-FE-2.5 | 설정 토글 | 권한 토글 → 저장 | P0 |
| TC-FE-2.6 | 삭제 확인 | 삭제 클릭 → 다이얼로그 → 확인/취소 | P1 |

## 4. 테스트 데이터

### 픽스처: 최소 .claude 프로젝트
```
test-fixtures/minimal/
└── .claude/
    └── CLAUDE.md
```

### 픽스처: 완전한 .claude 프로젝트
```
test-fixtures/full/
└── .claude/
    ├── CLAUDE.md
    ├── settings.json
    ├── agents/
    │   ├── coordinator.md
    │   └── developer.md
    ├── skills/
    │   └── feature/
    │       ├── SKILL.md
    │       └── reference/guide.md
    └── rules/
        ├── backend/
        │   └── python.md     (paths: ["**/*.py"])
        └── governance/
            └── approval.md   (no paths = always)
```

### 픽스처: 오류가 있는 프로젝트
```
test-fixtures/broken/
└── .claude/
    ├── CLAUDE.md
    ├── settings.json          ← 깨진 JSON
    ├── agents/
    │   └── bad-agent.md       ← name 필드 누락
    └── skills/
        └── broken-skill/
            └── SKILL.md       ← 깨진 YAML
```

## 5. 테스트 환경

| 환경 | 용도 | 설정 |
|------|------|------|
| 로컬 | 개발 중 TDD | pytest + vitest, test-fixtures/ 사용 |
| CI | PR 검증 | GitHub Actions, SQLite (테스트 DB) |

### 테스트 실행 명령

```bash
# 백엔드 전체
make test-be

# 백엔드 특정 모듈
cd backend && .venv/bin/python -m pytest tests/test_parser.py -v

# 프론트엔드 전체
make test-fe

# 전체
make test
```

## 6. 합격 기준

### MVP 출시 기준
- [ ] 백엔드 테스트 커버리지 80% 이상
- [ ] 프론트엔드 컴포넌트 테스트 전수
- [ ] 모든 P0 테스트 케이스 통과
- [ ] CI 파이프라인에서 전체 테스트 자동 실행
- [ ] 파싱 정확도: 3종 .claude 픽스처 모두 정상 처리

### 각 릴리스 기준
| 버전 | 합격 기준 |
|------|----------|
| v0.1 (뷰어) | TC-1.*, TC-2.1~2.3, TC-3.1~3.3, TC-4.1~4.2, TC-5.* 전체 통과 |
| v0.2 (편집) | + TC-2.4~2.10, TC-3.4~3.8, TC-4.3~4.7, TC-FE-2.* 전체 통과 |
| v0.3 (검증) | + TC-6.* 전체 통과 |
| v1.0 (안정) | 전체 TC 통과 + 커버리지 기준 충족 |
