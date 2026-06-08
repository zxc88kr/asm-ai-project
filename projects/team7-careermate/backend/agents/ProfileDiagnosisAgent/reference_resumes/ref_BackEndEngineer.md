# BackEnd Engineer Resume Set

> Target: Korea / Entry-level Developer / Max Internship Experience  
> Role: BackEnd Engineer  
> Purpose: 100-point benchmark resumes for comparing junior developer resumes  
> Reference Basis: 한국 백엔드 채용 공고에서 반복적으로 요구되는 Java, Spring Boot, MySQL, Redis, AWS, API 설계, 트랜잭션, 성능 개선, 테스트, 배포 경험을 기준으로 구성함. 또한 공개된 신입 백엔드 이력서 사례에서 자주 보이는 Redis 캐싱, Kafka 비동기 처리, 동시성 제어, 데이터 정합성 개선 경험의 흐름을 참고함.  
> Note: 아래 Resume은 특정 개인의 이력서를 복제한 것이 아니라, 실제 채용 시장에서 강하게 평가되는 백엔드 역량 패턴을 기반으로 재구성한 고품질 비교군 Resume입니다.

---

# 1. Common Resume — BackEnd Engineer

## 김도윤 | BackEnd Engineer

Email: doyoon.kim.backend@gmail.com  
GitHub: https://github.com/doyoon-backend  
Portfolio: https://doyoon-backend.dev  
Blog: https://blog.doyoon-backend.dev  
LinkedIn: https://linkedin.com/in/doyoon-kim-backend  

---

## Summary

사용자 기능을 안정적인 서버 구조로 구현하는 데 집중하는 신입 BackEnd Engineer입니다.

Java, Spring Boot, JPA, MySQL, Redis, Docker, AWS를 활용해 회원, 인증, 결제, 알림, 관리자 기능이 포함된 웹 서비스를 직접 설계·구현·배포했습니다. 단순 CRUD 구현을 넘어 트랜잭션 정합성, N+1 문제, DB 인덱스, 캐싱, 예외 처리, 테스트 코드, CI/CD까지 고려한 백엔드 개발 경험이 있습니다.

팀 프로젝트에서는 API 설계, ERD 설계, 인증/인가, 서버 배포, 장애 로그 분석을 담당했으며, 서비스 기능을 안정적으로 운영 가능한 구조로 만드는 것에 관심이 많습니다.

---

## Core Competencies

- Java & Spring Boot 기반 REST API 개발
- JPA 기반 도메인 모델링 및 트랜잭션 처리
- MySQL ERD 설계 및 쿼리 성능 개선
- Redis 기반 캐싱 및 인증 토큰 관리
- Spring Security 기반 인증/인가 구현
- AWS EC2, RDS, S3 기반 서비스 배포
- Docker 기반 개발·배포 환경 구성
- JUnit5, Mockito 기반 테스트 코드 작성
- GitHub Actions 기반 CI/CD 구성
- 장애 로그 분석 및 API 응답 속도 개선

---

## Skills

### Language

- Java
- SQL
- JavaScript
- Python

### Backend

- Spring Boot
- Spring MVC
- Spring Security
- Spring Data JPA
- QueryDSL
- REST API
- JWT
- OAuth2
- WebSocket
- Validation
- Exception Handling

### Database

- MySQL
- PostgreSQL
- Redis
- H2
- Database Indexing
- Transaction
- Lock
- Query Optimization

### Infra / DevOps

- AWS EC2
- AWS RDS
- AWS S3
- Nginx
- Docker
- Docker Compose
- GitHub Actions
- Linux
- HTTPS
- Domain 연결

### Test / Tools

- JUnit5
- Mockito
- Spring Rest Docs
- Postman
- Swagger
- Git
- GitHub Projects
- Notion
- Slack

---

## Experience

### BackEnd Developer Intern

**FitLogics**  
2025.07 - 2025.12

사용자 건강 데이터 기반 식단·운동 기록 서비스를 운영하는 스타트업에서 백엔드 개발 인턴으로 근무했습니다.

### Key Contributions

- Spring Boot 기반 식단 기록, 체중 기록, 목표 칼로리 계산 API 개발
- 사용자별 주간 영양 통계 조회 API를 구현하고 MySQL index 적용으로 평균 응답 시간 780ms에서 210ms로 개선
- JPA N+1 문제가 발생하던 식단 상세 조회 API를 fetch join과 DTO projection으로 개선하여 쿼리 수 47개에서 5개로 감소
- Redis를 활용해 자주 조회되는 음식 영양 정보 데이터를 캐싱하여 DB 부하 감소
- JWT access token, refresh token 기반 인증 구조를 개선하고 refresh token을 Redis에 저장
- 관리자용 사용자 조회, 신고 내역 조회, 계정 비활성화 API 구현
- JUnit5와 Mockito 기반 단위 테스트 및 통합 테스트를 작성하여 주요 서비스 로직 테스트 커버리지 62% 달성
- GitHub Actions 기반 CI pipeline을 구성하여 PR 생성 시 build와 test가 자동 실행되도록 개선
- 운영 로그에서 500 error 발생 원인을 분석하고 공통 예외 처리 구조를 개선하여 반복 장애 감소
- 프론트엔드 개발자와 협업하여 API 명세를 Swagger로 관리하고 응답 형식 표준화

### Tech Stack

