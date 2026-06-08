# AI Product Engineer Resume Set

> Target: Korea / Entry-level Developer / Max Internship Experience  
> Role: AI Product Engineer  
> Purpose: 100-point benchmark resumes for comparing junior developer resumes  
> Note: 아래 Resume은 특정 개인의 이력서를 복제한 것이 아니라, 공개된 합격 Resume 패턴과 최근 AI Product Engineer 채용 요구 역량을 기반으로 재구성한 고품질 비교군 Resume입니다.

---

# 1. Common Resume — AI Product Engineer

## 김도윤 | AI Product Engineer

Email: doyoon.kim.dev@gmail.com  
GitHub: https://github.com/doyoon-ai  
Portfolio: https://doyoon-ai.dev  
Blog: https://blog.doyoon-ai.dev  
LinkedIn: https://linkedin.com/in/doyoon-kim-ai  

---

## Summary

사용자 문제를 AI 기능으로 해결하는 데 집중하는 신입 AI Product Engineer입니다.  
LLM 기반 RAG 서비스, AI 문서 요약, 개인화 추천, 프롬프트 평가 시스템을 직접 설계·구현했으며, 단순 모델 사용을 넘어 **검색 품질, 응답 정확도, 비용, 지연시간, 사용자 경험**을 함께 개선하는 프로젝트를 수행했습니다.

FastAPI, Spring Boot, React, LangChain, OpenAI API, Hugging Face, PostgreSQL, Redis, Docker를 활용해 AI 기능을 실제 웹 서비스 형태로 배포한 경험이 있습니다.  
AI 모델 자체의 성능뿐 아니라 사용자의 행동 데이터, 실패 케이스, 피드백 루프를 기반으로 제품을 개선하는 방식에 관심이 많습니다.

---

## Core Competencies

- LLM Application Development
- Retrieval-Augmented Generation
- Prompt Engineering & Evaluation
- AI Feature Prototyping
- Backend API Development
- Product Metrics Analysis
- Vector Search Optimization
- User Feedback Loop Design
- AI 서비스 비용 및 응답 속도 개선
- Cross-functional Collaboration

---

## Skills

### AI / LLM

- OpenAI API
- Claude API
- Hugging Face Transformers
- LangChain
- LlamaIndex
- Sentence Transformers
- RAG
- Embedding Search
- Prompt Engineering
- Prompt Evaluation
- Few-shot Prompting
- Function Calling
- Tool Calling

### Backend

- Python
- FastAPI
- Java
- Spring Boot
- REST API
- JWT Authentication
- WebSocket
- JPA
- SQLAlchemy

### Frontend

- React
- TypeScript
- JavaScript
- Tailwind CSS
- Zustand
- Axios
- Chart.js

### Database / Infra

- PostgreSQL
- MySQL
- Redis
- FAISS
- Chroma
- Pinecone
- Docker
- GitHub Actions
- AWS EC2
- AWS S3
- Nginx

### Data / Evaluation

- Pandas
- NumPy
- Scikit-learn
- A/B Test Design
- User Event Tracking
- Retrieval Precision
- Answer Relevance
- Hallucination Case Analysis

---

## Experience

### AI Product Engineer Intern

**NeuroDesk Labs**  
2025.07 - 2025.12

B2B 문서 기반 AI 검색·요약 SaaS의 LLM 기능 개발 인턴으로 참여했습니다.

- 사내 문서 기반 Q&A 기능의 RAG 파이프라인을 개선하여 Top-3 검색 정확도를 71%에서 86%로 향상
- 문서 chunk size, overlap, embedding model, reranking 전략을 실험하여 답변 누락 케이스 34% 감소
- OpenAI API 호출 비용을 줄이기 위해 prompt compression 및 캐싱 전략을 적용하여 월 예상 비용 27% 절감
- 사용자 질문 로그를 기반으로 실패 유형을 5개 카테고리로 분류하고, 평가 데이터셋 420개를 구축
- FastAPI 기반 AI 응답 API를 개발하고, 평균 응답 시간을 4.8초에서 2.9초로 개선
- PM, 디자이너, 백엔드 개발자와 협업하여 AI 답변 신뢰도 표시 UI와 출처 문서 하이라이트 기능 구현
- LangChain 기반 prototype 코드를 production API 구조로 리팩터링하여 유지보수성 개선
- AI 답변에 출처 문서 ID, chunk 위치, confidence score를 함께 반환하도록 API 설계

#### Tech Stack

Python, FastAPI, LangChain, OpenAI API, PostgreSQL, Redis, Chroma, Docker, AWS EC2

---

## Projects

---

### Project 1. AskDocu — 문서 기반 AI Q&A SaaS

GitHub: https://github.com/doyoon-ai/askdocu  
Demo: https://askdocu.doyoon-ai.dev  
Period: 2025.03 - 2025.06  
Role: AI Product Engineer / Backend Lead

PDF, Notion export, Markdown 문서를 업로드하면 문서 내용을 기반으로 질문에 답변하는 RAG 기반 AI Q&A 서비스입니다.

#### Problem

