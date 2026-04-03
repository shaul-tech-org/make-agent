---
paths:
  - "**/app/**"
  - "**/src/**"
  - "**/internal/**"
---

# 모놀리식 (Monolithic) 아키텍처 규칙

## 모듈 분리 원칙
- 단일 배포 단위이지만 내부는 모듈로 분리
- 모듈 간 의존성 최소화 (인터페이스 기반)
- 패키지/네임스페이스로 경계 정의
- 순환 의존 금지

## 레이어드 아키텍처
```
Presentation (Controller/Handler)
    ↓
Application (Service/UseCase)
    ↓
Domain (Entity/ValueObject)
    ↓
Infrastructure (Repository/External API)
```
- 상위 레이어만 하위 레이어 참조 (역방향 금지)
- Domain 레이어는 외부 의존성 없음 (순수 비즈니스 로직)

## 모듈러 모놀리스 (권장)
```
app/
├── modules/
│   ├── user/          ← 사용자 모듈
│   │   ├── controller/
│   │   ├── service/
│   │   ├── repository/
│   │   └── model/
│   ├── order/         ← 주문 모듈
│   │   ├── controller/
│   │   ├── service/
│   │   └── ...
│   └── payment/       ← 결제 모듈
```
- 모듈 간 통신: 인터페이스/이벤트 (직접 참조 금지)
- MSA 전환 준비: 모듈 = 미래의 서비스 후보

## 단일 DB
- 하나의 DB에 모든 테이블
- 트랜잭션 ACID 보장 (MSA 대비 강점)
- 스키마 네이밍: 모듈별 prefix 또는 스키마 분리

## 확장 전략
- 수직 확장 (Scale Up): 서버 스펙 증가
- 수평 확장 (Scale Out): 로드밸런서 + 복제 서버
- 캐싱: Redis로 읽기 부하 분산
- 읽기 복제: DB Replica (읽기/쓰기 분리)

## MSA 전환 시점 판단
| 신호 | 조치 |
|------|------|
| 배포 주기가 팀 간 충돌 | 모듈 분리 → 독립 배포 검토 |
| 특정 모듈만 스케일링 필요 | 해당 모듈 서비스 분리 |
| 팀이 5+로 확대 | 서비스 소유권 분리 |
| 기술 스택 다양화 필요 | 폴리글랏 서비스 분리 |

## 주의사항
- "모놀리스 = 나쁨"이 아님. 시작은 모놀리스가 적합
- 모듈러 모놀리스 → MSA 점진적 전환이 가장 안전
- Big Bang MSA 전환은 리스크 높음