Java, Spring Boot, Spring Security, JPA, QueryDSL, MySQL, Redis, Docker, AWS EC2, AWS RDS, GitHub Actions

---

## Projects

---

### Project 1. MealBalance — 식단 관리 및 영양 분석 서비스

GitHub: https://github.com/doyoon-backend/mealbalance  
Demo: https://mealbalance.dev  
Period: 2025.03 - 2025.06  
Role: BackEnd Lead

사용자의 신체 정보와 목표를 기반으로 권장 칼로리와 영양소를 계산하고, 식단 기록과 주간 분석을 제공하는 서비스입니다.

### Problem

사용자는 식단을 기록하더라도 자신의 목표 대비 무엇이 부족하거나 초과되었는지 알기 어렵습니다. 또한 기록 데이터가 쌓일수록 주간 통계 조회 속도가 느려지는 문제가 발생했습니다.

### Solution

- 사용자 프로필 기반 권장 칼로리, 탄수화물, 단백질, 지방 목표량 계산
- 식단 기록, 음식 검색, 주간 통계, 체중 변화 API 설계
- 주간 통계 조회 성능 개선을 위해 복합 인덱스와 집계 쿼리 최적화 적용
- 자주 조회되는 음식 데이터에 Redis cache 적용
- 사용자별 목표 변경 이력을 저장하여 과거 기록과 현재 목표를 분리 관리

### Key Contributions

- 전체 ERD 설계 및 핵심 도메인 모델 구현
- 회원가입, 로그인, 이메일 중복 확인, JWT 인증 API 구현
- 식단 기록 생성·수정·삭제 시 사용자 권한 검증 로직 구현
- JPA dirty checking과 transaction boundary를 고려한 서비스 계층 설계
- 주간 통계 조회 API에서 N+1 문제를 해결하고 DTO projection 적용
- MySQL slow query log를 분석하여 index 적용 전후 성능 비교
- 공통 응답 형식, 공통 예외 처리, validation error response 표준화
- Docker Compose로 local 개발 환경을 통일
- GitHub Actions로 build, test 자동화
- AWS EC2, RDS, Nginx를 활용해 HTTPS 배포

### Impact

- 주간 통계 조회 평균 응답 시간 1.2초에서 280ms로 개선
- 식단 상세 조회 API 쿼리 수 35개에서 6개로 감소
- Redis cache 적용 후 음식 검색 API 평균 응답 시간 540ms에서 130ms로 개선
- 테스트 사용자 45명 기준 4주간 식단 기록 유지율 49% 달성
- 백엔드 API 42개 구현
- 주요 서비스 로직 테스트 78개 작성

### Tech Stack

Java, Spring Boot, Spring Security, JPA, QueryDSL, MySQL, Redis, Docker, AWS EC2, AWS RDS, Nginx, GitHub Actions

---

### Project 2. StudyMate — 스터디 매칭 및 일정 관리 플랫폼

GitHub: https://github.com/doyoon-backend/studymate  
Period: 2024.11 - 2025.02  
Role: BackEnd Developer

관심 기술, 지역, 온라인 여부, 일정 조건을 기반으로 스터디 그룹을 만들고 참여할 수 있는 플랫폼입니다.

### Problem

스터디 모집은 커뮤니티 게시글 중심으로 이루어져 신청 현황, 일정 조율, 멤버 관리가 어렵습니다. 특히 모집 마감, 승인, 탈퇴, 알림 처리에서 상태 관리가 복잡해집니다.

### Solution

- 스터디 생성, 신청, 승인, 거절, 탈퇴, 마감 상태를 명확한 상태 모델로 설계
- 신청 승인 시 정원 초과를 방지하기 위해 transaction과 pessimistic lock 적용
- 스터디 일정 생성 및 참여자 알림 기능 구현
- 관심 기술 태그 기반 검색 API 구현
- 알림 발송 실패를 고려한 재시도 가능한 구조 설계

### Key Contributions

- Study, Application, Member, Schedule, Notification 도메인 설계
- 스터디 신청 승인 과정에서 동시 요청 시 정원 초과가 발생하는 문제를 lock으로 해결
- QueryDSL을 활용해 기술 태그, 모집 상태, 지역, 온라인 여부 조건 검색 구현
- 신청 승인, 일정 등록 이벤트 발생 시 알림 테이블에 저장
- WebSocket 기반 실시간 알림 prototype 구현
- 테스트 코드로 동시성 승인 시나리오 검증
- API 문서를 Swagger로 관리하고 프론트엔드와 응답 스펙 협의

### Impact

- 동시 신청 테스트 100건 기준 정원 초과 발생률 0% 달성
- 복합 검색 API 평균 응답 시간 650ms에서 190ms로 개선
- 스터디 신청 상태 관련 버그 6건을 상태 enum과 validation 로직으로 해결
- 팀 프로젝트 내 백엔드 API 38개 중 25개 담당
- 동시성 테스트 코드 12개 작성

### Tech Stack

Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, WebSocket, JUnit5, Docker

---

### Project 3. OrderFlow — 주문·결제·재고 관리 API 서버

GitHub: https://github.com/doyoon-backend/orderflow  
Period: 2024.08 - 2024.10  
Role: BackEnd Developer

이커머스 환경에서 상품 주문, 결제 요청, 재고 차감, 주문 취소를 처리하는 백엔드 API 서버입니다.

### Problem

