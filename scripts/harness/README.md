# 멀티 하네스 빌드 시스템

Impeccable의 패턴을 참고한 멀티 AI 코딩 도구 지원 구조.

## 개요

`.claude/` 디렉토리를 단일 소스(Single Source of Truth)로 두고,
Cursor, Gemini CLI 등 다른 AI 코딩 도구 포맷으로 변환한다.

## 구조

```
.claude/                    # 단일 소스 (현재 사용 중)
├── agents/                 # Claude Code 전용 (다른 도구 미지원)
├── skills/                 # → 모든 도구로 변환 가능
├── rules/                  # Claude Code 전용 (다른 도구는 별도 방식)
└── CLAUDE.md               # → .cursorrules, GEMINI.md 등으로 변환

dist/                       # 빌드 출력
├── cursor/.cursor/skills/  # Cursor 포맷
├── gemini/.gemini/skills/  # Gemini CLI 포맷
```

## 플레이스홀더

소스 파일에서 사용 가능한 플레이스홀더:

| 플레이스홀더 | Claude Code | Cursor | Gemini |
|-------------|-------------|--------|--------|
| `{{model}}` | Claude | the model | Gemini |
| `{{config_file}}` | CLAUDE.md | .cursorrules | GEMINI.md |
| `{{command_prefix}}` | / | / | / |
| `{{ask_instruction}}` | AskUserQuestion tool | ask directly | ask directly |

## 설정

`providers.json`에 프로바이더별 설정 정의.

## 변환 규칙

| 소스 (.claude/) | Cursor | Gemini |
|----------------|--------|--------|
| skills/ | .cursor/skills/ | .gemini/skills/ |
| agents/ | ❌ (미지원) | ❌ (미지원) |
| rules/ | .cursorrules에 병합 | GEMINI.md에 병합 |
| CLAUDE.md | .cursorrules | GEMINI.md |

## 사용법 (향후 구현)

```bash
# 전체 빌드
python scripts/harness/build.py

# 특정 프로바이더만
python scripts/harness/build.py --provider cursor
```
