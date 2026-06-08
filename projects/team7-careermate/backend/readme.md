# Backend

## FastAPI 기반으로 작성되는 백엔드 서버입니다.

### 기술 스택

- Python

- FastAPI

### 역할

- 클라이언트 요청 처리

- REST API 제공

- 로드맵 생성 API 제공

### 실행 방법 (리눅스 환경)

- python3 -m venv myenv 

- source ./myenv/bin/activate

- pip install -r requirements.txt

- uvicorn main:app --reload

- curl -X POST "http://localhost:8000/api/users/roadmap" \
-H "Content-Type: application/json" \
-d '{
  "majorAndYear": "컴퓨터공학과/3학년",
  "currentStatus": "백엔드 개발 준비 중",
  "interests": ["웹 개발", "AI", "클라우드"],
  "targetJob": "백엔드 개발자",
  "preferredCompanyType": "스타트업",
  "availableTime": "하루 3시간",
  "concerns": ["포트폴리오 부족", "실무 경험 부족"]
}' | jq

### API 문서 

- localhost:8000/api/users/roadmap - post

- request 더미데이터
{
  "majorAndYear": "컴퓨터공학과/3학년",
  "currentStatus": "백엔드 개발 준비 중",
  "interests": ["웹 개발", "AI", "클라우드"],
  "targetJob": "백엔드 개발자",
  "preferredCompanyType": "스타트업",
  "availableTime": "하루 3시간",
  "concerns": ["포트폴리오 부족", "실무 경험 부족"]
}