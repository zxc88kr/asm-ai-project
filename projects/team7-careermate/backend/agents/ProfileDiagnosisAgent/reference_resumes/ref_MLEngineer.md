# ML Engineer Resume Set

> Target: Korea / Entry-level Developer / Max Internship Experience  
> Role: Machine Learning Engineer  
> Purpose: 100-point benchmark resumes for comparing junior developer resumes  
> Reference Basis: ML Engineer Resume 예시와 MLOps 연구·채용 흐름에서 반복적으로 요구되는 Python, PyTorch, TensorFlow, SQL, Feature Engineering, Model Training, Evaluation, Model Serving, Docker, Kubernetes, MLflow, Weights & Biases, Airflow, Spark, Cloud, Monitoring 역량을 기준으로 구성함.  
> Note: 아래 Resume은 특정 개인의 이력서를 복제한 것이 아니라, 실제 채용 시장에서 강하게 평가되는 ML Engineer 역량 패턴을 기반으로 재구성한 고품질 비교군 Resume입니다.

---

# 1. Common Resume — ML Engineer

## 김도윤 | Machine Learning Engineer

Email: doyoon.kim.ml@gmail.com  
GitHub: https://github.com/doyoon-ml  
Portfolio: https://doyoon-ml.dev  
Blog: https://blog.doyoon-ml.dev  
LinkedIn: https://linkedin.com/in/doyoon-kim-ml  

---

## Summary

모델을 학습하는 데서 끝나지 않고, 실제 서비스에서 사용할 수 있는 형태로 배포·평가·개선하는 데 집중하는 신입 Machine Learning Engineer입니다.

Python, PyTorch, TensorFlow, Scikit-learn, FastAPI, Docker, MLflow, Weights & Biases, Airflow, PostgreSQL, AWS를 활용해 추천 시스템, 이미지 분류, NLP 분류, 예측 모델을 직접 개발했습니다. 단순 notebook 실험이 아니라 **데이터 전처리, 피처 엔지니어링, 모델 학습, 실험 추적, 평가 지표 설계, API 서빙, 배치 추론, 모니터링**까지 고려한 ML 프로젝트 경험이 있습니다.

팀 프로젝트에서는 제품 요구사항에 맞는 모델 지표를 정의하고, 성능뿐 아니라 추론 속도, 비용, 재학습 가능성, 데이터 품질을 함께 고려했습니다.

---

## Core Competencies

- Supervised Learning / Deep Learning 모델 개발
- PyTorch / TensorFlow 기반 모델 학습
- Feature Engineering 및 데이터 전처리
- MLflow / W&B 기반 실험 관리
- 모델 평가 지표 설계 및 오류 분석
- FastAPI 기반 모델 서빙 API 구현
- Docker 기반 모델 배포 환경 구성
- Airflow 기반 Batch Inference Pipeline 구축
- 모델 추론 속도 및 메모리 최적화
- 데이터 품질 검증 및 Drift 기초 모니터링
- Product Metric과 ML Metric 연결
- 백엔드·데이터·프론트엔드 팀과 협업

---

## Skills

### Language

- Python
- SQL
- Java Basic
- Bash
- JavaScript Basic

### Machine Learning

- PyTorch
- TensorFlow
- Scikit-learn
- XGBoost
- LightGBM
- CatBoost Basic
- Hugging Face Transformers
- OpenCV
- Pandas
- NumPy
- SciPy

### ML Engineering

- MLflow
- Weights & Biases
- DVC Basic
- FastAPI
- BentoML Basic
- ONNX Basic
- Docker
- Airflow
- Batch Inference
- Online Inference
- Model Registry
- Experiment Tracking
- Feature Store Concept

### Data / Database

- PostgreSQL
- MySQL
- BigQuery Basic
- Redis Basic
- S3
- Data Validation
- Train / Validation / Test Split
- Cross Validation
- Imbalanced Data Handling

### Cloud / Infra

- AWS EC2
- AWS S3
- AWS RDS
- AWS Lambda Basic
- GitHub Actions
- Linux
- Nginx Basic

### Evaluation / Monitoring

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- RMSE
- MAE
- NDCG
- MAP@K
- Confusion Matrix
- Error Analysis
- Data Drift Basic
- Model Performance Monitoring Basic

---

## Experience

### Machine Learning Engineer Intern

**FitLogics AI Lab**  
2025.07 - 2025.12

사용자 건강 데이터 기반 식단·운동 기록 서비스를 운영하는 스타트업에서 추천 모델과 예측 모델 개발을 담당했습니다.

### Key Contributions

- 사용자 식단 기록, 체중 변화, 활동량 데이터를 기반으로 개인화 식단 추천 모델 prototype 개발
- LightGBM 기반 체중 변화 예측 모델을 개발하여 baseline 대비 MAE 18% 개선
- 사용자별 음식 선호도를 반영하기 위해 implicit feedback 기반 ranking feature 생성
- 음식 추천 후보 생성 후 reranking하는 2-stage recommendation pipeline 설계
- MLflow를 도입하여 dataset version, hyperparameter, metric, artifact를 실험별로 관리
- FastAPI 기반 추천 API를 구현하고 평균 응답 시간을 420ms 이하로 유지
- Airflow 기반 일별 batch feature generation pipeline 작성
- 모델 입력 데이터의 null ratio, outlier, distribution shift를 점검하는 data validation script 작성
- 추천 결과 클릭률과 저장률을 분석하여 offline metric과 product metric 간 차이를 검토
- 백엔드 개발자와 협업해 추천 API 응답 schema와 fallback logic 설계

### Impact

- 체중 변화 예측 MAE baseline 대비 18% 개선
- 추천 후보 Top-10 offline NDCG@10 0.41에서 0.58로 개선
- 추천 API 평균 응답 시간 420ms 이하 유지
- 추천 결과 저장률 17%에서 26%로 개선
- ML 실험 63개를 MLflow로 관리
- 일별 feature generation 수동 작업을 Airflow DAG로 자동화

