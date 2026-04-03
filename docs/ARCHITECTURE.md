# 아키텍처 설계: make-agent

## 1. 시스템 개요

```
┌─────────────────────────────────────────────────────┐
│                    브라우저 (React)                    │
│  ┌──────────┬──────────┬──────────┬──────────┐      │
│  │ 대시보드  │ 에이전트  │  스킬    │  규칙    │      │
│  │          │ 뷰/편집   │ 뷰/편집  │ 뷰/편집  │      │
│  └──────────┴──────────┴──────────┴──────────┘      │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴──────────────────────────────┐
│                  FastAPI 백엔드                        │
│  ┌──────────────────────────────────────────┐       │
│  │              API Layer (Router)           │       │
│  ├──────────────────────────────────────────┤       │
│  │            Service Layer                  │       │
│  ├──────────┬──────────┬────────────────────┤       │
│  │  Parser  │ Validator│    Writer           │       │
│  └──────────┴──────────┴────────────────────┘       │
│                       │                              │
│              ┌────────┴────────┐                     │
│              │  File System    │                     │
│              │  (.claude/)     │                     │
│              └─────────────────┘                     │
└──────────────────────────────────────────────────────┘
```

## 2. 아키텍처 패턴

### 모듈러 모놀리스
- 단일 FastAPI 서버 안에서 모듈별 분리
- 모듈 간 의존성은 서비스 레이어를 통해서만

### 레이어 구조

```
Router (API 엔드포인트)
  ↓ 요청/응답 변환
Service (비즈니스 로직)
  ↓ 도메인 연산
Parser / Writer / Validator (데이터 접근)
  ↓ 파일 I/O
File System (.claude/)
```

**핵심 원칙**: DB 없이 파일 시스템이 유일한 저장소. 파싱 결과를 메모리에 캐싱하되, 쓰기는 항상 파일에 직접.

## 3. 백엔드 모듈 구조

```
backend/app/
├── core/                          # 기존 scaffold (DB, 로깅, 에러, 보안, 메트릭)
│   ├── database.py                # ※ 이 프로젝트에서는 미사용 (파일 기반)
│   ├── exceptions.py
│   ├── error_handler.py
│   ├── logging.py
│   ├── metrics.py
│   └── security.py
│
├── modules/
│   ├── project/                   # 프로젝트 로딩/관리
│   │   ├── router.py              # POST /load, GET /current, GET /stats
│   │   ├── service.py             # 프로젝트 상태 관리, 캐시
│   │   ├── schemas/
│   │   └── exceptions.py
│   │
│   ├── parser/                    # .claude 파일 파싱 (읽기 전용)
│   │   ├── service.py             # 파싱 오케스트레이터
│   │   ├── frontmatter.py         # YAML frontmatter 파서
│   │   ├── agent_parser.py        # agents/*.md 파싱
│   │   ├── skill_parser.py        # skills/*/SKILL.md 파싱
│   │   ├── rule_parser.py         # rules/**/*.md 파싱
│   │   ├── settings_parser.py     # settings.json 파싱
│   │   └── claude_md_parser.py    # CLAUDE.md 파싱
│   │
│   ├── agent/                     # 에이전트 CRUD
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas/
│   │   └── exceptions.py
│   │
│   ├── skill/                     # 스킬 CRUD
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas/
│   │   └── exceptions.py
│   │
│   ├── rule/                      # 규칙 CRUD
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas/
│   │   └── exceptions.py
│   │
│   ├── settings/                  # 설정 관리
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas/
│   │   └── exceptions.py
│   │
│   ├── validator/                 # 검증
│   │   ├── router.py
│   │   ├── service.py             # 전체 검증 오케스트레이터
│   │   ├── schema_validator.py    # frontmatter 스키마 검증
│   │   ├── reference_validator.py # 참조 무결성 검증
│   │   ├── glob_validator.py      # glob 패턴 유효성
│   │   └── schemas/
│   │
│   └── writer/                    # 파일 쓰기 (공통)
│       ├── service.py             # frontmatter + body → 파일 저장
│       ├── frontmatter_writer.py  # YAML frontmatter 직렬화
│       └── backup.py              # 저장 전 .bak 백업
│
└── config.py
```

## 4. 파서 아키텍처

### frontmatter 파싱 흐름

```
.md 파일
  ↓
frontmatter.py: --- 구분자로 YAML/body 분리
  ↓
┌─────────────┬──────────────┐
│ YAML dict   │ Markdown str │
│ (메타데이터)  │ (본문)        │
└─────────────┴──────────────┘
  ↓                ↓
Pydantic 모델     그대로 보존
  검증 + 변환
```

### 파서 인터페이스 (Protocol)

```python
class FileParser(Protocol):
    def parse(self, file_path: Path) -> ParseResult: ...
    def parse_directory(self, dir_path: Path) -> list[ParseResult]: ...
```

