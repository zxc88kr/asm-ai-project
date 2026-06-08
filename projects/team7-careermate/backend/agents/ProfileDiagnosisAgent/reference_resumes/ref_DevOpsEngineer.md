# DevOps Engineer Resume Set

> Target: Korea / Entry-level Developer / Max Internship Experience  
> Role: DevOps Engineer  
> Purpose: 100-point benchmark resumes for comparing junior developer resumes  
> Reference Basis: 최근 DevOps Engineer Resume 및 채용 흐름에서 반복적으로 요구되는 AWS, Docker, Kubernetes, Terraform, CI/CD, GitHub Actions, Jenkins, Linux, Monitoring, Logging, IaC, DevSecOps, Observability, SRE 기초 역량을 기준으로 구성함.  
> Note: 아래 Resume은 특정 개인의 이력서를 복제한 것이 아니라, 실제 채용 시장에서 강하게 평가되는 DevOps 역량 패턴을 기반으로 재구성한 고품질 비교군 Resume입니다.

---

# 1. Common Resume — DevOps Engineer

## 김도윤 | DevOps Engineer

Email: doyoon.kim.devops@gmail.com  
GitHub: https://github.com/doyoon-devops  
Portfolio: https://doyoon-devops.dev  
Blog: https://blog.doyoon-devops.dev  
LinkedIn: https://linkedin.com/in/doyoon-kim-devops  

---

## Summary

개발팀이 더 빠르고 안정적으로 서비스를 배포할 수 있는 환경을 만드는 데 집중하는 신입 DevOps Engineer입니다.

AWS, Docker, GitHub Actions, Jenkins, Kubernetes, Terraform, Prometheus, Grafana, Nginx, Linux를 활용해 웹 서비스의 CI/CD, 컨테이너화, 클라우드 배포, 모니터링, 로그 수집, 장애 알림 환경을 직접 구축했습니다. 단순 배포 스크립트 작성이 아니라 **배포 자동화, 장애 탐지, 롤백 전략, 환경 분리, 인프라 재현성, 보안 설정, 비용 최적화**까지 고려한 DevOps 프로젝트 경험이 있습니다.

팀 프로젝트에서는 백엔드·프론트엔드 개발자가 기능 개발에 집중할 수 있도록 배포 파이프라인과 운영 환경을 표준화했으며, 장애 발생 시 원인을 추적할 수 있는 로그·메트릭 기반 관측 가능성 구축에 관심이 많습니다.

---

## Core Competencies

- AWS 기반 서비스 배포 및 운영
- Docker 기반 애플리케이션 컨테이너화
- GitHub Actions / Jenkins 기반 CI/CD Pipeline 구축
- Nginx Reverse Proxy 및 HTTPS 설정
- Kubernetes 기본 리소스 배포 및 운영
- Terraform 기반 Infrastructure as Code
- Prometheus / Grafana 기반 모니터링
- Loki / CloudWatch 기반 로그 수집
- Slack Alert 기반 장애 알림
- Blue-Green / Rolling Deployment 기초 구현
- Linux Server 운영 및 Shell Script 자동화
- Secret 관리 및 환경 변수 분리
- 개발·스테이징·운영 환경 분리

---

## Skills

### Cloud

- AWS EC2
- AWS RDS
- AWS S3
- AWS VPC Basic
- AWS IAM
- AWS CloudWatch
- AWS Route 53
- AWS ALB Basic
- AWS ECR Basic

### Container / Orchestration

- Docker
- Docker Compose
- Kubernetes
- Minikube
- Helm Basic
- Nginx
- Container Registry

### CI/CD

- GitHub Actions
- Jenkins
- Argo CD Basic
- Build Pipeline
- Test Automation
- Deployment Pipeline
- Rollback Strategy
- Blue-Green Deployment
- Rolling Deployment

### Infrastructure as Code

- Terraform
- Terraform State
- Terraform Module Basic
- AWS Provider
- Remote State Basic

### Monitoring / Logging

- Prometheus
- Grafana
- Loki
- Promtail
- AWS CloudWatch
- Node Exporter
- cAdvisor
- Alertmanager
- Slack Webhook

### Security / DevSecOps

- IAM Least Privilege Basic
- Secret Management
- GitHub Secrets
- Snyk Basic
- Trivy
- Container Image Scanning
- Dependency Vulnerability Scanning
- HTTPS / TLS
- Security Group

### OS / Scripting

- Linux
- Ubuntu
- Bash
- Shell Script
- Cron
- Systemd
- Nginx Log
- SSH

### Collaboration

- Git
- GitHub
- Notion
- Slack
- Jira Basic
- Postman
- Swagger

---

## Experience

### DevOps Engineer Intern

**FitLogics**  
2025.07 - 2025.12

사용자 건강 데이터 기반 식단·운동 기록 서비스를 운영하는 스타트업에서 배포 자동화, 모니터링, 클라우드 운영 환경 개선을 담당했습니다.

### Key Contributions

- Spring Boot, React 기반 서비스를 Docker Compose로 컨테이너화하여 개발·배포 환경 차이 감소
- GitHub Actions 기반 CI/CD pipeline을 구축하여 main branch merge 후 build, test, Docker image push, EC2 deploy 자동화
- 수동 배포 과정을 자동화하여 평균 배포 시간을 35분에서 7분으로 단축
- Nginx reverse proxy와 Certbot을 활용해 HTTPS 적용 및 도메인 연결 구성
- AWS EC2, RDS, S3 기반 운영 환경을 정리하고 보안 그룹과 IAM 권한을 최소 권한 기준으로 재설정
- Prometheus, Grafana, Node Exporter, cAdvisor를 구성하여 CPU, memory, disk, container metric dashboard 구축
- Loki와 Promtail을 활용해 application log를 수집하고 Grafana에서 에러 로그 검색 가능하도록 개선
- API 5xx error rate, CPU 사용률, disk 사용량 기준 Slack alert 설정
- 배포 실패 시 이전 Docker image로 rollback하는 script 작성
- Trivy 기반 Docker image vulnerability scanning을 CI pipeline에 추가
- 운영 환경 변수와 secret을 GitHub Secrets와 서버 환경 변수로 분리하여 repository 내 민감 정보 노출 방지
- 장애 발생 시 로그와 metric을 기반으로 원인 분석 문서를 작성하고 재발 방지 checklist 정리