### Tech Stack

Python, PyTorch, LightGBM, Scikit-learn, Pandas, FastAPI, MLflow, Airflow, PostgreSQL, Docker, AWS EC2, AWS S3

---

## Projects

---

### Project 1. MealRec — 개인화 식단 추천 시스템

GitHub: https://github.com/doyoon-ml/mealrec  
Demo: https://mealrec.doyoon-ml.dev  
Period: 2025.03 - 2025.06  
Role: ML Engineer

사용자의 목표 칼로리, 영양소 목표, 식습관, 음식 선호도를 기반으로 개인화 식단을 추천하는 ML 기반 추천 시스템입니다.

### Problem

기존 식단 추천은 사용자의 목표와 선호도를 충분히 반영하지 못해 추천 결과를 다시 수정하거나 재검색하는 비율이 높았습니다. 또한 단순 인기 음식 추천은 개인의 알레르기, 목표 영양소, 선호 음식과 맞지 않는 문제가 있었습니다.

### Solution

- 사용자 프로필, 식단 기록, 음식 검색 로그, 저장 기록을 기반으로 추천 feature 생성
- Rule-based candidate generation과 ML-based reranking을 결합한 추천 구조 설계
- 영양소 제약 조건을 만족하지 못하는 후보는 filtering
- LightGBM Ranker를 활용해 사용자별 음식 후보를 재정렬
- 추천 결과에 "추천 이유"를 제공하기 위한 feature importance 기반 explanation 생성
- Offline metric과 사용자 행동 metric을 함께 추적

### Key Contributions

- food_dim, user_food_interaction, user_nutrition_goal 데이터셋 설계
- 사용자-음식 interaction matrix 생성
- 최근 7일 섭취 패턴, 선호 카테고리, 목표 대비 부족 영양소 feature 생성
- popularity baseline, content-based filtering, LightGBM Ranker 성능 비교
- NDCG@10, MAP@10, coverage, diversity 지표로 추천 품질 평가
- MLflow로 feature set, model parameter, metric, artifact 관리
- FastAPI 기반 추천 inference API 구현
- Redis cache로 동일 사용자 추천 결과 TTL 관리
- 추천 실패 시 rule-based fallback 적용
- Docker 기반 학습·서빙 환경 구성

### Impact

- NDCG@10 0.38에서 0.61로 개선
- MAP@10 0.21에서 0.39로 개선
- 추천 결과 재생성률 34%에서 19%로 감소
- 추천 저장률 15%에서 28%로 개선
- 평균 inference latency 350ms 이하 유지
- 테스트 사용자 50명 기준 추천 만족도 4.3 / 5.0 기록

### Tech Stack

Python, LightGBM, Scikit-learn, Pandas, NumPy, FastAPI, Redis, PostgreSQL, MLflow, Docker, AWS EC2

---

### Project 2. ReviewClassifier — 커머스 리뷰 감성·이슈 분류 모델

GitHub: https://github.com/doyoon-ml/reviewclassifier  
Period: 2024.11 - 2025.02  
Role: ML Engineer

커머스 리뷰를 긍정·부정·중립 감성으로 분류하고, 배송·품질·가격·사용성·고객지원 이슈 카테고리로 자동 분류하는 NLP 모델 프로젝트입니다.

### Problem

제품 리뷰가 많아질수록 운영자와 제품 담당자가 반복되는 불만을 빠르게 파악하기 어렵습니다. 단순 키워드 기반 분류는 표현이 다양하거나 문맥이 필요한 리뷰를 제대로 분류하지 못했습니다.

### Solution

- 리뷰 텍스트 전처리 및 라벨링 데이터셋 구축
- TF-IDF + Logistic Regression baseline 구축
- KoBERT fine-tuning 기반 감성 분류 모델 개발
- Multi-label issue classification 모델 구현
- Error analysis를 통해 라벨 불균형과 짧은 리뷰 문제 개선
- Batch inference pipeline으로 일별 리뷰 분류 자동화

### Key Contributions

- 리뷰 8만 건 수집 및 중복 제거
- 6,000건 수동 라벨링 데이터셋 구축
- 형태소 분석, 특수문자 제거, emoji normalization 적용
- Class imbalance 문제를 class weight와 oversampling으로 완화
- KoBERT fine-tuning 실험 24회 수행
- Confusion matrix 기반 오류 유형 분석
- 부정 리뷰 중 배송/품질/가격/사용성/고객지원 카테고리 분류
- FastAPI 기반 단건 리뷰 분류 API와 batch inference script 구현
- W&B로 loss, F1-score, confusion matrix 추적

### Impact

- 감성 분류 Macro F1 0.71에서 0.86으로 개선
- 이슈 카테고리 분류 Micro F1 0.79 달성
- 수동 리뷰 분류 작업 시간 약 80% 단축
- 일별 리뷰 5만 건 batch inference 처리 가능
- 제품별 부정 이슈 Top-5 자동 추출 기능 제공

### Tech Stack

Python, PyTorch, Hugging Face Transformers, KoBERT, Scikit-learn, Pandas, FastAPI, W&B, Docker

---

### Project 3. DefectVision — 제조 결함 이미지 분류 모델

GitHub: https://github.com/doyoon-ml/defectvision  
Period: 2024.08 - 2024.10  
Role: Computer Vision / ML Engineer

제조 공정 이미지에서 정상·스크래치·오염·균열 결함을 분류하는 Computer Vision 모델 프로젝트입니다.

### Problem

제조 결함 이미지는 클래스 불균형이 심하고, 결함 영역이 작아 단순 CNN 모델로는 특정 결함을 놓치는 문제가 있었습니다.

### Solution