기존 문서 검색은 키워드 중심이라 사용자가 정확한 용어를 모르면 원하는 정보를 찾기 어려웠습니다. 또한 LLM 단독 답변은 출처가 불명확해 업무 문서 검색에 사용하기 어려웠습니다.

#### Solution

- 문서를 chunk 단위로 분리하고 embedding vector를 생성하여 semantic search 구현
- 검색된 chunk를 기반으로 답변을 생성하는 RAG pipeline 설계
- 답변마다 출처 문서, 페이지, 문단 위치를 함께 표시
- 질문 유형에 따라 검색 query를 재작성하는 query rewriting prompt 적용
- 동일 질문 반복 시 Redis cache를 활용하여 응답 시간 단축
- 사용자가 답변에 thumbs up/down을 남길 수 있도록 피드백 루프 설계

#### Key Contributions

- PDF parsing, chunking, embedding, vector search, answer generation까지 end-to-end pipeline 구현
- Chunk size 300, 500, 800 tokens 실험 후 retrieval precision 기준 최적값 선정
- FAISS와 Chroma를 비교하여 local 개발 환경에서는 FAISS, 배포 환경에서는 Chroma 사용
- 프롬프트에 "근거 없는 답변 금지" 규칙과 출처 기반 답변 형식을 적용
- 답변 실패 케이스를 hallucination, insufficient context, ambiguous question, parsing error로 분류
- 사용자 질문 1,200개를 기준으로 top-k, temperature, prompt format을 튜닝

#### Impact

- 자체 평가셋 300개 기준 answer relevance 78%에서 88%로 향상
- hallucination 발생률 18%에서 7%로 감소
- 평균 응답 시간 5.2초에서 3.1초로 개선
- 반복 질문 cache hit 적용 후 동일 질문 응답 시간 74% 감소
- 베타 사용자 42명으로부터 평균 만족도 4.4 / 5.0 기록

#### Tech Stack

Python, FastAPI, LangChain, OpenAI API, Chroma, FAISS, PostgreSQL, Redis, React, TypeScript, Docker, AWS EC2

---

### Project 2. MealFit AI — 식단 관리 AI 코치

GitHub: https://github.com/doyoon-ai/mealfit-ai  
Demo: https://mealfit-ai.doyoon-ai.dev  
Period: 2024.11 - 2025.02  
Role: Full-stack / AI Feature Developer

사용자의 목표 체중, 활동량, 식습관, 알레르기 정보를 기반으로 식단을 추천하고 주간 영양 데이터를 분석하는 AI 식단 관리 서비스입니다.

#### Problem

기존 식단 앱은 사용자가 직접 음식을 기록해야 하며, 기록 후에도 어떤 행동을 개선해야 하는지 알기 어려웠습니다.

#### Solution

- 사용자 프로필 기반 권장 칼로리와 탄단지 목표량 계산
- LLM을 활용한 주간 식단 피드백 생성
- 영양 섭취 데이터 기반 부족·초과 영양소 자동 분석
- 사용자의 선호 음식과 제한 음식을 반영한 식단 추천 prompt 설계
- 주간 체중 변화와 섭취량을 시각화하는 dashboard 구현

#### Key Contributions

- Spring Boot 기반 사용자, 식단 기록, 목표 설정 API 개발
- React 기반 주간 영양 분석 dashboard 구현
- LLM 응답이 의학적 진단처럼 보이지 않도록 safety prompt와 disclaimer 적용
- 식단 추천 결과를 JSON schema 기반으로 파싱하여 프론트엔드 렌더링 안정화
- 사용자가 추천 식단을 수정하면 다음 추천에 반영되도록 preference memory 설계
- Chart.js를 활용해 칼로리, 단백질, 탄수화물, 지방 섭취 추이를 시각화

#### Impact

- 테스트 사용자 35명 기준 주간 식단 기록 유지율 52% 달성
- 식단 추천 재생성률을 41%에서 23%로 감소
- 사용자의 목표 영양소 대비 오차를 평균 19%에서 11%로 개선
- 사용자 피드백 기반 prompt 개선 8회 수행

#### Tech Stack

Java, Spring Boot, React, MySQL, OpenAI API, Chart.js, Docker, AWS EC2

---

### Project 3. ReviewSense — 리뷰 기반 제품 인사이트 분석 도구

GitHub: https://github.com/doyoon-ai/reviewsense  
Period: 2024.08 - 2024.10  
Role: Data / AI Engineer

커머스 리뷰 데이터를 수집하여 제품의 장점, 불만, 개선 요청을 자동으로 분류하고 요약하는 AI 분석 도구입니다.

#### Problem

리뷰가 수천 개 이상 쌓이면 제품 담당자가 반복되는 불만이나 개선 요구를 빠르게 파악하기 어렵습니다.

#### Solution

- 리뷰 텍스트 전처리 및 중복 제거 pipeline 구현
- 감성 분석과 topic clustering을 활용해 리뷰 유형 분류
- LLM을 활용해 제품별 핵심 불만과 개선 아이디어 요약
- 관리자 화면에서 리뷰 카테고리별 비중과 대표 문장을 확인할 수 있도록 구현