주문과 재고 차감은 여러 사용자가 동시에 접근할 수 있어 데이터 정합성이 중요합니다. 단순 CRUD 방식으로 구현하면 재고가 음수가 되거나 결제 실패 후 주문 상태가 잘못 남을 수 있습니다.

### Solution

- 주문 생성, 결제 요청, 결제 성공, 결제 실패, 주문 취소 상태 흐름 설계
- 재고 차감 시 pessimistic lock과 optimistic lock 방식 비교
- 결제 실패 시 주문 상태 rollback 및 재고 복구 로직 구현
- 주문 상태 변경 이력을 별도 테이블에 저장
- idempotency key를 활용한 중복 주문 요청 방지

### Key Contributions

- Product, Order, OrderItem, Payment, StockHistory 도메인 설계
- 주문 생성 시 상품 가격 snapshot을 저장하여 가격 변경 이슈 방지
- 결제 API timeout 상황을 고려한 pending 상태 설계
- 재고 차감 로직에 동시성 테스트 작성
- 주문 취소 시 상태 검증과 재고 복구 트랜잭션 구현
- idempotency key 기반 중복 요청 방지 filter 구현
- 테스트 환경에서 Testcontainers를 활용해 MySQL 통합 테스트 수행

### Impact

- 동시 주문 요청 300건 기준 재고 정합성 유지
- 중복 주문 요청 방지 로직 적용 후 중복 주문 생성 0건
- 주문 상태 변경 이력 저장으로 디버깅 시간 단축
- 핵심 주문 서비스 테스트 커버리지 84% 달성

### Tech Stack

Java, Spring Boot, JPA, MySQL, Redis, JUnit5, Testcontainers, Docker

---

## Education

### 한국대학교 컴퓨터공학과

2020.03 - 2026.02 예정  
GPA: 4.17 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 데이터베이스
- 컴퓨터네트워크
- 소프트웨어공학
- 객체지향프로그래밍
- 웹프로그래밍

---

## Awards / Activities

### 2025 교내 웹 서비스 개발 경진대회 대상

2025.05

- MealBalance 프로젝트로 대상 수상
- 식단 기록과 주간 영양 분석 기능을 안정적인 API 구조로 구현
- 성능 개선 과정과 테스트 결과를 발표하여 기술 완성도 항목 최고점 획득

### Backend Engineering Study Lead

2024.09 - 2025.06

- 10명 규모의 백엔드 스터디 운영
- 주제: Spring Boot, JPA, transaction, Redis, DB index, 테스트 코드, AWS 배포
- 매주 코드 리뷰와 장애 사례 분석 진행

### Open Source Contribution

2025.02 - 2025.04

- Spring Boot sample project README 개선
- Docker Compose 기반 local 실행 환경 문서화
- validation error response 예제 추가

---

## Certifications

- SQLD
- 정보처리기사 필기 합격
- AWS Certified Cloud Practitioner 준비 중

---

## Technical Writing

- "JPA N+1 문제를 발견하고 해결한 과정"
- "식단 통계 API 응답 시간을 1.2초에서 280ms로 줄인 방법"
- "Redis Cache를 적용할 때 고려해야 할 TTL과 무효화 전략"
- "주문 시스템에서 동시성 문제를 테스트하는 방법"
- "Spring Boot 예외 처리 구조를 표준화한 경험"

---

## Strengths

- 단순 기능 구현보다 데이터 정합성, 성능, 테스트, 운영 가능성을 함께 고려합니다.
- JPA와 MySQL을 사용할 때 쿼리 수, 인덱스, 트랜잭션 범위를 의식하며 개발합니다.
- API 명세, 에러 응답, 인증 구조를 일관성 있게 설계합니다.
- 팀 프로젝트에서 프론트엔드 개발자와 적극적으로 API 스펙을 조율한 경험이 있습니다.
- 신입 수준에서 요구되는 CRUD를 넘어 캐싱, 동시성, 배포, 테스트까지 경험했습니다.

---

## Resume Keywords

BackEnd Engineer, Java, Spring Boot, Spring Security, JPA, QueryDSL, MySQL, Redis, REST API, JWT, OAuth2, Docker, AWS EC2, AWS RDS, Nginx, GitHub Actions, JUnit5, Mockito, Testcontainers, Transaction, Database Indexing, Query Optimization, Caching, Concurrent Request, API Design

---

# 2. Big Tech / Enterprise Target Resume — BackEnd Engineer

## 이서현 | BackEnd Engineer

Email: seohyun.lee.backend@gmail.com  
GitHub: https://github.com/seohyun-backend  
Portfolio: https://seohyun-backend.dev  
Blog: https://tech.seohyun-backend.dev  
LinkedIn: https://linkedin.com/in/seohyun-lee-backend  

---

## Summary

대규모 서비스 환경에서 안정적이고 확장 가능한 서버를 설계하는 데 관심이 있는 신입 BackEnd Engineer입니다.

Java, Spring Boot, JPA, MySQL, Redis, Kafka, Docker, AWS를 활용해 주문, 알림, 검색, 인증, 관리자 API를 구현했습니다. 특히 트랜잭션 정합성, 동시성 제어, DB 인덱싱, 캐시 전략, 비동기 처리, 테스트 자동화, 장애 대응 가능성을 중요하게 생각합니다.

대기업·중견기업·빅테크 환경에서 요구되는 안정성, 확장성, 가독성, 협업 가능성을 기준으로 코드를 작성하며, 기능 구현 후 반드시 성능 측정과 테스트를 통해 개선합니다.