- 이미지 전처리와 augmentation pipeline 구성
- ResNet, EfficientNet, MobileNet 모델 비교
- Class imbalance를 해결하기 위해 weighted loss와 oversampling 적용
- Grad-CAM으로 모델이 결함 영역을 참고하는지 시각화
- ONNX 변환을 통해 추론 속도 개선
- FastAPI 기반 이미지 분류 API 구현

### Key Contributions

- 이미지 12,000장 데이터셋 정리
- train/validation/test split을 제품 batch 기준으로 분리하여 data leakage 방지
- Albumentations 기반 augmentation 적용
- EfficientNet-B0 fine-tuning으로 성능 개선
- Precision, Recall, F1-score를 클래스별로 분석
- 불량 미탐을 줄이기 위해 recall 중심 threshold 조정
- Grad-CAM 기반 오류 분석 리포트 작성
- PyTorch 모델을 ONNX로 변환하고 추론 latency 비교
- Docker 기반 inference server 구성

### Impact

- Macro F1 0.74에서 0.89로 개선
- 결함 클래스 평균 Recall 0.68에서 0.87로 개선
- ONNX 변환 후 평균 추론 시간 120ms에서 58ms로 개선
- 결함 미탐률 22%에서 8%로 감소
- 모델 오류 분석 리포트 18건 작성

### Tech Stack

Python, PyTorch, EfficientNet, OpenCV, Albumentations, ONNX, FastAPI, Docker, W&B

---

## Education

### 한국대학교 컴퓨터공학과

2020.03 - 2026.02 예정  
GPA: 4.18 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 운영체제
- 인공지능
- 기계학습
- 딥러닝
- 컴퓨터비전
- 자연어처리
- 확률과 통계
- 선형대수

---

## Awards / Activities

### 2025 교내 AI 모델링 경진대회 대상

2025.05

- MealRec 프로젝트로 대상 수상
- 추천 품질, 영양 제약 조건, 제품 지표 개선 가능성을 함께 제시
- Offline metric과 사용자 피드백을 함께 활용한 점에서 높은 평가를 받음

### AI / ML Engineering Study Lead

2024.09 - 2025.06

- 10명 규모의 ML Engineering 스터디 운영
- 주제: PyTorch, 추천 시스템, NLP, Computer Vision, MLflow, 모델 서빙, MLOps
- 매주 논문 구현, 모델 실험 리포트, 코드 리뷰 진행

### Open Source Contribution

2025.01 - 2025.04

- PyTorch 예제 repository README 개선
- Hugging Face Korean NLP 예제 문서 오타 수정
- MLflow sample project 실행 오류 수정 PR 기여

---

## Certifications

- SQLD
- 정보처리기사 필기 합격
- AWS Certified Cloud Practitioner 준비 중
- TensorFlow Developer Certificate 준비 중

---

## Technical Writing

- "추천 시스템에서 Offline Metric과 Product Metric이 달랐던 이유"
- "MLflow로 실험을 관리하면서 바뀐 개발 방식"
- "KoBERT 감성 분류 모델을 Fine-tuning한 과정"
- "Class Imbalance 문제를 해결하기 위해 시도한 방법들"
- "ONNX 변환으로 이미지 분류 추론 속도를 개선한 경험"

---

## Strengths

- 모델 성능뿐 아니라 실제 서비스 적용 가능성, 추론 속도, 데이터 품질, 재학습 가능성을 함께 고려합니다.
- 실험을 재현 가능하게 관리하고, 결과를 지표와 오류 분석으로 설명합니다.
- 추천, NLP, Computer Vision 프로젝트를 모두 수행하며 다양한 ML 문제 유형을 경험했습니다.
- 백엔드 개발자와 협업해 모델을 API 형태로 서빙할 수 있습니다.
- 신입 수준에서 요구되는 모델링 역량을 넘어 MLOps와 제품 적용 경험을 갖추고 있습니다.

---

## Resume Keywords

Machine Learning Engineer, ML Engineer, Python, PyTorch, TensorFlow, Scikit-learn, XGBoost, LightGBM, Hugging Face, Transformers, Computer Vision, NLP, Recommendation System, Feature Engineering, Model Training, Model Evaluation, MLflow, Weights & Biases, FastAPI, Docker, Airflow, Batch Inference, Online Inference, Model Serving, Model Monitoring, Data Drift, ONNX, AWS

---

# 2. Big Tech / Enterprise Target Resume — ML Engineer

## 이서현 | Machine Learning Engineer

Email: seohyun.lee.ml@gmail.com  
GitHub: https://github.com/seohyun-ml  
Portfolio: https://seohyun-ml.dev  
Blog: https://tech.seohyun-ml.dev  
LinkedIn: https://linkedin.com/in/seohyun-lee-ml  

---

## Summary

대규모 서비스 환경에서 재현 가능하고 안정적인 ML 시스템을 구축하는 데 관심이 있는 신입 Machine Learning Engineer입니다.

Python, PyTorch, TensorFlow, Scikit-learn, Spark, Airflow, MLflow, W&B, Docker, Kubernetes, AWS를 활용해 추천, NLP, Computer Vision, 예측 모델을 학습·평가·배포했습니다. 특히 대기업·중견기업·빅테크 환경에서 중요하게 평가되는 **실험 재현성, 데이터 버저닝, 모델 레지스트리, 모델 서빙 안정성, 배치 추론, 성능 모니터링, 데이터 드리프트 대응, 비용·지연시간 최적화**를 중요하게 생각합니다.

모델 개발과 소프트웨어 엔지니어링을 연결해, 데이터 사이언스 결과물이 실제 제품에서 안정적으로 동작할 수 있도록 만드는 것을 목표로 합니다.

---

## Core Competencies