### Impact

- 평균 배포 시간 35분에서 7분으로 80% 단축
- 수동 배포 오류 6건을 배포 자동화 이후 0건으로 감소
- 장애 탐지 평균 시간을 40분에서 8분 이내로 단축
- 운영 서버 resource dashboard 8개 구축
- Docker image 보안 취약점 17건 탐지 및 base image 업데이트
- 개발자 onboarding 환경 구축 시간을 2시간에서 20분으로 단축

### Tech Stack

AWS EC2, AWS RDS, AWS S3, Docker, Docker Compose, GitHub Actions, Nginx, Prometheus, Grafana, Loki, Trivy, Bash, Linux

---

## Projects

---

### Project 1. DeployMate — Spring Boot & React 서비스 CI/CD 플랫폼

GitHub: https://github.com/doyoon-devops/deploymate  
Demo: https://deploymate.doyoon-devops.dev  
Period: 2025.03 - 2025.06  
Role: DevOps Engineer

Spring Boot 백엔드와 React 프론트엔드 서비스를 대상으로 Docker 기반 배포 환경과 GitHub Actions CI/CD pipeline을 구축한 프로젝트입니다.

### Problem

팀 프로젝트에서 배포는 특정 개발자의 로컬 환경에 의존했고, 수동 명령어 실행 중 실수가 자주 발생했습니다. 또한 배포 실패 시 원인을 파악하거나 이전 버전으로 되돌리는 과정이 명확하지 않았습니다.

### Solution

- Backend, Frontend, MySQL, Redis를 Docker Compose로 구성
- GitHub Actions로 build, test, Docker image build, image push, deploy 자동화
- 개발·스테이징·운영 환경 변수를 분리
- 배포 전 health check를 수행하고 실패 시 자동 rollback
- Nginx reverse proxy로 frontend와 backend routing 구성
- Slack Webhook으로 배포 성공·실패 알림 제공

### Key Contributions

- Spring Boot Dockerfile과 React multi-stage Dockerfile 작성
- GitHub Actions workflow를 backend-ci, frontend-ci, deploy로 분리
- Gradle test 실패 시 배포가 중단되도록 quality gate 구성
- Docker image tag를 commit SHA 기반으로 관리
- EC2 서버에서 blue-green style 배포 script 작성
- `/health` endpoint 기반 배포 후 health check 적용
- `.env`, GitHub Secrets, 서버 환경 변수를 분리하여 secret 노출 방지
- Nginx access log와 error log를 수집하고 장애 분석에 활용
- README에 local 실행, 배포, rollback, troubleshooting 문서화

### Impact

- 배포 시간 42분에서 8분으로 단축
- 배포 실패 시 rollback 소요 시간 20분에서 2분으로 단축
- 신규 팀원 local 개발 환경 구축 시간 2시간에서 15분으로 단축
- 수동 배포 실수 0건 달성
- CI build failure를 PR 단계에서 발견하여 main branch 장애 유입 감소

### Tech Stack

GitHub Actions, Docker, Docker Compose, AWS EC2, AWS RDS, Nginx, Bash, Spring Boot, React, MySQL, Redis

---

### Project 2. ObservaStack — 서비스 모니터링 및 로그 수집 시스템

GitHub: https://github.com/doyoon-devops/observastack  
Period: 2024.11 - 2025.02  
Role: DevOps Engineer

운영 중인 웹 서비스의 서버 metric, container metric, application log를 수집하고 장애 알림을 제공하는 observability stack 프로젝트입니다.

### Problem

서비스 장애가 발생해도 CPU, memory, disk, API error rate, container 상태를 한곳에서 확인하기 어려웠고, 사용자가 문제를 제보한 뒤에야 장애를 인지하는 경우가 많았습니다.

### Solution

- Prometheus로 server와 container metric 수집
- Grafana dashboard로 주요 운영 지표 시각화
- Loki와 Promtail로 application log 수집
- Alertmanager와 Slack Webhook으로 장애 알림 구성
- 장애 대응 checklist와 dashboard 사용 문서 작성

### Key Contributions

- Node Exporter로 CPU, memory, disk, network metric 수집
- cAdvisor로 container별 CPU, memory, restart count 수집
- Prometheus scrape config와 alert rule 작성
- Grafana dashboard 9개 구성
- Loki label 설계를 service, environment, log_level 기준으로 구성
- API 5xx error, CPU 80% 이상, disk 85% 이상, container restart 기준 alert rule 작성
- 장애 시점 metric과 log를 함께 확인할 수 있도록 dashboard link 구성
- 장애 대응 Runbook 작성

### Impact

- 장애 탐지 평균 시간 45분에서 7분으로 단축
- 로그 검색 시간 30분에서 5분 이내로 단축
- API 5xx error 증가를 Slack으로 자동 감지
- 운영 dashboard 9개와 alert rule 14개 구축
- 장애 대응 Runbook 12개 작성

### Tech Stack

Prometheus, Grafana, Loki, Promtail, Alertmanager, Node Exporter, cAdvisor, Docker Compose, Slack Webhook, Linux

---

### Project 3. InfraLab — Terraform 기반 AWS 인프라 자동화

GitHub: https://github.com/doyoon-devops/infralab  
Period: 2024.08 - 2024.10  
Role: Cloud / IaC Engineer

AWS EC2, RDS, S3, Security Group, IAM 리소스를 Terraform으로 정의하고 재현 가능한 인프라 환경을 구성한 프로젝트입니다.

### Problem

AWS Console에서 수동으로 리소스를 생성하면 설정 누락이 발생하기 쉽고, 동일한 환경을 다시 만들거나 변경 이력을 추적하기 어렵습니다.

### Solution

