# 요구사항 명세서: make-agent

## 1. 기능 요구사항

### FR-1: 프로젝트 로딩

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-1.1 | 로컬 경로를 입력받아 .claude 디렉토리를 탐색할 수 있다 | P0 | ✅ |
| FR-1.2 | CLAUDE.md를 파싱하여 프로젝트 개요를 표시한다 | P0 | ✅ |
| FR-1.3 | settings.json을 파싱하여 설정을 표시한다 | P0 | ✅ |
| FR-1.4 | .claude 디렉토리가 없는 경로에 대해 에러를 표시한다 | P0 | ✅ |
| FR-1.5 | 파싱 오류(깨진 YAML, 잘못된 JSON)를 경고로 표시한다 | P1 | |
| FR-1.6 | 최근 열었던 프로젝트 목록을 유지한다 | P2 | |

### FR-2: 에이전트 관리

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-2.1 | agents/ 디렉토리의 모든 에이전트를 목록으로 표시한다 | P0 | ✅ |
| FR-2.2 | 에이전트의 frontmatter(name, description, model, memory)를 표시한다 | P0 | ✅ |
| FR-2.3 | 에이전트의 마크다운 본문을 표시한다 | P0 | ✅ |
| FR-2.4 | 새 에이전트 파일을 생성할 수 있다 | P0 | ✅ |
| FR-2.5 | 에이전트의 frontmatter를 폼으로 편집할 수 있다 | P0 | ✅ |
| FR-2.6 | 에이전트 본문을 마크다운 에디터로 편집할 수 있다 | P0 | ✅ |
| FR-2.7 | 에이전트를 삭제할 수 있다 (확인 다이얼로그 필수) | P1 | |
| FR-2.8 | 에이전트 간 위임 관계를 조직도로 시각화한다 | P1 | |
| FR-2.9 | model 필드에 유효한 모델 목록을 제안한다 (sonnet, opus, haiku) | P1 | |
| FR-2.10 | agent-memory/ 디렉토리의 메모리를 뷰어로 표시한다 | P2 | |

### FR-3: 스킬 관리

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-3.1 | skills/ 디렉토리의 모든 스킬을 목록으로 표시한다 | P0 | ✅ |
| FR-3.2 | 스킬의 frontmatter(name, description, user-invocable, argument-hint)를 표시한다 | P0 | ✅ |
| FR-3.3 | 스킬의 SKILL.md 본문을 표시한다 | P0 | ✅ |
| FR-3.4 | 새 스킬(디렉토리 + SKILL.md)을 생성할 수 있다 | P0 | ✅ |
| FR-3.5 | 스킬의 frontmatter를 폼으로 편집할 수 있다 | P0 | ✅ |
| FR-3.6 | 스킬 본문을 마크다운 에디터로 편집할 수 있다 | P0 | ✅ |
| FR-3.7 | reference/ 디렉토리의 참조 문서를 관리할 수 있다 (추가/편집/삭제) | P1 | |
| FR-3.8 | 스킬 간 의존성(전제조건)을 파이프라인으로 시각화한다 | P1 | |
| FR-3.9 | user-invocable 스킬을 구분하여 표시한다 | P0 | ✅ |
| FR-3.10 | 스킬을 삭제할 수 있다 (디렉토리 전체, 확인 필수) | P1 | |

### FR-4: 규칙 관리

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-4.1 | rules/ 디렉토리의 모든 규칙을 카테고리별로 표시한다 | P0 | ✅ |
| FR-4.2 | 규칙의 frontmatter(paths)와 본문을 표시한다 | P0 | ✅ |
| FR-4.3 | 새 규칙 파일을 생성할 수 있다 (카테고리 선택) | P0 | ✅ |
| FR-4.4 | 규칙의 paths(glob 패턴)를 편집할 수 있다 | P0 | ✅ |
| FR-4.5 | 규칙 본문을 마크다운 에디터로 편집할 수 있다 | P0 | ✅ |
| FR-4.6 | 새 카테고리(하위 디렉토리)를 생성할 수 있다 | P1 | |
| FR-4.7 | glob 패턴이 어떤 파일에 매칭되는지 미리보기를 제공한다 | P1 | |
| FR-4.8 | paths가 없는 규칙(항상 로드)을 구분하여 표시한다 | P0 | ✅ |
| FR-4.9 | 규칙을 삭제할 수 있다 (확인 필수) | P1 | |
| FR-4.10 | 규칙 적용 범위 매트릭스를 시각화한다 (규칙 × 파일 패턴) | P2 | |