---

## Core Competencies

- Java / Spring Boot 기반 백엔드 API 개발
- 도메인 중심 설계 및 계층형 아키텍처 구성
- MySQL 트랜잭션, lock, index 기반 정합성 관리
- Redis cache, distributed lock, rate limit 구현
- Kafka 기반 비동기 이벤트 처리
- 대용량 데이터 조회 성능 개선
- 테스트 가능한 서비스 계층 설계
- CI/CD 및 배포 자동화
- API 장애 로그 분석 및 재발 방지
- 코드 리뷰 기반 협업

---

## Skills

### Language

- Java
- Kotlin Basic
- SQL
- Python
- Bash

### Backend

- Spring Boot
- Spring MVC
- Spring Security
- Spring Data JPA
- QueryDSL
- Spring Batch Basic
- REST API
- JWT
- OAuth2
- Validation
- Global Exception Handling

### Database / Data

- MySQL
- PostgreSQL
- Redis
- Elasticsearch
- H2
- Database Index
- Transaction Isolation
- Pessimistic Lock
- Optimistic Lock
- Pagination
- Query Optimization

### Messaging / Async

- Kafka
- RabbitMQ Basic
- Event-driven Architecture
- Outbox Pattern Basic
- Retry
- Dead Letter Queue Concept

### Infra / DevOps

- AWS EC2
- AWS RDS
- AWS S3
- AWS CloudWatch Basic
- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Linux

### Test / Quality

- JUnit5
- Mockito
- AssertJ
- Testcontainers
- Spring Rest Docs
- Locust
- SonarLint
- Postman

---

## Experience

### BackEnd Engineer Intern

**CommerceCore Korea**  
2025.06 - 2025.12

이커머스 주문·상품·알림 시스템을 운영하는 플랫폼 개발팀에서 백엔드 인턴으로 근무했습니다.

### Key Contributions

- Spring Boot 기반 주문 조회, 주문 취소, 상품 재고 조회, 관리자 주문 검색 API 개발
- 주문 조회 API에서 발생한 N+1 문제를 fetch join과 batch size 설정으로 개선하여 쿼리 수 121개에서 9개로 감소
- 대용량 주문 검색 API에 복합 인덱스와 cursor pagination을 적용하여 p95 응답 시간 2.8초에서 620ms로 개선
- Redis cache를 적용해 상품 상세 API의 DB 조회량을 약 43% 감소
- 주문 상태 변경 이벤트를 Kafka로 발행하고 알림 서비스가 비동기로 소비하는 구조 구현
- 결제 실패 후 주문 상태 불일치 케이스를 분석하고 상태 전이 validation 로직 추가
- 관리자 API의 검색 조건이 늘어나면서 복잡해진 쿼리를 QueryDSL 기반 동적 쿼리로 리팩터링
- JUnit5, Mockito, Testcontainers를 활용해 주문 상태 변경과 재고 차감 통합 테스트 작성
- GitHub Actions build-test-deploy pipeline에서 테스트 실패 시 배포가 중단되도록 개선
- 운영 로그를 기반으로 400, 401, 409, 500 error를 분류하고 공통 에러 코드 문서화

### Impact

- 주문 검색 API p95 응답 시간 78% 개선
- 상품 상세 API DB read traffic 43% 감소
- 주문 상태 관련 CS 문의 재현 시간을 30분에서 10분 이내로 단축
- 주문·재고 핵심 로직 테스트 96개 작성
- 사내 코드 리뷰에서 "신입 인턴이지만 운영 관점까지 고려한 구현"이라는 피드백 수신

### Tech Stack

Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, Kafka, Docker, AWS EC2, AWS RDS, GitHub Actions

---

## Projects

---

### Project 1. OrderHub — 대용량 주문·재고 처리 시스템

GitHub: https://github.com/seohyun-backend/orderhub  
Demo: https://orderhub.dev  
Period: 2025.02 - 2025.05  
Role: BackEnd Lead

상품 주문, 재고 차감, 결제 상태 관리, 주문 취소, 관리자 검색 기능을 포함한 이커머스 백엔드 시스템입니다.

### Problem

이커머스 서비스에서는 동시에 많은 사용자가 같은 상품을 주문할 수 있고, 주문·결제·재고 상태가 일관되지 않으면 실제 비즈니스 장애로 이어질 수 있습니다.

### Solution

- 주문 생성, 결제 대기, 결제 완료, 결제 실패, 주문 취소 상태 모델 설계
- 재고 차감 시 optimistic lock과 pessimistic lock 성능 비교
- 주문 생성 요청에 idempotency key 적용
- 주문 상태 변경 이벤트를 Kafka로 발행
- 관리자 주문 검색 API에 cursor pagination과 index 적용
- 주문 상태 변경 이력을 저장하여 장애 분석 가능성 확보

### Technical Details

- Product, Stock, Order, OrderItem, Payment, OrderHistory 도메인 설계
- 주문 생성 시 상품 가격 snapshot 저장
- 동일 요청 재처리를 방지하기 위해 Redis에 idempotency key 저장
- 결제 실패 이벤트 발생 시 주문 상태와 재고 복구를 하나의 transaction으로 처리
- 재고 차감 시 version field 기반 optimistic lock 적용
- 높은 충돌 상황에서는 pessimistic lock이 더 안정적인 것을 부하 테스트로 검증
- Kafka producer callback을 활용해 이벤트 발행 실패 로그 저장
- 주문 검색 API에서 offset pagination을 cursor pagination으로 변경
- created_at, status, user_id 복합 인덱스 적용
- Testcontainers를 활용해 MySQL 기반 통합 테스트 구성