- Terraform으로 AWS 인프라 리소스 선언
- 개발·스테이징 환경을 variable로 분리
- Security Group과 IAM policy를 최소 권한 기준으로 작성
- Terraform plan 결과를 PR에서 확인할 수 있도록 CI 구성
- S3 backend를 활용한 remote state 구조 실습

### Key Contributions

- VPC, subnet, security group, EC2, RDS, S3 module 작성
- Terraform variable과 output 구조 설계
- 환경별 tfvars 파일 분리
- IAM policy를 서비스별 최소 권한 기준으로 작성
- GitHub Actions에서 terraform fmt, validate, plan 실행
- Terraform state lock과 remote state 개념 학습 및 문서화
- 보안 그룹 inbound rule을 최소화하고 SSH 접근 IP 제한
- 인프라 변경 전후 diff를 README에 기록

### Impact

- AWS 인프라 재생성 시간을 1시간 이상에서 10분 이내로 단축
- 수동 설정 누락 문제 감소
- 환경별 인프라 차이를 코드로 확인 가능
- Terraform module 6개 작성
- PR 기반 인프라 변경 review flow 구축

### Tech Stack

Terraform, AWS EC2, AWS RDS, AWS S3, AWS IAM, AWS VPC, GitHub Actions, Linux

---

## Education

### 한국대학교 컴퓨터공학과

2020.03 - 2026.02 예정  
GPA: 4.14 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 컴퓨터네트워크
- 데이터베이스
- 클라우드컴퓨팅
- 분산시스템
- 소프트웨어공학
- 정보보안

---

## Awards / Activities

### 2025 교내 클라우드 인프라 경진대회 대상

2025.05

- DeployMate 프로젝트로 대상 수상
- CI/CD, Docker 기반 배포 자동화, rollback, monitoring 환경을 구현
- 운영 가능성과 자동화 완성도 항목에서 최고 점수 획득

### Cloud Native Study Lead

2024.09 - 2025.06

- 10명 규모의 Cloud Native 스터디 운영
- 주제: Docker, Kubernetes, AWS, Terraform, GitHub Actions, Prometheus, Grafana
- 매주 인프라 실습과 장애 사례 분석 진행
- 팀 프로젝트 배포 환경 코드 리뷰 담당

### Open Source Contribution

2025.01 - 2025.04

- Docker Compose 예제 repository README 개선
- Prometheus exporter 설정 문서 오타 수정
- Terraform AWS module 예제 주석 개선 PR 기여

---

## Certifications

- AWS Certified Cloud Practitioner
- SQLD
- 정보처리기사 필기 합격
- Certified Kubernetes Administrator 준비 중

---

## Technical Writing

- "GitHub Actions로 Spring Boot 배포 자동화하기"
- "Docker Compose로 개발 환경을 통일한 경험"
- "Prometheus와 Grafana로 장애를 빨리 발견하는 방법"
- "Terraform을 처음 도입할 때 실수하기 쉬운 것들"
- "배포 실패 시 Rollback Script를 만든 이유"

---

## Strengths

- 개발자가 기능 개발에 집중할 수 있도록 반복 작업을 자동화합니다.
- 인프라를 수동 설정이 아니라 코드와 문서로 관리하는 것을 중요하게 생각합니다.
- 배포 자동화뿐 아니라 모니터링, 로그, 알림, rollback까지 운영 흐름 전체를 고려합니다.
- 보안 그룹, secret, IAM 권한처럼 기본 보안 설정을 놓치지 않으려 합니다.
- 신입 수준에서 요구되는 Linux, Docker, AWS를 넘어 CI/CD, IaC, Observability까지 경험했습니다.

---

## Resume Keywords

DevOps Engineer, Cloud Engineer, Platform Engineer, AWS, Docker, Docker Compose, Kubernetes, Terraform, GitHub Actions, Jenkins, CI/CD, Nginx, Linux, Bash, Prometheus, Grafana, Loki, Alertmanager, CloudWatch, Infrastructure as Code, Monitoring, Logging, Blue-Green Deployment, Rolling Deployment, Rollback, Secret Management, Trivy, DevSecOps

---

# 2. Big Tech / Enterprise Target Resume — DevOps Engineer

## 이서현 | DevOps Engineer

Email: seohyun.lee.devops@gmail.com  
GitHub: https://github.com/seohyun-devops  
Portfolio: https://seohyun-devops.dev  
Blog: https://tech.seohyun-devops.dev  
LinkedIn: https://linkedin.com/in/seohyun-lee-devops  

---

## Summary

대규모 서비스 환경에서 안정적이고 재현 가능한 인프라와 배포 플랫폼을 구축하는 데 관심이 있는 신입 DevOps Engineer입니다.

AWS, Kubernetes, Terraform, Helm, Argo CD, GitHub Actions, Jenkins, Prometheus, Grafana, Loki, CloudWatch를 활용해 컨테이너 기반 배포 환경, GitOps, IaC, 모니터링, 보안 스캔, 장애 대응 체계를 구축했습니다. 특히 대기업·중견기업·빅테크 환경에서 중요하게 평가되는 **배포 안정성, 인프라 표준화, 권한 관리, 관측 가능성, SLO/SLI, 보안 내재화, 운영 자동화**를 중요하게 생각합니다.

DevOps를 단순히 배포 담당이 아니라 개발 생산성, 서비스 신뢰성, 운영 효율성을 높이는 플랫폼 엔지니어링 관점으로 접근합니다.

---

## Core Competencies

- AWS 기반 Production-like 인프라 설계
- Kubernetes 기반 Microservice 배포 및 운영
- Terraform 기반 IaC 및 환경 표준화
- Helm Chart 기반 Kubernetes 배포 템플릿화
- Argo CD 기반 GitOps Workflow 구성
- GitHub Actions / Jenkins 기반 CI/CD Pipeline 구축
- Prometheus / Grafana 기반 SLI Dashboard 구성
- Loki / CloudWatch 기반 로그 수집 및 장애 분석
- Trivy / Snyk 기반 Container & Dependency Security Scanning
- IAM / Secret / Network Security 기본 설계
- Blue-Green / Canary / Rolling Deployment 전략
- SLO / Error Budget 기초 설계
- Cost Monitoring 및 Resource Request/Limit 최적화

