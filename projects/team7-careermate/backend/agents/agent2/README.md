# Agent2 - Job Requirement Extractor

CareerMate의 `job_requirement` 노드만 독립 실행할 수 있는 FastAPI MVP입니다.

## 위치 결정

`backend/readme.md`에는 agent 파일을 backend 내부에 두라는 지시가 없어서, 기존 backend와 충돌하지 않도록 루트에 `agent2/` 전용 폴더로 구성했습니다.

## 입력

- `target_role`: 목표직무
- `company_type`: 희망기업유형

## 동작

1. DuckDuckGo HTML 검색으로 채용공고 후보를 찾습니다.
2. DuckDuckGo `df=y` 최근 1년 필터와 `2026/2025`, `채용중`, `최근 1년` 검색어를 함께 사용합니다.
3. 상위 결과 일부의 페이지 텍스트를 짧게 수집합니다.
4. 명시적으로 오래된 날짜가 있거나 `마감`, `채용 종료`, `expired` 같은 문구가 있으면 제외합니다.
5. Upstage Solar LLM API로 요구역량을 정리합니다.
6. LLM/API 키/검색 실패 시에도 규칙 기반 폴백 JSON을 반환합니다.

검색엔진 기반 MVP라 최신성을 절대 보장하지는 못하지만, 1년 이내 공고를 우선 수집하도록 제한합니다.

## 실행

```powershell
cd C:\Users\kyjii\SW_maestro\AI_Edu\swmaestro-team07-ai-study
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r agent2\requirements.txt
$env:UPSTAGE_API_KEY="YOUR_UPSTAGE_API_KEY"
python -m uvicorn agent2.main:app --reload --port 8002
```

브라우저에서 `http://127.0.0.1:8002`를 열면 확인용 웹페이지를 사용할 수 있습니다.

## API

```http
POST /agent2/job-requirement
Content-Type: application/json
```

```json
{
  "target_role": "백엔드 개발자",
  "company_type": "스타트업",
  "max_results": 5
}
```

**응답:**

```json
{
  "companies": [{"name": "예시기업", "url": "https://..."}],
  "required_skills": ["Python으로 API 서버를 구현하고 디버깅하는 능력"],
  "preferred_skills": ["Docker로 애플리케이션 실행 환경을 구성하는 능력"],
  "required_experience": ["REST API 개발 경험"],
  "keywords": ["백엔드", "API", "스타트업"]
}
```

## 보안

API 키는 코드에 저장하지 않습니다. 반드시 `UPSTAGE_API_KEY` 환경변수로 주입하세요.
