# Data Engineer Resume Set

> Target: Korea / Entry-level Developer / Max Internship Experience  
> Role: Data Engineer  
> Purpose: 100-point benchmark resumes for comparing junior developer resumes  
> Reference Basis: 한국 및 글로벌 Data Engineer 채용·Resume 흐름에서 반복적으로 요구되는 Python, SQL, Airflow, Spark, Kafka, AWS, ETL/ELT, Data Warehouse, Data Quality, Monitoring, Batch/Streaming Pipeline 역량을 기준으로 구성함.  
> Note: 아래 Resume은 특정 개인의 이력서를 복제한 것이 아니라, 실제 채용 시장에서 강하게 평가되는 데이터 엔지니어 역량 패턴을 기반으로 재구성한 고품질 비교군 Resume입니다.

---

# 1. Common Resume — Data Engineer

## 김도윤 | Data Engineer

Email: doyoon.kim.data@gmail.com  
GitHub: https://github.com/doyoon-data  
Portfolio: https://doyoon-data.dev  
Blog: https://blog.doyoon-data.dev  
LinkedIn: https://linkedin.com/in/doyoon-kim-data  

---

## Summary

데이터를 안정적으로 수집·정제·적재하고, 분석과 제품 의사결정에 활용 가능한 형태로 만드는 데 집중하는 신입 Data Engineer입니다.

Python, SQL, Airflow, Spark, Kafka, PostgreSQL, BigQuery, Docker, AWS를 활용해 배치·스트리밍 데이터 파이프라인을 직접 설계하고 구축했습니다. 단순 데이터 처리 스크립트 작성이 아니라 **데이터 품질, 재처리 가능성, 스케줄링, 모니터링, 파티셔닝, 쿼리 성능, 데이터 신선도**까지 고려한 데이터 엔지니어링 경험이 있습니다.

팀 프로젝트에서는 서비스 로그, 사용자 이벤트, 주문 데이터, 리뷰 데이터를 수집하여 Data Mart와 Dashboard를 구성했고, 데이터 분석가와 백엔드 개발자가 신뢰할 수 있는 데이터 기반으로 일할 수 있도록 데이터 모델과 파이프라인을 개선했습니다.

---

## Core Competencies

- Python / SQL 기반 데이터 처리
- Airflow 기반 Workflow Orchestration
- Spark 기반 대용량 데이터 처리
- Kafka 기반 실시간 이벤트 수집
- ETL / ELT Pipeline 설계
- Data Warehouse / Data Mart 모델링
- 데이터 품질 검증 및 이상 탐지
- Batch Pipeline 재처리 구조 설계
- Query Optimization 및 Partitioning
- AWS S3 / Glue / Redshift / Athena 활용
- Docker 기반 데이터 파이프라인 실행 환경 구성
- 분석가·백엔드·ML 엔지니어와의 협업

---

## Skills

### Language

- Python
- SQL
- Java Basic
- Bash
- JavaScript Basic

### Data Engineering

- Apache Airflow
- Apache Spark
- PySpark
- Apache Kafka
- dbt Basic
- ETL
- ELT
- Data Warehouse
- Data Mart
- Data Lake
- Batch Processing
- Stream Processing
- Data Quality Check
- Data Lineage Basic

### Database / Warehouse

- PostgreSQL
- MySQL
- BigQuery
- Redshift Basic
- Snowflake Basic
- MongoDB Basic
- Redis Basic

### Cloud / Infra

- AWS S3
- AWS EC2
- AWS RDS
- AWS Glue Basic
- AWS Athena
- AWS Lambda Basic
- Docker
- Docker Compose
- GitHub Actions
- Linux
- Nginx Basic

### Analytics / Visualization

- Pandas
- NumPy
- Jupyter
- Metabase
- Superset Basic
- Looker Studio
- Tableau Basic
- Google Analytics Basic

### Testing / Monitoring

- Pytest
- Great Expectations Basic
- Airflow SLA
- Data Quality Rule
- Logging
- Slack Alert
- Prometheus Basic
- Grafana Basic

---

## Experience

### Data Engineer Intern

**FitLogics**  
2025.07 - 2025.12

사용자 건강 데이터 기반 식단·운동 기록 서비스를 운영하는 스타트업에서 데이터 파이프라인과 분석용 데이터 마트를 구축했습니다.

### Key Contributions

- 서비스 DB의 사용자, 식단 기록, 체중 기록, 목표 설정 데이터를 분석용 PostgreSQL Data Mart로 적재하는 ETL pipeline 구현
- Airflow DAG 18개를 작성하여 일별·시간별 batch pipeline을 자동화
- 식단 기록 이벤트 로그를 Kafka로 수집하고 소비자 프로세스를 통해 raw event table에 적재
- 데이터 중복 적재 문제를 해결하기 위해 idempotent load 구조와 upsert strategy 적용
- 주간 영양 분석 dashboard에 필요한 user_daily_nutrition, user_weekly_summary mart table 설계
- SQL 집계 쿼리를 최적화하여 dashboard 평균 조회 시간을 4.2초에서 780ms로 개선
- 데이터 품질 검증 rule을 도입하여 null ratio, duplicate key, date range, foreign key mismatch를 매일 점검
- Pipeline 실패 시 Slack alert를 발송하고, 실패 지점부터 재처리할 수 있도록 task 단위 dependency 정리
- 분석가와 협업해 activation, retention, diet_record_completion 지표 정의
- 백엔드 개발자와 이벤트 스키마를 협의하여 user_id, session_id, event_time, event_type, properties 구조 표준화

### Impact

