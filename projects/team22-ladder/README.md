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
uvicorn app.main:app --reload
```

**Frontend** (새 터미널)

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
