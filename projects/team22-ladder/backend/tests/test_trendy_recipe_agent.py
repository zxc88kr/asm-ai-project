import pytest
from fastapi.testclient import TestClient

from app import main
from app.agents.trendy_recipe_agent import (
    TrendyRecipeGenerationError,
    _normalize_ingredients,
    _search_trending_recipes,
    _validate_recipes,
)


def _base_normalized_state():
    return {
        "raw_input": {},
        "normalized_input": {
            "ingredients": ["김치", "두부"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": ["간장"],
            "tools": [],
            "extra_ingredients": [],
        },
    }


def test_normalize_raises_on_empty():
    state = {"raw_input": {}}
    with pytest.raises(TrendyRecipeGenerationError, match="재료가 없습니다"):
        _normalize_ingredients(state)


def test_normalize_deduplicates_ingredients():
    state = {
        "raw_input": {
            "ingredients": ["김치", "김치", "두부"],
            "sauces": ["간장"],
        }
    }
    result = _normalize_ingredients(state)
    assert result["normalized_input"]["ingredients"] == ["김치", "두부"]


def test_search_node_fallback_on_ddg_error(monkeypatch):
    def raise_on_init(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr("app.agents.trendy_recipe_agent.DDGS", raise_on_init)

    state = _base_normalized_state()
    result = _search_trending_recipes(state)
    assert result["search_context"] == ""


def test_search_node_builds_context(monkeypatch):
    fake_results = [
        {"title": "마약 계란장조림", "body": "SNS에서 유행하는 레시피"},
        {"title": "버터 감자조림", "body": "틱톡에서 인기"},
    ]

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def text(self, query, max_results=3):
            return fake_results

    monkeypatch.setattr("app.agents.trendy_recipe_agent.DDGS", FakeDDGS)

    state = _base_normalized_state()
    result = _search_trending_recipes(state)
    assert "마약 계란장조림" in result["search_context"]
    assert "버터 감자조림" in result["search_context"]


def test_validate_normalizes_trendy_categories():
    state = {
        **_base_normalized_state(),
        "llm_text": """
        {
          "trendy": [
            {
              "name": "마약 계란장조림",
              "difficulty": 9,
              "ingredients": ["계란", "간장"],
              "ingredient_amounts": {"계란": "4개", "간장": "4큰술"},
              "missing_ingredients": [],
              "steps": ["1. 계란을 삶는다.", "2) 간장에 절인다."]
            }
          ],
          "sns": []
        }
        """,
    }

    result = _validate_recipes(state)
    recipe = result["recipes"]["trendy"][0]

    assert recipe["name"] == "마약 계란장조림"
    assert recipe["difficulty"] == 5
    assert recipe["time"] == "20분"
    assert recipe["steps"] == ["계란을 삶는다.", "간장에 절인다."]


def test_validate_limits_to_three_per_category():
    items = [
        {
            "name": f"레시피{i}",
            "difficulty": 2,
            "ingredients": ["김치"],
            "steps": ["조리한다"],
        }
        for i in range(5)
    ]
    state = {
        **_base_normalized_state(),
        "llm_text": f'{{"trendy": {__import__("json").dumps(items, ensure_ascii=False)}, "sns": {__import__("json").dumps(items, ensure_ascii=False)}}}',
    }

    result = _validate_recipes(state)
    assert len(result["recipes"]["trendy"]) == 3
    assert len(result["recipes"]["sns"]) == 3


def test_validate_raises_on_empty_recipes():
    state = {
        **_base_normalized_state(),
        "llm_text": '{"trendy": [], "sns": []}',
    }
    with pytest.raises(TrendyRecipeGenerationError, match="레시피 후보가 없습니다"):
        _validate_recipes(state)


def test_endpoint_400_on_no_ingredients():
    client = TestClient(main.app)
    response = client.post("/recipes/generate/trendy", json={})
    assert response.status_code == 400
    assert "재료" in response.json()["detail"]


def test_endpoint_returns_trendy_and_sns(monkeypatch):
    def fake_generate(payload):
        assert "김치" in payload["ingredients"]
        return {
            "trendy": [
                {
                    "name": "마약 계란장조림",
                    "difficulty": 2,
                    "time": "20분",
                    "summary": "SNS 유행 레시피",
                    "ingredients": ["계란", "간장"],
                    "ingredient_amounts": {"계란": "4개", "간장": "4큰술"},
                    "missing_ingredients": [],
                    "steps": ["계란을 삶는다", "간장에 절인다"],
                    "youtube_query": "마약 계란장조림 레시피",
                }
            ],
            "sns": [],
        }

    monkeypatch.setattr(main, "generate_trendy_recipes", fake_generate)
    client = TestClient(main.app)

    response = client.post("/recipes/generate/trendy", json={"ingredients": ["김치"]})

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"trendy", "sns"}
    assert body["trendy"][0]["name"] == "마약 계란장조림"


def test_endpoint_503_on_llm_error(monkeypatch):
    def fake_generate(payload):
        raise TrendyRecipeGenerationError("LLM 오류가 발생했습니다")

    monkeypatch.setattr(main, "generate_trendy_recipes", fake_generate)
    client = TestClient(main.app)

    response = client.post("/recipes/generate/trendy", json={"ingredients": ["김치"]})

    assert response.status_code == 503