- 수동 SQL 리포트 작성 시간을 주 6시간에서 1시간 이하로 단축
- 주요 dashboard 조회 시간 81% 개선
- 데이터 누락 탐지까지 평균 1일 이상 걸리던 문제를 Airflow alert 기반 15분 이내 인지 가능하도록 개선
- 데이터 품질 검증 rule 36개 작성
- 일 평균 120만 건 이벤트 로그 적재 pipeline 안정화
- 데이터 마트 14개 테이블 설계 및 운영

### Tech Stack

Python, SQL, Airflow, Kafka, PostgreSQL, MySQL, Pandas, Docker, AWS EC2, AWS S3, Metabase

---

## Projects

---

### Project 1. LogLake — 서비스 이벤트 로그 데이터 파이프라인

GitHub: https://github.com/doyoon-data/loglake  
Demo: https://loglake.doyoon-data.dev  
Period: 2025.03 - 2025.06  
Role: Data Engineer

웹 서비스의 사용자 행동 이벤트를 수집하고, 분석 가능한 형태로 정제하여 Data Mart와 Dashboard를 제공하는 데이터 파이프라인 프로젝트입니다.

### Problem

서비스 로그가 애플리케이션 서버와 DB에 흩어져 있어 사용자의 행동 흐름을 분석하기 어려웠습니다. 또한 이벤트 스키마가 일관되지 않아 지표 계산 결과가 자주 달라지는 문제가 있었습니다.

### Solution

- Kafka 기반 사용자 이벤트 수집 구조 설계
- Raw, Staging, Mart 계층으로 데이터 저장 구조 분리
- Airflow를 활용해 일별 집계 batch pipeline 자동화
- 이벤트 스키마 validation과 데이터 품질 rule 적용
- Metabase dashboard로 activation, retention, conversion 지표 시각화
- 실패한 pipeline을 task 단위로 재처리할 수 있도록 설계

### Key Contributions

- event_name, user_id, session_id, event_time, page_url, properties 기반 이벤트 스키마 설계
- Kafka producer SDK prototype 작성
- Kafka consumer를 통해 raw_event table에 event log 적재
- Airflow DAG로 raw to staging, staging to mart 처리 자동화
- 중복 이벤트 제거를 위해 event_id 기준 deduplication 적용
- event_time 기준 partitioning으로 일별 집계 쿼리 성능 개선
- 사용자 funnel 분석용 mart_user_funnel 테이블 설계
- retention 분석용 cohort table 생성
- Pytest 기반 transformation logic 테스트 작성
- Slack alert로 DAG 실패, row count 급감, null ratio 증가 알림 구현

### Impact

- 일 평균 300만 건 이벤트 처리 pipeline 구축
- 이벤트 중복률 2.8%에서 0.2% 이하로 감소
- Funnel dashboard 조회 시간 5.6초에서 920ms로 개선
- 지표 계산 SQL 수동 실행 작업 90% 자동화
- 데이터 품질 이슈 탐지 시간을 평균 24시간에서 20분 이내로 단축
- 분석용 mart table 11개 구축

### Tech Stack

Python, SQL, Kafka, Airflow, PostgreSQL, Docker, Metabase, AWS EC2, AWS S3, Pytest

---

### Project 2. ReviewPipeline — 커머스 리뷰 데이터 수집·분석 파이프라인

GitHub: https://github.com/doyoon-data/reviewpipeline  
Period: 2024.11 - 2025.02  
Role: Data Engineer

커머스 리뷰 데이터를 수집, 정제, 분류하고 제품별 인사이트 Dashboard에 적재하는 데이터 파이프라인입니다.

### Problem

리뷰 데이터는 중복, 오타, 누락, 비정형 텍스트가 많아 제품별 불만과 개선 요청을 안정적으로 분석하기 어렵습니다.

### Solution

- 리뷰 데이터 수집 crawler와 정제 pipeline 구현
- Raw review, cleaned review, review_feature, product_summary 계층으로 데이터 모델링
- Spark 기반 대용량 텍스트 전처리 처리
- 리뷰 중복 제거, 언어 감지, 금칙어 제거, 길이 기준 필터링 적용
- 제품별 카테고리, 감성, 키워드 집계 mart table 생성
- Airflow로 수집·정제·집계 workflow 자동화

### Key Contributions

- Python crawler로 상품 1,200개, 리뷰 80만 건 수집
- PySpark를 활용해 리뷰 텍스트 정제 및 feature 추출
- 리뷰 중복 제거를 위해 normalized_text hash key 생성
- 제품별 일간 리뷰 수, 부정 리뷰 비율, 키워드 빈도 집계
- 데이터 품질 rule로 review_id 중복, rating range, empty text 비율 점검
- Airflow backfill을 활용해 과거 데이터 재처리 구조 구성
- Metabase dashboard에서 제품별 부정 리뷰 추이와 대표 키워드 제공

### Impact

- 리뷰 80만 건 처리 시간 4시간 20분에서 38분으로 단축
- 중복 리뷰 6.4% 제거
- 제품별 리뷰 분석 리포트 생성 작업을 수동 3시간에서 자동 15분 이내로 개선
- 부정 리뷰 급증 탐지 rule 구현
- 리뷰 데이터 품질 rule 28개 작성

### Tech Stack

Python, PySpark, Airflow, PostgreSQL, Pandas, BeautifulSoup, Docker, Metabase

---

### Project 3. FoodData Warehouse — 식품 영양 데이터 웨어하우스

GitHub: https://github.com/doyoon-data/fooddata-warehouse  
Period: 2024.08 - 2024.10  
Role: Data Engineer

공공 식품 영양 데이터, 사용자 식단 기록 데이터, 음식 검색 로그를 통합하여 식단 추천과 영양 분석에 활용할 수 있는 Data Warehouse 프로젝트입니다.

### Problem