---

## Skills

### Cloud

- AWS EC2
- AWS EKS Basic
- AWS RDS
- AWS S3
- AWS ECR
- AWS VPC
- AWS IAM
- AWS ALB
- AWS CloudWatch
- AWS Route 53
- AWS Cost Explorer

### Container / Kubernetes

- Docker
- Docker Compose
- Kubernetes
- Helm
- Kustomize Basic
- Argo CD
- Ingress
- ConfigMap
- Secret
- Deployment
- StatefulSet Basic
- HPA Basic
- Resource Requests / Limits

### CI/CD

- GitHub Actions
- Jenkins
- Argo CD
- GitOps
- Build Pipeline
- Test Pipeline
- Deploy Pipeline
- Canary Deployment Basic
- Blue-Green Deployment
- Rollback
- Quality Gate

### Infrastructure as Code

- Terraform
- Terraform Module
- Terraform Remote State
- Terraform Workspace
- AWS Provider
- tfsec Basic
- Checkov Basic

### Observability

- Prometheus
- Grafana
- Loki
- Promtail
- Alertmanager
- CloudWatch
- Node Exporter
- kube-state-metrics
- cAdvisor
- OpenTelemetry Basic

### Security / DevSecOps

- IAM Least Privilege
- Security Group
- Network ACL Basic
- Secret Management
- GitHub Secrets
- Kubernetes Secret
- External Secrets Concept
- Trivy
- Snyk Basic
- OWASP Dependency-Check
- Container Image Scanning
- IaC Scanning
- TLS / HTTPS

### OS / Scripting

- Linux
- Bash
- Shell Script
- Python Basic
- Cron
- Systemd
- Nginx
- SSH
- TCP/IP
- DNS

---

## Experience

### DevOps Engineer Intern

**CommerceCore Platform Team**  
2025.06 - 2025.12

이커머스 플랫폼의 배포 자동화, Kubernetes 운영, 모니터링, 보안 스캔 파이프라인 개선을 담당했습니다.

### Key Contributions

- Spring Boot microservice 6개와 React admin service를 Docker image로 표준화
- GitHub Actions 기반 CI pipeline을 개선하여 build, test, image scan, image push, manifest update 자동화
- Argo CD 기반 GitOps 배포 workflow를 구성하여 application manifest와 배포 이력을 Git으로 관리
- Kubernetes namespace를 dev, staging, prod로 분리하고 환경별 ConfigMap, Secret, resource limit 설정
- Helm chart를 작성하여 서비스별 중복 Kubernetes manifest를 약 48% 감소
- Prometheus, Grafana, kube-state-metrics 기반 cluster와 application dashboard 구축
- API error rate, p95 latency, pod restart, CPU throttling 기준 alert rule 작성
- Loki 기반 service log 수집을 구성하고 trace_id 기준 로그 검색 가능하도록 logging convention 제안
- Trivy image scanning과 dependency vulnerability scanning을 CI에 추가하여 critical 취약점 발견 시 배포 중단
- Terraform으로 ECR, S3, RDS, IAM, security group 리소스를 코드화
- Resource request/limit을 조정하여 staging cluster over-provisioning 비용 23% 절감
- 장애 대응 Runbook을 작성하고 장애 모의 훈련에서 MTTD와 MTTR 측정

### Impact

- 배포 lead time 45분에서 11분으로 단축
- Kubernetes manifest 중복 48% 감소
- 배포 이력 추적 누락 0건 달성
- Critical image vulnerability 12건 사전 차단
- 장애 탐지 평균 시간 35분에서 6분으로 단축
- Staging cluster 비용 23% 절감
- 운영 dashboard 14개, alert rule 26개 구축
- Runbook 기반 장애 복구 시간을 40분에서 15분으로 단축

### Tech Stack

AWS, Kubernetes, Docker, Helm, Argo CD, GitHub Actions, Terraform, Prometheus, Grafana, Loki, Trivy, Jenkins, Linux

---

## Projects

---

### Project 1. KubeDeploy Platform — Kubernetes 기반 GitOps 배포 플랫폼

GitHub: https://github.com/seohyun-devops/kubedeploy-platform  
Demo: https://kubedeploy.seohyun-devops.dev  
Period: 2025.02 - 2025.05  
Role: DevOps / Platform Engineer

여러 microservice를 Kubernetes에 배포하고, GitHub Actions와 Argo CD를 활용해 GitOps 방식으로 운영하는 배포 플랫폼 프로젝트입니다.

### Problem

서비스가 여러 개로 나뉘면 각 서비스의 Dockerfile, Kubernetes manifest, 환경 변수, 배포 방식이 달라져 운영 복잡도가 증가합니다. 수동 kubectl 배포는 이력 추적과 rollback이 어렵습니다.

### Solution

- Service별 Docker image build pipeline 표준화
- Kubernetes manifest를 Helm chart로 템플릿화
- Argo CD로 GitOps 기반 배포 구성
- 개발·스테이징·운영 namespace 분리
- 배포 후 health check와 rollback 전략 구성
- Prometheus와 Grafana로 service SLI dashboard 구축

### Technical Details

- Spring Boot service 4개, React service 1개를 Docker image로 구성
- GitHub Actions에서 test, build, Trivy scan, image push 수행
- 배포 repository의 Helm values image tag를 자동 업데이트
- Argo CD가 manifest 변경을 감지해 Kubernetes cluster에 sync
- Ingress Nginx로 service routing 구성
- ConfigMap과 Secret으로 환경 설정 분리
- HPA를 설정하여 CPU 사용률 기준 pod auto scaling 실습
- Prometheus로 request count, error rate, latency metric 수집
- Grafana dashboard에서 RED metric과 resource metric 시각화
- 배포 실패 시 Argo CD rollback과 이전 image tag 복구 절차 문서화

