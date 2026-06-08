# DevOps Engineer — Foreign / Global Company Target Resume

## Daniel Kim | DevOps Engineer

Email: daniel.kim.devops@gmail.com  
GitHub: https://github.com/danielkim-devops  
Portfolio: https://danielkim-devops.dev  
Blog: https://blog.danielkim-devops.dev  
LinkedIn: https://linkedin.com/in/danielkim-devops  

---

## Summary

Entry-level DevOps Engineer with hands-on experience building CI/CD pipelines, containerized deployment environments, cloud infrastructure, observability stacks, and infrastructure-as-code workflows. Skilled in AWS, Docker, Kubernetes, Terraform, GitHub Actions, Jenkins, Helm, Argo CD, Prometheus, Grafana, Loki, Nginx, Linux, and Bash.

Built DevOps projects that reduced deployment lead time, improved rollback speed, increased observability, standardized infrastructure, and integrated security checks into delivery pipelines. Strong interest in platform engineering, developer productivity, cloud reliability, DevSecOps, and automation.

---

## Skills

### Cloud / Infra

- AWS EC2
- AWS RDS
- AWS S3
- AWS ECR
- AWS IAM
- AWS VPC
- AWS ALB
- AWS Route 53
- AWS CloudWatch
- AWS Cost Explorer

### Container / Orchestration

- Docker
- Docker Compose
- Kubernetes
- Helm
- Argo CD
- Kustomize Basic
- Ingress Nginx
- ConfigMap
- Secret
- HPA Basic
- Resource Requests / Limits

### CI/CD

- GitHub Actions
- Jenkins
- GitOps
- Build Pipeline
- Test Pipeline
- Deploy Pipeline
- Blue-Green Deployment
- Rolling Deployment
- Rollback
- Health Check
- Quality Gate

### Infrastructure as Code

- Terraform
- Terraform Modules
- Terraform Remote State
- Terraform Workspace
- AWS Provider
- tfsec Basic
- Checkov Basic

### Observability / Reliability

- Prometheus
- Grafana
- Loki
- Promtail
- Alertmanager
- CloudWatch
- Node Exporter
- cAdvisor
- kube-state-metrics
- SLI / SLO Basic
- Runbook
- Postmortem

### Security / DevSecOps

- IAM Least Privilege
- Security Groups
- Secret Management
- GitHub Secrets
- Kubernetes Secrets
- Trivy
- Snyk Basic
- OWASP Dependency-Check
- Container Image Scanning
- IaC Scanning
- HTTPS / TLS

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
- Nginx

---

## Experience

### DevOps Engineer Intern

**CommerceCore Platform Team**  
Jun 2025 - Dec 2025

Worked on CI/CD, Kubernetes deployment, monitoring, logging, infrastructure automation, and DevSecOps improvements for an e-commerce platform.

- Standardized Docker images for 6 Spring Boot microservices and 1 React admin service.
- Improved GitHub Actions CI pipeline by automating build, test, Trivy image scan, Docker image push, and deployment manifest updates.
- Reduced deployment lead time from 45 minutes to 11 minutes by replacing manual deployment steps with CI/CD automation and GitOps workflow.
- Implemented Argo CD-based GitOps deployment, enabling deployment history tracking and rollback through Git-managed Kubernetes manifests.
- Created Helm charts to reduce duplicated Kubernetes manifests by 48%.
- Separated Kubernetes namespaces for dev, staging, and production with environment-specific ConfigMaps, Secrets, and resource limits.
- Built Prometheus and Grafana dashboards for API error rate, p95 latency, pod restarts, CPU throttling, memory usage, and node resource utilization.
- Reduced average incident detection time from 35 minutes to 6 minutes by configuring Alertmanager and Slack alerts.
- Integrated Trivy and dependency vulnerability scanning into CI, blocking deployments with critical image vulnerabilities.
- Used Terraform to provision AWS ECR, S3, RDS, IAM, and security group resources.
- Reduced staging cluster over-provisioning cost by 23% by tuning resource requests and limits.
- Wrote incident runbooks and participated in failure simulation exercises to measure MTTD and MTTR.