식품 영양 데이터는 출처마다 단위, 음식명, 카테고리, 누락값 기준이 달라 사용자 식단 기록과 연결하기 어렵습니다.

### Solution

- 공공 데이터와 서비스 DB 데이터를 통합하는 ETL pipeline 구성
- 음식명 normalization과 category mapping rule 적용
- Nutrition fact table과 food dimension table 설계
- 음식 검색 로그를 기반으로 인기 음식 mart table 생성
- 데이터 품질 검증 rule로 영양소 값 범위와 단위 일관성 점검

### Key Contributions

- CSV, JSON, DB source를 하나의 staging schema로 통합
- 음식명 전처리: 공백, 특수문자, 브랜드명, 용량 표현 normalize
- food_dim, nutrition_fact, user_food_log, popular_food_mart 테이블 설계
- SQL window function을 활용한 음식 검색 순위 계산
- 영양소 단위 kcal, g, mg 기준 변환 rule 구현
- Airflow DAG로 일별 음식 데이터 갱신 자동화
- 데이터 변경 이력을 관리하기 위해 updated_at과 source_version 필드 추가

### Impact

- 음식 검색 매칭률 64%에서 87%로 개선
- 영양소 단위 불일치 오류 93% 감소
- 인기 음식 조회 API용 mart table 제공으로 평균 조회 시간 1.1초에서 140ms로 개선
- 공공 데이터 업데이트 반영 작업 자동화
- 데이터 품질 검증 SQL 22개 작성

### Tech Stack

Python, SQL, Airflow, PostgreSQL, Pandas, Docker, AWS S3, Metabase

---

## Education

### 한국대학교 컴퓨터공학과

2020.03 - 2026.02 예정  
GPA: 4.16 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 운영체제
- 컴퓨터네트워크
- 빅데이터처리
- 데이터마이닝
- 인공지능
- 확률과 통계
- 소프트웨어공학

---

## Awards / Activities

### 2025 교내 데이터 파이프라인 경진대회 대상

2025.05

- LogLake 프로젝트로 대상 수상
- 사용자 이벤트 수집, 데이터 품질 검증, Dashboard 자동화를 구현
- 데이터 신뢰성과 파이프라인 안정성 항목에서 최고 점수 획득

### Data Engineering Study Lead

2024.09 - 2025.06

- 10명 규모의 데이터 엔지니어링 스터디 운영
- 주제: SQL, Airflow, Spark, Kafka, Data Warehouse, dbt, 데이터 품질
- 매주 실제 서비스 로그 데이터를 기반으로 ETL 실습 진행
- Airflow DAG 코드 리뷰와 SQL 최적화 리뷰 진행

### Open Source Contribution

2025.01 - 2025.04

- Airflow 예제 DAG 문서 오타 수정
- dbt sample project README 개선
- 데이터 품질 체크 예제 repository에 Korean README 추가

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- 정보처리기사 필기 합격
- Google Analytics Certification 준비 중

---

## Technical Writing

- "Airflow DAG를 재처리 가능하게 설계하는 방법"
- "서비스 이벤트 로그 스키마를 설계하며 배운 점"
- "Data Mart와 Dashboard 사이에서 발생하는 지표 불일치 해결"
- "PySpark로 리뷰 데이터 80만 건 처리 시간을 줄인 과정"
- "데이터 품질 검증 Rule을 어디까지 만들어야 할까"

---

## Strengths

- 데이터 수집부터 정제, 적재, 검증, Dashboard 제공까지 end-to-end로 구현할 수 있습니다.
- 데이터 파이프라인을 단순히 작동하게 만드는 것보다 재처리 가능성, 품질 검증, 모니터링을 중요하게 봅니다.
- 분석가와 제품팀이 신뢰할 수 있는 지표를 사용할 수 있도록 데이터 정의와 테이블 구조를 명확히 설계합니다.
- SQL 성능과 데이터 모델링을 함께 고려하며, 지표 계산의 일관성을 중요하게 생각합니다.
- 신입 수준에서 요구되는 SQL/Python을 넘어 Airflow, Spark, Kafka, Cloud 기반 데이터 파이프라인 경험을 갖추고 있습니다.

---

## Resume Keywords

Data Engineer, Python, SQL, Airflow, Spark, PySpark, Kafka, ETL, ELT, Data Pipeline, Data Warehouse, Data Mart, Data Lake, PostgreSQL, MySQL, BigQuery, Redshift, AWS S3, AWS Glue, AWS Athena, Docker, Data Quality, Data Validation, Batch Processing, Stream Processing, Partitioning, Query Optimization, Metabase, Superset

---

# 2. Big Tech / Enterprise Target Resume — Data Engineer

## 이서현 | Data Engineer

Email: seohyun.lee.data@gmail.com  
GitHub: https://github.com/seohyun-data  
Portfolio: https://seohyun-data.dev  
Blog: https://tech.seohyun-data.dev  
LinkedIn: https://linkedin.com/in/seohyun-lee-data  

---

## Summary

대규모 데이터 환경에서 안정적이고 확장 가능한 데이터 파이프라인을 설계하는 데 관심이 있는 신입 Data Engineer입니다.

Python, SQL, Spark, Airflow, Kafka, dbt, BigQuery, Redshift, AWS를 활용해 배치·스트리밍 파이프라인과 분석용 데이터 모델을 구축했습니다. 특히 대기업·중견기업·빅테크 환경에서 중요하게 평가되는 **데이터 신뢰성, lineage, SLA, 재처리 가능성, 비용 최적화, 데이터 품질, 스키마 관리, 대용량 처리 성능**을 중요하게 생각합니다.

데이터를 단순히 옮기는 것이 아니라, 분석가·ML 엔지니어·제품팀이 신뢰할 수 있는 데이터 플랫폼을 만드는 것을 목표로 합니다.