### Impact

- 수동 배포 시간을 50분에서 9분으로 단축
- 배포 이력 추적 가능성 100% 확보
- 서비스별 Kubernetes manifest 중복 52% 감소
- Rollback 소요 시간 25분에서 3분으로 단축
- API 5xx error와 p95 latency를 dashboard에서 실시간 확인 가능
- 배포 실패 원인 추적 시간을 30분에서 8분 이내로 단축

### Tech Stack

Kubernetes, Docker, Helm, Argo CD, GitHub Actions, AWS EC2, ECR, Ingress Nginx, Prometheus, Grafana, Loki, Trivy

---

### Project 2. Terraform Landing Zone — AWS 인프라 표준화 프로젝트

GitHub: https://github.com/seohyun-devops/terraform-landing-zone  
Period: 2024.11 - 2025.01  
Role: Cloud / IaC Engineer

AWS VPC, subnet, security group, EC2, RDS, ECR, S3, IAM, ALB를 Terraform module로 구성하여 재사용 가능한 인프라 표준 환경을 만든 프로젝트입니다.

### Problem

AWS 리소스를 콘솔에서 직접 생성하면 환경별 차이가 생기고 변경 이력을 추적하기 어렵습니다. 또한 네트워크와 권한 설정이 명확하지 않으면 보안 사고와 운영 장애로 이어질 수 있습니다.

### Solution

- Terraform module 기반 AWS 인프라 구성
- dev, staging, prod 환경별 변수 분리
- Remote state와 state lock 구조 구성
- IAM policy와 security group을 최소 권한 기준으로 작성
- PR에서 terraform fmt, validate, plan 자동 실행
- tfsec, Checkov 기반 IaC security scanning 적용

### Key Contributions

- network, compute, database, storage, iam, security module 작성
- VPC public/private subnet 구조 설계
- Bastion host 없이 SSM Session Manager를 사용하는 구조 검토 및 문서화
- RDS subnet group과 security group 분리
- ECR repository와 lifecycle policy 작성
- S3 remote backend 구성
- Terraform module input/output 문서화
- GitHub Actions에서 terraform plan 결과를 PR comment로 출력
- tfsec로 public ingress, open security group, weak encryption 설정 탐지
- 인프라 변경 승인 checklist 작성

### Impact

- 신규 환경 생성 시간을 2시간 이상에서 15분 이내로 단축
- 수동 설정 누락으로 인한 환경 차이 감소
- Terraform module 9개 작성
- IaC security issue 18건 사전 탐지
- PR 기반 인프라 변경 review flow 구축
- 개발·스테이징 환경의 네트워크 구조 표준화

### Tech Stack

Terraform, AWS VPC, AWS EC2, AWS RDS, AWS ECR, AWS S3, AWS IAM, AWS ALB, GitHub Actions, tfsec, Checkov

---

### Project 3. Reliability Dashboard — SLO 기반 서비스 신뢰성 모니터링

GitHub: https://github.com/seohyun-devops/reliability-dashboard  
Period: 2024.08 - 2024.10  
Role: SRE / Observability Engineer

웹 서비스의 가용성, 지연시간, 에러율을 SLI로 정의하고 SLO 기반 dashboard와 alert rule을 구성한 프로젝트입니다.

### Problem

단순 CPU 사용률이나 서버 다운 여부만으로는 사용자가 실제로 경험하는 서비스 품질을 알기 어렵습니다. 개발팀은 사용자 관점의 지표를 기준으로 장애를 감지하고 개선해야 합니다.

### Solution

- Availability, Latency, Error Rate를 핵심 SLI로 정의
- Prometheus metric과 application log를 함께 수집
- Grafana SLO dashboard 구성
- Error budget burn rate 개념을 적용한 alert rule 작성
- 장애 대응 Runbook 작성
- 배포 전후 SLI 변화를 비교하는 dashboard 구성

### Key Contributions

- RED method 기반 request rate, error rate, duration metric 수집
- Spring Boot Actuator와 Prometheus endpoint 연동
- Grafana dashboard에서 p50, p95, p99 latency 시각화
- 5xx error rate와 p95 latency threshold alert rule 작성
- Error budget burn rate alert 개념을 학습하고 실습 적용
- Loki log query로 특정 trace_id의 요청 흐름 추적
- 장애 대응 Runbook과 postmortem template 작성
- 배포 후 30분간 latency와 error rate를 집중 관찰하는 release dashboard 구성

### Impact

- 장애 탐지 평균 시간 40분에서 5분으로 단축
- 배포 후 regression 탐지 가능
- 사용자 관점의 availability, latency, error rate dashboard 구축
- 장애 대응 Runbook 15개 작성
- Postmortem template 도입으로 장애 원인·대응·재발 방지 기록 표준화

### Tech Stack

Prometheus, Grafana, Loki, Alertmanager, Spring Boot Actuator, Docker, Linux, Slack Webhook

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
- 컴퓨터네트워크
- 데이터베이스
- 분산시스템
- 클라우드컴퓨팅
- 정보보안
- 소프트웨어공학

---

## Awards

### 2025 SW 중심대학 공동 클라우드 네이티브 경진대회 최우수상

2025.08

- KubeDeploy Platform 프로젝트로 최우수상 수상
- Kubernetes, GitOps, Helm, Observability, Rollback 자동화를 end-to-end로 구현
- 운영 안정성과 플랫폼화 가능성에서 높은 평가를 받음

### 2024 교내 네트워크·운영체제 경진대회 은상

2024.11

- Linux, TCP/IP, DNS, HTTP, Process, Memory, File System 문제 풀이
- 120명 중 7위

---

## Activities

### Platform Engineering Study Lead

2025.01 - 2025.06

- 12명 규모의 Platform Engineering 스터디 운영
- 주제: Kubernetes, Terraform, GitOps, Observability, SRE, DevSecOps
- 매주 인프라 코드 리뷰와 장애 대응 시나리오 실습 진행
- Kubernetes manifest와 Helm chart best practice 발표

