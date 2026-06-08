# Machine Learning Engineer — Foreign / Global Company Target Resume

## Daniel Kim | Machine Learning Engineer

Email: daniel.kim.ml@gmail.com  
GitHub: https://github.com/danielkim-ml  
Portfolio: https://danielkim-ml.dev  
Blog: https://blog.danielkim-ml.dev  
LinkedIn: https://linkedin.com/in/danielkim-ml  

---

## Summary

Entry-level Machine Learning Engineer with experience building, evaluating, serving, and monitoring ML models for recommendation, NLP, computer vision, and prediction use cases. Skilled in Python, PyTorch, TensorFlow, Scikit-learn, LightGBM, Hugging Face, FastAPI, Docker, MLflow, Weights & Biases, Airflow, PostgreSQL, and AWS.

Built ML projects beyond notebooks by implementing feature pipelines, experiment tracking, model registries, inference APIs, batch inference jobs, data validation, latency optimization, and product metric analysis. Strong interest in production ML systems that connect model quality with business and user outcomes.

---

## Skills

### Machine Learning

- Python
- PyTorch
- TensorFlow
- Scikit-learn
- LightGBM
- XGBoost
- Hugging Face Transformers
- OpenCV
- Pandas
- NumPy
- Recommendation Systems
- NLP
- Computer Vision
- Feature Engineering
- Hyperparameter Tuning

### MLOps / Engineering

- MLflow
- Weights & Biases
- DVC Basic
- FastAPI
- Docker
- Airflow
- ONNX
- Batch Inference
- Online Inference
- Model Registry
- Model Monitoring
- Data Validation
- Drift Detection Basic

### Data / Infra

- SQL
- PostgreSQL
- MySQL
- Redis Basic
- AWS EC2
- AWS S3
- AWS RDS
- GitHub Actions
- Linux

### Evaluation

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- NDCG@K
- MAP@K
- RMSE
- MAE
- Latency
- Throughput
- Error Analysis

---

## Experience

### Machine Learning Engineer Intern

**CommerceCore AI Platform Team**  
Jun 2025 - Dec 2025

Worked on recommendation, review classification, and ML pipeline improvements for an e-commerce AI platform.

- Built PySpark feature pipelines for recommendation models using user clicks, purchases, category preferences, price preferences, and recent activity windows.
- Improved LightGBM ranking model NDCG@10 from 0.49 to 0.63 through feature engineering, candidate filtering, and hyperparameter tuning.
- Reduced daily batch inference runtime from 72 minutes to 29 minutes by optimizing feature joins, partitioning, and model inference batching.
- Implemented FastAPI-based online inference endpoint with Redis caching, maintaining p95 latency below 180ms.
- Added MLflow Model Registry to track staging and production model versions with dataset hash, feature version, parameters, metrics, and artifacts.
- Built data validation checks for feature null ratio, distribution drift, category cardinality, and out-of-range values.
- Analyzed offline recommendation metrics against actual click-through rate and created segment-level model performance reports.
- Used Weights & Biases to track model experiments, confusion matrices, ranking metrics, and error-analysis artifacts.
- Collaborated with data engineers to align feature table definitions and with backend engineers to define inference API contracts.
- Improved recommendation click-through rate by 11% relative in an internal A/B-style evaluation.

---

## Projects

### RecSys Platform — Recommendation Training and Serving Pipeline

GitHub: https://github.com/danielkim-ml/recsys-platform  
Period: Feb 2025 - May 2025  
Role: Machine Learning Engineer

End-to-end recommendation system with training, experiment tracking, batch inference, online serving, and monitoring.

- Built feature datasets from user-item interaction logs with event_type, event_time, category, price, and user profile features.
- Compared popularity baseline, matrix factorization, and LightGBM Ranker using NDCG@10, MAP@10, Recall@50, coverage, and diversity.
- Improved NDCG@10 from 0.44 to 0.66 and MAP@10 from 0.27 to 0.43.
- Reduced daily batch inference time from 85 minutes to 31 minutes by batching predictions and optimizing joins.
- Built FastAPI online inference service with Redis caching and p95 latency below 160ms.
- Managed 91 experiments and 12 model versions using MLflow.
- Implemented model degradation alerts based on NDCG threshold, feature null ratio, and distribution shift.
- Designed fallback recommendations for cold-start users using popularity, category preference, and location-based rules.

Tech Stack: Python, PySpark, LightGBM, Scikit-learn, MLflow, Airflow, FastAPI, Redis, PostgreSQL, Docker, AWS S3

---

### Review Intelligence — NLP Review Classification System

GitHub: https://github.com/danielkim-ml/review-intelligence  
Period: Nov 2024 - Jan 2025  
Role: NLP Engineer

NLP system that classifies product reviews by sentiment, issue category, and urgency.

- Built an 8,000-sample labeled dataset for sentiment and issue classification from 120K product reviews.
- Compared TF-IDF baseline, KoBERT, and KLUE-RoBERTa models.
- Improved sentiment Macro F1 from 0.73 to 0.88 through fine-tuning, label cleanup, class weighting, and threshold tuning.
- Increased negative review recall from 0.69 to 0.90 to prioritize operational issue detection.
- Achieved 0.82 Micro F1 for multi-label issue classification across shipping, quality, price, usability, and support categories.
- Built batch inference pipeline that generated product_issue_daily_mart for dashboards.
- Created FastAPI endpoint for single-review classification with confidence score and human-review fallback.
- Categorized model errors into short text, sarcasm, mixed sentiment, and ambiguous label groups.

Tech Stack: Python, PyTorch, Hugging Face Transformers, KoBERT, KLUE-RoBERTa, W&B, FastAPI, PostgreSQL, Docker

---

## Education

### Korea University of Technology — B.S. in Computer Science

Mar 2020 - Feb 2026 expected  
GPA: 4.18 / 4.5

Relevant Coursework:

- Data Structures
- Algorithms
- Artificial Intelligence
- Machine Learning
- Deep Learning
- Natural Language Processing
- Computer Vision
- Linear Algebra
- Probability and Statistics
- Database Systems
- Operating Systems

---

## Awards & Activities

### Grand Prize — University AI Modeling Contest

May 2025

- Won grand prize with RecSys Platform.
- Presented recommendation architecture, experiment tracking, batch inference, online serving, and model monitoring strategy.

### MLOps Study Lead

Jan 2025 - Jun 2025

- Led a 12-member study group on MLflow, W&B, DVC, Airflow, Docker, FastAPI, model serving, and drift monitoring.
- Organized end-to-end ML deployment mini-projects and model review sessions.

---

## Certifications

- SQLD
- AWS Certified Cloud Practitioner, in progress
- TensorFlow Developer Certificate, in progress
- Engineer Information Processing, written exam passed

---

## Keywords

Machine Learning Engineer, ML Engineer, MLOps, Python, PyTorch, TensorFlow, Scikit-learn, LightGBM, XGBoost, Hugging Face, NLP, Computer Vision, Recommendation System, Feature Engineering, Model Training, Model Evaluation, MLflow, Weights & Biases, Docker, FastAPI, Airflow, Batch Inference, Online Inference, Model Registry, Model Monitoring, Data Drift, ONNX, AWS