#### Key Contributions

- KoSentenceBERT 기반 embedding 생성
- KMeans clustering과 silhouette score를 활용해 적정 cluster 수 탐색
- LLM 요약 prompt에 대표 리뷰와 cluster label을 함께 제공하여 요약 품질 개선
- 부정 리뷰를 배송, 품질, 가격, 사용성, 고객지원 카테고리로 자동 분류
- 관리자용 dashboard에서 카테고리별 비율과 트렌드를 시각화

#### Impact

- 8,000개 리뷰 데이터 기준 수동 분류 대비 82% 일치율 달성
- 리뷰 분석 시간 약 3시간에서 15분 이내로 단축
- 제품별 핵심 불만 Top 5 자동 추출 기능 구현
- 비개발자 사용자 5명을 대상으로 usability test 진행 후 UI 개선

#### Tech Stack

Python, Pandas, Scikit-learn, Sentence Transformers, OpenAI API, FastAPI, React, PostgreSQL

---

## Education

### 한국대학교 컴퓨터공학과

2020.03 - 2026.02 예정  
GPA: 4.18 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 데이터베이스
- 컴퓨터네트워크
- 인공지능
- 기계학습
- 소프트웨어공학
- 확률과 통계

---

## Awards / Activities

### 2025 교내 AI 서비스 해커톤 대상

2025.05

- 문서 기반 AI Q&A 서비스 AskDocu로 대상 수상
- RAG 기반 출처 제공 기능과 답변 신뢰도 UI를 구현
- 심사위원 피드백: "AI 기능이 단순 데모가 아니라 실제 업무 문제 해결 흐름을 갖추고 있음"

### Google Developer Student Clubs AI Core Member

2024.09 - 2025.06

- LLM Application Study 운영
- RAG, prompt engineering, vector database 세션 발표
- 팀 프로젝트 코드 리뷰 및 기술 문서 작성 담당

### 오픈소스 기여

2025.01 - 2025.04

- LangChain 기반 예제 repository에 Korean document QA sample PR 기여
- README 한국어 번역 및 Chroma 설정 오류 수정

---

## Certifications

- 정보처리기사 필기 합격
- SQLD
- AWS Certified Cloud Practitioner
- TensorFlow Developer Certificate 준비 중

---

## Publications / Writing

### Blog Articles

- "RAG에서 chunk size가 답변 품질에 미치는 영향"
- "LLM 서비스의 hallucination을 줄이기 위한 5가지 실험"
- "AI Product Engineer에게 필요한 백엔드 설계 감각"
- "Prompt Engineering보다 중요한 Prompt Evaluation"

---

## Strengths

- AI 모델을 단순히 호출하는 데 그치지 않고, 검색 품질·비용·속도·UX까지 함께 개선합니다.
- 제품 문제를 먼저 정의하고, AI가 실제로 그 문제를 해결하는지 지표로 검증합니다.
- 신입 수준에서 구현 가능한 범위를 넘어서, 배포·로그·피드백·평가까지 고려한 AI 기능 개발 경험이 있습니다.
- PM, 디자이너, 백엔드 개발자와 협업하며 AI 기능을 제품 흐름 안에 녹이는 데 강점이 있습니다.

---

# 2. Big Tech / Enterprise Target Resume — AI Product Engineer

## 이서현 | AI Product Engineer

Email: seohyun.lee.ai@gmail.com  
GitHub: https://github.com/seohyun-ai  
Portfolio: https://seohyun-ai.dev  
Blog: https://tech.seohyun-ai.dev  
LinkedIn: https://linkedin.com/in/seohyun-lee-ai  

---

## Summary

신뢰성 높은 AI 기능을 안정적인 서비스 구조로 구현하는 데 강점이 있는 신입 AI Product Engineer입니다.  
RAG 기반 문서 검색, LLM 평가 자동화, 응답 지연시간 최적화, API 비용 절감, 테스트 가능한 AI pipeline 설계 경험이 있습니다.

대기업·빅테크 환경에서 요구되는 **확장성, 안정성, 재현성, 평가 가능성, 장애 대응 가능성**을 중요하게 생각하며, AI 기능을 실험 단계에서 끝내지 않고 production-ready 구조로 만드는 데 집중합니다.

Python, FastAPI, Java, Spring Boot, PostgreSQL, Redis, Docker, GitHub Actions, AWS를 활용해 AI 기능과 백엔드 시스템을 함께 설계했습니다.  
CS 기본기와 소프트웨어 엔지니어링 원칙을 바탕으로 유지보수 가능한 AI Product를 만드는 것을 목표로 합니다.

---

## Core Competencies

- Production-grade LLM Application
- RAG Architecture
- LLM Evaluation Pipeline
- Backend System Design
- API Latency Optimization
- Cost-aware AI Serving
- Observability for AI Features
- Testable Prompt Pipeline
- Data-driven Product Improvement
- Secure API Design

---

## Skills

### Programming

- Python
- Java
- TypeScript
- SQL
- Bash

### AI / Machine Learning