- Production-ready ML Pipeline 설계
- PyTorch / TensorFlow 기반 Deep Learning 모델 개발
- MLflow / W&B 기반 실험 추적 및 모델 관리
- Spark / Airflow 기반 대용량 학습 데이터 처리
- Feature Engineering Pipeline 구축
- Model Registry 및 배포 버전 관리
- FastAPI / Docker / Kubernetes 기반 모델 서빙
- Batch Inference / Online Inference 구조 설계
- 모델 성능·데이터 품질 모니터링
- Drift Detection 및 재학습 Trigger 설계
- 모델 최적화: Quantization, ONNX 변환
- ML 시스템 테스트 및 CI/CD 기초

---

## Skills

### Language

- Python
- SQL
- Java Basic
- C++ Basic
- Bash

### ML / Deep Learning

- PyTorch
- TensorFlow
- Scikit-learn
- XGBoost
- LightGBM
- Hugging Face Transformers
- OpenCV
- TorchVision
- TorchServe Basic
- ONNX
- Optuna
- Pandas
- NumPy

### MLOps / ML Platform

- MLflow
- Weights & Biases
- DVC
- Airflow
- Kubeflow Basic
- BentoML Basic
- FastAPI
- Docker
- Kubernetes Basic
- GitHub Actions
- Model Registry
- Feature Store Concept
- Data Versioning
- Model Versioning

### Data / Big Data

- PostgreSQL
- MySQL
- BigQuery Basic
- Spark
- PySpark
- Kafka Basic
- AWS S3
- Parquet
- Data Validation
- Data Quality Check

### Cloud / Infra

- AWS EC2
- AWS S3
- AWS RDS
- AWS ECR Basic
- AWS SageMaker Basic
- Kubernetes Basic
- Nginx
- Linux

### Evaluation / Monitoring

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- NDCG
- MAP@K
- RMSE
- MAE
- Latency
- Throughput
- Drift Detection
- Shadow Deployment Concept
- A/B Test Concept

---

## Experience

### Machine Learning Engineer Intern

**CommerceCore AI Platform Team**  
2025.06 - 2025.12

이커머스 플랫폼의 추천·검색·리뷰 분석 모델을 개발하는 AI Platform 팀에서 ML pipeline과 모델 서빙 개선을 담당했습니다.

### Key Contributions

- 사용자 클릭·구매 로그 기반 추천 모델 학습 데이터셋을 PySpark로 생성
- 상품 추천 LightGBM Ranker 모델을 개선하여 NDCG@10 0.49에서 0.63으로 향상
- MLflow Model Registry를 도입하여 staging, production 모델 버전 관리 구조 구성
- Airflow 기반 daily feature generation과 batch inference DAG 작성
- 추천 모델 batch inference 처리 시간을 72분에서 29분으로 단축
- FastAPI 기반 online inference endpoint를 구현하고 p95 latency 180ms 이하 유지
- 모델 입력 feature의 null ratio, distribution drift, category cardinality 변화를 모니터링
- 추천 모델의 offline metric과 실제 클릭률 간 차이를 분석하고 segment별 성능 리포트 작성
- W&B를 활용해 hyperparameter, metric, artifact, confusion matrix를 추적
- Docker 기반 학습·서빙 환경을 분리하고 GitHub Actions로 테스트 자동화

### Impact

- 추천 NDCG@10 29% 개선
- Batch inference 처리 시간 60% 개선
- Online inference p95 latency 180ms 이하 유지
- 추천 클릭률 11% 상대 개선
- 모델 버전 추적 누락 문제 해결
- 데이터 품질 검증 rule 48개 작성
- Segment별 모델 성능 리포트 자동화

### Tech Stack

Python, PySpark, LightGBM, PyTorch, MLflow, W&B, Airflow, FastAPI, Docker, PostgreSQL, AWS S3, AWS EC2

---

## Projects

---

### Project 1. RecSys Platform — 추천 모델 학습·서빙 파이프라인

GitHub: https://github.com/seohyun-ml/recsys-platform  
Demo: https://recsys-platform.dev  
Period: 2025.02 - 2025.05  
Role: ML Engineer

이커머스 클릭·구매 로그를 기반으로 추천 모델을 학습하고, batch inference와 online inference를 모두 제공하는 ML pipeline 프로젝트입니다.

### Problem

추천 모델은 단순히 offline metric이 높아도 실제 사용자 클릭률이 개선되지 않을 수 있습니다. 또한 실험 결과가 notebook에 흩어져 있으면 모델 버전, 데이터셋, feature set을 추적하기 어렵습니다.

### Solution

- Raw log, feature table, training dataset, inference output 계층 설계
- Candidate generation과 ranking model을 분리
- MLflow 기반 실험 추적과 모델 레지스트리 구성
- Airflow 기반 daily training / batch inference pipeline 구축
- FastAPI 기반 online inference API 구현
- Segment별 성능 분석과 drift monitoring 적용
- Docker 기반 학습·서빙 환경 구성

### Technical Details

- user_id, item_id, event_type, event_time 기반 interaction log 전처리
- 최근 7일·30일 클릭 수, 구매 수, category preference, price preference feature 생성
- Popularity, Matrix Factorization, LightGBM Ranker 모델 비교
- NDCG@10, MAP@10, Recall@50, Coverage, Diversity 지표로 평가
- MLflow에 dataset hash, feature version, hyperparameter, metric 저장
- Redis cache로 online inference 결과 caching
- Batch inference output을 PostgreSQL recommendation table에 적재
- Feature null ratio와 value distribution을 매일 점검
- 모델 성능이 threshold 이하로 떨어지면 Slack alert 발송
- Canary deployment 개념을 적용해 일부 사용자 segment에만 신규 모델 적용하는 구조 설계

### Impact

- NDCG@10 0.44에서 0.66으로 개선
- MAP@10 0.27에서 0.43으로 개선
- 추천 클릭률 9.8% 상대 개선
- Daily batch inference 시간 85분에서 31분으로 단축
- Online inference p95 latency 160ms 이하 유지
- ML 실험 91개와 모델 버전 12개 관리
- 모델 성능 저하 탐지 시간을 1일에서 30분 이내로 단축

