# Plane 워크플로우 표준

## 이슈 상태 흐름

```
Backlog → Todo → In Progress → Done
                      ↓
                   Blocked → (해결 후) In Progress
```

## API 사용법

```bash
source scripts/plane-api.sh

# 프로젝트 이슈 조회
./scripts/plane-status.sh

# 이슈 상태 변경
plane_update_issue_state "$PROJECT_ID" "$ISSUE_ID" "$(plane_get_state_id "$PROJECT_ID" "In Progress")"

# 코멘트 작성
plane_add_comment "$PROJECT_ID" "$ISSUE_ID" "<p>작업 내용</p>"

# Sub-issue 생성
plane_create_sub_issue "$PROJECT_ID" "$PARENT_ISSUE_ID" \
  "[Task] 작업 제목" "<p>설명</p>" "medium" "$TODO_STATE"
```

## 코멘트 형식

### 작업 시작
```html
<p><strong>🔄 작업 시작</strong><br/>{작업 내용 요약}</p>
```

### 작업 완료
```html
<p><strong>✅ 작업 완료</strong><br/>- 변경 사항 1<br/>- 변경 사항 2<br/><br/>커밋: {해시}</p>
```

### 블로커 보고
```html
<p><strong>🚫 BLOCKED</strong><br/>원인: {블로커 원인}<br/>필요한 도움: {무엇이 필요한지}<br/>제안: {해결 방안}</p>
```

## 규칙

- 이슈 없이 작업하지 않음
- 상태 변경을 즉시 반영
- 모든 행동을 코멘트에 기록
- 위임 시 충분한 컨텍스트 포함