### FR-5: 설정 관리

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-5.1 | settings.json을 시각적으로 편집할 수 있다 | P0 | ✅ |
| FR-5.2 | permissions.allow/ask를 토글로 전환할 수 있다 | P0 | ✅ |
| FR-5.3 | CLAUDE.md를 마크다운 에디터로 편집할 수 있다 | P0 | ✅ |
| FR-5.4 | 사용 가능한 도구 목록을 표시한다 (Read, Write, Edit, Bash, Agent 등) | P1 | |
| FR-5.5 | enabledPlugins를 토글로 관리할 수 있다 | P1 | |
| FR-5.6 | effortLevel을 드롭다운으로 선택할 수 있다 | P1 | |

### FR-6: 검증

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-6.1 | 에이전트 frontmatter 필수 필드(name, description, model) 누락을 감지한다 | P1 | |
| FR-6.2 | 스킬 frontmatter 필수 필드(name, description) 누락을 감지한다 | P1 | |
| FR-6.3 | 스킬이 참조하는 reference 파일의 존재 여부를 확인한다 | P1 | |
| FR-6.4 | CLAUDE.md에 언급된 에이전트/스킬이 실제로 존재하는지 확인한다 | P2 | |
| FR-6.5 | settings.json의 JSON 스키마를 검증한다 | P1 | |
| FR-6.6 | 미사용 파일(어디서도 참조되지 않는 reference)을 감지한다 | P2 | |
| FR-6.7 | glob 패턴의 문법 유효성을 검사한다 | P1 | |

### FR-7: 시각화

| ID | 요구사항 | 우선순위 | MVP |
|----|----------|---------|-----|
| FR-7.1 | 에이전트 위임 관계를 트리 다이어그램으로 표시한다 | P1 | |
| FR-7.2 | 스킬 파이프라인을 DAG(방향 비순환 그래프)로 표시한다 | P1 | |
| FR-7.3 | 프로젝트 통계(에이전트 수, 스킬 수, 규칙 수)를 대시보드에 표시한다 | P0 | ✅ |

## 2. 비기능 요구사항

### NFR-1: 성능

| ID | 요구사항 | 기준 |
|----|----------|------|
| NFR-1.1 | 프로젝트 로딩 (100개 파일 이하) | < 1초 |
| NFR-1.2 | 파일 저장 | < 500ms |
| NFR-1.3 | 검증 실행 | < 2초 |
| NFR-1.4 | UI 페이지 전환 | < 300ms |

### NFR-2: 보안

| ID | 요구사항 |
|----|----------|
| NFR-2.1 | 로컬 파일시스템만 접근, 외부 네트워크 전송 없음 |
| NFR-2.2 | 파일 쓰기 전 원본 백업 (.bak) |
| NFR-2.3 | 삭제 작업 시 반드시 사용자 확인 요구 |
| NFR-2.4 | .claude 디렉토리 외부 파일 접근 차단 |

### NFR-3: 사용성

| ID | 요구사항 |
|----|----------|
| NFR-3.1 | 키보드만으로 모든 기능 접근 가능 |
| NFR-3.2 | 다크 모드 기본 (개발자 도구 컨셉) |
| NFR-3.3 | 한국어 UI 기본 |
| NFR-3.4 | 마크다운 프리뷰 + 코드 하이라이팅 |
| NFR-3.5 | 변경 사항 표시 (수정됨 인디케이터) |

### NFR-4: 호환성

| ID | 요구사항 |
|----|----------|
| NFR-4.1 | Chrome, Firefox, Safari 최신 2개 버전 지원 |
| NFR-4.2 | Python 3.11+ |
| NFR-4.3 | Node.js 20+ |
| NFR-4.4 | macOS, Linux, Windows(WSL) 지원 |

### NFR-5: 유지보수성

| ID | 요구사항 |
|----|----------|
| NFR-5.1 | 백엔드 테스트 커버리지 80% 이상 |
| NFR-5.2 | 프론트엔드 컴포넌트 테스트 필수 |
| NFR-5.3 | API 문서 자동 생성 (FastAPI /docs) |
| NFR-5.4 | 모듈러 모놀리스 아키텍처 (모듈별 독립 테스트 가능) |