### CS / Infra Interview Study

2024.07 - 2024.12

- 운영체제, 네트워크, 데이터베이스, 보안 면접 스터디 참여
- TCP 3-way handshake, DNS, TLS, Load Balancing, Process, Thread, Deadlock 주제 발표

---

## Certifications

- AWS Certified Cloud Practitioner
- SQLD
- 정보처리기사 필기 합격
- Certified Kubernetes Administrator 준비 중
- HashiCorp Terraform Associate 준비 중

---

## Technical Writing

- "GitOps 배포가 수동 kubectl보다 안전한 이유"
- "Kubernetes Manifest를 Helm Chart로 줄인 과정"
- "Terraform Module을 설계하며 배운 점"
- "SLO와 Error Budget을 개인 프로젝트에 적용해본 경험"
- "Trivy와 tfsec로 CI/CD에 보안을 넣은 방법"

---

## Strengths

- 인프라와 배포 환경을 코드로 관리하고 재현 가능하게 만드는 것을 중요하게 생각합니다.
- DevOps를 단순 배포 자동화가 아니라 개발자 생산성, 서비스 신뢰성, 운영 효율성 개선으로 이해합니다.
- Kubernetes, Terraform, GitOps, Observability, DevSecOps를 end-to-end로 연결한 경험이 있습니다.
- 장애를 숨기지 않고 metric, log, runbook, postmortem으로 학습 가능한 형태로 남깁니다.
- 대기업·빅테크에서 중요하게 보는 표준화, 보안, 신뢰성, 운영 가능성을 신입 수준에서 설득력 있게 보여줄 수 있습니다.

---

## Resume Keywords

DevOps Engineer, Platform Engineer, SRE, Cloud Engineer, AWS, Kubernetes, EKS, Docker, Helm, Argo CD, GitOps, Terraform, Infrastructure as Code, GitHub Actions, Jenkins, CI/CD, Prometheus, Grafana, Loki, Alertmanager, CloudWatch, SLO, SLI, Error Budget, Trivy, Snyk, tfsec, Checkov, DevSecOps, IAM, VPC, Nginx, Linux, Bash, Blue-Green Deployment, Canary Deployment, Rolling Deployment

---

# 3. Tech Startup Target Resume — DevOps Engineer

## 박민재 | DevOps Engineer

Email: minjae.park.devops@gmail.com  
GitHub: https://github.com/minjae-startup-devops  
Portfolio: https://minjae-devops.dev  
Blog: https://blog.minjae-devops.dev  
LinkedIn: https://linkedin.com/in/minjae-park-devops  

---

## Summary

초기 스타트업에서 빠르게 배포 가능한 인프라를 만들고, 작은 팀의 개발 속도와 운영 안정성을 동시에 높이는 데 강점이 있는 신입 DevOps Engineer입니다.

AWS, Docker, GitHub Actions, Terraform, Nginx, Prometheus, Grafana, CloudWatch, Sentry, Slack Alert를 활용해 MVP부터 베타 운영까지 필요한 배포 자동화, 모니터링, 로그 수집, 비용 관리, 장애 대응 환경을 구축했습니다. 작은 팀에서 백엔드·프론트엔드 개발자와 협업하며 **배포 시간 단축, 장애 탐지, 서버 비용 절감, 개발 환경 표준화, 운영 자동화**를 주도한 경험이 있습니다.

스타트업 환경에서 중요한 빠른 실행력, 비용 효율성, 단순하지만 확장 가능한 인프라 설계, 개발자 경험 개선을 중요하게 생각합니다.

---

## Core Competencies

- MVP Infra Setup
- 빠른 CI/CD Pipeline 구축
- AWS 기반 비용 효율적 배포 환경 구성
- Docker Compose 기반 개발·운영 환경 표준화
- GitHub Actions 기반 자동 배포
- Nginx Reverse Proxy 및 HTTPS 구성
- Terraform 기반 최소 인프라 코드화
- Prometheus / Grafana / CloudWatch 기반 모니터링
- Sentry / Slack Alert 기반 장애 알림
- 배포 실패 rollback script 작성
- Secret 및 환경 변수 관리
- 서버 비용 모니터링 및 리소스 최적화
- 작은 팀의 개발자 경험 개선

---

## Skills

### Cloud / Infra

- AWS EC2
- AWS RDS
- AWS S3
- AWS CloudWatch
- AWS Route 53
- AWS IAM
- AWS ECR Basic
- AWS Lightsail Basic
- Vercel
- Railway
- Cloudflare

### Container / Deployment

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Jenkins Basic
- Blue-Green Deployment Basic
- Rolling Restart
- Health Check
- Rollback Script

### Infrastructure as Code

- Terraform
- Terraform AWS Provider
- Environment Variables
- Remote State Basic
- Module Basic

### Monitoring / Incident

- Prometheus
- Grafana
- CloudWatch
- Sentry
- Loki Basic
- Slack Webhook
- Uptime Kuma
- Alert Rule
- Runbook
- Postmortem

### Security

- IAM Least Privilege Basic
- Security Group
- HTTPS / TLS
- GitHub Secrets
- Environment Secret
- Docker Image Scanning
- Trivy Basic
- Dependabot
- SSH Key Management

### OS / Scripting

- Linux
- Ubuntu
- Bash
- Shell Script
- Cron
- Systemd
- SSH
- DNS
- TCP/IP

### Collaboration

- Git
- GitHub
- Notion
- Slack
- Linear
- Figma Basic
- Postman
- Swagger

---

## Experience

### Founding DevOps Engineer Intern

**LocalLoop**  
2025.05 - 2025.11

동네 기반 소모임·예약 플랫폼을 만드는 초기 스타트업에서 MVP 인프라, CI/CD, 모니터링, 장애 대응 환경을 구축했습니다.

### Key Contributions

