---
paths:
  - "**/.github/**"
  - "**/Jenkinsfile"
  - "**/.gitlab-ci*"
---

# CI/CD 규칙

## GitHub Actions
- 테스트: PR마다 자동 실행
- 빌드: 메인 브랜치 머지 시 이미지 빌드/푸시
- 시크릿: GitHub Secrets 사용 (워크플로우에 하드코딩 금지)

## 배포
- Blue-Green 무중단 배포 권장
- 배포 전 테스트 통과 필수
- 롤백 절차 문서화
