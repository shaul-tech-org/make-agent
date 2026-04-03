# API 명세서: make-agent

## Base URL
```
http://localhost:8000/api/v1
```

## 공통 규칙
- Content-Type: `application/json`
- 에러 응답: `{ "error": str, "detail": str, "status_code": int, "request_id": str }`
- 모든 응답에 `X-Request-Id` 헤더 포함

---

## 1. 프로젝트 (Project)

### POST /projects/load
프로젝트 경로를 지정하여 .claude 디렉토리를 로딩한다.

**Request**
```json
{
  "path": "/home/user/my-project"
}
```

**Response 200**
```json
{
  "path": "/home/user/my-project/.claude",
  "stats": {
    "agent_count": 8,
    "skill_count": 10,
    "rule_count": 12,
    "invocable_skill_count": 7,
    "rule_category_count": 6,
    "has_claude_md": true,
    "has_settings": true
  },
  "warnings": ["agents/bad.md: invalid YAML frontmatter"]
}
```

**에러**
| 상태 | 조건 |
|------|------|
| 400 | .claude 디렉토리가 없음 |
| 400 | 경로가 존재하지 않음 |

### GET /projects/current
현재 로딩된 프로젝트 정보를 반환한다.

**Response 200** — ProjectResponse (위와 동일)

**에러** — 404: 로딩된 프로젝트 없음

### GET /projects/stats
프로젝트 통계만 반환한다.

**Response 200** — ProjectStats

---

## 2. 에이전트 (Agents)

### GET /agents
에이전트 목록을 반환한다.

**Response 200**
```json
[
  {
    "name": "ceo",
    "description": "CEO — 전략, 위임",
    "model": "opus",
    "memory": "project",
    "body": "# CEO\n\n...",
    "file_path": "agents/ceo.md"
  }
]
```

### GET /agents/{name}
특정 에이전트의 상세 정보를 반환한다.

**에러** — 404: 에이전트 없음

### POST /agents
새 에이전트를 생성한다.

**Request**
```json
{
  "name": "data-engineer",
  "description": "데이터 파이프라인 개발",
  "model": "sonnet",
  "memory": null,
  "body": "# Data Engineer\n\n데이터 파이프라인을 설계하고 구현한다."
}
```

**Response 201** — AgentResponse

**에러**
| 상태 | 조건 |
|------|------|
| 409 | 이미 존재하는 이름 |
| 422 | name 형식 오류 (kebab-case 아님) |
| 422 | 필수 필드 누락 |

### PUT /agents/{name}
에이전트를 수정한다.

**Request** — AgentUpdateRequest (변경할 필드만)
```json
{
  "description": "수정된 설명",
  "body": "# Updated\n\n수정된 본문"
}
```

**Response 200** — AgentResponse

**에러** — 404: 에이전트 없음

### DELETE /agents/{name}
에이전트를 삭제한다.

**Response 204** — No Content

**에러** — 404: 에이전트 없음

---

## 3. 스킬 (Skills)

### GET /skills
스킬 목록을 반환한다.

**Query Parameters**
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| invocable | bool | user-invocable 필터 |

**Response 200**
```json
[
  {
    "name": "decompose",
    "description": "복합 요청을 세부 작업으로 분해",
    "user_invocable": true,
    "argument_hint": "[복합 요청 내용]",
    "body": "# /decompose\n\n...",
    "references": ["dependency-patterns.md", "sizing-guide.md"],
    "file_path": "skills/decompose/SKILL.md"
  }
]
```

### GET /skills/{name}
특정 스킬의 상세 정보를 반환한다.

### POST /skills
새 스킬을 생성한다. 디렉토리와 SKILL.md를 함께 생성.

**Request**
```json
{
  "name": "my-skill",
  "description": "커스텀 스킬",
  "user_invocable": true,
  "argument_hint": "[인자]",
  "body": "# /my-skill\n\n워크플로우..."
}
```

**Response 201** — SkillResponse

### PUT /skills/{name}
스킬을 수정한다.

### DELETE /skills/{name}
스킬을 삭제한다 (디렉토리 전체).