- OpenAI API
- Claude API
- Hugging Face
- LangChain
- LlamaIndex
- Sentence Transformers
- PyTorch
- Scikit-learn
- RAG
- Embedding Search
- Reranking
- Prompt Evaluation
- LLM Guardrails

### Backend / Server

- FastAPI
- Spring Boot
- REST API
- JPA
- SQLAlchemy
- JWT
- OAuth2
- WebSocket
- Batch Processing

### Database / Search

- PostgreSQL
- MySQL
- Redis
- Elasticsearch
- FAISS
- Chroma
- Pinecone

### Infra / DevOps

- Docker
- Docker Compose
- GitHub Actions
- AWS EC2
- AWS S3
- AWS RDS
- Nginx
- Linux

### Testing / Monitoring

- Pytest
- JUnit5
- Postman
- Locust
- Prometheus Basic
- Grafana Basic
- Structured Logging
- Error Tracking

---

## Experience

### AI Software Engineer Intern

**Databridge AI Solutions**  
2025.06 - 2025.12

기업 내부 지식 문서를 활용한 AI Assistant 플랫폼 개발팀에서 LLM 기능과 백엔드 API 개선을 담당했습니다.

#### Key Contributions

- 사내 문서 18,000개를 대상으로 RAG 검색 pipeline을 개선하여 top-5 retrieval hit rate를 76%에서 89%로 향상
- Query rewriting, metadata filtering, hybrid search를 도입하여 부정확한 문서 검색 케이스 31% 감소
- 답변 생성 전 context validation layer를 추가하여 hallucination 리포트 건수 42% 감소
- LLM 응답 API의 p95 latency를 6.4초에서 3.8초로 개선
- Redis cache와 streaming response를 적용하여 사용자 체감 응답 속도 개선
- Prompt template을 versioning하고 evaluation dataset과 연결하여 prompt 변경 시 회귀 테스트 가능하도록 설계
- AI 응답 실패 로그를 structured logging으로 수집하고 failure type dashboard를 구축
- 개인정보 포함 가능성이 있는 문서 chunk를 masking하는 preprocessing module 구현
- PM, 보안 담당자, 백엔드 엔지니어와 협업하여 enterprise 고객 요구사항에 맞춘 출처 기반 답변 기능 구현

#### Impact

- 사내 PoC 고객 3개 팀 대상 AI Assistant 재사용 의향 87% 달성
- LLM API 월 예상 비용 24% 절감
- 운영 중 발생한 LLM timeout 이슈를 분석하여 retry policy와 fallback response 적용
- QA 담당자의 수동 검증 시간을 약 40% 단축

#### Tech Stack

Python, FastAPI, LangChain, OpenAI API, PostgreSQL, Redis, Elasticsearch, Docker, AWS EC2, GitHub Actions

---

## Projects

---

### Project 1. Enterprise Knowledge Assistant

GitHub: https://github.com/seohyun-ai/enterprise-knowledge-assistant  
Demo: https://eka.seohyun-ai.dev  
Period: 2025.02 - 2025.05  
Role: AI Backend Engineer

기업 내부 문서, 정책, 회의록을 기반으로 정확한 답변과 출처를 제공하는 RAG 기반 AI Assistant입니다.

#### Problem

기업 내부 지식은 여러 문서 저장소에 흩어져 있으며, 일반 검색으로는 최신 문서와 정확한 근거를 찾기 어렵습니다.  
또한 LLM 답변은 근거가 없거나 오래된 문서를 참조할 경우 업무에 사용하기 어렵습니다.

#### Solution

- 문서 업로드, parsing, chunking, embedding, indexing pipeline 구현
- 문서 metadata 기반 필터링으로 부서, 문서 타입, 생성일 기준 검색 가능
- BM25와 dense vector search를 결합한 hybrid retrieval 구현
- 검색 결과 reranking을 통해 context 품질 개선
- 답변에 source document, page, paragraph index 제공
- Prompt versioning과 evaluation dataset 기반 regression test 구현

#### Technical Details

- PDF, Markdown, HTML 문서 parser 구현
- Chunk size 512 tokens, overlap 80 tokens 기준으로 기본 pipeline 구성
- Query rewriting prompt를 통해 사용자의 모호한 질문을 검색 친화적 query로 변환
- 검색 결과가 threshold 미만이면 답변을 거부하도록 guardrail 적용
- Prompt template 변경 시 golden dataset 500개에 대해 자동 평가 실행
- FastAPI dependency 구조를 활용해 retriever, generator, evaluator module 분리
- Docker Compose로 API server, PostgreSQL, Redis, vector DB 실행 환경 구성

#### Impact

- Golden QA dataset 기준 exact source match 64%에서 81%로 향상
- Answer relevance score 3.7 / 5.0에서 4.4 / 5.0으로 개선
- RAG pipeline regression test 자동화로 prompt 변경 검증 시간 2시간에서 15분으로 단축
- p95 API latency 5.9초에서 3.6초로 개선
- 동일 질문 cache hit 시 평균 응답 시간 1초 이하 달성

#### Tech Stack