---

## Core Competencies

- 대용량 Batch / Streaming Data Pipeline 설계
- Spark / PySpark 기반 분산 처리
- Airflow 기반 Workflow Orchestration
- Kafka 기반 Event Streaming
- Data Warehouse / Data Mart Modeling
- dbt 기반 SQL Transformation
- Data Quality / Data Contract / Schema Validation
- Partitioning / Clustering / Query Optimization
- Pipeline SLA / Freshness Monitoring
- Cloud Data Platform 운영
- Cost-aware Data Processing
- 분석가·ML 엔지니어 협업용 데이터셋 제공

---

## Skills

### Language

- Python
- SQL
- Scala Basic
- Java Basic
- Bash

### Data Engineering

- Apache Airflow
- Apache Spark
- PySpark
- Apache Kafka
- dbt
- Great Expectations
- Data Build Tool
- ETL
- ELT
- CDC Concept
- Data Contract
- Schema Registry Concept
- Batch Processing
- Stream Processing

### Data Platform

- BigQuery
- Redshift
- Snowflake Basic
- PostgreSQL
- MySQL
- Elasticsearch Basic
- Redis Basic
- Parquet
- ORC
- Delta Lake Basic
- Apache Iceberg Basic

### Cloud / Infra

- AWS S3
- AWS Glue
- AWS Athena
- AWS EMR Basic
- AWS Redshift
- AWS Lambda
- AWS CloudWatch
- Docker
- Docker Compose
- GitHub Actions
- Linux

### Monitoring / Quality

- Airflow SLA
- Data Freshness
- Row Count Check
- Null Ratio Check
- Duplicate Check
- Distribution Drift Basic
- Slack Alert
- Prometheus Basic
- Grafana Basic
- Logging

### Analytics / BI

- Metabase
- Superset
- Looker Studio
- Tableau Basic
- Amplitude Basic

---

## Experience

### Data Engineer Intern

**CommerceCore Korea**  
2025.06 - 2025.12

이커머스 플랫폼의 주문, 상품, 검색, 결제, 사용자 행동 데이터를 처리하는 데이터 플랫폼 팀에서 인턴으로 근무했습니다.

### Key Contributions

- 일 평균 2,500만 건 규모의 사용자 이벤트와 주문 데이터를 처리하는 Airflow batch pipeline 개선
- Spark 기반 sessionization job을 최적화하여 처리 시간을 96분에서 38분으로 단축
- S3 raw data, staging table, mart table로 이어지는 layered architecture 정리
- 주문·결제 데이터의 지표 불일치 문제를 해결하기 위해 order_status, payment_status 기준 정의 문서화
- dbt model을 도입하여 daily_order_mart, product_performance_mart, user_funnel_mart 생성
- BigQuery partitioning과 clustering을 적용하여 주요 분석 쿼리 비용 42% 절감
- Kafka 이벤트 스키마 변경으로 발생한 downstream pipeline 실패를 줄이기 위해 schema validation rule 추가
- Airflow DAG 실패 시 Slack alert와 retry policy를 개선하여 장애 인지 시간을 평균 50분에서 8분으로 단축
- Great Expectations 기반 데이터 품질 검증을 도입하여 null ratio, duplicate key, referential integrity 점검
- ML팀의 추천 모델 학습을 위해 사용자 클릭·구매 이력 feature table 제공

### Impact

- Spark job 처리 시간 60% 개선
- BigQuery 분석 쿼리 비용 42% 절감
- 데이터 pipeline 실패 인지 시간 84% 단축
- 주문 지표 불일치 관련 문의 70% 감소
- 데이터 품질 검증 rule 54개 작성
- Mart table 21개와 dbt model 34개 관리
- ML feature table 6개 제공

### Tech Stack

Python, SQL, PySpark, Airflow, Kafka, dbt, BigQuery, AWS S3, AWS Glue, Great Expectations, Docker, GitHub Actions

---

## Projects

---

### Project 1. CommerceData Platform — 이커머스 데이터 플랫폼

GitHub: https://github.com/seohyun-data/commerce-data-platform  
Demo: https://commerce-data-platform.dev  
Period: 2025.02 - 2025.05  
Role: Data Engineer

이커머스 서비스의 주문, 결제, 상품, 검색, 클릭 이벤트를 수집·정제·적재하여 분석과 추천 모델 학습에 활용할 수 있도록 만든 데이터 플랫폼입니다.

### Problem

이커머스 데이터는 주문 DB, 결제 로그, 상품 DB, 검색 로그, 클릭 이벤트 등 여러 source에 흩어져 있으며, 각 팀이 다른 기준으로 지표를 계산하면 매출·전환율·재구매율이 일관되지 않게 됩니다.

### Solution

- Raw, Staging, Warehouse, Mart 계층으로 데이터 구조 분리
- Airflow 기반 batch pipeline 자동화
- Kafka 기반 clickstream 수집
- dbt 기반 SQL transformation과 지표 정의 관리
- Great Expectations 기반 데이터 품질 검증
- ML feature table 제공
- BigQuery partitioning과 clustering으로 비용·성능 최적화

### Technical Details

- 주문, 결제, 상품, 사용자, 이벤트 source별 ingestion pipeline 구성
- S3에 raw data를 날짜별 partition으로 저장
- PySpark로 raw event data를 session 단위로 집계
- dbt model로 fact_order, fact_payment, dim_product, dim_user 설계
- user_funnel_mart, product_performance_mart, daily_revenue_mart 구축
- order_id, user_id, product_id 기준 referential integrity check 적용
- event_time과 ingestion_time을 분리하여 지연 이벤트 처리
- Airflow backfill 전략으로 과거 데이터 재처리 가능하게 설계
- BigQuery partition pruning이 가능하도록 event_date column 관리
- Dashboard와 ML 학습 데이터셋이 동일한 mart를 참조하도록 구조 통일