### Tech Stack

Python, PySpark, LightGBM, Scikit-learn, MLflow, Airflow, FastAPI, Redis, PostgreSQL, Docker, AWS S3, GitHub Actions

---

### Project 2. Review Intelligence — 리뷰 NLP 분류·요약 모델

GitHub: https://github.com/seohyun-ml/review-intelligence  
Period: 2024.11 - 2025.01  
Role: NLP / ML Engineer

커머스 리뷰 데이터를 감성, 이슈 유형, 긴급도 기준으로 분류하고 운영자에게 요약 결과를 제공하는 NLP 모델 프로젝트입니다.

### Problem

리뷰 데이터는 비정형 텍스트이고, 부정 리뷰가 급증하거나 특정 이슈가 반복될 경우 빠르게 탐지해야 합니다. 단순 키워드 기반 rule은 문맥을 이해하지 못하고, 운영자가 직접 확인하기에는 시간이 많이 걸립니다.

### Solution

- KoBERT fine-tuning 기반 감성 분류 모델 개발
- Multi-label classification으로 배송, 품질, 가격, 사용성, 고객지원 이슈 분류
- Class imbalance 완화를 위한 focal loss 실험
- Error analysis 기반 라벨 정의 개선
- Batch inference pipeline과 운영자 dashboard용 output table 제공
- 모델 추론 결과 confidence score와 대표 리뷰를 함께 제공

### Key Contributions

- 리뷰 12만 건 수집 및 전처리
- 8,000건 수동 라벨링 데이터셋 구축
- TF-IDF baseline, KoBERT, KLUE-RoBERTa 모델 비교
- W&B로 실험 결과와 confusion matrix 관리
- Label noise를 줄이기 위해 disagree sample 재검토 프로세스 구성
- Threshold tuning으로 부정 리뷰 recall 개선
- Batch inference 결과를 product_issue_daily_mart에 적재
- FastAPI 기반 단건 리뷰 분류 API 구현
- 모델 오류를 short text, sarcasm, mixed sentiment, ambiguous label로 분류

### Impact

- 감성 분류 Macro F1 0.73에서 0.88로 개선
- 부정 리뷰 Recall 0.69에서 0.90으로 개선
- 이슈 유형 Multi-label Micro F1 0.82 달성
- 운영자 리뷰 확인 시간을 약 75% 단축
- 일별 부정 이슈 급증 탐지 rule 제공
- 모델 오류 분석 리포트 24건 작성

### Tech Stack

Python, PyTorch, Hugging Face Transformers, KoBERT, KLUE-RoBERTa, W&B, FastAPI, PostgreSQL, Docker

---

### Project 3. VisionServe — 이미지 분류 모델 서빙 시스템

GitHub: https://github.com/seohyun-ml/visionserve  
Period: 2024.08 - 2024.10  
Role: Computer Vision / ML Platform Engineer

이미지 분류 모델을 학습하고 ONNX 변환, Docker 배포, API 서빙, 추론 성능 모니터링까지 구성한 ML serving 프로젝트입니다.

### Problem

Computer Vision 모델은 notebook에서 높은 성능을 보여도 실제 서비스 API로 배포하면 latency, memory usage, batch size, model loading time 문제가 발생할 수 있습니다.

### Solution

- EfficientNet 기반 이미지 분류 모델 fine-tuning
- PyTorch 모델을 ONNX로 변환하여 inference 최적화
- FastAPI 기반 inference server 구현
- Docker image로 모델 서버 패키징
- Prometheus style metric endpoint로 latency, error count, request count 수집
- 모델 입력 이미지 validation과 예외 처리 구현

### Key Contributions

- 이미지 20,000장 데이터셋 전처리
- Albumentations 기반 augmentation 적용
- Train/validation/test split을 source batch 기준으로 분리하여 leakage 방지
- EfficientNet-B0, ResNet50, MobileNetV3 성능·속도 비교
- ONNX Runtime을 적용해 inference latency 개선
- FastAPI UploadFile 기반 이미지 inference endpoint 구현
- 모델 warm-up 로직으로 첫 요청 latency 감소
- Docker image size를 줄이기 위해 slim base image 적용
- Locust로 동시 요청 부하 테스트 수행
- 잘못된 이미지 포맷, 과대 파일, timeout 예외 처리

### Impact

- Macro F1 0.76에서 0.91로 개선
- 평균 추론 latency 145ms에서 62ms로 개선
- 첫 요청 latency 1.8초에서 310ms로 개선
- Docker image size 2.1GB에서 780MB로 감소
- 동시 요청 100개 기준 error rate 1% 이하 유지
- 모델 서빙 관련 운영 지표 8개 수집

### Tech Stack

Python, PyTorch, EfficientNet, OpenCV, ONNX Runtime, FastAPI, Docker, Locust, Prometheus Basic

---

## Education

### 서울기술대학교 컴퓨터공학부

2020.03 - 2026.02 예정  
GPA: 4.28 / 4.5  
Major GPA: 4.37 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 운영체제
- 데이터베이스
- 컴퓨터네트워크
- 인공지능
- 기계학습
- 딥러닝
- 자연어처리
- 컴퓨터비전
- 확률과 통계
- 선형대수

---

## Awards

### 2025 SW 중심대학 공동 AI 경진대회 최우수상

2025.08

- RecSys Platform 프로젝트로 최우수상 수상
- 추천 모델 학습, 실험 관리, 배치 추론, 온라인 서빙, 모니터링을 end-to-end로 구현
- 모델 성능뿐 아니라 운영 가능성과 재현성을 제시한 점에서 높은 평가를 받음

### 2024 교내 ML 모델링 경진대회 은상

2024.11

- 리뷰 감성 분류 모델로 은상 수상
- 라벨 불균형과 오류 분석 개선 과정을 발표
- Macro F1과 Recall 개선 결과를 수치로 제시

