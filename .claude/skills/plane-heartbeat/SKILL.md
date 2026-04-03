---
name: plane-heartbeat
description: "Plane 기반 Heartbeat 프로토콜. 에이전트가 실행될 때마다 수행하는 표준 절차."
user-invocable: true
---

# Plane Heartbeat Protocol

Paperclip의 Heartbeat 패턴을 Plane 이슈 관리로 구현한다.
에이전트가 실행될 때마다 이 절차를 따른다.

→ *Consult [plane-api-reference](references/plane-api-reference.md) for API usage details.*

## Step 1: 현황 파악

```bash
source scripts/plane-api.sh
./scripts/plane-status.sh
```

현재 프로젝트의 이슈 현황을 확인한다.

## Step 2: 내 할당 이슈 확인

나에게 할당된 이슈 중:
1. **In Progress** — 먼저 처리 (이미 시작한 작업)
2. **Todo** — 다음 처리
3. **Blocked** — 새 컨텍스트가 있을 때만

## Step 3: 이슈 작업 시작

```bash
# 이슈 상태를 In Progress로 변경
plane_update_issue_state "$PROJECT_ID" "$ISSUE_ID" "$(plane_get_state_id "$PROJECT_ID" "In Progress")"

# 시작 코멘트 작성
plane_add_comment "$PROJECT_ID" "$ISSUE_ID" "<p>작업 시작</p>"
```

## Step 4: 작업 수행

실제 도메인 작업 수행 (코딩, 리서치, 리뷰 등)

## Step 5: 결과 기록

```bash
# 완료 코멘트 (작업 내용 상세 기록)
plane_add_comment "$PROJECT_ID" "$ISSUE_ID" "<p>작업 완료<br/>- 변경 사항 1<br/>- 변경 사항 2</p>"

# 상태 업데이트
plane_update_issue_state "$PROJECT_ID" "$ISSUE_ID" "$(plane_get_state_id "$PROJECT_ID" "Done")"
```

## Step 6: 위임 (필요 시)

작업을 분해하여 다른 에이전트에게 위임:

```bash
# Sub-issue 생성
plane_create_sub_issue "$PROJECT_ID" "$PARENT_ISSUE_ID" \
  "[Task] 구체적 작업 제목" \
  "<p>작업 상세 설명</p>" \
  "medium" \
  "$TODO_STATE_ID"
```

## Step 7: 블로커 처리

블로커 발생 시:
1. 이슈 상태를 Blocked로 변경 (없으면 코멘트에 "BLOCKED" 명시)
2. 블로커 내용과 해결 방법을 코멘트에 기록
3. 상급자에게 에스컬레이션 (상급자 이슈에 코멘트)

## 필수 규칙

- **모든 행동을 Plane 코멘트에 기록** (추적 가능성)
- **이슈 없이 작업하지 않음** (이슈 먼저 생성)
- **상태 변경을 즉시 반영** (In Progress → Done/Blocked)
- **위임 시 충분한 컨텍스트** 포함