### Impact

- 동시 주문 요청 1,000건 테스트에서 재고 정합성 유지
- 중복 주문 요청 0건 달성
- 관리자 주문 검색 p95 응답 시간 3.1초에서 540ms로 개선
- offset pagination 대비 deep page 조회 성능 86% 개선
- 주문 상태 변경 이력 저장으로 실패 케이스 추적 가능
- 핵심 도메인 테스트 커버리지 87% 달성

### Tech Stack

Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, Kafka, Docker, Testcontainers, GitHub Actions, AWS EC2

---

### Project 2. NotifyLink — 이벤트 기반 알림 시스템

GitHub: https://github.com/seohyun-backend/notifylink  
Period: 2024.11 - 2025.01  
Role: BackEnd Developer

서비스 내 주문, 댓글, 팔로우, 시스템 공지 이벤트를 받아 사용자에게 알림을 발송하는 비동기 알림 서버입니다.

### Problem

주요 서비스 로직에서 알림 발송을 동기 처리하면 외부 API 지연이나 실패가 전체 요청 속도와 안정성에 영향을 줍니다.

### Solution

- 도메인 이벤트를 Kafka topic으로 발행
- 알림 서버가 이벤트를 소비하여 알림 데이터 저장
- 발송 실패 시 retry count와 next retry time을 관리
- 중복 이벤트 처리를 방지하기 위해 event idempotency 적용
- 사용자별 읽지 않은 알림 수를 Redis로 관리

### Key Contributions

- NotificationEvent schema 설계
- Kafka consumer group 기반 이벤트 소비 구조 구현
- 알림 저장과 발송 요청을 분리하여 장애 격리
- 동일 eventId 중복 수신 시 무시하도록 unique constraint 적용
- Redis를 활용해 unread count 조회 API 응답 시간 개선
- 실패한 알림을 재처리하는 batch job 구현
- 알림 목록 조회 API에 cursor pagination 적용
- 부하 테스트를 통해 batch size와 consumer concurrency 조정

### Impact

- 알림 발송 로직 분리 후 주문 API 평균 응답 시간 410ms에서 180ms로 개선
- 중복 알림 생성 0건 달성
- 읽지 않은 알림 수 조회 평균 응답 시간 95ms 이하 유지
- 이벤트 10만 건 처리 테스트에서 consumer lag 안정화
- 알림 실패 재처리 성공률 96% 달성

### Tech Stack

Java, Spring Boot, Kafka, MySQL, Redis, Spring Batch, Docker, JUnit5

---

### Project 3. SearchBoard — 대용량 게시글 검색 API

GitHub: https://github.com/seohyun-backend/searchboard  
Period: 2024.08 - 2024.10  
Role: BackEnd Developer

게시글 100만 건을 대상으로 키워드 검색, 태그 검색, 정렬, 필터링을 제공하는 검색 API 서버입니다.

### Problem

게시글 데이터가 많아질수록 LIKE 기반 검색과 offset pagination은 응답 속도가 급격히 느려집니다.

### Solution

- MySQL index 기반 검색 성능 한계 측정
- Elasticsearch를 활용한 전문 검색 구현
- 인기 게시글과 최신 게시글 조회에 Redis cache 적용
- offset pagination을 cursor pagination으로 개선
- 검색어 로그를 저장해 인기 검색어 API 구현

### Key Contributions

- 게시글 bulk insert script 작성
- MySQL LIKE 검색, full-text index, Elasticsearch 검색 성능 비교
- Elasticsearch index mapping 설계
- 검색 결과 정렬 기준을 relevance, latest, view count로 분리
- Redis sorted set을 활용한 인기 검색어 저장
- 검색 API 부하 테스트 및 병목 분석
- API 응답 DTO를 경량화하여 네트워크 응답 크기 감소

### Impact

- 100만 건 기준 검색 API 평균 응답 시간 2.4초에서 180ms로 개선
- deep pagination 응답 시간 1.8초에서 240ms로 개선
- 인기 게시글 API cache hit rate 72% 달성
- 검색 결과 응답 payload 크기 38% 감소

### Tech Stack

Java, Spring Boot, MySQL, Elasticsearch, Redis, Docker, Locust, JUnit5

---

## Education

### 서울기술대학교 컴퓨터공학부

2020.03 - 2026.02 예정  
GPA: 4.25 / 4.5  
Major GPA: 4.34 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 데이터베이스
- 컴퓨터네트워크
- 분산시스템
- 소프트웨어공학
- 객체지향설계

---

## Awards

### 2025 SW 중심대학 공동 해커톤 최우수상

2025.08

- OrderHub 프로젝트로 최우수상 수상
- 주문·재고 동시성 문제를 해결하고 부하 테스트 결과를 발표
- 정합성과 확장성을 고려한 백엔드 설계로 높은 평가를 받음

### 2024 교내 알고리즘 경진대회 은상

2024.11

- 150명 중 8위
- Graph, DP, Binary Search, Greedy 문제 풀이

---

## Activities

### Backend Performance Study Lead

2025.01 - 2025.06

