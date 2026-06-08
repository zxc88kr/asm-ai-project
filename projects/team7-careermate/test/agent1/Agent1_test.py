import os
import sys
import json

# 프로젝트 루트 경로를 sys.path에 추가하여 backend 패키지를 임포트할 수 있도록 함
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
sys.path.append(PROJECT_ROOT)

from backend.agents.ProfileDiagnosisAgent.ProfileDiagnosisAgent import Agent1

def execute_agent1_test():
    # 1. API 키 환경 변수 확인
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        print("❌ 에러: UPSTAGE_API_KEY 환경 변수가 로드되지 않았습니다.")
        print("💡 .env 파일에 키가 있거나 쉘에 등록되어 있는지 확인하세요.")
        return

    print(f"🔑 API Key 확인 완료 (길이: {len(api_key)})")
    
    # 2. 에이전트 1 인스턴스 생성
    agent1 = Agent1()
    
    # 3. 모의 온보딩 입력 데이터
    major = "컴퓨터공학과"
    current_status = "대학 졸업생"
    interests = ["Backend", "Database"]
    target_job = "Backend Engineer"
    preferred_company_type = "외국계" # 외국계 맞춤 잣대 가동
    available_time = "20시간 이상"
    concerns = [
        "영어로 진행되는 기술 면접이나 글로벌 협업 문서화 작업이 조금 걱정됩니다.",
        "TDD 기반의 clean code 개발 실무 경험이나 오픈소스 기여 경험이 없어 고민입니다."
    ]
    
    # 4. 백엔드가 PDF 파일에서 파싱해 넘겨줄 가상의 이력서 텍스트 (사용자 스펙)
    # 학력, 수강과목, 몇 가지 기술 및 프로젝트 내용 포함
    mock_resume_text = """
# 외국계 기업 타겟 Resume — 신입 백엔드 개발자

> Target: 국내 소재 외국계 기업 / 글로벌 IT 기업 한국 지사 / 외국계 SaaS 기업
> Role: Junior BackEnd Engineer / Software Engineer
> Level: 대학교 4학년 졸업 전 / 신입 / 인턴 경험 없음 또는 제한적
> Language: Korean Resume Format with Global Resume Style
> Purpose: 국내 신입 백엔드 개발자의 외국계 기업 지원용 비교군 Resume

---

# 박준호 | Junior BackEnd Engineer

Email: [junho.park.backend@gmail.com](mailto:junho.park.backend@gmail.com)
GitHub: https://github.com/junho-park-dev
Blog: https://velog.io/@junho-backend
Portfolio: https://junho-backend.dev
LinkedIn: https://linkedin.com/in/junho-park-backend

---

## Summary

Java와 Spring Boot를 중심으로 웹 백엔드 개발을 학습하고 있는 신입 백엔드 개발자입니다.
대학교 팀 프로젝트와 개인 프로젝트를 통해 회원 인증, 게시판, 예약, 도서 대여, 관리자 기능 등 기본적인 웹 서비스 API를 설계하고 구현했습니다.

Spring Boot, Spring Data JPA, MySQL, Spring Security, JWT, Swagger, GitHub, Postman을 활용해 REST API를 개발한 경험이 있으며, 프론트엔드 개발자와 API 명세를 맞추고 실제 화면과 연동하는 과정을 경험했습니다.

아직 대규모 트래픽이나 운영 환경 경험은 부족하지만, 백엔드 개발자로서 API 설계, 데이터베이스 모델링, 인증/인가, 예외 처리, 테스트 코드, 배포 자동화 역량을 꾸준히 확장하고 있습니다.
외국계 기업에서 중요하게 보는 명확한 커뮤니케이션, 문서화, 협업, 자기주도 학습을 바탕으로 성장하고자 합니다.

---

## Core Competencies

* Java / Spring Boot 기반 REST API 개발
* Spring Data JPA 기반 CRUD 기능 구현
* MySQL 기반 테이블 설계 및 데이터 관리
* Spring Security / JWT 기반 인증 기능 구현
* Controller, Service, Repository 계층 분리
* Swagger 기반 API 문서화
* Postman 기반 API 테스트
* GitHub 기반 협업 및 코드 관리
* 프론트엔드와 API 명세 조율 경험
* 기본적인 AWS EC2 배포 학습 경험
* 문제 발생 시 로그와 에러 메시지를 기반으로 원인 분석

---

## Skills

### Language

* Java
* SQL
* JavaScript
* Python Basic
* HTML
* CSS

### Backend

* Spring Boot
* Spring MVC
* Spring Data JPA
* Spring Security
* REST API
* JWT
* Validation
* Global Exception Handling Basic

### Database

* MySQL
* MariaDB
* H2
* Basic Database Modeling
* Basic SQL Query
* Entity Relationship Mapping

### Frontend

* React Basic
* Thymeleaf
* HTML
* CSS
* Bootstrap
* Axios

### Tools

* Git
* GitHub
* IntelliJ IDEA
* VS Code
* Postman
* Swagger
* Notion
* Slack

### Deployment / Infra

* AWS EC2 Basic
* AWS RDS Basic
* Docker Basic
* Linux Basic
* Netlify Basic

---

## Education

### 한빛대학교 소프트웨어학부

2020.03 - 2026.02 졸업 예정
GPA: 3.64 / 4.5

### Relevant Coursework

* 자료구조
* 알고리즘
* 객체지향프로그래밍
* 데이터베이스
* 운영체제
* 컴퓨터네트워크
* 웹프로그래밍
* 소프트웨어공학
* 정보보안개론

---

## Projects

---

## 1. Book Rental Service — 도서 대여 관리 서비스

GitHub: https://github.com/junho-park-dev/book-rental-service
Period: 2025.03 - 2025.06
Team Size: 4
Role: BackEnd Developer

도서관 환경을 가정하여 사용자가 도서를 검색하고 대여·반납할 수 있는 웹 기반 도서 대여 관리 서비스입니다.
학교 캡스톤디자인 프로젝트로 진행했으며, 백엔드 API 개발과 데이터베이스 설계를 주로 담당했습니다.

### 주요 구현 내용

* Spring Boot 기반 도서 대여 관리 REST API 구현
* 회원가입, 로그인, 도서 등록, 도서 수정, 도서 삭제, 도서 검색 API 개발
* 사용자별 도서 대여 내역 조회 기능 구현
* 도서 대여 및 반납 상태 관리 기능 구현
* 관리자 권한을 가진 사용자만 도서 등록·수정·삭제가 가능하도록 권한 처리
* Spring Security와 JWT를 활용한 인증 기능 구현
* MySQL 기반 회원, 도서, 대여 내역 테이블 설계
* Swagger를 활용해 API 명세 확인 가능하도록 구성
* Postman을 활용해 주요 API 요청과 응답 테스트 수행

### 기여한 부분

* 회원, 도서, 대여 내역 Entity를 설계하고 JPA 연관관계를 설정했습니다.
* 초기에는 도서 테이블에 대여 여부만 저장했지만, 사용자별 대여 이력 관리가 어렵다는 문제를 발견했습니다.
* 이후 RentalHistory 테이블을 분리하여 회원과 도서를 연결하는 구조로 수정했습니다.
* 관리자와 일반 사용자의 권한을 구분하여 API 접근 제어를 구현했습니다.
* 프론트엔드 팀원이 API를 쉽게 사용할 수 있도록 Swagger와 Notion에 API 설명을 정리했습니다.
* 프로젝트 발표 전 주요 기능을 Postman으로 검증하고, 오류가 발생한 API를 수정했습니다.

### 결과

* 총 22개 백엔드 API 구현
* 회원, 도서, 대여 내역 관련 주요 기능 완성
* 교내 캡스톤디자인 장려상 수상
* 팀 프로젝트에서 백엔드 핵심 기능 담당
* API 문서화를 통해 프론트엔드 연동 과정에서 발생하는 질문 감소

### 아쉬운 점

* 동시 대여 요청 상황을 충분히 고려하지 못했습니다.
* 테스트 코드를 체계적으로 작성하지 못했습니다.
* 최종 배포 환경이 안정적이지 않아 로컬 시연 중심으로 발표했습니다.
* 다음 프로젝트에서는 동시성 제어, 테스트 코드, 배포 환경 구축을 더 깊게 적용하고 싶습니다.

### Tech Stack

Java, Spring Boot, Spring Security, Spring Data JPA, JWT, MySQL, Swagger, Postman, GitHub

---

## 2. Club Recruit Board — 동아리 모집 게시판

GitHub: https://github.com/junho-park-dev/club-recruit-board
Period: 2024.10 - 2024.12
Team Size: 3
Role: BackEnd Developer

학교 동아리 모집 글을 등록하고, 학생들이 모집 글을 조회하거나 신청할 수 있는 게시판 서비스입니다.
게시글, 댓글, 신청 기능을 중심으로 백엔드 API를 구현했습니다.

### 주요 구현 내용

* 동아리 모집 글 작성, 수정, 삭제 API 구현
* 모집 글 목록 조회 및 상세 조회 API 구현
* 댓글 작성 및 삭제 API 구현
* 모집 신청 및 신청자 목록 조회 API 구현
* 작성자만 모집 글을 수정·삭제할 수 있도록 권한 검증 로직 추가
* 같은 사용자가 동일 모집 글에 중복 신청하지 못하도록 검증 로직 구현
* MySQL 기반 회원, 모집 글, 신청, 댓글 테이블 설계
* React 프론트엔드와 Axios 기반 API 연동 지원

### 기여한 부분

* 모집 글과 신청 도메인의 Entity와 Repository를 구현했습니다.
* Service 계층에서 작성자 검증, 중복 신청 검증, 댓글 삭제 검증 로직을 작성했습니다.
* API 응답 형식이 프로젝트 중간에 자주 바뀌면서 프론트엔드 연동 오류가 발생했습니다.
* 이후 팀원들과 공통 응답 형식을 정하고, 성공 응답과 에러 응답 구조를 일부 통일했습니다.
* Swagger를 적용하여 API 목록과 요청 파라미터를 확인할 수 있도록 했습니다.
* GitHub Pull Request를 통해 팀원들과 변경 내용을 공유했습니다.

### 결과

* 모집 글, 댓글, 신청 관련 API 구현 완료
* 프론트엔드 화면과 API 연동 완료
* 팀 프로젝트 최종 발표에서 주요 기능 정상 시연
* API 응답 형식 정리 후 프론트엔드 연동 오류 감소

### 아쉬운 점

* 프로젝트 초기에 API 명세를 충분히 정하지 않아 중간 수정이 많았습니다.
* 예외 처리 구조가 일관되지 않아 일부 API의 에러 응답 형식이 달랐습니다.
* Service 클래스에 로직이 많아져 코드가 다소 복잡해졌습니다.
* 테스트 코드와 성능 개선 경험은 부족했습니다.

### Tech Stack

Java, Spring Boot, Spring Data JPA, MySQL, React, Axios, Swagger, GitHub

---

## 3. Schedule API Server — 일정 관리 API 서버

GitHub: https://github.com/junho-park-dev/schedule-api
Period: 2024.07 - 2024.08
Type: Personal Project
Role: BackEnd Developer

Spring Boot와 JPA의 기본 구조를 연습하기 위해 만든 간단한 일정 관리 REST API 서버입니다.

### 주요 구현 내용

* 일정 등록 API 구현
* 일정 수정 API 구현
* 일정 삭제 API 구현
* 일정 목록 조회 API 구현
* 날짜별 일정 조회 API 구현
* 일정 완료 여부 변경 API 구현
* 요청 DTO와 응답 DTO 분리
* Validation을 활용한 입력값 검증
* H2 데이터베이스를 활용한 로컬 테스트 환경 구성

### 기여한 부분

* Controller, Service, Repository 계층을 나누어 구현했습니다.
* 처음에는 Entity를 그대로 응답으로 반환했지만, 이후 DTO를 분리하는 방식으로 수정했습니다.
* 일정 제목, 날짜, 완료 여부를 관리하는 Schedule Entity를 설계했습니다.
* Postman을 사용해 각 API의 요청과 응답을 검증했습니다.
* README에 API 목록과 실행 방법을 정리했습니다.

### 결과

* Spring Boot REST API 기본 구조 이해
* DTO 분리와 Validation 적용 경험
* JPA Repository를 활용한 기본 CRUD 구현 경험
* Postman 기반 API 테스트 경험

### 아쉬운 점

* 로그인 기능이 없어 사용자별 일정 관리는 구현하지 못했습니다.
* 예외 처리가 단순하게 구현되었습니다.
* 테스트 코드를 작성하지 않았습니다.
* 배포까지 진행하지 못했습니다.

### Tech Stack

Java, Spring Boot, Spring Data JPA, H2, Validation, Postman

---

## Experience

### 교내 캡스톤디자인

2025.03 - 2025.06

* 도서 대여 관리 서비스를 주제로 4인 팀 프로젝트 진행
* 백엔드 API 개발 담당
* 회원, 도서, 대여 내역 관련 기능 구현
* 팀원들과 GitHub, Notion을 활용해 일정과 역할 관리
* 최종 발표 자료 작성 및 서비스 시연 참여

---

## Activities

### Java & Spring Boot Study

2024.09 - 2025.02

* 주 1회 Spring Boot 스터디 참여
* 회원가입, 로그인, 게시판, 댓글 기능 구현 실습
* JPA 연관관계, Spring Security, JWT 학습
* 각자 구현한 코드를 GitHub에 업로드하고 간단한 코드 리뷰 진행

### Algorithm Study

2024.03 - 2024.08

* 백준과 프로그래머스 문제 풀이
* 구현, 문자열, 정렬, 스택, 큐, BFS/DFS 문제 학습
* 일부 풀이를 블로그에 정리

---

## Awards

### 교내 캡스톤디자인 장려상

2025.06

* 도서 대여 관리 서비스로 장려상 수상
* 백엔드 API 구현과 프로젝트 발표 참여

---

## Certifications

* SQLD 준비 중
* 정보처리기사 필기 준비 중

---

## Technical Writing

### Blog

* Spring Boot 프로젝트 구조 정리
* JPA 연관관계 기초
* JWT 로그인 구현 과정
* Spring Security 설정 중 발생한 오류 정리
* Postman으로 API 테스트하기
* DTO를 사용하는 이유 정리

---

## Strengths

* Spring Boot 기반 REST API 개발의 기본 흐름을 이해하고 있습니다.
* JPA를 활용해 간단한 도메인 모델과 CRUD 기능을 구현할 수 있습니다.
* 프론트엔드 개발자와 API 요청·응답 형식을 맞추며 협업한 경험이 있습니다.
* 프로젝트 진행 중 발생한 문제를 검색, 공식 문서, 팀원과의 논의를 통해 해결하려고 노력합니다.
* 아직 부족한 부분을 인식하고 있으며, 테스트 코드, 배포, 성능 개선, 동시성 제어를 학습하고 있습니다.

---

## Areas for Improvement

* 테스트 코드 작성 경험 부족
* 실제 운영 환경 배포 경험 부족
* 대용량 트래픽 처리 경험 부족
* Redis, Docker, AWS 활용 경험 부족
* DB 인덱스, 쿼리 최적화 경험 부족
* 동시성 제어 경험 부족

---

## Keywords

Junior BackEnd Engineer, Java, Spring Boot, Spring MVC, Spring Data JPA, Spring Security, REST API, JWT, MySQL, H2, Swagger, Postman, Git, GitHub, Backend Developer, API Development, Database, Authentication, Authorization, CRUD, Validation, DTO, Controller, Service, Repository


"""

    print("\n🚀 [테스트 실행] 에이전트 1 리디자인 진단 시동 (2단계 API 체이닝)...")
    
    try:
        # 비동기식 진단 호출 진행 (asyncio.run)
        import asyncio
        result = asyncio.run(agent1.default(
            major=major,
            currentStatus=current_status,
            interests=interests,
            targetJob=target_job,
            preferredCompanyType=preferred_company_type,
            availableTime=available_time,
            concerns=concerns,
            resumeText=mock_resume_text # 파싱 텍스트 주입
        ))
        
        print("\n🎉 [테스트 결과 분석 완료]")
        print("-----------------------------------------------------------------")
        print(f"✅ 요약 (summary):\n{result['summary']}\n")
        print(f"✅ 강점 (strengths):\n{result['strengths']}\n")
        print(f"✅ 약점 (weaknesses):\n{result['weaknesses']}\n")
        print(f"✅ 보유 기술 (owned_skills):\n{result['owned_skills']}\n")
        print(f"✅ 판단 근거 (evidence):")
        print(json.dumps(result['evidence'], ensure_ascii=False, indent=2))
        print("-----------------------------------------------------------------")
        
        # 스키마 정합성 검증
        expected_keys = {"summary", "strengths", "weaknesses", "owned_skills", "evidence"}
        if expected_keys.issubset(result.keys()):
            print("🚀 최종 출력 스펙 정합성 검증 완료: ALL PASS!")
        else:
            print("⚠️ 경고: 아웃풋 딕셔너리에 일부 필수 필드가 빠져 있습니다.")
            
    except Exception as e:
        print(f"❌ 진단 실행 중 예외 에러 발생: {e}")

if __name__ == "__main__":
    execute_agent1_test()