- Spring Boot API, Next.js frontend, MySQL, Redis 기반 서비스를 AWS와 Vercel에 배포
- GitHub Actions 기반 backend CI/CD를 구축하여 test, Docker build, image push, EC2 deploy 자동화
- frontend는 Vercel preview deployment를 활용해 PR별 테스트 URL 제공
- Docker Compose 기반 local 개발 환경을 구성하여 신규 개발자 onboarding 시간 단축
- Nginx reverse proxy, HTTPS, domain, CORS 설정을 정리하여 운영 배포 안정화
- AWS EC2, RDS, S3 비용을 매주 확인하고 instance type, storage, log retention을 조정
- Prometheus, Grafana, CloudWatch, Sentry를 활용해 서버 metric, API error, frontend error를 모니터링
- 예약 API 장애 발생 시 Slack alert와 runbook을 기반으로 원인 파악 및 rollback 수행
- 운영 환경 변수를 GitHub Secrets와 서버 secret으로 분리하고 repository 내 민감 정보 제거
- Uptime Kuma로 주요 endpoint health check와 외부 사용자 관점의 가용성 모니터링 구성
- 배포 실패 시 이전 Docker image tag로 복구하는 rollback script 작성
- 장애 대응 후 postmortem 문서를 작성하고 재발 방지 action item 관리

### Startup Impact

- 평균 배포 시간 40분에서 6분으로 단축
- 신규 개발자 local 환경 구축 시간 3시간에서 20분으로 단축
- 베타 운영 중 주요 장애 탐지 시간을 평균 50분에서 7분으로 단축
- AWS 월 비용 31% 절감
- 배포 실패 rollback 시간을 25분에서 3분으로 단축
- 6주간 베타 사용자 380명 규모 서비스 운영 지원
- Runbook 18개와 postmortem 7개 작성

### Tech Stack

AWS EC2, AWS RDS, AWS S3, Vercel, Docker, Docker Compose, GitHub Actions, Nginx, Prometheus, Grafana, CloudWatch, Sentry, Uptime Kuma, Bash

---

## Projects

---

### Project 1. StartupOps — 초기 스타트업용 배포·모니터링 템플릿

GitHub: https://github.com/minjae-startup-devops/startupops  
Demo: https://startupops.dev  
Period: 2025.01 - 2025.04  
Role: DevOps Engineer / Platform Engineer

초기 스타트업이 Spring Boot, Next.js, MySQL, Redis 기반 서비스를 빠르게 배포하고 모니터링할 수 있도록 만든 DevOps template 프로젝트입니다.

### Problem

초기 스타트업은 기능 개발 속도가 중요하지만, 배포와 운영 환경이 정리되지 않으면 배포 실수, 장애 인지 지연, 신규 개발자 onboarding 지연이 반복됩니다. 그러나 처음부터 복잡한 Kubernetes 환경을 도입하기에는 비용과 운영 부담이 큽니다.

### Solution

- Docker Compose 기반 local 및 production-like 환경 제공
- GitHub Actions 기반 backend / frontend CI/CD pipeline 구성
- AWS EC2, RDS, S3, Vercel 기반 저비용 배포 구조 설계
- Prometheus, Grafana, Sentry, Uptime Kuma 기반 최소 운영 모니터링 구성
- Nginx, HTTPS, domain, environment variable 설정 문서화
- Rollback script와 장애 대응 Runbook 제공

### Key Contributions

- Spring Boot, Next.js, MySQL, Redis, Nginx Docker Compose 구성
- GitHub Actions workflow template 작성
- Backend build, test, Docker image push, EC2 deploy 자동화
- Frontend preview deployment와 production deployment 분리
- `.env.example`, secret checklist, environment setup guide 작성
- Prometheus metric, Grafana dashboard, Sentry error tracking 구성
- Health check endpoint와 Uptime Kuma 연동
- AWS 비용 절감을 위한 instance sizing guide 작성
- 배포 실패 시 이전 image tag로 rollback하는 script 작성
- 장애 대응 checklist, postmortem template, release note template 작성

### Impact

- MVP 인프라 구축 시간을 2일에서 3시간 이내로 단축
- 수동 배포 명령어 12단계를 1단계로 자동화
- 신규 개발자 onboarding 시간을 3시간에서 15분으로 단축
- 장애 탐지 시간을 사용자 제보 이후에서 5분 이내 알림으로 개선
- AWS 월 예상 비용 28% 절감 가능한 구조 제안
- 초기 서비스 3개 프로젝트에 재사용 가능한 template 제공

### Tech Stack

AWS EC2, AWS RDS, AWS S3, Vercel, Docker, Docker Compose, GitHub Actions, Nginx, Prometheus, Grafana, Sentry, Uptime Kuma, Bash

---

### Project 2. CostGuard — AWS 비용 모니터링 및 알림 도구

GitHub: https://github.com/minjae-startup-devops/costguard  
Period: 2024.10 - 2024.12  
Role: Cloud Automation Engineer

초기 스타트업이나 개인 프로젝트에서 AWS 비용을 추적하고 비정상 비용 증가를 Slack으로 알림하는 자동화 도구입니다.

### Problem

초기 팀에서는 AWS 비용을 정기적으로 확인하지 않아 사용하지 않는 리소스, 과한 instance type, log retention 설정 때문에 예상보다 큰 비용이 발생할 수 있습니다.

### Solution

- AWS Cost Explorer API를 활용해 일별 비용 수집
- 서비스별 비용을 PostgreSQL에 저장
- 비용 급증 기준을 설정하고 Slack으로 알림
- EC2, RDS, S3, CloudWatch log 사용량을 주기적으로 점검
- 미사용 리소스 후보를 리포트로 생성
- 비용 dashboard를 Metabase로 시각화

### Key Contributions

- AWS Cost Explorer API 연동 script 작성
- 비용 데이터를 daily_aws_cost table에 적재
- 전일 대비 30% 이상 비용 증가 시 Slack alert 발송
- EC2 stopped instance, unattached EBS, 오래된 snapshot 탐지 script 작성
- CloudWatch log retention 미설정 log group 탐지
- S3 bucket size와 storage class 사용량 조회
- 주간 비용 리포트를 Markdown으로 생성
- GitHub Actions scheduled workflow로 매일 실행되도록 구성