각 파서(agent, skill, rule)는 이 인터페이스를 구현.

## 5. 쓰기 아키텍처

### 쓰기 흐름

```
편집 데이터 (Pydantic 모델)
  ↓
Service: 비즈니스 검증
  ↓
Writer: frontmatter YAML + body 결합
  ↓
Backup: 기존 파일 → .bak
  ↓
파일 시스템에 저장
```

### 원자적 쓰기
1. 임시 파일에 쓰기 (.tmp)
2. 기존 파일 백업 (.bak)
3. 임시 파일 → 대상 파일 이동 (rename, 원자적)

## 6. 프론트엔드 구조

```
frontend/src/
├── api/
│   ├── client.ts              # fetchJson 기반 API 클라이언트
│   ├── agents.ts              # 에이전트 API 호출
│   ├── skills.ts              # 스킬 API 호출
│   ├── rules.ts               # 규칙 API 호출
│   ├── settings.ts            # 설정 API 호출
│   └── types.ts               # 공통 타입
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx        # 사이드바 네비게이션
│   │   ├── Header.tsx         # 상단 프로젝트 정보
│   │   └── Layout.tsx         # 전체 레이아웃
│   │
│   ├── agents/
│   │   ├── AgentList.tsx      # 에이전트 목록
│   │   ├── AgentForm.tsx      # 에이전트 편집 폼
│   │   └── AgentOrgChart.tsx  # 조직도 (P1)
│   │
│   ├── skills/
│   │   ├── SkillList.tsx      # 스킬 목록
│   │   ├── SkillForm.tsx      # 스킬 편집 폼
│   │   └── SkillPipeline.tsx  # 파이프라인 (P1)
│   │
│   ├── rules/
│   │   ├── RuleTree.tsx       # 카테고리 트리
│   │   ├── RuleForm.tsx       # 규칙 편집 폼
│   │   └── GlobTester.tsx     # glob 테스터 (P1)
│   │
│   ├── settings/
│   │   ├── SettingsEditor.tsx # settings.json 편집
│   │   └── ClaudeMdEditor.tsx # CLAUDE.md 편집
│   │
│   ├── shared/
│   │   ├── MarkdownEditor.tsx # 마크다운 에디터 + 프리뷰
│   │   ├── FrontmatterForm.tsx# YAML frontmatter 폼 생성기
│   │   ├── LoadingSpinner.tsx
│   │   ├── EmptyState.tsx
│   │   └── ErrorMessage.tsx
│   │
│   └── dashboard/
│       └── Dashboard.tsx      # 프로젝트 개요 + 통계
│
├── pages/
│   ├── DashboardPage.tsx
│   ├── AgentsPage.tsx
│   ├── SkillsPage.tsx
│   ├── RulesPage.tsx
│   └── SettingsPage.tsx
│
├── hooks/
│   ├── useProject.ts          # 프로젝트 상태
│   ├── useAgents.ts           # 에이전트 CRUD
│   ├── useSkills.ts           # 스킬 CRUD
│   └── useRules.ts            # 규칙 CRUD
│
├── App.tsx                    # 라우팅 + 레이아웃
├── index.css                  # Tailwind 디자인 토큰
└── main.tsx
```

## 7. 상태 관리

### 서버 상태 (API 데이터)
- **방식**: React Query 또는 SWR 없이 단순 fetch + useState
- **이유**: 데이터량이 적고 (수십 개 파일), 캐시 복잡도 불필요

### 클라이언트 상태
- **현재 프로젝트 경로**: Context API
- **편집 중 변경사항**: 컴포넌트 로컬 state
- **수정됨 인디케이터**: dirty 플래그

## 8. 주요 기술 결정

| 결정 | 선택 | 대안 | 이유 |
|------|------|------|------|
| 저장소 | 파일 시스템 직접 | SQLite 캐시 | .claude가 파일 기반, 단일 진실 소스 유지 |
| 파싱 | python-frontmatter | 직접 구현 | 검증된 라이브러리, YAML+Markdown 분리 |
| 마크다운 에디터 | textarea + 프리뷰 | Monaco Editor | MVP에서는 단순함 우선 |
| 라우팅 | react-router-dom | - | SPA 표준 |
| 스타일링 | Tailwind CSS v4 | CSS Modules | 스켈레톤에서 이미 설정됨 |

## 9. 보안 고려사항

| 위협 | 대응 |
|------|------|
| Path Traversal | 프로젝트 경로 밖 접근 차단 (realpath 검증) |
| 파일 덮어쓰기 | .bak 백업 후 원자적 쓰기 |
| XSS (마크다운 렌더링) | DOMPurify로 sanitize |
| 임의 파일 삭제 | .claude/ 내부만 삭제 허용, 확인 필수 |