Python, FastAPI, LangChain, Elasticsearch, Chroma, PostgreSQL, Redis, Docker, GitHub Actions, AWS EC2

---

### Project 2. LLM Evaluation Studio

GitHub: https://github.com/seohyun-ai/llm-evaluation-studio  
Period: 2024.11 - 2025.01  
Role: AI Tooling Engineer

LLM prompt, model, retrieval 설정을 비교하고 정량 평가할 수 있는 내부 도구 형태의 프로젝트입니다.

#### Problem

LLM 기반 기능은 prompt를 조금만 수정해도 응답 품질이 달라지지만, 많은 팀이 이를 감각적으로 판단합니다.  
AI 기능을 안정적으로 운영하려면 평가 데이터셋, 기준 지표, 회귀 테스트가 필요합니다.

#### Solution

- Prompt version별 응답 결과를 저장하고 비교하는 evaluation dashboard 구현
- Relevance, groundedness, conciseness, refusal accuracy 기준의 평가 항목 설계
- LLM-as-a-judge와 human review를 함께 사용할 수 있도록 평가 flow 구현
- 모델별 비용, 응답 시간, 점수를 비교하는 report 생성
- Regression test 실패 시 GitHub Actions에서 알림 발생

#### Key Contributions

- 평가 데이터셋 schema 설계
- Prompt version, model name, temperature, top-k, retrieval config를 실험 단위로 저장
- LLM judge prompt를 개선하여 human label과의 agreement를 68%에서 79%로 향상
- 평가 결과를 CSV와 Markdown report로 export하는 기능 구현
- 실패 케이스를 hallucination, missing context, unsafe response, verbose answer로 자동 분류

#### Impact

- Prompt 실험 결과 비교 시간을 70% 단축
- RAG project의 prompt 변경 안정성을 높이는 데 활용
- 개인 프로젝트 3개에 공통 evaluation framework로 재사용
- 평가 기준을 문서화하여 협업자가 동일한 기준으로 AI 응답을 리뷰할 수 있도록 개선

#### Tech Stack

Python, FastAPI, React, TypeScript, PostgreSQL, OpenAI API, Docker, GitHub Actions

---

### Project 3. AI Issue Triage Bot

GitHub: https://github.com/seohyun-ai/ai-issue-triage-bot  
Period: 2024.08 - 2024.10  
Role: Backend / AI Automation Developer

GitHub issue 내용을 분석하여 우선순위, 담당 영역, 예상 원인을 자동 분류하는 AI 기반 issue triage bot입니다.

#### Problem

오픈소스나 개발팀에서는 issue가 쌓일수록 중복 이슈, 버그 리포트, 기능 요청을 빠르게 구분하기 어렵습니다.

#### Solution

- GitHub issue webhook을 수신하는 backend server 구현
- Issue title, body, labels, comments를 기반으로 LLM classification 수행
- 중복 issue 후보를 embedding search로 탐색
- Bot comment로 재현 단계 누락 여부와 필요한 추가 정보를 자동 안내
- Slack webhook으로 high-priority issue 알림 전송

#### Key Contributions

- GitHub App webhook signature verification 구현
- Issue embedding index를 구축하여 유사 issue top-5 추천
- Prompt injection 방지를 위해 issue 본문과 system instruction을 분리
- Classification 결과를 priority, type, component, confidence score로 구조화
- 실패한 분류 결과를 재학습 데이터로 저장하는 review queue 구현

#### Impact

- 테스트 repository 4개에서 issue 600개 기준 triage 정확도 84% 달성
- 중복 issue 탐색 정확도 top-5 기준 78% 달성
- Maintainer가 issue 확인에 소요하는 시간을 약 35% 절감
- Webhook 처리 실패율 1% 미만 유지

#### Tech Stack

Python, FastAPI, GitHub API, OpenAI API, PostgreSQL, FAISS, Docker, Slack Webhook

---

## Education

### 서울기술대학교 컴퓨터공학부

2020.03 - 2026.02 예정  
GPA: 4.26 / 4.5  
Major GPA: 4.35 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 데이터베이스
- 컴퓨터네트워크
- 인공지능
- 기계학습
- 자연어처리
- 소프트웨어공학
- 분산시스템

---

## Awards

### 2025 SW 중심대학 공동 AI 해커톤 최우수상

2025.08

- Enterprise Knowledge Assistant 프로젝트로 최우수상 수상
- 평가 가능한 RAG pipeline과 출처 기반 답변 기능 구현
- 심사 기준 중 기술 완성도와 확장성 항목 최고 점수 획득

### 2024 교내 알고리즘 경진대회 은상

2024.11

- Graph, Dynamic Programming, Greedy 문제 풀이
- 120명 중 7위

---

## Activities

### AI Engineering Study Lead

2025.01 - 2025.06

- 12명 규모의 AI Engineering 스터디 운영
- 주제: RAG, vector search, prompt evaluation, LLM serving, AI safety
- 매주 논문 또는 기술 블로그를 읽고 실습 코드 작성
- 발표 자료와 실습 repository 공개

### Backend Engineering Study

2024.03 - 2024.12

