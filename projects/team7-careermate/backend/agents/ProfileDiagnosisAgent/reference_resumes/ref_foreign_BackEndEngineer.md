# BackEnd Engineer — Foreign / Global Company Target Resume

## Daniel Kim | BackEnd Engineer

Email: daniel.kim.backend@gmail.com  
GitHub: https://github.com/danielkim-backend  
Portfolio: https://danielkim-backend.dev  
Blog: https://blog.danielkim-backend.dev  
LinkedIn: https://linkedin.com/in/danielkim-backend  

---

## Summary

Entry-level BackEnd Engineer with experience building reliable APIs, transactional systems, and cloud-deployed services using Java, Spring Boot, JPA, MySQL, Redis, Docker, AWS, and GitHub Actions. Strong understanding of API design, database modeling, transaction boundaries, caching, testing, and performance optimization.

Built backend systems for nutrition tracking, study matching, order management, and notification workflows. Focused on writing maintainable service-layer code, improving query performance, preventing data inconsistency, and designing production-ready APIs with clear error handling and observability.

---

## Skills

### Backend

- Java
- Spring Boot
- Spring MVC
- Spring Security
- Spring Data JPA
- QueryDSL
- REST API
- JWT
- OAuth2
- WebSocket Basic
- Validation
- Global Exception Handling

### Database

- MySQL
- PostgreSQL
- Redis
- H2
- Database Indexing
- Transaction Isolation
- Optimistic Lock
- Pessimistic Lock
- Query Optimization
- Cursor Pagination

### Infra / DevOps

- Docker
- Docker Compose
- AWS EC2
- AWS RDS
- AWS S3
- Nginx
- GitHub Actions
- Linux
- HTTPS
- CI/CD Basic

### Testing / Tools

- JUnit5
- Mockito
- AssertJ
- Testcontainers
- Spring Rest Docs
- Swagger
- Postman
- Git
- GitHub Projects

---

## Experience

### BackEnd Engineer Intern

**CommerceCore Korea**  
Jun 2025 - Dec 2025

Worked on order, product, inventory, and admin APIs for an e-commerce platform.

- Built Spring Boot APIs for order search, order cancellation, product inventory lookup, and admin order management.
- Reduced p95 latency of the admin order search API from 2.8s to 620ms by adding composite indexes, cursor pagination, and QueryDSL-based dynamic queries.
- Reduced query count in order detail API from 121 to 9 by fixing JPA N+1 issues using fetch joins, batch size tuning, and DTO projection.
- Implemented Redis caching for product detail APIs, reducing database read traffic by 43%.
- Added validation logic for order status transitions to prevent inconsistent states after payment failure and cancellation scenarios.
- Built integration tests with JUnit5, Mockito, and Testcontainers for inventory deduction, order cancellation, and payment failure flows.
- Standardized API error responses for 400, 401, 403, 404, 409, and 500 errors and documented them with Swagger.
- Improved CI reliability by configuring GitHub Actions to run build and test checks before deployment.
- Collaborated with frontend engineers to align API contracts, pagination behavior, error codes, and loading states.

---

## Projects

### OrderHub — Transactional Order and Inventory System

GitHub: https://github.com/danielkim-backend/orderhub  
Period: Feb 2025 - May 2025  
Role: BackEnd Lead

E-commerce backend system that handles product orders, inventory deduction, payment status, cancellation, idempotency, and admin search.

- Designed domain models for Product, Stock, Order, OrderItem, Payment, and OrderHistory using Spring Boot, JPA, and MySQL.
- Prevented overselling under concurrent requests by comparing optimistic locking and pessimistic locking strategies under load tests.
- Maintained inventory consistency under 1,000 concurrent order requests in test scenarios.
- Implemented idempotency keys with Redis to prevent duplicate order creation from repeated client requests.
- Stored product price snapshots at order time to prevent price-change inconsistencies.
- Built payment failure and cancellation flows that restored inventory and updated order status in a single transaction.
- Replaced offset pagination with cursor pagination, improving deep-page query latency by 86%.
- Reduced admin order search p95 latency from 3.1s to 540ms through indexing and query optimization.
- Added Testcontainers-based integration tests for MySQL transaction behavior.

Tech Stack: Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, JUnit5, Testcontainers, Docker, GitHub Actions

---

### StudyMate — Study Group Matching Platform

GitHub: https://github.com/danielkim-backend/studymate  
Period: Nov 2024 - Jan 2025  
Role: BackEnd Engineer

Platform that allows users to create study groups, apply to join, approve members, manage schedules, and receive notifications.

- Designed APIs for study creation, application submission, approval, rejection, withdrawal, schedule creation, and notification.
- Applied pessimistic locking to prevent capacity overflow when multiple users applied to the same study group concurrently.
- Achieved zero over-capacity approvals in 100 concurrent approval test cases.
- Implemented QueryDSL-based search APIs with filters for technology tags, region, online/offline mode, and recruitment status.
- Built WebSocket-based real-time notification prototype for application approval and schedule updates.
- Wrote concurrency tests for application approval and capacity validation flows.
- Standardized API documentation using Swagger to reduce frontend integration errors.

Tech Stack: Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, WebSocket, JUnit5, Docker

---

## Education

### Korea University of Technology — B.S. in Computer Science

Mar 2020 - Feb 2026 expected  
GPA: 4.17 / 4.5

Relevant Coursework:

- Data Structures
- Algorithms
- Operating Systems
- Database Systems
- Computer Networks
- Object-Oriented Programming
- Software Engineering
- Distributed Systems

---

## Awards & Activities

### Grand Prize — University Web Service Development Contest

May 2025

- Won grand prize with MealBalance API and dashboard.
- Presented API design, database schema, caching strategy, query optimization, and test coverage improvements.

### Backend Engineering Study Lead

Sep 2024 - Jun 2025

- Led weekly study sessions on Spring Boot, JPA, transaction handling, Redis caching, database indexing, testing, and AWS deployment.
- Reviewed backend project code and documented common performance issues.

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner, in progress
- Engineer Information Processing, written exam passed

---

## Keywords

BackEnd Engineer, Software Engineer, Java, Spring Boot, JPA, QueryDSL, MySQL, Redis, REST API, Spring Security, JWT, OAuth2, Docker, AWS EC2, AWS RDS, GitHub Actions, JUnit5, Mockito, Testcontainers, Transaction, Concurrency, Database Indexing, Query Optimization, Cursor Pagination, Caching, API Design