### GET /skills/{name}/references
스킬의 reference 파일 목록을 반환한다.

**Response 200**
```json
[
  {
    "name": "dependency-patterns.md",
    "file_path": "skills/decompose/reference/dependency-patterns.md"
  }
]
```

### POST /skills/{name}/references
reference 파일을 추가한다.

**Request**
```json
{
  "name": "new-guide.md",
  "content": "# 가이드\n\n내용..."
}
```

---

## 4. 규칙 (Rules)

### GET /rules
규칙 목록을 카테고리별로 반환한다.

**Response 200**
```json
{
  "categories": [
    {
      "name": "backend/python",
      "rules": [
        {
          "name": "general",
          "category": "backend/python",
          "paths": ["**/*.py"],
          "body": "# Python 공통 규칙\n...",
          "file_path": "rules/backend/python/general.md",
          "always_loaded": false
        }
      ]
    },
    {
      "name": "governance",
      "rules": [
        {
          "name": "approval",
          "category": "governance",
          "paths": [],
          "body": "# 승인 규칙\n...",
          "file_path": "rules/governance/approval.md",
          "always_loaded": true
        }
      ]
    }
  ]
}
```

### GET /rules/{category}/{name}
특정 규칙의 상세 정보를 반환한다.

- `category`는 슬래시 포함 가능: `backend/python`
- 경로 예: `GET /rules/backend%2Fpython/general`

### POST /rules
규칙을 생성한다.

**Request**
```json
{
  "name": "go",
  "category": "backend",
  "paths": ["**/*.go", "**/go.mod"],
  "body": "# Go 규칙\n\n..."
}
```

### PUT /rules/{category}/{name}
규칙을 수정한다.

### DELETE /rules/{category}/{name}
규칙을 삭제한다.

### POST /rules/test-glob
glob 패턴이 어떤 파일에 매칭되는지 테스트한다.

**Request**
```json
{
  "pattern": "**/*.py",
  "base_path": null
}
```

**Response 200**
```json
{
  "pattern": "**/*.py",
  "matched_files": [
    "backend/app/main.py",
    "backend/app/config.py",
    "backend/tests/test_health.py"
  ],
  "match_count": 3
}
```

---

## 5. 설정 (Settings)

### GET /settings
settings.json을 반환한다. 파일이 없으면 기본값 반환.

**Response 200**
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "ask": ["Bash", "Edit", "Write"]
  },
  "effort_level": "high",
  "enabled_plugins": {}
}
```

### PUT /settings
settings.json을 수정한다.

**Request** — 변경할 필드만
```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Agent"],
    "ask": ["Bash", "Edit", "Write"]
  }
}
```

### GET /claude-md
CLAUDE.md 내용을 반환한다.

**Response 200**
```json
{
  "content": "# My Project\n\n프로젝트 설명...",
  "exists": true
}
```

### PUT /claude-md
CLAUDE.md를 수정한다.

**Request**
```json
{
  "content": "# Updated Project\n\n수정된 내용..."
}
```

---

## 6. 검증 (Validation)

### POST /validate
현재 프로젝트의 전체 설정을 검증한다.

**Response 200**
```json
{
  "valid": false,
  "errors": [
    {
      "type": "missing_field",
      "file_path": "agents/bad-agent.md",
      "message": "필수 필드 'model'이 누락되었습니다",
      "severity": "error"
    }
  ],
  "warnings": [
    {
      "type": "broken_reference",
      "file_path": "skills/feature/SKILL.md",
      "message": "참조된 'reference/missing.md'를 찾을 수 없습니다",
      "severity": "warning"
    }
  ]
}
```

### 검증 항목

| 유형 | 설명 | 심각도 |
|------|------|--------|
| missing_field | frontmatter 필수 필드 누락 | error |
| invalid_model | model 값이 유효하지 않음 | error |
| invalid_glob | glob 패턴 문법 오류 | error |
| invalid_json | settings.json 파싱 실패 | error |
| broken_reference | 참조된 파일 없음 | warning |
| unused_reference | 어디서도 참조되지 않는 파일 | warning |
| missing_claude_md | CLAUDE.md 없음 | warning |