---

## Projects

### KubeDeploy Platform — Kubernetes GitOps Deployment Platform

GitHub: https://github.com/danielkim-devops/kubedeploy-platform  
Period: Feb 2025 - May 2025  
Role: DevOps / Platform Engineer

Kubernetes-based GitOps deployment platform for multiple microservices.

- Containerized 4 Spring Boot services and 1 React service with Docker.
- Built GitHub Actions workflows for test, build, Trivy scan, image push, and Helm values update.
- Configured Argo CD to sync Kubernetes manifests from a deployment repository.
- Reduced manual deployment time from 50 minutes to 9 minutes.
- Reduced rollback time from 25 minutes to 3 minutes using GitOps rollback and image tag restoration.
- Built Helm charts for service deployment, ingress, config, secret, resource limits, and health checks.
- Configured Ingress Nginx routing for multiple services.
- Added Prometheus metrics and Grafana dashboards for request rate, error rate, latency, and resource usage.
- Improved deployment failure investigation time from 30 minutes to under 8 minutes by centralizing logs and deployment history.

Tech Stack: Kubernetes, Docker, Helm, Argo CD, GitHub Actions, AWS EC2, AWS ECR, Ingress Nginx, Prometheus, Grafana, Loki, Trivy

---

### Terraform Landing Zone — AWS Infrastructure as Code

GitHub: https://github.com/danielkim-devops/terraform-landing-zone  
Period: Nov 2024 - Jan 2025  
Role: Cloud / IaC Engineer

Reusable Terraform modules for AWS infrastructure standardization.

- Built Terraform modules for VPC, subnet, security group, EC2, RDS, ECR, S3, IAM, and ALB.
- Reduced new environment setup time from over 2 hours to under 15 minutes.
- Separated dev, staging, and production environments using tfvars and workspace strategy.
- Configured S3 remote state and documented state locking concepts.
- Added GitHub Actions workflow for terraform fmt, validate, plan, tfsec, and Checkov.
- Detected 18 IaC security issues including overly permissive ingress rules and missing encryption settings.
- Implemented PR-based infrastructure review flow with terraform plan output comments.
- Documented infrastructure change checklist, module inputs, outputs, and rollback considerations.

Tech Stack: Terraform, AWS VPC, AWS EC2, AWS RDS, AWS ECR, AWS S3, AWS IAM, AWS ALB, GitHub Actions, tfsec, Checkov

---

## Education

### Korea University of Technology — B.S. in Computer Science

Mar 2020 - Feb 2026 expected  
GPA: 4.14 / 4.5

Relevant Coursework:

- Data Structures
- Algorithms
- Operating Systems
- Computer Networks
- Database Systems
- Distributed Systems
- Cloud Computing
- Information Security
- Software Engineering

---

## Awards & Activities

### Grand Prize — University Cloud Infrastructure Contest

May 2025

- Won grand prize with KubeDeploy Platform.
- Presented CI/CD automation, Kubernetes GitOps deployment, Helm chart standardization, observability, rollback, and security scanning.

### Platform Engineering Study Lead

Jan 2025 - Jun 2025

- Led weekly sessions on Docker, Kubernetes, Terraform, GitOps, CI/CD, observability, SRE, and DevSecOps.
- Organized infrastructure code reviews and incident-response simulations.

---

## Certifications

- AWS Certified Cloud Practitioner
- HashiCorp Terraform Associate, in progress
- Certified Kubernetes Administrator, in progress
- SQLD
- Engineer Information Processing, written exam passed

---

## Keywords

DevOps Engineer, Platform Engineer, SRE, Cloud Engineer, AWS, Docker, Kubernetes, Helm, Argo CD, GitOps, Terraform, Infrastructure as Code, GitHub Actions, Jenkins, CI/CD, Prometheus, Grafana, Loki, Alertmanager, CloudWatch, SLI, SLO, Error Budget, Linux, Bash, Nginx, Trivy, Snyk, tfsec, Checkov, DevSecOps, IAM, VPC, Secret Management, Blue-Green Deployment, Canary Deployment, Rolling Deployment, Rollback