- 12명 규모의 백엔드 성능 개선 스터디 운영
- 주제: DB index, JPA N+1, Redis cache, Kafka, lock, 부하 테스트
- 매주 성능 개선 전후 결과를 수치로 정리
- 팀원 코드 리뷰와 성능 테스트 리포트 작성

### CS Interview Study

2024.07 - 2024.12

- 운영체제, 네트워크, 데이터베이스, 알고리즘 면접 스터디 참여
- TCP 3-way handshake, transaction isolation, deadlock, indexing, cache consistency 주제 발표

---

## Certifications

- SQLD
- 정보처리기사 필기 합격
- AWS Certified Cloud Practitioner
- TOEIC Speaking IH

---

## Technical Writing

- "주문 시스템에서 동시성 문제를 해결한 세 가지 방법"
- "Offset Pagination을 Cursor Pagination으로 바꾼 이유"
- "JPA N+1 문제를 쿼리 수 기준으로 개선한 과정"
- "Kafka를 알림 시스템에 적용하면서 배운 점"
- "MySQL Index 설계 전후 성능 비교"

---

## Strengths

- 백엔드 기능을 구현할 때 데이터 정합성과 장애 상황을 먼저 고려합니다.
- 성능 개선을 감각이 아니라 측정 결과로 설명합니다.
- 테스트 코드와 부하 테스트를 통해 구현의 안정성을 검증합니다.
- 대기업·빅테크에서 중요하게 보는 CS 기본기, API 설계, DB, 캐시, 비동기 처리 경험을 갖추고 있습니다.
- 코드 리뷰에서 읽기 쉬운 구조와 명확한 책임 분리를 중요하게 생각합니다.

---

## Resume Keywords

BackEnd Engineer, Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, Kafka, Elasticsearch, REST API, Spring Security, JWT, OAuth2, Docker, AWS, GitHub Actions, JUnit5, Mockito, Testcontainers, Transaction, Lock, Optimistic Lock, Pessimistic Lock, Database Index, Cursor Pagination, Query Optimization, Caching, Event-driven Architecture, Distributed System

---

# 3. Tech Startup Target Resume — BackEnd Engineer

## 박민재 | BackEnd Engineer

Email: minjae.park.backend@gmail.com  
GitHub: https://github.com/minjae-startup-backend  
Portfolio: https://minjae-backend.dev  
Blog: https://blog.minjae-backend.dev  
LinkedIn: https://linkedin.com/in/minjae-park-backend  

---

## Summary

빠르게 제품을 만들고 실제 사용자 피드백을 기반으로 서버를 개선하는 데 강점이 있는 신입 BackEnd Engineer입니다.

Spring Boot, Node.js, MySQL, Redis, Supabase, Docker, AWS, Vercel을 활용해 MVP부터 운영 가능한 API 서버까지 직접 개발했습니다. 작은 팀에서 요구사항 정리, ERD 설계, API 구현, 배포, 로그 분석, 성능 개선, 관리자 기능 개발까지 주도한 경험이 있습니다.

스타트업 환경에서 중요한 빠른 실행력, 제품 이해도, 오너십을 갖추고 있으며, 사용자의 문제를 해결하기 위해 백엔드 구조를 단순하고 빠르게 만들되 이후 확장 가능한 방향으로 개선하는 것을 지향합니다.

---

## Core Competencies

- MVP Backend Development
- 빠른 API 설계 및 배포
- Spring Boot / Node.js 기반 서버 개발
- 인증, 결제, 알림, 관리자 기능 구현
- MySQL / PostgreSQL 기반 데이터 모델링
- Redis cache 및 rate limit 구현
- AWS / Vercel / Railway 기반 빠른 배포
- Product Metrics 기반 기능 개선
- 사용자 피드백 기반 API 개선
- 작은 팀에서의 end-to-end ownership

---

## Skills

### Language

- Java
- TypeScript
- JavaScript
- SQL
- Python

### Backend

- Spring Boot
- Spring Security
- JPA
- QueryDSL
- Node.js
- Express
- NestJS Basic
- REST API
- JWT
- OAuth2
- WebSocket
- Cron Job

### Database / Storage

- MySQL
- PostgreSQL
- Redis
- Supabase
- Firebase
- AWS S3
- Database Index
- Transaction

### Infra / DevOps

- AWS EC2
- AWS RDS
- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Vercel
- Railway
- Render
- Cloudflare

### Product / Collaboration

- Swagger
- Postman
- Notion
- Slack
- Linear
- Google Analytics
- Mixpanel Basic
- Amplitude Basic

---

## Experience

### Founding BackEnd Engineer Intern

**LocalLoop**  
2025.05 - 2025.11

동네 기반 소모임·예약 플랫폼을 만드는 초기 스타트업에서 백엔드 인턴으로 근무했습니다.

### Key Contributions

- MVP 단계에서 회원, 소모임, 예약, 결제 요청, 알림, 관리자 API를 8주 안에 구현
- Spring Boot 기반 API 서버를 설계하고 AWS EC2, RDS, S3, Nginx 환경에 배포
- 카카오 OAuth 로그인과 JWT 인증 구조를 구현하여 회원가입 전환율 개선
- 소모임 예약 시 정원 초과 문제를 transaction과 lock으로 해결
- Redis를 활용해 인기 소모임 목록과 지역별 추천 데이터를 캐싱
- 예약 확정, 취소, 마감 이벤트에 대한 알림 기능 구현
- 관리자 페이지용 신고 조회, 유저 제재, 소모임 비공개 처리 API 구현
- 사용자 행동 로그를 기반으로 예약 생성 funnel을 분석하고 API 응답 속도 병목 개선
- 초기 사용자 300명 규모의 베타 운영 중 발생한 장애 로그를 분석하고 재발 방지 처리
- 디자이너, 프론트엔드 개발자와 매일 API 스펙을 조율하며 빠른 배포 사이클 유지