## 3. API 엔드포인트 개요

### 프로젝트
| Method | Path | 설명 |
|--------|------|------|
| POST | /api/v1/projects/load | 프로젝트 경로로 .claude 로딩 |
| GET | /api/v1/projects/current | 현재 프로젝트 정보 |
| GET | /api/v1/projects/stats | 프로젝트 통계 |

### 에이전트
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/v1/agents | 에이전트 목록 |
| GET | /api/v1/agents/{name} | 에이전트 상세 |
| POST | /api/v1/agents | 에이전트 생성 |
| PUT | /api/v1/agents/{name} | 에이전트 수정 |
| DELETE | /api/v1/agents/{name} | 에이전트 삭제 |

### 스킬
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/v1/skills | 스킬 목록 |
| GET | /api/v1/skills/{name} | 스킬 상세 |
| POST | /api/v1/skills | 스킬 생성 |
| PUT | /api/v1/skills/{name} | 스킬 수정 |
| DELETE | /api/v1/skills/{name} | 스킬 삭제 |
| GET | /api/v1/skills/{name}/references | 참조 문서 목록 |
| POST | /api/v1/skills/{name}/references | 참조 문서 추가 |

### 규칙
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/v1/rules | 규칙 목록 (카테고리별) |
| GET | /api/v1/rules/{category}/{name} | 규칙 상세 |
| POST | /api/v1/rules | 규칙 생성 |
| PUT | /api/v1/rules/{category}/{name} | 규칙 수정 |
| DELETE | /api/v1/rules/{category}/{name} | 규칙 삭제 |
| POST | /api/v1/rules/test-glob | glob 패턴 매칭 테스트 |

### 설정
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/v1/settings | settings.json 조회 |
| PUT | /api/v1/settings | settings.json 수정 |
| GET | /api/v1/claude-md | CLAUDE.md 조회 |
| PUT | /api/v1/claude-md | CLAUDE.md 수정 |

### 검증
| Method | Path | 설명 |
|--------|------|------|
| POST | /api/v1/validate | 전체 설정 검증 |

## 4. 데이터 모델

### Agent
```
{
  name: string          // kebab-case, 필수
  description: string   // 역할 설명, 필수
  model: string         // "sonnet" | "opus" | "haiku", 필수
  memory: string?       // "project" | "session", 선택
  body: string          // 마크다운 본문
  file_path: string     // 파일 경로 (읽기 전용)
}
```

### Skill
```
{
  name: string              // kebab-case, 필수
  description: string       // 설명, 필수
  user_invocable: boolean   // 기본값 false
  argument_hint: string?    // user_invocable=true일 때
  body: string              // 마크다운 본문
  references: string[]      // reference/ 파일 목록
  file_path: string         // 파일 경로 (읽기 전용)
}
```

### Rule
```
{
  name: string          // 파일명 (확장자 제외)
  category: string      // 카테고리 (디렉토리명)
  paths: string[]       // glob 패턴 배열, 빈 배열 = 항상 로드
  body: string          // 마크다운 본문
  file_path: string     // 파일 경로 (읽기 전용)
}
```

### Settings
```
{
  permissions: {
    allow: string[]     // 자동 허용 도구
    ask: string[]       // 확인 필요 도구
  }
  effortLevel: string?          // "low" | "medium" | "high"
  enabledPlugins: Record<string, boolean>?
}
```

## 5. 화면 구성 (Wire-level)

```
┌──────────────────────────────────────────────┐
│  make-agent              [프로젝트 경로] [열기] │
├──────┬───────────────────────────────────────┤
│      │                                       │
│ 사이드│  메인 컨텐츠 영역                      │
│ 바    │                                       │
│      │  ┌─────────────────────────────────┐  │
│ 대시  │  │  에이전트/스킬/규칙 목록 + 편집  │  │
│ 보드  │  │                                 │  │
│ 에이  │  │  좌: 목록/트리                  │  │
│ 전트  │  │  우: 편집기 (frontmatter + body) │  │
│ 스킬  │  │                                 │  │
│ 규칙  │  └─────────────────────────────────┘  │
│ 설정  │                                       │
│ 검증  │                                       │
│      │                                       │
└──────┴───────────────────────────────────────┘
```