### Impact

- 일 평균 3,000만 건 이벤트 처리
- 주요 매출 dashboard 쿼리 시간 18초에서 3.2초로 개선
- BigQuery 월 예상 비용 38% 절감
- 지표 불일치 문의 60% 감소
- ML 추천 모델 학습용 feature 생성 시간을 4시간에서 45분으로 단축
- 데이터 품질 이슈 탐지 시간을 평균 1일에서 10분 이내로 단축

### Tech Stack

Python, SQL, PySpark, Airflow, Kafka, dbt, BigQuery, AWS S3, AWS Glue, Great Expectations, Docker, Metabase

---

### Project 2. StreamPulse — 실시간 사용자 이벤트 처리 파이프라인

GitHub: https://github.com/seohyun-data/streampulse  
Period: 2024.11 - 2025.01  
Role: Data Engineer

웹·앱 사용자 이벤트를 실시간으로 수집하고, 실시간 dashboard와 batch mart에 동시에 활용할 수 있도록 설계한 streaming data pipeline입니다.

### Problem

마케팅 캠페인과 제품 실험을 운영하려면 이벤트 발생 후 빠르게 지표를 확인해야 하지만, 기존 일별 batch 방식으로는 실시간 대응이 어렵습니다.

### Solution

- Kafka topic 기반 이벤트 수집 구조 설계
- Consumer group을 분리하여 raw 저장과 실시간 집계 처리 분리
- 이벤트 스키마 validation 적용
- 늦게 도착한 이벤트 처리를 위해 event_time 기준 window 설계
- 실시간 집계 결과를 Redis와 PostgreSQL에 저장
- batch pipeline과 실시간 집계 결과를 비교하는 reconciliation job 구현

### Key Contributions

- page_view, click, signup, purchase 이벤트 스키마 설계
- Kafka producer SDK prototype 구현
- Python consumer로 raw event 저장
- Spark Structured Streaming prototype으로 5분 window 집계 구현
- consumer lag, event throughput, error count metric 수집
- 잘못된 이벤트는 dead-letter topic으로 분리
- 실시간 dashboard용 active_user_5min, conversion_5min table 설계
- batch result와 streaming result 차이를 검증하는 SQL 작성

### Impact

- 이벤트 발생 후 dashboard 반영 시간 24시간에서 1분 이내로 개선
- 잘못된 이벤트로 인한 pipeline 중단 0건
- Dead-letter topic 기반 오류 이벤트 추적 가능
- 5분 단위 active user, signup conversion 지표 제공
- 초당 1,500건 이벤트 처리 테스트 통과

### Tech Stack

Python, SQL, Kafka, Spark Structured Streaming, PostgreSQL, Redis, Docker, Grafana

---

### Project 3. Data Quality Monitor

GitHub: https://github.com/seohyun-data/data-quality-monitor  
Period: 2024.08 - 2024.10  
Role: Data Platform Engineer

데이터 파이프라인에서 발생하는 품질 이슈를 자동으로 탐지하고 알림을 보내는 데이터 품질 모니터링 도구입니다.

### Problem

데이터 파이프라인은 성공했더라도 실제 데이터가 비정상일 수 있습니다. 예를 들어 row count가 급감하거나, null 값이 급증하거나, 특정 source 데이터가 지연되면 dashboard와 ML 모델에 잘못된 결과가 전달됩니다.

### Solution

- Table별 품질 rule을 YAML로 정의
- Row count, null ratio, duplicate ratio, freshness, value range 검증
- 검증 결과를 PostgreSQL에 저장
- 실패 시 Slack alert 발송
- 품질 이슈 추이를 dashboard로 시각화
- Airflow DAG와 연동 가능한 Python package 형태로 구성

### Key Contributions

- Rule configuration schema 설계
- SQL 기반 품질 검증 query generator 구현
- Airflow operator 형태로 재사용 가능한 check module 구현
- 품질 실패 severity를 warning, critical로 분류
- 최근 7일 평균 대비 row count 급감 탐지 rule 구현
- 실패 이력을 기반으로 table별 reliability score 계산
- 품질 검증 결과 dashboard 구현

### Impact

- 데이터 품질 rule 70개 관리 가능
- 품질 검증 로직 재사용으로 신규 table 검증 설정 시간 30분에서 5분으로 단축
- Row count 급감, null ratio 증가, freshness delay 탐지 가능
- Airflow pipeline 성공 후에도 데이터 이상을 탐지하는 구조 구현
- 분석용 dashboard 신뢰도 개선

### Tech Stack

Python, SQL, PostgreSQL, Airflow, Great Expectations Basic, Docker, Slack Webhook, Metabase

---

## Education

### 서울기술대학교 컴퓨터공학부

2020.03 - 2026.02 예정  
GPA: 4.27 / 4.5  
Major GPA: 4.36 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 운영체제
- 컴퓨터네트워크
- 분산시스템
- 빅데이터처리
- 데이터마이닝
- 확률과 통계
- 소프트웨어공학

---

## Awards

### 2025 SW 중심대학 공동 데이터 경진대회 최우수상

2025.08

- CommerceData Platform 프로젝트로 최우수상 수상
- 이커머스 데이터 플랫폼, 품질 검증, 비용 최적화, ML feature table 제공 구조 발표
- 데이터 신뢰성과 확장성 항목에서 최고점 획득

### 2024 교내 SQL 최적화 경진대회 은상

2024.11

- 140명 중 6위
- Index, join order, window function, partition pruning 기반 쿼리 개선

---

## Activities

### Data Platform Study Lead

2025.01 - 2025.06