### Startup Impact

- MVP 출시 후 6주간 가입자 380명 확보
- 소모임 예약 전환율 18%에서 31%로 개선
- 인기 소모임 API 평균 응답 시간 920ms에서 170ms로 개선
- 예약 중복 생성 이슈 0건으로 감소
- 관리자 CS 처리 시간을 줄이는 내부 API 14개 구현
- 2주 단위 product iteration 5회 참여

### Tech Stack

Java, Spring Boot, JPA, MySQL, Redis, AWS EC2, AWS RDS, AWS S3, Docker, Nginx, GitHub Actions

---

## Projects

---

### Project 1. LocalMeet — 지역 기반 모임·예약 플랫폼

GitHub: https://github.com/minjae-startup-backend/localmeet  
Demo: https://localmeet.dev  
Period: 2025.01 - 2025.04  
Role: Founder / BackEnd Engineer

지역 기반으로 소모임을 만들고, 사용자가 날짜별로 신청·예약할 수 있는 커뮤니티 플랫폼입니다.

### Problem

초기 커뮤니티 서비스는 빠르게 출시해야 하지만, 예약·정원·승인·취소와 같은 기능은 데이터 정합성이 중요합니다. 또한 작은 팀에서는 관리자 기능이 부족하면 CS 대응 속도가 느려집니다.

### Solution

- 회원, 모임, 일정, 예약, 결제 요청, 알림, 신고, 관리자 도메인 설계
- 정원 초과를 방지하기 위해 예약 생성 transaction과 lock 적용
- 카카오 OAuth 로그인과 JWT 인증 구현
- 인기 모임, 지역별 모임 목록에 Redis cache 적용
- 관리자용 유저 제재, 신고 처리, 모임 비공개 API 구현
- 예약 funnel 데이터를 저장하여 이탈 구간 분석 가능하도록 설계

### Key Contributions

- 전체 ERD 설계 및 API 55개 구현
- 예약 생성 시 동일 유저 중복 예약과 정원 초과를 동시에 검증
- 예약 취소 시 결제 상태와 예약 상태를 분리하여 상태 꼬임 방지
- Redis cache TTL을 모임 상태 변경 이벤트와 함께 갱신
- S3 presigned URL 기반 이미지 업로드 구현
- 예약 생성, 취소, 마감 이벤트에 따른 알림 로직 구현
- 관리자 권한과 일반 사용자 권한을 Spring Security로 분리
- Docker Compose로 local 개발 환경 구성
- AWS EC2, RDS, S3, Nginx 기반 HTTPS 배포
- 사용자 인터뷰를 통해 "모임 개설자 관리 기능 부족" 문제를 발견하고 호스트 대시보드 API 추가

### Impact

- 베타 사용자 210명 확보
- 모임 생성 84건, 예약 신청 430건 발생
- 예약 생성 API 평균 응답 시간 620ms에서 190ms로 개선
- 인기 모임 API cache hit rate 76% 달성
- 예약 중복 생성 이슈 0건 달성
- 관리자 신고 처리 시간 평균 15분에서 5분 이하로 단축
- 1인 백엔드로 MVP 설계, 구현, 배포, 운영까지 완료

### Tech Stack

Java, Spring Boot, Spring Security, JPA, QueryDSL, MySQL, Redis, AWS EC2, AWS RDS, AWS S3, Docker, Nginx, GitHub Actions

---

### Project 2. LaunchCart — 소규모 브랜드용 주문 관리 API

GitHub: https://github.com/minjae-startup-backend/launchcart  
Period: 2024.10 - 2024.12  
Role: BackEnd Developer

소규모 브랜드가 상품을 등록하고 주문을 관리할 수 있는 경량 이커머스 백엔드 API입니다.

### Problem

초기 브랜드는 복잡한 커머스 솔루션보다 빠르게 상품을 등록하고 주문을 받을 수 있는 단순한 시스템이 필요합니다. 하지만 주문, 결제, 재고, 배송 상태는 최소한의 정합성이 보장되어야 합니다.

### Solution

- 상품 등록, 옵션 관리, 장바구니, 주문 생성, 주문 취소, 배송 상태 API 구현
- 주문 생성 시 상품 가격과 옵션 정보를 snapshot으로 저장
- 재고 차감과 주문 상태 변경을 하나의 transaction으로 관리
- 관리자용 주문 검색과 상태 변경 API 구현
- 외부 결제 API 연동을 가정한 payment callback endpoint 구현

### Key Contributions

- Product, ProductOption, Cart, Order, Payment, Delivery 도메인 설계
- 주문 생성 시 재고 부족, 품절, 가격 변경 케이스 처리
- payment callback 중복 수신을 고려해 idempotency 처리
- 주문 검색 API에 상태, 날짜, 유저 조건 기반 QueryDSL 동적 쿼리 적용
- 주문 목록 조회에 cursor pagination 적용
- 관리자 주문 메모와 상태 변경 이력 저장 기능 구현
- API 명세를 Swagger로 제공하여 프론트엔드 개발 속도 개선

