# 데이터 모델 설계: make-agent

## 1. 개요

make-agent는 DB가 아닌 **파일 시스템이 유일한 저장소**이다. Pydantic 모델은 파싱 결과를 표현하고, API 요청/응답을 검증하는 데 사용된다.

## 2. 도메인 모델

### Project (프로젝트)

```python
class Project(BaseModel):
    path: str                        # .claude 디렉토리 절대 경로
    claude_md: str | None            # CLAUDE.md 내용
    settings: Settings | None        # settings.json 파싱 결과
    agents: list[Agent]              # 에이전트 목록
    skills: list[Skill]              # 스킬 목록
    rules: list[Rule]                # 규칙 목록
    stats: ProjectStats              # 통계

class ProjectStats(BaseModel):
    agent_count: int
    skill_count: int
    rule_count: int
    invocable_skill_count: int
    rule_category_count: int
    has_claude_md: bool
    has_settings: bool
```

### Agent (에이전트)

```python
class AgentFrontmatter(BaseModel):
    name: str                        # kebab-case, 필수
    description: str                 # 역할 설명, 필수
    model: str                       # "sonnet" | "opus" | "haiku", 필수
    memory: str | None = None        # "project" | "session"

class Agent(BaseModel):
    frontmatter: AgentFrontmatter
    body: str                        # 마크다운 본문
    file_path: str                   # 상대 경로 (agents/ceo.md)
```

### Skill (스킬)

```python
class SkillFrontmatter(BaseModel):
    name: str                        # kebab-case, 필수
    description: str                 # 설명, 필수
    user_invocable: bool = False     # 사용자 호출 가능 여부
    argument_hint: str | None = None # 인자 힌트

class Skill(BaseModel):
    frontmatter: SkillFrontmatter
    body: str                        # 마크다운 본문
    references: list[str]            # reference/ 파일명 목록
    file_path: str                   # 상대 경로 (skills/decompose/SKILL.md)
```

### Rule (규칙)

```python
class RuleFrontmatter(BaseModel):
    paths: list[str] = []            # glob 패턴, 빈 배열 = 항상 로드

class Rule(BaseModel):
    name: str                        # 파일명 (확장자 제외)
    category: str                    # 카테고리 경로 (backend/python)
    frontmatter: RuleFrontmatter
    body: str                        # 마크다운 본문
    file_path: str                   # 상대 경로 (rules/backend/python/general.md)
    always_loaded: bool              # paths가 비었으면 True
```

### Settings (설정)

```python
class Permissions(BaseModel):
    allow: list[str] = []            # 자동 허용 도구
    ask: list[str] = []              # 확인 필요 도구

class Settings(BaseModel):
    permissions: Permissions = Permissions()
    effort_level: str | None = None  # "low" | "medium" | "high"
    enabled_plugins: dict[str, bool] = {}
```

## 3. API 스키마 (Request / Response)

### 프로젝트

```python
# Request
class ProjectLoadRequest(BaseModel):
    path: str = Field(max_length=1000)  # 디렉토리 경로

# Response
class ProjectResponse(BaseModel):
    path: str
    stats: ProjectStats
    warnings: list[str] = []         # 파싱 경고
```

### 에이전트

```python
# Request (생성/수정)
class AgentCreateRequest(BaseModel):
    name: str = Field(pattern=r'^[a-z][a-z0-9-]*$', max_length=50)
    description: str = Field(max_length=500)
    model: str = Field(pattern=r'^(sonnet|opus|haiku)$')
    memory: str | None = Field(None, pattern=r'^(project|session)$')
    body: str = ""

class AgentUpdateRequest(BaseModel):
    description: str | None = Field(None, max_length=500)
    model: str | None = Field(None, pattern=r'^(sonnet|opus|haiku)$')
    memory: str | None = None
    body: str | None = None

# Response
class AgentResponse(BaseModel):
    name: str
    description: str
    model: str
    memory: str | None
    body: str
    file_path: str
```

### 스킬

```python
# Request
class SkillCreateRequest(BaseModel):
    name: str = Field(pattern=r'^[a-z][a-z0-9-]*$', max_length=50)
    description: str = Field(max_length=500)
    user_invocable: bool = False
    argument_hint: str | None = Field(None, max_length=200)
    body: str = ""

class SkillUpdateRequest(BaseModel):
    description: str | None = Field(None, max_length=500)
    user_invocable: bool | None = None
    argument_hint: str | None = None
    body: str | None = None

# Response
class SkillResponse(BaseModel):
    name: str
    description: str
    user_invocable: bool
    argument_hint: str | None
    body: str
    references: list[str]
    file_path: str
```

### 규칙

```python
# Request
class RuleCreateRequest(BaseModel):
    name: str = Field(pattern=r'^[a-z][a-z0-9-]*$', max_length=50)
    category: str = Field(max_length=100)    # "backend/python"
    paths: list[str] = []
    body: str = ""

class RuleUpdateRequest(BaseModel):
    paths: list[str] | None = None
    body: str | None = None

# Response
class RuleResponse(BaseModel):
    name: str
    category: str
    paths: list[str]
    body: str
    file_path: str
    always_loaded: bool
```

### 설정

```python
# Request
class SettingsUpdateRequest(BaseModel):
    permissions: Permissions | None = None
    effort_level: str | None = None
    enabled_plugins: dict[str, bool] | None = None

class ClaudeMdUpdateRequest(BaseModel):
    content: str

# Response
class SettingsResponse(BaseModel):
    permissions: Permissions
    effort_level: str | None
    enabled_plugins: dict[str, bool]

class ClaudeMdResponse(BaseModel):
    content: str
    exists: bool
```

### 검증

```python
class ValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

class ValidationIssue(BaseModel):
    type: str          # "missing_field", "broken_reference", "invalid_glob"
    file_path: str     # 문제가 있는 파일
    message: str       # 설명
    severity: str      # "error" | "warning"
```

### glob 테스트

```python
class GlobTestRequest(BaseModel):
    pattern: str
    base_path: str | None = None     # None이면 프로젝트 루트

class GlobTestResponse(BaseModel):
    pattern: str
    matched_files: list[str]
    match_count: int
```

## 4. 파일 ↔ 모델 매핑

```
파일 시스템                          Pydantic 모델
──────────────────                 ──────────────
.claude/CLAUDE.md                → str (raw content)
.claude/settings.json            → Settings
.claude/agents/ceo.md            → Agent (frontmatter + body)
.claude/skills/decompose/SKILL.md → Skill (frontmatter + body + references)
.claude/rules/backend/python.md  → Rule (frontmatter + body + category)
```

### frontmatter 직렬화 규칙

**읽기 (파싱)**:
```
---
name: ceo
description: "CEO 역할"
model: opus
---

# CEO
본문 내용...
```
→ `Agent(frontmatter=AgentFrontmatter(name="ceo", ...), body="# CEO\n본문 내용...")`

**쓰기 (저장)**:
```python
Agent(frontmatter=..., body=...)
```
→ `---\nname: ceo\n...\n---\n\n# CEO\n본문 내용...`

### 주의사항
- frontmatter에 없는 커스텀 필드는 **보존**해야 함 (라운드트립 안전)
- body의 마크다운 포맷팅(줄바꿈, 들여쓰기)은 **그대로 유지**
- YAML에서 문자열 따옴표는 필요할 때만 사용 (특수문자 포함 시)