- 12명 규모의 데이터 플랫폼 스터디 운영
- 주제: Airflow, Spark, Kafka, dbt, Data Warehouse, Data Quality, Cost Optimization
- 매주 공개 데이터셋 기반 pipeline 구현과 코드 리뷰 진행
- 데이터 품질 실패 사례와 재처리 전략 발표

### CS / Database Study

2024.07 - 2024.12

- 운영체제, 네트워크, 데이터베이스, 분산시스템 스터디 참여
- Transaction isolation, indexing, replication, partitioning, consistency 주제 발표

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- 정보처리기사 필기 합격
- Google Cloud BigQuery Skill Badge 준비 중

---

## Technical Writing

- "Data Engineer가 지표 정의 문서를 반드시 관리해야 하는 이유"
- "Spark Job 처리 시간을 96분에서 38분으로 줄인 과정"
- "BigQuery 비용을 줄이기 위한 Partitioning과 Clustering 전략"
- "Airflow Backfill을 안전하게 설계하는 방법"
- "Streaming Pipeline에서 Late Event를 처리하는 방식"

---

## Strengths

- 대용량 데이터 파이프라인을 설계할 때 성능, 비용, 품질, 재처리 가능성을 함께 고려합니다.
- 데이터 품질 검증과 모니터링을 파이프라인의 필수 요소로 봅니다.
- 분석가와 ML 엔지니어가 신뢰할 수 있는 데이터셋을 사용할 수 있도록 지표 정의와 테이블 구조를 명확히 관리합니다.
- Spark, Airflow, Kafka, dbt, Cloud 기반 데이터 플랫폼 경험을 갖추고 있습니다.
- 대기업·빅테크에서 중요하게 보는 데이터 신뢰성, 확장성, 운영 가능성을 신입 수준에서 설득력 있게 보여줄 수 있습니다.

---

## Resume Keywords

Data Engineer, Data Platform Engineer, Python, SQL, PySpark, Spark, Airflow, Kafka, dbt, BigQuery, Redshift, Snowflake, AWS S3, AWS Glue, AWS Athena, Data Warehouse, Data Lake, Data Mart, ETL, ELT, Batch Processing, Stream Processing, Data Quality, Data Contract, Schema Validation, Partitioning, Clustering, Query Optimization, Cost Optimization, Data Freshness, SLA, Great Expectations

---

# 3. Tech Startup Target Resume — Data Engineer

## 박민재 | Data Engineer

Email: minjae.park.data@gmail.com  
GitHub: https://github.com/minjae-startup-data  
Portfolio: https://minjae-data.dev  
Blog: https://blog.minjae-data.dev  
LinkedIn: https://linkedin.com/in/minjae-park-data  

---

## Summary

초기 제품의 데이터를 빠르게 수집·정리하고, 제품 의사결정에 바로 사용할 수 있는 지표와 파이프라인을 만드는 데 강점이 있는 신입 Data Engineer입니다.

Python, SQL, Airflow, PostgreSQL, BigQuery, Kafka, Supabase, AWS, Metabase를 활용해 MVP 단계의 서비스 로그 수집, 지표 정의, Data Mart 구축, Dashboard 자동화를 수행했습니다. 작은 팀에서 백엔드 개발자, PM, 마케터와 협업하며 **가입 전환율, 예약 전환율, 리텐션, 활성 사용자, 캠페인 성과**를 측정할 수 있는 데이터 기반을 만들었습니다.

스타트업 환경에서 중요한 빠른 실행력, 데이터 기반 의사결정, 비용 효율성, 단순하지만 확장 가능한 파이프라인 설계를 중요하게 생각합니다.

---

## Core Competencies

- 초기 제품 데이터 인프라 구축
- Product Analytics Event Tracking 설계
- SQL 기반 지표 정의 및 Dashboard 자동화
- Airflow 기반 경량 ETL Pipeline 구축
- BigQuery / PostgreSQL 기반 Data Mart 설계
- 사용자 행동 로그 수집 및 Funnel 분석
- Retention / Cohort 분석 데이터셋 구축
- 마케팅 캠페인 데이터 통합
- 비용 효율적인 Cloud Data Pipeline 설계
- PM·마케터·개발자와 빠른 협업
- 데이터 품질 검증 및 운영 알림

---

## Skills

### Language

- Python
- SQL
- JavaScript Basic
- Bash

### Data Engineering

- Airflow
- Kafka Basic
- dbt Basic
- ETL
- ELT
- Batch Pipeline
- Event Tracking
- Data Mart
- Funnel Analysis
- Cohort Analysis
- Retention Analysis
- Data Quality Check

### Database / Analytics

- PostgreSQL
- MySQL
- BigQuery
- Supabase
- Firebase
- Redis Basic
- Google Analytics
- Mixpanel Basic
- Amplitude Basic
- Metabase
- Looker Studio

### Cloud / Infra

- AWS S3
- AWS EC2
- AWS RDS
- AWS Lambda Basic
- Docker
- Docker Compose
- GitHub Actions
- Vercel Log Basic
- Cloudflare Analytics Basic

### Collaboration

- Notion
- Slack
- Linear
- Figma Basic
- Jira Basic

---

## Experience

### Founding Data Engineer Intern

**LocalLoop**  
2025.05 - 2025.11

동네 기반 소모임·예약 플랫폼을 만드는 초기 스타트업에서 제품 데이터 수집, 지표 정의, Dashboard 구축을 담당했습니다.

### Key Contributions