- Spring Boot, JPA, Redis, AWS 배포 학습
- 대규모 트래픽 상황에서 cache, indexing, pagination, transaction 처리 방식 학습
- 개인 프로젝트에 Redis caching과 DB index 최적화 적용

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- 정보처리기사 필기 합격
- TOEIC Speaking IH

---

## Technical Writing

- "RAG 시스템에서 평가 데이터셋을 먼저 만들어야 하는 이유"
- "LLM Prompt를 테스트 가능한 코드로 관리하는 방법"
- "Vector Search와 Keyword Search를 함께 써야 하는 이유"
- "AI Product에서 Latency와 Cost를 함께 보는 법"

---

## Resume Keywords

AI Product Engineer, LLM Engineer, RAG, Retrieval-Augmented Generation, Prompt Engineering, Prompt Evaluation, Vector Database, LangChain, FastAPI, Spring Boot, PostgreSQL, Redis, Elasticsearch, OpenAI API, Claude API, Docker, AWS, GitHub Actions, MLOps, LLM Evaluation, AI Backend, Product Metrics, Cost Optimization, Latency Optimization

---

# 3. Tech Startup Target Resume — AI Product Engineer

## 박민재 | AI Product Engineer

Email: minjae.park.ai@gmail.com  
GitHub: https://github.com/minjae-product-ai  
Portfolio: https://minjae-ai-product.dev  
Blog: https://blog.minjae-ai-product.dev  
LinkedIn: https://linkedin.com/in/minjae-park-ai  

---

## Summary

빠르게 문제를 정의하고 AI 기능을 제품으로 출시하는 데 강점이 있는 신입 AI Product Engineer입니다.  
LLM, RAG, 추천 시스템, AI Agent를 활용해 MVP를 빠르게 만들고, 사용자 행동 데이터와 피드백을 기반으로 기능을 개선한 경험이 있습니다.

단순히 모델을 붙이는 개발자가 아니라, **사용자가 왜 이 기능을 쓰는지, 어떤 지표가 개선되어야 하는지, 어떤 실패 케이스가 제품 신뢰도를 떨어뜨리는지**를 함께 고민합니다.

작은 팀에서 기획, 프론트엔드, 백엔드, AI pipeline, 배포, 사용자 인터뷰까지 주도한 경험이 있으며, 불확실성이 큰 초기 제품 환경에서 빠른 실험과 실행을 즐깁니다.

---

## Core Competencies

- AI MVP Development
- LLM Product Prototyping
- Full-cycle Product Development
- User Problem Discovery
- Rapid Experimentation
- RAG / AI Agent Development
- Product Analytics
- Retention-focused Feature Iteration
- No-code / Low-code Workflow Integration
- Startup-style Ownership

---

## Skills

### AI Product

- LLM Application
- RAG
- AI Agent
- Prompt Engineering
- Prompt A/B Testing
- User Feedback Loop
- AI UX Writing
- Function Calling
- Tool Calling
- Recommendation Logic
- Personalization

### Engineering

- Python
- FastAPI
- JavaScript
- TypeScript
- React
- Next.js
- Node.js
- Spring Boot
- REST API
- WebSocket

### Data / Analytics

- PostgreSQL
- Supabase
- Firebase
- Amplitude
- Google Analytics
- Mixpanel Basic
- Pandas
- Event Tracking
- Funnel Analysis
- Cohort Retention

### Infra / Tools

- Vercel
- Docker
- AWS EC2
- AWS S3
- Railway
- GitHub Actions
- Slack API
- Notion API
- Google Calendar API
- Stripe Test Integration

---

## Experience

### Founding AI Engineer Intern

**Promptly Studio**  
2025.05 - 2025.11

초기 단계 AI productivity startup에서 AI 기능 prototype 개발, 사용자 인터뷰, MVP 출시, 지표 개선을 담당했습니다.

#### Key Contributions

- 회의록 기반 AI task extraction 기능을 3주 만에 MVP로 구현하여 베타 사용자 120명 확보
- OpenAI function calling을 활용해 회의록에서 action item, owner, due date를 구조화
- Notion API, Slack API 연동을 구현하여 AI가 추출한 task를 사용자의 업무 도구로 자동 전송
- 사용자 인터뷰 18건을 진행하여 "AI 결과 수정 비용이 높다"는 문제를 발견하고 inline edit UX 개선
- Prompt A/B test를 통해 task extraction 정확도를 72%에서 88%로 향상
- 무료 사용자 기준 LLM API 비용이 높아지는 문제를 해결하기 위해 summarization cache와 model routing 적용
- GPT-4 계열 모델과 경량 모델을 작업 난이도에 따라 분기하여 요청당 평균 비용 36% 절감
- Mixpanel event tracking을 설계하여 activation, task export, weekly retention 지표 추적
- 베타 기간 중 WAU 120명, task export rate 46%, 4주차 retention 31% 달성

#### Startup Impact

- 기획부터 배포까지 AI 기능 4개를 직접 출시
- PM 없이 사용자 인터뷰, 문제 정의, 기능 우선순위 결정에 참여
- 초기 투자 미팅용 product demo 개발 지원
- 고객사 PoC 요구사항을 반영해 B2B workspace 기능 prototype 구현