---

## Activities

### MLOps Study Lead

2025.01 - 2025.06

- 12명 규모의 MLOps 스터디 운영
- 주제: MLflow, W&B, DVC, Airflow, Docker, FastAPI, 모델 모니터링, 데이터 드리프트
- 매주 논문 또는 기술 블로그를 읽고 실습 코드 작성
- 모델 학습부터 API 서빙까지 end-to-end 미니 프로젝트 진행

### CS / ML Paper Study

2024.07 - 2024.12

- 운영체제, 네트워크, 데이터베이스, 머신러닝 논문 스터디 참여
- 추천 시스템, Transformer, CNN, 모델 압축, 분산 학습 기초 발표

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner
- 정보처리기사 필기 합격
- TensorFlow Developer Certificate 준비 중

---

## Technical Writing

- "추천 모델을 MLflow Model Registry로 관리한 경험"
- "Offline NDCG와 실제 클릭률이 다르게 나온 이유"
- "ONNX Runtime으로 이미지 분류 모델 추론 속도를 개선한 과정"
- "Airflow로 Batch Inference Pipeline을 구성하는 방법"
- "Model Drift를 처음 모니터링할 때 봐야 할 지표"

---

## Strengths

- 모델 학습과 서빙, 모니터링, 재학습 가능성까지 end-to-end로 고려합니다.
- 실험 결과를 재현 가능하게 관리하고, 모델 버전과 데이터셋 버전을 추적합니다.
- 대용량 데이터 처리와 ML 모델링을 연결해 실제 서비스용 feature pipeline을 만들 수 있습니다.
- ML metric과 product metric을 함께 분석하여 모델 개선 방향을 설정합니다.
- 대기업·빅테크에서 중요하게 보는 안정성, 재현성, 운영 가능성을 신입 수준에서 설득력 있게 보여줄 수 있습니다.

---

## Resume Keywords

Machine Learning Engineer, ML Engineer, MLOps, Python, SQL, PyTorch, TensorFlow, Scikit-learn, LightGBM, XGBoost, Hugging Face, Spark, PySpark, Airflow, MLflow, Weights & Biases, DVC, Docker, Kubernetes, FastAPI, Model Serving, Online Inference, Batch Inference, Model Registry, Feature Engineering, Model Monitoring, Data Drift, ONNX, Recommendation System, NLP, Computer Vision, AWS SageMaker

---

# 3. Tech Startup Target Resume — ML Engineer

## 박민재 | Machine Learning Engineer

Email: minjae.park.ml@gmail.com  
GitHub: https://github.com/minjae-startup-ml  
Portfolio: https://minjae-ml.dev  
Blog: https://blog.minjae-ml.dev  
LinkedIn: https://linkedin.com/in/minjae-park-ml  

---

## Summary

초기 제품에서 ML 기능을 빠르게 실험하고 실제 사용자 지표 개선으로 연결하는 데 강점이 있는 신입 Machine Learning Engineer입니다.

Python, PyTorch, Scikit-learn, LightGBM, Hugging Face, FastAPI, Docker, PostgreSQL, AWS를 활용해 추천, 분류, 예측, NLP 기반 기능을 MVP 형태로 구현하고 배포했습니다. 작은 팀에서 데이터 수집, 모델 학습, API 서빙, 프론트엔드 연동, 사용자 피드백 분석까지 직접 수행한 경험이 있습니다.

스타트업 환경에서 중요한 빠른 실험, 비용 효율적인 모델 선택, 단순하지만 운영 가능한 ML pipeline, product metric 중심의 개선을 중요하게 생각합니다.

---

## Core Competencies

- ML MVP 개발
- 빠른 모델 baseline 구축 및 개선
- Product Metric 기반 모델 개선
- Recommendation / Ranking 모델 개발
- NLP Classification / Summarization 활용
- FastAPI 기반 모델 서빙
- Docker 기반 배포
- 사용자 피드백 기반 데이터셋 개선
- Batch Inference 자동화
- 비용 효율적인 모델 선택
- PM·프론트엔드·백엔드와 빠른 협업
- 작은 팀에서 end-to-end ML ownership

---

## Skills

### Language

- Python
- SQL
- JavaScript Basic
- Bash

### ML / AI

- PyTorch
- Scikit-learn
- LightGBM
- XGBoost
- Hugging Face Transformers
- Sentence Transformers
- OpenAI API Basic
- Pandas
- NumPy
- Optuna Basic
- OpenCV Basic

### ML Engineering

- FastAPI
- Docker
- MLflow Basic
- W&B
- Airflow Basic
- Cron-based Batch Job
- Model Serving
- Batch Inference
- Feature Engineering
- Experiment Tracking
- Data Validation

### Database / Infra

- PostgreSQL
- MySQL
- Redis Basic
- AWS EC2
- AWS S3
- AWS RDS
- Supabase
- Vercel
- GitHub Actions

### Product / Analytics

- Google Analytics
- Mixpanel Basic
- Event Tracking
- Funnel Analysis
- Click-through Rate
- Conversion Rate
- Retention Basic
- A/B Test Basic
- User Interview

---

## Experience

### Founding ML Engineer Intern

**LocalLoop AI**  
2025.05 - 2025.11

동네 기반 소모임·예약 플랫폼을 만드는 초기 스타트업에서 개인화 추천과 사용자 이탈 예측 모델을 개발했습니다.

### Key Contributions