- 가입, 온보딩, 모임 조회, 예약 신청, 예약 취소, 호스트 승인 이벤트 스키마 설계
- 웹 프론트엔드와 백엔드 로그를 통합하여 PostgreSQL 기반 product_event table 구축
- Airflow DAG로 서비스 DB와 이벤트 로그를 매일 BigQuery로 적재
- signup_funnel, reservation_funnel, host_activity, weekly_retention mart table 설계
- PM과 함께 activation, reservation conversion, host response time, 4-week retention 지표 정의
- Metabase dashboard를 구축해 제품팀이 매일 핵심 지표를 확인할 수 있도록 자동화
- 광고 캠페인 UTM 데이터를 회원가입 이벤트와 연결하여 캠페인별 가입 전환율 분석 가능하도록 개선
- 데이터 누락을 탐지하기 위해 이벤트별 row count, null ratio, event_name whitelist rule 적용
- 비용 문제를 줄이기 위해 BigQuery partitioning을 적용하고 오래된 raw log를 S3 archive로 이동
- 사용자 인터뷰 결과와 행동 데이터를 함께 분석하여 예약 신청 이탈 구간을 발견

### Startup Impact

- 제품 핵심 지표 dashboard 0개에서 12개 구축
- 수동 지표 집계 시간을 주 8시간에서 30분 이하로 단축
- 예약 신청 funnel에서 날짜 선택 단계 이탈률 37%를 발견하고 UI 개선 근거 제공
- 캠페인별 가입 전환율 분석으로 비효율 광고 예산 22% 절감
- 이벤트 누락 탐지 시간을 평균 2일에서 30분 이내로 단축
- 베타 사용자 380명 규모의 제품 데이터 기반 구축

### Tech Stack

Python, SQL, Airflow, PostgreSQL, BigQuery, Supabase, AWS S3, Docker, Metabase, Google Analytics, Mixpanel

---

## Projects

---

### Project 1. StartupMetrics — 초기 스타트업용 제품 지표 데이터 파이프라인

GitHub: https://github.com/minjae-startup-data/startupmetrics  
Demo: https://startupmetrics.dev  
Period: 2025.01 - 2025.04  
Role: Data Engineer / Product Analyst

초기 스타트업이 회원가입, 온보딩, 결제, 예약, 리텐션 지표를 자동으로 수집하고 분석할 수 있도록 만든 경량 데이터 파이프라인입니다.

### Problem

초기 스타트업은 제품 지표가 필요하지만, 별도 데이터팀이 없어서 PM이나 개발자가 매번 SQL을 직접 실행하거나 GA 화면을 수동으로 확인하는 경우가 많습니다. 이로 인해 지표 정의가 흔들리고 의사결정 속도가 느려집니다.

### Solution

- 웹·서버 이벤트를 공통 event schema로 수집
- PostgreSQL raw_event table과 BigQuery 분석 테이블로 분리
- Airflow 기반 일별 ETL 자동화
- Funnel, Cohort, Retention, Revenue mart table 생성
- Metabase dashboard template 제공
- 이벤트 누락과 중복을 감지하는 데이터 품질 rule 적용

### Key Contributions

- event_name, user_id, anonymous_id, session_id, event_time, source, properties 기반 스키마 설계
- JavaScript event tracking snippet prototype 구현
- Server-side event ingestion API 구현
- Airflow DAG로 raw event to mart pipeline 구성
- Funnel 계산 SQL template 작성
- Cohort retention mart table 설계
- UTM source, campaign, medium 기준 attribution table 구성
- Metabase dashboard 16개 작성
- 신규 이벤트 추가 시 tracking plan을 작성하도록 Notion template 제작
- 데이터 품질 check 결과를 Slack으로 알림

### Impact

- 가입, 온보딩, 예약, 결제 funnel dashboard 자동화
- SQL 수동 집계 작업 85% 감소
- 이벤트 누락 탐지 시간 2일에서 20분 이내로 단축
- 초기 제품 3개에 재사용 가능한 pipeline template 제공
- product team이 매일 확인 가능한 north-star metric dashboard 구축
- BigQuery partitioning 적용으로 쿼리 비용 31% 절감

### Tech Stack

Python, SQL, Airflow, PostgreSQL, BigQuery, Metabase, Docker, AWS S3, Google Analytics, Slack Webhook

---

### Project 2. CampaignBridge — 마케팅 캠페인 데이터 통합 파이프라인

GitHub: https://github.com/minjae-startup-data/campaignbridge  
Period: 2024.10 - 2024.12  
Role: Data Engineer

Google Analytics, 광고 UTM, 회원가입 이벤트, 구매 데이터를 통합하여 캠페인별 성과를 분석하는 데이터 파이프라인입니다.

### Problem

마케팅 캠페인 성과를 보려면 광고 플랫폼, GA, 서비스 DB, 결제 데이터를 각각 확인해야 하며, 가입·구매 전환 기준이 일관되지 않아 의사결정이 어렵습니다.

### Solution

- UTM parameter와 user event를 연결하는 attribution table 설계
- 회원가입, 온보딩 완료, 구매 이벤트를 campaign 기준으로 집계
- 일별 캠페인 성과 mart table 생성
- GA export 데이터와 서비스 DB 데이터를 통합
- CAC, conversion rate, revenue per campaign 계산 SQL 작성
- Metabase dashboard로 캠페인별 성과 시각화

### Key Contributions

- UTM parsing logic 구현
- anonymous_id와 user_id 매핑 테이블 설계
- Campaign dimension table과 daily_campaign_performance mart table 설계
- 중복 유입 이벤트 제거 rule 적용
- Airflow DAG로 GA data, service DB, payment data 적재 자동화
- 캠페인별 funnel dashboard 구현
- 데이터가 늦게 들어오는 경우를 고려해 최근 3일 rolling reprocessing 적용

### Impact

