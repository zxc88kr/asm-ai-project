# Data Engineer — Foreign / Global Company Target Resume

## Daniel Kim | Data Engineer

Email: daniel.kim.data@gmail.com  
GitHub: https://github.com/danielkim-data  
Portfolio: https://danielkim-data.dev  
Blog: https://blog.danielkim-data.dev  
LinkedIn: https://linkedin.com/in/danielkim-data  

---

## Summary

Entry-level Data Engineer with hands-on experience building batch and streaming data pipelines using Python, SQL, Airflow, Spark, Kafka, PostgreSQL, BigQuery, AWS, Docker, and dbt. Experienced in designing raw, staging, warehouse, and mart layers for analytics and product decision-making.

Built data pipelines for user events, e-commerce orders, reviews, nutrition records, campaign attribution, and retention analytics. Focused on data quality, pipeline reliability, query performance, data freshness, cost optimization, and collaboration with analysts, product managers, backend engineers, and ML engineers.

---

## Skills

### Data Engineering

- Python
- SQL
- Airflow
- Spark
- PySpark
- Kafka
- dbt
- ETL
- ELT
- Batch Processing
- Stream Processing
- Data Warehouse
- Data Mart
- Data Lake
- Data Quality
- Data Validation
- Backfill Strategy

### Database / Warehouse

- PostgreSQL
- MySQL
- BigQuery
- Redshift Basic
- Snowflake Basic
- Redis Basic
- Parquet
- Partitioning
- Clustering
- Query Optimization

### Cloud / Infra

- AWS S3
- AWS EC2
- AWS RDS
- AWS Glue Basic
- AWS Athena
- Docker
- Docker Compose
- GitHub Actions
- Linux

### Analytics / Monitoring

- Pandas
- NumPy
- Metabase
- Superset Basic
- Looker Studio
- Great Expectations Basic
- Slack Alert
- Airflow SLA
- Data Freshness
- Row Count Check
- Null Ratio Check
- Duplicate Check

---

## Experience

### Data Engineer Intern

**CommerceCore Korea**  
Jun 2025 - Dec 2025

Worked on e-commerce event, order, product, payment, and marketing datasets for analytics and ML teams.

- Improved a daily PySpark sessionization job processing 25M user events per day, reducing runtime from 96 minutes to 38 minutes.
- Built Airflow DAGs for raw-to-staging and staging-to-mart pipelines across clickstream, order, product, and payment data.
- Designed dbt models for daily_order_mart, product_performance_mart, user_funnel_mart, and campaign_attribution_mart.
- Reduced BigQuery query cost by 42% by applying partitioning, clustering, and query pruning strategies.
- Added data quality checks for null ratio, duplicate keys, row count drops, referential integrity, and freshness delays.
- Reduced pipeline failure detection time from 50 minutes to 8 minutes by improving Airflow alerts and Slack notifications.
- Standardized order and payment status definitions, reducing metric discrepancy questions from business teams by 70%.
- Built feature tables for recommendation models, including user clicks, purchases, category preferences, and recent activity windows.
- Collaborated with analysts and product managers to define activation, conversion, revenue, and retention metrics.
- Documented pipeline ownership, upstream dependencies, data definitions, and backfill procedures.

---

## Projects

### CommerceData Platform — E-commerce Data Warehouse

GitHub: https://github.com/danielkim-data/commerce-data-platform  
Period: Feb 2025 - May 2025  
Role: Data Engineer

Data platform that ingests e-commerce order, payment, product, search, and clickstream data for analytics and ML use cases.

- Designed layered data architecture with raw, staging, warehouse, and mart layers.
- Processed 30M events per day using Kafka, PySpark, Airflow, BigQuery, and AWS S3.
- Built fact_order, fact_payment, dim_product, dim_user, user_funnel_mart, product_performance_mart, and daily_revenue_mart.
- Reduced dashboard query time from 18s to 3.2s through partitioning, clustering, aggregation marts, and query optimization.
- Reduced estimated BigQuery monthly cost by 38% using partition pruning and optimized materialized mart tables.
- Implemented Great Expectations checks for order_id uniqueness, product_id integrity, null ratios, and delayed event ingestion.
- Added late-event handling by separating event_time and ingestion_time.
- Built Airflow backfill strategy to reprocess historical data safely from failed task boundaries.
- Provided ML-ready feature tables, reducing recommendation training dataset generation time from 4 hours to 45 minutes.

Tech Stack: Python, SQL, PySpark, Airflow, Kafka, dbt, BigQuery, AWS S3, Great Expectations, Docker, Metabase

---

### StreamPulse — Real-time Event Pipeline

GitHub: https://github.com/danielkim-data/streampulse  
Period: Nov 2024 - Jan 2025  
Role: Data Engineer

Streaming pipeline that collects web events and updates near-real-time dashboards.

- Designed event schemas for page_view, click, signup, checkout_start, purchase, and search events.
- Implemented Kafka producer and consumer prototypes for event ingestion and raw event storage.
- Built 5-minute window aggregation using Spark Structured Streaming.
- Reduced dashboard freshness from 24 hours to under 1 minute.
- Added dead-letter topic handling for invalid event schemas to prevent pipeline failures.
- Monitored consumer lag, throughput, invalid event count, and processing latency.
- Created reconciliation SQL to compare streaming aggregates against daily batch results.

Tech Stack: Python, Kafka, Spark Structured Streaming, PostgreSQL, Redis, Docker, Grafana

---

## Education

### Korea University of Technology — B.S. in Computer Science

Mar 2020 - Feb 2026 expected  
GPA: 4.16 / 4.5

Relevant Coursework:

- Data Structures
- Algorithms
- Database Systems
- Operating Systems
- Computer Networks
- Big Data Processing
- Data Mining
- Statistics
- Distributed Systems

---

## Awards & Activities

### Grand Prize — University Data Pipeline Contest

May 2025

- Won grand prize with CommerceData Platform.
- Presented event ingestion, data warehouse modeling, data quality checks, dashboard optimization, and ML feature table design.

### Data Engineering Study Lead

Sep 2024 - Jun 2025

- Led weekly sessions on SQL, Airflow, Spark, Kafka, dbt, data warehouse modeling, data quality, and cost optimization.
- Reviewed Airflow DAGs and SQL performance reports.

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- Google Analytics Certification
- Engineer Information Processing, written exam passed

---

## Keywords

Data Engineer, Python, SQL, Airflow, Spark, PySpark, Kafka, dbt, BigQuery, Redshift, Snowflake, AWS S3, AWS Glue, AWS Athena, ETL, ELT, Data Pipeline, Data Warehouse, Data Lake, Data Mart, Batch Processing, Stream Processing, Data Quality, Data Validation, Partitioning, Clustering, Query Optimization, Data Freshness, Cost Optimization, Metabase