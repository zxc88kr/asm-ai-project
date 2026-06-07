# team22-ladder

> 프로젝트 한 줄 소개를 여기에 적어주세요.

## 기술 스택

- **Backend**: Python, FastAPI
- **Frontend**: Streamlit

## 실행 방법

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

`.env`에 `UPSTAGE_API_KEY` 값을 직접 입력해야 레시피 생성 Agent가 동작합니다.
`YOUTUBE_API_KEY`가 있으면 관련 영상 썸네일을 함께 조회하고, 없으면 YouTube 검색 링크만 제공합니다.

**Recipe Agent API 테스트**

```bash
cd backend
curl -X POST http://localhost:8000/recipes/generate \
  -H "Content-Type: application/json" \
  -d @examples/recipe_request.json
```

**Frontend** (새 터미널)

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp example.env .env
streamlit run app.py
```

- Frontend: http://localhost:8501
- Backend API 문서(Swagger): http://localhost:8000/docs

## 프로젝트 구조

```
team22-ladder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── .env.example
└── README.md
```