- 사용자 프로필, 지역, 관심사, 조회·예약 로그를 기반으로 모임 추천 모델 prototype 개발
- Popularity baseline에서 LightGBM Ranker 기반 reranking 모델로 개선하여 NDCG@10 0.36에서 0.57로 향상
- 모임 상세 조회 후 예약 신청 가능성을 예측하는 conversion prediction model 개발
- 모델 결과를 FastAPI 추천 API로 제공하고 프론트엔드 탐색 화면과 연동
- 추천 결과 클릭, 저장, 예약 여부를 event로 수집하여 모델 평가 데이터셋 개선
- 신규 사용자 cold-start 문제를 해결하기 위해 지역·관심사 기반 rule fallback 적용
- 모델 inference 비용과 지연시간을 줄이기 위해 사전 batch recommendation table 생성
- 사용자 인터뷰를 통해 "거리와 시간대가 추천 만족도에 중요하다"는 insight를 발견하고 feature에 반영
- PM과 함께 추천 클릭률, 예약 전환율, 추천 숨김률을 주요 product metric으로 정의
- 매주 실험 결과를 정리하여 feature 변경, 모델 변경, UX 변경을 구분해 리포트 작성

### Startup Impact

- 추천 영역 클릭률 18%에서 31%로 개선
- 추천 기반 예약 전환율 7.4%에서 12.8%로 개선
- NDCG@10 58% 개선
- Cold-start 사용자 추천 만족도 3.1 / 5.0에서 4.0 / 5.0으로 개선
- 추천 API 평균 응답 시간 240ms 이하 유지
- 2주 단위 product iteration 5회 참여

### Tech Stack

Python, LightGBM, Scikit-learn, Pandas, FastAPI, PostgreSQL, Redis, Docker, AWS EC2, Google Analytics, Mixpanel

---

## Projects

---

### Project 1. LocalRec — 지역 모임 개인화 추천 시스템

GitHub: https://github.com/minjae-startup-ml/localrec  
Demo: https://localrec.dev  
Period: 2025.01 - 2025.04  
Role: ML Engineer / Product Engineer

사용자의 지역, 관심사, 활동 시간대, 조회·예약 로그를 기반으로 지역 모임을 개인화 추천하는 ML 기반 추천 시스템입니다.

### Problem

초기 모임 서비스에서는 인기순 정렬만으로는 사용자별 관심사와 거리 조건을 반영하기 어렵습니다. 또한 데이터가 적은 초기 단계에서는 복잡한 딥러닝 모델보다 빠르게 검증 가능한 추천 구조가 필요했습니다.

### Solution

- Popularity baseline, content-based filtering, LightGBM Ranker를 비교
- 신규 사용자에게는 지역·관심사 기반 rule fallback 제공
- 기존 사용자에게는 조회, 저장, 예약 이력을 기반으로 ranking score 계산
- 추천 결과 클릭률과 예약 전환율을 함께 측정
- 추천 결과를 사전 계산해 API 응답 속도와 비용을 절감
- 사용자 피드백을 feature와 filtering rule에 반영

### Key Contributions

- user_profile, meeting_feature, user_meeting_interaction 데이터셋 설계
- 거리, 카테고리 일치도, 시간대 일치도, 가격대, 호스트 응답률 feature 생성
- 클릭, 저장, 예약 이벤트를 implicit feedback으로 변환
- NDCG@10, MAP@10, Coverage, Diversity 기준으로 추천 모델 평가
- LightGBM Ranker hyperparameter tuning 수행
- Batch recommendation table을 생성하는 cron job 구현
- FastAPI 기반 추천 API와 fallback logic 구현
- 추천 결과에 "가까운 위치", "관심 카테고리", "선호 시간대" 등 추천 이유 제공
- 추천 숨김 이벤트를 negative feedback으로 저장
- 사용자 인터뷰 18건을 바탕으로 추천 필터와 feature 개선

### Impact

- NDCG@10 0.34에서 0.59로 개선
- 추천 클릭률 16%에서 33%로 개선
- 추천 기반 예약 전환율 6.8%에서 13.1%로 개선
- Cold-start 사용자 추천 만족도 4.1 / 5.0 기록
- 추천 API 평균 응답 시간 210ms 이하 유지
- 베타 사용자 220명 대상 추천 실험 진행

### Tech Stack

Python, LightGBM, Scikit-learn, Pandas, FastAPI, PostgreSQL, Redis, Docker, AWS EC2

---

### Project 2. ChurnGuard — 사용자 이탈 예측 모델

GitHub: https://github.com/minjae-startup-ml/churnguard  
Period: 2024.10 - 2024.12  
Role: ML Engineer

초기 서비스 사용자의 행동 로그를 기반으로 7일 내 이탈 가능성을 예측하고, 리텐션 개선 실험에 활용할 수 있는 ML 모델입니다.

### Problem

초기 제품에서는 사용자가 왜 이탈하는지 빠르게 파악해야 하지만, 단순 DAU/WAU 지표만으로는 어떤 사용자가 위험군인지 알기 어렵습니다.

### Solution

- 가입 후 첫 24시간 행동을 기반으로 7일 내 재방문 여부 예측
- Logistic Regression, Random Forest, XGBoost 모델 비교
- 행동 feature와 프로필 feature를 결합
- SHAP을 활용해 이탈 예측에 영향을 주는 feature 설명
- 위험 사용자 segment를 dashboard에 제공
- PM이 리텐션 실험 대상자를 선정할 수 있도록 output table 생성

### Key Contributions

- signup, onboarding_complete, view_item, click_cta, create_item, invite_friend 이벤트 기반 feature 생성
- 사용자별 첫 24시간 행동 count, time-to-first-action, session duration feature 생성
- Label leakage를 방지하기 위해 예측 시점 이후 이벤트 제외
- Imbalanced dataset 문제를 class weight와 threshold tuning으로 개선
- ROC-AUC, PR-AUC, Recall@Top20% 기준으로 모델 평가
- SHAP summary plot으로 주요 feature 해석
- Batch inference script로 매일 churn_risk_user table 생성
- 위험군 사용자 대상 온보딩 개선 실험을 위한 segment 제공

### Impact

