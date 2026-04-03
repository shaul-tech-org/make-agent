# Plane API 레퍼런스

## 환경 설정

```bash
source scripts/plane-api.sh
```

## 주요 함수

### 프로젝트 조회
```bash
# 프로젝트 ID 조회
PROJECT_ID=$(plane_get_project_id_by_name "프로젝트명")

# 프로젝트 존재 확인
PROJECT_ID=$(plane_project_exists "프로젝트명")
```

### 상태 ID 조회
```bash
STATE_ID=$(plane_get_state_id "$PROJECT_ID" "Todo")
STATE_ID=$(plane_get_state_id "$PROJECT_ID" "In Progress")
STATE_ID=$(plane_get_state_id "$PROJECT_ID" "Done")
```

### 이슈 관리
```bash
# 이슈 생성
plane_create_issue "$PROJECT_ID" "제목" "<p>설명</p>" "medium" "$STATE_ID" '["label_id"]'

# 이슈 상태 변경
plane_update_issue_state "$PROJECT_ID" "$ISSUE_ID" "$STATE_ID"

# 이슈 설명 업데이트
plane_update_issue_description "$PROJECT_ID" "$ISSUE_ID" "$HTML_CONTENT"
```

### Sub-issue 관리
```bash
plane_create_sub_issue "$PROJECT_ID" "$PARENT_ID" \
  "[Task] 제목" "<p>설명</p>" "medium" "$TODO_STATE"
```

### 코멘트
```bash
plane_add_comment "$PROJECT_ID" "$ISSUE_ID" "<p>코멘트 내용</p>"
```

### 라벨
```bash
LABEL_ID=$(plane_get_label_id "$PROJECT_ID" "라벨명")
LABEL_ID=$(plane_create_label "$PROJECT_ID" "라벨명" | jq -r '.id')
```

## 상태 흐름

```
Backlog → Todo → In Progress → Done
```

## 우선순위

| 값 | 의미 |
|----|------|
| urgent | 즉시 |
| high | 4시간 |
| medium | 1~2일 |
| low | 백로그 |