- 캠페인별 가입 전환율과 구매 전환율 자동 집계
- 마케팅 리포트 작성 시간 주 5시간에서 40분으로 단축
- 중복 유입 이벤트 4.7% 제거
- 비효율 캠페인 식별로 테스트 광고 예산 18% 절감
- 캠페인 성과 기준을 문서화하여 PM·마케터 간 지표 해석 차이 감소

### Tech Stack

Python, SQL, Airflow, BigQuery, PostgreSQL, Google Analytics, Metabase, Docker

---

### Project 3. RetentionLab — 코호트 리텐션 분석 데이터 마트

GitHub: https://github.com/minjae-startup-data/retentionlab  
Period: 2024.07 - 2024.09  
Role: Data Engineer

사용자의 가입일, 첫 행동, 반복 방문, 핵심 행동 수행 여부를 기준으로 리텐션을 분석할 수 있는 데이터 마트 프로젝트입니다.

### Problem

단순 DAU, WAU만으로는 사용자가 실제로 제품에 남아 있는지 알기 어렵습니다. 초기 제품에서는 어떤 행동이 리텐션과 연결되는지 빠르게 확인해야 합니다.

### Solution

- 가입 cohort 기준 weekly retention table 생성
- 핵심 행동 수행 여부와 리텐션의 관계를 분석할 수 있는 feature table 설계
- 사용자별 first_action, first_reservation, first_purchase 시점 계산
- Retention dashboard와 cohort heatmap 구현
- 데이터 누락과 timezone 문제를 해결하기 위한 event_time normalization 적용

### Key Contributions

- user_cohort, user_activity_weekly, retention_matrix table 설계
- SQL window function으로 사용자별 첫 핵심 행동 시점 계산
- KST 기준 주차 계산 rule 표준화
- cohort별 week 1, week 2, week 4 retention 계산
- 핵심 행동 수행자와 미수행자 리텐션 비교 SQL 작성
- Metabase heatmap dashboard 구현
- 데이터 품질 검증으로 가입일 이전 이벤트, 중복 활동 이벤트 탐지

### Impact

- 4주차 retention을 자동 계산하는 mart table 구축
- 핵심 행동 수행자의 week 4 retention이 2.3배 높다는 insight 도출
- PM이 온보딩 개선 우선순위를 정하는 근거 제공
- 수동 cohort 분석 작업 90% 자동화
- timezone 오류로 인한 날짜 집계 불일치 해결

### Tech Stack

SQL, Python, PostgreSQL, BigQuery, Airflow, Metabase, Docker

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 예정  
GPA: 4.09 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 빅데이터처리
- 데이터마이닝
- 웹프로그래밍
- 운영체제
- 컴퓨터네트워크
- 확률과 통계
- 창업과 소프트웨어 제품 개발

---

## Awards / Activities

### 2025 대학 연합 데이터 제품 해커톤 대상

2025.06

- StartupMetrics 프로젝트로 대상 수상
- 초기 스타트업이 바로 사용할 수 있는 product analytics pipeline과 dashboard template 구현
- 제품 지표 정의, 데이터 자동화, 비용 효율성에서 높은 평가를 받음

### 2024 스타트업 MVP 해커톤 최우수상

2024.12

- CampaignBridge 프로젝트로 최우수상 수상
- 캠페인 유입부터 가입·구매까지 연결하는 데이터 파이프라인 구현
- 마케팅 의사결정에 바로 활용 가능한 dashboard 완성도에서 높은 평가를 받음

### Product Data Study Organizer

2024.09 - 2025.05

- 15명 규모의 제품 데이터 스터디 운영
- 주제: funnel, retention, cohort, event tracking, attribution, dashboard design
- 매주 실제 서비스 지표를 역설계하고 SQL로 구현

---

## Certifications

- SQLD
- Google Analytics Certification
- AWS Cloud Practitioner 준비 중
- 정보처리기사 필기 준비 중

---

## Product Metrics Experience

- Activation Rate
- Signup Conversion
- Onboarding Completion Rate
- Reservation Conversion Rate
- Purchase Conversion
- Weekly Active Users
- Cohort Retention
- 4-week Retention
- Campaign Conversion Rate
- CAC Basic
- Funnel Drop-off
- North Star Metric
- Event Completeness Rate

---

## Technical Writing

- "초기 스타트업에서 Event Tracking Plan을 먼저 만들어야 하는 이유"
- "Funnel 지표를 SQL로 안정적으로 계산하는 방법"
- "Retention Mart를 만들면서 겪은 Timezone 문제"
- "BigQuery 비용을 줄이기 위한 간단한 Partitioning 전략"
- "PM과 Data Engineer가 지표 정의를 맞추는 방법"

---

## Strengths

- 초기 제품에서 필요한 데이터 기반을 빠르게 구축할 수 있습니다.
- 제품 지표와 데이터 파이프라인을 연결해 PM과 마케터가 바로 사용할 수 있는 Dashboard를 제공합니다.
- 복잡한 플랫폼보다 작은 팀에 맞는 단순하고 비용 효율적인 구조를 먼저 만들고, 이후 확장 가능성을 고려합니다.
- 사용자 행동 데이터, 캠페인 데이터, 서비스 DB 데이터를 연결해 제품 개선 근거를 도출할 수 있습니다.
- 스타트업에서 중요한 속도, 오너십, 지표 이해도, 협업 능력을 갖추고 있습니다.

---

## Resume Keywords

Data Engineer, Startup Data Engineer, Product Data Engineer, Python, SQL, Airflow, BigQuery, PostgreSQL, Supabase, AWS S3, Docker, Metabase, Looker Studio, Google Analytics, Mixpanel, Event Tracking, Product Analytics, Funnel Analysis, Cohort Analysis, Retention Analysis, Attribution, Data Mart, ETL, ELT, Data Quality, Dashboard Automation, Cost Optimization, Product Metrics, Startup Metrics