---
paths:
  - "**/Dockerfile*"
  - "**/docker-compose*"
  - "**/.dockerignore"
---

# Docker 규칙

## Dockerfile
- 멀티 스테이지 빌드 사용 (빌드/실행 분리)
- 불필요한 레이어 최소화
- .dockerignore 필수
- 비 root 사용자로 실행

## Docker Compose
- 리소스 제한 설정 (CPU, 메모리)
- 로그: json-file 드라이버, max-size/max-file 설정
- healthcheck 설정
- restart: always (프로덕션)

## 보안
- 시크릿: 환경변수 또는 Docker secrets 사용 (이미지에 포함 금지)
- 최소 베이스 이미지 (alpine 권장)
- 정기적 이미지 업데이트
