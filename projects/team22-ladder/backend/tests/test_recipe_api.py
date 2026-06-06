from fastapi.testclient import TestClient

from app import main


def test_generate_recipes_requires_ingredients():
    client = TestClient(main.app)

    response = client.post("/recipes/generate", json={})

    assert response.status_code == 400
    assert "재료" in response.json()["detail"]


def test_generate_recipes_returns_recipe_categories(monkeypatch):
    def fake_generate_recipes(payload):
        assert payload["ingredients"] == ["김치"]
        return {
            "beginner": [
                {
                    "name": "김치볶음밥",
                    "difficulty": 1,
                    "time": "15분",
                    "summary": "김치와 밥을 볶는 기본 요리",
                    "ingredients": ["김치", "밥"],
                    "ingredient_amounts": {"김치": "100g", "밥": "1공기"},
                    "missing_ingredients": ["밥"],
                    "steps": ["김치를 썬다", "팬에 볶는다"],
                    "youtube_query": "김치볶음밥 레시피",
                }
            ],
            "microwave": [],
        }

    monkeypatch.setattr(main, "generate_recipes", fake_generate_recipes)
    client = TestClient(main.app)

    response = client.post("/recipes/generate", json={"ingredients": ["김치"]})

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"beginner", "microwave"}
    assert body["beginner"][0]["name"] == "김치볶음밥"