#### Tech Stack

Next.js, TypeScript, Python, FastAPI, OpenAI API, Supabase, PostgreSQL, Vercel, Slack API, Notion API, Mixpanel

---

## Projects

---

### Project 1. MeetingPilot — 회의록 기반 AI 업무 자동화 서비스

GitHub: https://github.com/minjae-product-ai/meetingpilot  
Demo: https://meetingpilot.dev  
Period: 2025.01 - 2025.04  
Role: Founder / AI Product Engineer

회의 음성 또는 텍스트 회의록을 업로드하면 AI가 핵심 요약, 의사결정, action item을 추출하고 Notion, Slack, Google Calendar로 연결해주는 AI productivity 서비스입니다.

#### Problem

회의 후 해야 할 일을 사람이 직접 정리하지 않으면 결정사항과 담당자가 누락됩니다.  
특히 작은 팀에서는 회의록 작성, 업무 분배, 일정 등록이 반복적인 운영 비용으로 작용합니다.

#### Solution

- 회의록을 agenda, decision, action item, risk, follow-up question으로 구조화
- LLM function calling을 활용해 JSON schema 기반 task extraction 구현
- Slack, Notion, Google Calendar API와 연동하여 추출된 업무를 자동 전송
- 사용자가 AI가 추출한 task를 수정하면 다음 추출 prompt에 반영되는 feedback loop 설계
- 회의록 길이에 따라 chunk summarize 후 final summary를 생성하는 map-reduce 방식 적용

#### Key Contributions

- Next.js 기반 onboarding, workspace, meeting detail, task export 화면 구현
- FastAPI 기반 AI extraction API와 integration API 개발
- 회의록 길이 초과 문제를 해결하기 위해 hierarchical summarization pipeline 구현
- Prompt A/B test를 통해 action item extraction prompt 6종 비교
- Export 성공률, 수정률, 삭제율을 추적하여 AI 결과 품질을 간접 측정
- 사용자 인터뷰를 통해 "요약보다 할 일 자동 등록이 더 중요하다"는 insight를 발견하고 product direction 수정
- 무료 사용자의 과도한 API 사용을 막기 위해 rate limit과 usage quota 적용

#### Impact

- 베타 사용자 160명 확보
- 회의록 업로드 후 task export 전환율 52% 달성
- 추출된 task의 사용자 수정률 38%에서 21%로 감소
- 평균 회의 정리 시간 20분에서 5분 이하로 단축
- 4주차 retention 29% 달성
- 사용자 인터뷰 24건, product iteration 11회 진행

#### Tech Stack

Next.js, TypeScript, FastAPI, Python, OpenAI API, PostgreSQL, Supabase, Vercel, Slack API, Notion API, Google Calendar API

---

### Project 2. ShopMate AI — 개인화 쇼핑 어시스턴트

GitHub: https://github.com/minjae-product-ai/shopmate-ai  
Demo: https://shopmate-ai.dev  
Period: 2024.09 - 2024.12  
Role: Full-stack AI Product Engineer

사용자의 예산, 취향, 사용 목적을 기반으로 상품 후보를 비교하고 구매 결정을 도와주는 AI 쇼핑 어시스턴트입니다.

#### Problem

사용자는 상품 리뷰와 스펙을 비교하는 데 많은 시간을 쓰지만, 실제로 본인에게 적합한 상품을 판단하기 어렵습니다.

#### Solution

- 사용자의 목적, 예산, 중요 기준을 대화형으로 수집
- 상품 리뷰와 스펙 정보를 embedding search로 검색
- LLM이 장단점, 추천 이유, 비추천 조건을 비교표로 생성
- 사용자가 선택한 상품과 거절한 상품을 기반으로 preference profile 업데이트
- 상품 추천 결과에 "왜 추천했는지"를 설명하는 explainable recommendation 제공

#### Key Contributions

- React 기반 대화형 상품 탐색 UI 구현
- FastAPI 기반 상품 검색 및 추천 API 개발
- 상품 리뷰 12,000건을 수집·전처리하여 embedding index 생성
- 사용자의 preference signal을 price sensitivity, brand preference, feature priority로 구조화
- 추천 결과의 클릭률과 저장률을 event tracking으로 수집
- Prompt에 "사용자 조건과 맞지 않는 상품은 추천하지 않기" 규칙 적용
- 추천 이유와 비추천 이유를 함께 보여주어 사용자 신뢰도 개선

#### Impact

- 테스트 사용자 80명 기준 추천 결과 클릭률 41% 달성
- 상품 비교 페이지 평균 체류 시간 2분 40초 기록
- 추천 결과 저장률 28% 달성
- 사용자 설문 기준 "구매 결정에 도움이 됨" 4.3 / 5.0
- 추천 재생성 요청률 33%에서 19%로 감소

#### Tech Stack

React, TypeScript, Python, FastAPI, OpenAI API, PostgreSQL, FAISS, BeautifulSoup, Pandas, Vercel

---