- ROC-AUC 0.72에서 0.86으로 개선
- Top 20% 위험군에서 실제 이탈 사용자 61% 포착
- 온보딩 완료 여부와 첫 핵심 행동 시간이 주요 feature임을 발견
- PM의 리텐션 실험 대상자 선정 시간 3시간에서 20분으로 단축
- 리텐션 개선 실험 설계 근거 제공

### Tech Stack

Python, XGBoost, Scikit-learn, Pandas, SHAP, PostgreSQL, Airflow Basic, Metabase

---

### Project 3. SupportTagger — 고객 문의 자동 분류 모델

GitHub: https://github.com/minjae-startup-ml/supporttagger  
Period: 2024.07 - 2024.09  
Role: NLP / ML Engineer

고객 문의 텍스트를 결제, 계정, 버그, 사용법, 환불, 기타 카테고리로 자동 분류하고 우선순위를 부여하는 NLP 모델입니다.

### Problem

초기 스타트업에서는 고객 문의를 수동으로 분류하다 보면 반복 문의를 파악하기 어렵고, 긴급한 버그 문의 대응이 늦어질 수 있습니다.

### Solution

- 문의 텍스트 라벨링 데이터셋 구축
- TF-IDF + Linear SVM baseline과 KoBERT fine-tuning 모델 비교
- 문의 카테고리와 긴급도 분류 모델 구현
- 운영자가 수정한 라벨을 다시 학습 데이터로 저장하는 feedback loop 설계
- FastAPI 기반 분류 API 구현
- Slack webhook으로 urgent 문의 알림 전송

### Key Contributions

- 고객 문의 15,000건 수집 및 개인정보 masking
- 3,000건 라벨링 데이터셋 구축
- 카테고리 불균형 문제를 class weight로 완화
- 짧은 문의와 복합 문의를 별도 오류 유형으로 분류
- Macro F1, class별 Recall 기준으로 모델 평가
- 운영자 수정 라벨을 feedback table에 저장
- 분류 confidence score가 낮을 경우 human review로 넘기는 rule 적용
- Slack 알림 메시지에 문의 카테고리, 긴급도, confidence score 포함

### Impact

- 문의 카테고리 분류 Macro F1 0.69에서 0.84로 개선
- 긴급 문의 Recall 0.63에서 0.88로 개선
- 수동 문의 분류 시간 약 65% 절감
- 긴급 문의 평균 인지 시간 40분에서 5분 이내로 단축
- 운영자 라벨 수정 데이터를 재학습 데이터로 누적하는 구조 구축

### Tech Stack

Python, Scikit-learn, PyTorch, Hugging Face Transformers, KoBERT, FastAPI, PostgreSQL, Docker, Slack Webhook

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 예정  
GPA: 4.10 / 4.5

Relevant Coursework:

- 자료구조
- 알고리즘
- 데이터베이스
- 인공지능
- 기계학습
- 딥러닝
- 자연어처리
- 확률과 통계
- 선형대수
- 창업과 소프트웨어 제품 개발

---

## Awards / Activities

### 2025 대학 연합 AI Product 해커톤 대상

2025.06

- LocalRec 프로젝트로 대상 수상
- 초기 데이터가 적은 상황에서 개인화 추천과 rule fallback을 결합한 점을 높게 평가받음
- 추천 클릭률과 예약 전환율 개선 결과를 함께 발표

### 2024 스타트업 ML MVP 해커톤 최우수상

2024.12

- ChurnGuard 프로젝트로 최우수상 수상
- 사용자 이탈 예측 모델과 PM이 활용 가능한 segment dashboard를 구현
- 모델 해석 가능성과 제품 적용 가능성에서 높은 평가를 받음

### Product ML Study Organizer

2024.09 - 2025.05

- 15명 규모의 제품 중심 ML 스터디 운영
- 주제: 추천 시스템, 이탈 예측, NLP 분류, A/B test, 모델 평가, 모델 서빙
- 매주 실제 서비스 지표를 기반으로 ML 문제를 정의하고 baseline 모델 구현

---

## Certifications

- SQLD
- Google Analytics Certification
- AWS Cloud Practitioner 준비 중
- 정보처리기사 필기 준비 중

---

## Product Metrics Experience

- Click-through Rate
- Conversion Rate
- Reservation Conversion
- Retention
- Churn Rate
- Recall@TopK
- NDCG@K
- MAP@K
- Model Latency
- Inference Cost
- Feedback Correction Rate
- Human Review Rate
- Recommendation Hide Rate

---

## Technical Writing

- "스타트업에서 추천 모델을 처음 만들 때 복잡한 딥러닝보다 중요한 것"
- "Cold-start 문제를 Rule-based Fallback으로 해결한 경험"
- "이탈 예측 모델을 PM이 실제로 쓰게 만들기까지"
- "Offline Metric보다 클릭률이 중요했던 추천 실험"
- "고객 문의 분류 모델에 Human Review Flow를 붙인 이유"

---

## Strengths

- 초기 제품에서 ML 기능을 빠르게 만들고 사용자 지표로 검증할 수 있습니다.
- 복잡한 모델보다 문제 상황에 맞는 단순하고 효과적인 baseline을 먼저 구축합니다.
- 모델 성능, 추론 속도, 비용, 사용자 피드백을 함께 고려합니다.
- 작은 팀에서 데이터 수집, 모델 학습, API 서빙, 제품 연동까지 넓게 책임질 수 있습니다.
- 스타트업에서 중요한 속도, 오너십, 제품 이해도, 실험 능력을 갖추고 있습니다.

---

## Resume Keywords

Machine Learning Engineer, Startup ML Engineer, Product ML Engineer, Python, SQL, PyTorch, Scikit-learn, LightGBM, XGBoost, Hugging Face, KoBERT, Recommendation System, Ranking Model, Churn Prediction, NLP Classification, Feature Engineering, FastAPI, Docker, PostgreSQL, Redis, AWS EC2, Batch Inference, Online Inference, Product Metrics, CTR, Conversion Rate, Retention, A/B Test, User Feedback, MVP