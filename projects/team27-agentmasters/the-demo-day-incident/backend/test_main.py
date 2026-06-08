import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_client_origins, get_db, get_trusted_proxy_ips
import models

# 테스트용 데이터베이스 설정 (인메모리 SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테스트 데이터베이스 의존성 오버라이드
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 각 테스트 실행 전후로 데이터베이스 테이블 생성 및 삭제
@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

# --- 기본 API 테스트 ---

def test_update_clue_state():
    response = client.post("/api/clues/1", headers={"user-id": "testuser"})
    assert response.status_code == 200
    db = TestingSessionLocal()
    clue_state = db.query(models.ClueState).filter_by(user_id="testuser", clue_id=1).first()
    assert clue_state is not None
    db.close()

def test_get_clues():
    client.post("/api/clues/1", headers={"user-id": "testuser"})
    response = client.get("/api/clues", headers={"user-id": "testuser"})
    assert response.status_code == 200
    assert len(response.json()["clues"]) == 1

def test_update_character_state():
    response = client.post("/api/character/1", headers={"user-id": "testuser"})
    assert response.status_code == 200
    db = TestingSessionLocal()
    char_state = db.query(models.CharacterState).filter_by(user_id="testuser", character_id=1).first()
    assert char_state is not None
    db.close()

def test_get_characters():
    client.post("/api/character/1", headers={"user-id": "testuser"})
    response = client.get("/api/characters", headers={"user-id": "testuser"})
    assert response.status_code == 200
    assert len(response.json()["characters"]) == 1

def test_get_character_messages_empty():
    response = client.get("/api/characters/1/messages", headers={"user-id": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert data["character_id"] == 1
    assert data["messages"] == []

# --- LLM 연동 테스트 ---

def test_character_chat_with_llm():
    """LLM 연동 후 인물 대화 생성 및 조회 테스트"""
    response_post = client.post(
        "/api/characters/1/messages",
        headers={"user-id": "testuser"},
        json={"content": "안녕하세요. 당신은 누구신가요?"}
    )
    assert response_post.status_code == 200
    data_post = response_post.json()

    assert data_post["character_id"] == 1
    assert "content" in data_post
    assert isinstance(data_post["content"], str)
    assert data_post["content"] != ""

    print(f"\n[LLM 응답] 인물 대화: {data_post['content']}")

    response_get = client.get("/api/characters/1/messages", headers={"user-id": "testuser"})
    assert response_get.status_code == 200
    data_get = response_get.json()

    assert len(data_get["messages"]) == 2
    assert data_get["messages"][0]["content"] == "안녕하세요. 당신은 누구신가요?"
    assert data_get["messages"][1]["content"] == data_post["content"]

def test_deduction_incorrect_with_llm():
    """LLM 연동 후 '오답' 추리 제출 테스트"""
    payload = {
        "content": "민재는 범인이 아니다. 그는 단지 피곤했을 뿐이다.",
        "character": 1,
        "clues": [1, 2]
    }
    response = client.post(
        "/api/deductions",
        headers={"user-id": "testuser"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert "comment" in data
    assert "result" in data
    assert data["result"] is False
    assert isinstance(data["comment"], str)

    print(f"\n[LLM 응답] 오답 추리 코멘트: {data['comment']}")

def test_deduction_correct_with_llm():
    """LLM 연동 후 '정답' 추리 제출 테스트"""
    payload = {
        "content": "사건의 진실을 밝혀냈습니다. 범인은 바로 아리아입니다.",
        "character": 4,
        "clues": [5, 6]
    }
    response = client.post(
        "/api/deductions",
        headers={"user-id": "testuser"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert "comment" in data
    assert "result" in data
    assert data["result"] is True
    assert isinstance(data["comment"], str)

    print(f"\n[LLM 응답] 정답 추리 코멘트: {data['comment']}")

# --- CORS 테스트 ---

def test_cors_allowed_origin():
    """허용된 출처(Origin)에서 온 요청을 테스트합니다."""
    allowed_origin = os.environ.get("CLIENT_ORIGIN_URL", "http://localhost:3000")
    # 필수 헤더인 'user-id'를 추가합니다.
    headers = {"Origin": allowed_origin, "user-id": "test-cors-user"}
    response = client.get("/api/clues", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin

def test_cors_origin_config_accepts_comma_separated_values(monkeypatch):
    monkeypatch.setenv(
        "CLIENT_ORIGIN_URL",
        "https://game.example.com, https://admin.example.com",
    )

    assert get_client_origins() == [
        "https://game.example.com",
        "https://admin.example.com",
    ]


def test_trusted_proxy_ips_config_accepts_comma_separated_values(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_IPS", "127.0.0.1, 172.18.0.0/16")

    assert get_trusted_proxy_ips() == ["127.0.0.1", "172.18.0.0/16"]


def test_cors_disallowed_origin():
    """허용되지 않은 출처(Origin)에서 온 요청을 테스트합니다."""
    # 필수 헤더인 'user-id'를 추가합니다.
    headers = {"Origin": "http://evil.com", "user-id": "test-cors-user"}
    response = client.get("/api/clues", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers

def test_cors_preflight_request():
    """브라우저의 Preflight(OPTIONS) 요청을 테스트합니다."""
    allowed_origin = os.environ.get("CLIENT_ORIGIN_URL", "http://localhost:3000")
    headers = {
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-User-Id, Content-Type",
    }
    response = client.options("/api/clues/1", headers=headers)
    assert response.status_code == 200
    # Preflight 응답은 본문이 비어있거나 'OK'일 수 있으므로, 본문 내용은 검증하지 않습니다.
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


def test_cors_preflight_behind_nginx_proxy_manager():
    """Nginx Proxy Manager forwards public scheme and host to the backend."""
    allowed_origin = os.environ.get("CLIENT_ORIGIN_URL", "http://localhost:3000")
    headers = {
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-User-Id, Content-Type",
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": "api.example.com",
        "Host": "backend:8000",
    }

    response = client.options("/api/clues/1", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