### Project 3. CareerMate AI — 신입 개발자 Resume 피드백 서비스

GitHub: https://github.com/minjae-product-ai/careermate-ai  
Period: 2024.06 - 2024.08  
Role: AI Product Engineer

신입 개발자의 이력서를 분석하여 직무 적합도, 프로젝트 설명, 성과 수치화, ATS 키워드, 개선 방향을 제안하는 AI Resume Review 서비스입니다.

#### Problem

신입 개발자는 자신의 프로젝트를 어떤 기준으로 이력서에 표현해야 하는지 알기 어렵고, 직무별로 어떤 키워드를 강조해야 하는지도 파악하기 어렵습니다.

#### Solution

- Resume markdown을 입력받아 항목별 completeness score 계산
- 직무별 benchmark resume과 비교하여 누락된 역량 제안
- 프로젝트 bullet point를 impact 중심으로 재작성
- AI가 평가한 항목에 대해 근거 문장을 함께 제공
- 사용자가 수정 전후 Resume을 비교할 수 있도록 diff viewer 구현

#### Key Contributions

- 직무별 평가 rubric 설계: backend, frontend, AI engineer, data engineer
- LLM 기반 resume section parser 구현
- 프로젝트 설명을 Problem, Action, Result 구조로 변환하는 rewrite prompt 설계
- ATS keyword coverage와 quantification ratio를 계산하는 scoring logic 구현
- 사용자의 민감 정보를 masking한 뒤 LLM API로 전송하는 preprocessing layer 구현
- 개선 전후 점수 변화를 시각화하는 dashboard 구현

#### Impact

- 테스트 사용자 55명 기준 평균 Resume completeness score 62점에서 84점으로 향상
- 프로젝트 bullet point 정량화 비율 28%에서 73%로 개선
- 사용자 만족도 4.5 / 5.0
- 1인 프로젝트로 기획, 개발, 배포, 피드백 수집까지 완료

#### Tech Stack

Next.js, TypeScript, FastAPI, Python, OpenAI API, PostgreSQL, Tailwind CSS, Vercel

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 예정  
GPA: 4.05 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 웹프로그래밍
- 인공지능
- 기계학습
- 인간컴퓨터상호작용
- 소프트웨어공학
- 창업과 소프트웨어 제품 개발

---

## Awards / Activities

### 2025 초기창업 AI 서비스 해커톤 대상

2025.06

- MeetingPilot 프로젝트로 대상 수상
- 회의록에서 업무를 추출하고 Slack, Notion으로 자동 전송하는 AI workflow 구현
- "즉시 사용할 수 있는 제품 완성도와 사용자 문제 정의가 뛰어남"이라는 평가를 받음

### 2024 대학 연합 사이드프로젝트 경진대회 최우수상

2024.12

- ShopMate AI 프로젝트로 최우수상 수상
- 사용자 취향 기반 상품 비교와 추천 이유 설명 기능 구현
- 4주간 사용자 테스트를 진행하고 지표 기반 개선 결과 발표

### Startup Product Study Organizer

2024.09 - 2025.05

- 15명 규모의 AI Product Study 운영
- 매주 AI 제품 1개를 선정해 onboarding, activation, retention 관점에서 분석
- RAG product, AI writing tool, AI meeting assistant, AI coding assistant 사례 발표

---

## Certifications

- SQLD
- Google Analytics Certification
- AWS Cloud Practitioner 준비 중
- 정보처리기사 필기 준비 중

---

## Product Metrics Experience

- Activation Rate
- Weekly Active Users
- 4-week Retention
- Export Conversion Rate
- Prompt A/B Test
- Click-through Rate
- Save Rate
- User Feedback Score
- API Cost per User
- Average Response Latency
- Task Completion Time

---

## Technical Writing

- "AI Product Engineer는 모델보다 문제 정의가 먼저다"
- "LLM 기능의 품질을 사용자 행동 데이터로 평가하는 방법"
- "회의록 AI 서비스에서 요약보다 중요한 것은 Action Item이다"
- "Prompt A/B Test를 제품 개발에 적용한 경험"
- "AI 기능의 비용을 줄이기 위한 Model Routing 전략"

---

## Strengths

- 빠르게 MVP를 만들고 실제 사용자에게 검증합니다.
- AI 기능을 제품 지표와 연결하여 개선합니다.
- 기획, 프론트엔드, 백엔드, AI pipeline, 배포까지 혼자서도 end-to-end로 수행할 수 있습니다.
- 사용자의 피드백을 prompt, UX, API, 데이터 구조 개선으로 연결합니다.
- 스타트업 환경에서 중요한 속도, 오너십, 실험, 학습 능력을 갖추고 있습니다.

---

## Resume Keywords

AI Product Engineer, AI Engineer, LLM Product, AI MVP, RAG, Prompt Engineering, Function Calling, Tool Calling, AI Agent, Product Analytics, User Feedback Loop, Next.js, React, TypeScript, FastAPI, Python, OpenAI API, Supabase, PostgreSQL, Slack API, Notion API, Google Calendar API, Product Metrics, Retention, Activation, AI UX, Startup Engineer