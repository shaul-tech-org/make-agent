---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
---

# Heartbeat 필수 규칙

모든 에이전트는 Heartbeat 프로토콜을 따라야 한다.

## 필수
- 매 Heartbeat 시작 시 /api/agents/me로 신원 확인
- 작업 수행 전 반드시 checkout (409 시 다른 작업 선택)
- 모든 수정 API에 X-Paperclip-Run-Id 헤더 포함
- 작업 완료/진행/블로커 시 반드시 상태 업데이트
- 코멘트로 진행 상황 기록

## 금지
- 409 Conflict 재시도
- 체크아웃 없이 작업 수행
- Heartbeat 내에서 무한 루프
- 다른 에이전트의 체크아웃된 작업 수정