### Impact

- 미사용 EBS와 snapshot 정리로 테스트 계정 비용 22% 절감
- 비용 급증 탐지 시간을 월말 정산 이후에서 일 단위로 단축
- CloudWatch log retention 미설정 9건 탐지
- 주간 비용 리포트 작성 자동화
- 초기 팀에서 비용 관리 checklist로 재사용 가능

### Tech Stack

Python, AWS Cost Explorer, AWS EC2, AWS S3, AWS CloudWatch, PostgreSQL, GitHub Actions, Slack Webhook, Metabase

---

### Project 3. IncidentBot — 장애 알림 및 대응 자동화 봇

GitHub: https://github.com/minjae-startup-devops/incidentbot  
Period: 2024.07 - 2024.09  
Role: DevOps Automation Engineer

Prometheus Alertmanager와 Slack을 연동하여 장애 알림, 담당자 호출, Runbook 링크 제공, postmortem template 생성을 자동화하는 도구입니다.

### Problem

작은 팀에서는 장애 알림이 와도 어떤 사람이 대응해야 하는지, 어떤 dashboard를 봐야 하는지, 어떤 runbook을 따라야 하는지 정리되어 있지 않아 복구 시간이 길어집니다.

### Solution

- Alertmanager webhook을 수신하는 bot server 구현
- Alert label에 따라 담당자, severity, runbook link를 매핑
- Slack channel에 장애 요약, dashboard link, runbook link 자동 전송
- 장애 종료 시 postmortem template 자동 생성
- 반복 장애를 확인할 수 있도록 incident history 저장

### Key Contributions

- FastAPI 기반 Alertmanager webhook receiver 구현
- Alert rule naming convention 설계
- service, severity, environment label 기준 routing logic 작성
- Slack Block Kit 메시지 구성
- Grafana dashboard link와 Loki log query link 자동 생성
- Incident start, acknowledge, resolve 상태 관리
- Postmortem Markdown template 자동 생성
- 반복 장애 횟수를 service별로 집계하는 dashboard 구성

### Impact

- 장애 대응 시작 시간을 평균 20분에서 5분 이내로 단축
- Runbook 누락으로 인한 대응 지연 감소
- Postmortem 작성 시간을 40분에서 10분으로 단축
- 반복 장애 top service를 확인할 수 있는 dashboard 제공
- 장애 대응 프로세스를 작은 팀에서도 표준화

### Tech Stack

Python, FastAPI, Prometheus Alertmanager, Slack API, Grafana, Loki, PostgreSQL, Docker

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 예정  
GPA: 4.08 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 컴퓨터네트워크
- 데이터베이스
- 클라우드컴퓨팅
- 정보보안
- 소프트웨어공학
- 창업과 소프트웨어 제품 개발

---

## Awards / Activities

### 2025 대학 연합 클라우드 MVP 해커톤 대상

2025.06

- StartupOps 프로젝트로 대상 수상
- 초기 스타트업이 빠르게 사용할 수 있는 배포·모니터링 템플릿을 구현
- 비용 효율성과 실용성, 개발자 경험 개선 측면에서 높은 평가를 받음

### 2024 스타트업 운영 자동화 해커톤 최우수상

2024.12

- CostGuard 프로젝트로 최우수상 수상
- AWS 비용 모니터링, 미사용 리소스 탐지, Slack 비용 알림 자동화 구현
- 초기 팀의 비용 관리 문제를 현실적으로 해결한 점에서 높은 평가를 받음

### Startup DevOps Study Organizer

2024.09 - 2025.05

- 15명 규모의 스타트업 DevOps 스터디 운영
- 주제: Docker, AWS, GitHub Actions, Terraform, Monitoring, Cost Optimization, Incident Response
- 매주 실제 서비스 배포 구조를 분석하고 최소 운영 환경을 직접 구축

---

## Certifications

- AWS Certified Cloud Practitioner
- SQLD
- 정보처리기사 필기 준비 중
- HashiCorp Terraform Associate 준비 중

---

## Product / Ops Metrics Experience

- Deployment Lead Time
- Deployment Frequency
- Rollback Time
- Change Failure Rate Basic
- Mean Time To Detect
- Mean Time To Recovery
- API Error Rate
- Uptime
- Cloud Cost
- Resource Utilization
- Build Failure Rate
- Onboarding Time
- Alert Noise
- Incident Count

---

## Technical Writing

- "초기 스타트업에서 Kubernetes보다 Docker Compose가 먼저였던 이유"
- "GitHub Actions로 배포 시간을 40분에서 6분으로 줄인 경험"
- "AWS 비용을 31% 줄이기 위해 확인한 것들"
- "장애 알림에 Runbook 링크를 붙인 이유"
- "개발자 Onboarding 시간을 줄이는 DevOps 템플릿 만들기"

---

## Strengths

- 작은 팀이 빠르게 제품을 출시할 수 있도록 단순하고 실용적인 인프라를 설계합니다.
- 과도한 복잡도를 피하고, 현재 단계에 맞는 DevOps 도구와 구조를 선택합니다.
- 배포 자동화, 모니터링, 장애 알림, 비용 관리까지 운영에 필요한 최소 체계를 빠르게 구축할 수 있습니다.
- 개발자 경험을 중요하게 생각하며, onboarding, local environment, preview deployment를 개선합니다.
- 스타트업에서 중요한 속도, 비용 효율성, 오너십, 장애 대응력을 갖추고 있습니다.

---

## Resume Keywords

DevOps Engineer, Startup DevOps Engineer, Cloud Engineer, AWS, Docker, Docker Compose, GitHub Actions, Terraform, Nginx, Linux, Bash, CI/CD, Vercel, Railway, CloudWatch, Prometheus, Grafana, Sentry, Uptime Kuma, Slack Alert, Incident Response, Runbook, Postmortem, Cost Optimization, AWS Cost Explorer, Secret Management, HTTPS, Rollback, MVP Infra, Developer Experience