### Impact

- 주문 생성부터 배송 상태 변경까지 전체 flow 구현
- 중복 결제 callback 처리 시 주문 상태 중복 변경 0건
- 관리자 주문 검색 API 평균 응답 시간 720ms에서 230ms로 개선
- API 명세 기반 협업으로 프론트엔드 연동 오류 감소
- 주문 상태 관련 테스트 코드 48개 작성

### Tech Stack

Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, Docker, Swagger, JUnit5

---

### Project 3. TeamPulse — 팀 업무 공유 및 알림 서비스

GitHub: https://github.com/minjae-startup-backend/teampulse  
Period: 2024.07 - 2024.09  
Role: Full-stack / BackEnd Focus

작은 팀이 업무를 공유하고 댓글, 멘션, 마감일 알림을 받을 수 있는 협업 도구입니다.

### Problem

초기 팀에서는 업무 공유가 메신저 중심으로 이루어져 담당자, 마감일, 변경 이력이 누락되기 쉽습니다.

### Solution

- 워크스페이스, 프로젝트, 태스크, 댓글, 멘션, 알림 도메인 설계
- 멘션 발생 시 알림 생성
- 마감일이 임박한 태스크를 cron job으로 탐색하여 알림 발송
- WebSocket 기반 실시간 알림 prototype 구현
- 태스크 변경 이력을 저장하여 추적 가능하도록 설계

### Key Contributions

- Node.js Express 기반 prototype 구현 후 Spring Boot로 마이그레이션
- Workspace별 사용자 권한 관리 구현
- 태스크 상태 변경 이력을 TaskHistory로 저장
- 댓글 작성 시 멘션 파싱 후 알림 생성
- Redis pub/sub을 활용한 실시간 알림 prototype 구현
- 프로젝트별 태스크 통계 API 구현
- 초기 사용자 피드백을 반영해 태스크 quick update API 추가

### Impact

- 팀 사용자 7개 그룹, 총 64명 테스트
- 태스크 생성 후 담당자 지정률 37%에서 68%로 개선
- 마감일 누락 피드백 40% 감소
- 실시간 알림 적용 후 댓글 확인 지연 감소
- prototype에서 production 구조로 리팩터링하며 API 응답 형식 표준화

### Tech Stack

Java, Spring Boot, Node.js, Express, MySQL, Redis, WebSocket, Docker, AWS EC2

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 예정  
GPA: 4.08 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 웹프로그래밍
- 운영체제
- 컴퓨터네트워크
- 소프트웨어공학
- 창업과 소프트웨어 제품 개발

---

## Awards / Activities

### 2025 대학 연합 사이드프로젝트 경진대회 대상

2025.06

- LocalMeet 프로젝트로 대상 수상
- 빠른 MVP 출시, 실제 사용자 테스트, 예약 정합성 개선 경험을 발표
- "제품 문제 해결과 백엔드 안정성을 모두 고려했다"는 평가를 받음

### 2024 스타트업 MVP 해커톤 최우수상

2024.12

- LaunchCart 프로젝트로 최우수상 수상
- 소규모 브랜드를 위한 주문 관리 API와 관리자 기능 구현
- 48시간 안에 기획, API 구현, 배포까지 완료

### Product Engineering Study Organizer

2024.09 - 2025.05

- 15명 규모의 제품 개발 스터디 운영
- 주제: MVP 설계, API 우선순위, 사용자 피드백, 백엔드 확장성
- 매주 실제 서비스 하나를 분석하고 API 구조를 역설계

---

## Certifications

- SQLD
- 정보처리기사 필기 준비 중
- AWS Cloud Practitioner 준비 중

---

## Product Metrics Experience

- Signup Conversion
- Reservation Conversion Rate
- API Response Time
- Cache Hit Rate
- Admin Processing Time
- Weekly Active Users
- Funnel Drop-off
- Error Rate
- Retention Basic
- User Feedback Score

---

## Technical Writing

- "스타트업 MVP에서 백엔드가 먼저 챙겨야 할 것"
- "예약 서비스에서 정원 초과를 막는 방법"
- "Redis Cache로 인기 모임 API를 개선한 과정"
- "관리자 API가 초기 서비스 운영에 중요한 이유"
- "작은 팀에서 API 명세를 빠르게 맞추는 방법"

---

## Strengths

- 요구사항이 불명확한 상황에서도 빠르게 API 구조를 잡고 MVP를 출시할 수 있습니다.
- 제품 지표와 사용자 피드백을 기반으로 백엔드 우선순위를 조정합니다.
- 작은 팀에서 백엔드, 배포, 관리자 기능, 장애 대응까지 넓게 책임질 수 있습니다.
- 빠른 개발 속도와 최소한의 안정성 사이에서 균형을 잡습니다.
- 스타트업에서 중요한 오너십, 실행력, 제품 이해도를 갖추고 있습니다.

---

## Resume Keywords

BackEnd Engineer, Startup Engineer, Java, Spring Boot, Node.js, Express, JPA, QueryDSL, MySQL, PostgreSQL, Redis, REST API, JWT, OAuth2, Docker, AWS EC2, AWS RDS, AWS S3, Nginx, GitHub Actions, MVP, Product Metrics, API Design, Reservation System, Payment Flow, Admin API, Cache, Transaction, Lock, User Feedback, Fast Iteration