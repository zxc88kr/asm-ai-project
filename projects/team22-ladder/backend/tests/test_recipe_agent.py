from app.recipe_agent import (
    _active_recipe_categories,
    _attach_youtube_videos,
    _extract_youtube_video_from_html,
    _append_log,
    _looks_like_forced_combo,
    _normalize_ingredients,
    _parse_json_object,
    _select_recipe_categories,
    _validate_recipes,
)


def test_append_log_prints_to_terminal(capsys):
    result = _append_log({"logs": []}, "재료 정리 시작")

    captured = capsys.readouterr()

    assert result["logs"] == ["재료 정리 시작"]
    assert "[recipe_agent] 재료 정리 시작" in captured.out


def test_validate_recipes_normalizes_missing_fields():
    state = {
        "normalized_input": {
            "ingredients": ["김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": ["간장"],
            "tools": ["전자레인지"],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
          "top_recipes": [],
          "beginner": [
            {
              "name": "김치무침",
              "difficulty": 9,
              "ingredients": ["김치", "참기름"],
              "ingredient_amounts": {"김치": "100g", "참기름": "5ml", "없는재료": "1개"},
              "missing_ingredients": ["김치 100g", "참기름 5ml"],
              "steps": ["1. 김치를 썬다.", "2) 참기름을 넣는다.", "첫째, 그릇에 담는다."]
            }
          ],
          "microwave": []
        }
        """,
    }

    result = _validate_recipes(state)
    recipe = result["recipes"]["beginner"][0]

    assert recipe["difficulty"] == 5
    assert recipe["time"] == "20분"
    assert recipe["summary"] == "김치무침"
    assert recipe["ingredient_amounts"] == {"김치": "100g", "참기름": "5ml"}
    assert recipe["missing_ingredients"] == ["참기름"]
    assert recipe["steps"] == ["김치를 썬다.", "참기름을 넣는다.", "그릇에 담는다."]
    assert recipe["youtube_query"] == "김치무침 김치 참기름 레시피"


def test_validate_recipes_splits_amounts_from_ingredient_names():
    state = {
        "normalized_input": {
            "ingredients": ["김치", "두부"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": ["간장"],
            "tools": ["전자레인지"],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
          "beginner": [
            {
              "name": "김치두부조림",
              "ingredients": ["김치 100g", "두부 1/2모", "간장 15ml", "물 100ml"],
              "ingredient_amounts": {
                "김치 100g": "100g",
                "두부 1/2모": "1/2모",
                "간장 15ml": "15ml",
                "물 100ml": "100ml"
              },
              "missing_ingredients": ["김치 100g", "물 100ml"]
            }
          ],
          "microwave": []
        }
        """,
    }

    result = _validate_recipes(state)
    recipe = result["recipes"]["beginner"][0]

    assert recipe["ingredients"] == ["김치", "두부", "간장", "물"]
    assert recipe["ingredient_amounts"] == {
        "김치": "100g",
        "두부": "1/2모",
        "간장": "15ml",
        "물": "100ml",
    }
    assert recipe["missing_ingredients"] == ["물"]


def test_parse_json_repairs_missing_comma_between_sections():
    parsed = _parse_json_object(
        """
        {
          "beginner": [
            {"name": "김치볶음밥", "ingredients": ["김치"]}
          ]
          "microwave": []
        }
        """
    )

    assert parsed["beginner"][0]["name"] == "김치볶음밥"
    assert parsed["microwave"] == []


def test_validate_recipes_filters_forced_ingredient_combo_names():
    state = {
        "normalized_input": {
            "ingredients": ["김치", "두부", "목살", "계란", "양파", "마늘"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": [],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
          "beginner": [
            {"name": "김치볶음밥", "ingredients": ["김치", "밥"]},
            {"name": "계란두부김치전", "ingredients": ["계란", "두부", "김치"]},
            {"name": "두부김치", "ingredients": ["두부", "김치"]},
            {"name": "김치두부된장국", "ingredients": ["김치", "두부", "된장"]}
          ],
          "microwave": []
        }
        """,
    }

    result = _validate_recipes(state)
    names = [recipe["name"] for recipe in result["recipes"]["beginner"]]

    assert names == ["김치볶음밥", "두부김치"]


def test_forced_combo_detection_keeps_common_recipe_exception():
    owned = {"김치", "두부", "계란"}

    assert _looks_like_forced_combo("계란두부김치찜", owned) is True
    assert _looks_like_forced_combo("두부김치", owned) is False


def test_validate_recipes_dedupes_and_filters_microwave_category():
    state = {
        "normalized_input": {
            "ingredients": ["계란", "두부", "김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": ["전자레인지"],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
          "beginner": [],
          "microwave": [
            {
              "name": "계란찜",
              "ingredients": ["계란", "물"],
              "steps": ["전자레인지용 그릇에 넣고 익힌다"]
            },
            {
              "name": "계란찜 (다시)",
              "ingredients": ["계란", "물"],
              "steps": ["전자레인지로 다시 익힌다"]
            },
            {
              "name": "두부김치",
              "ingredients": ["두부", "김치"],
              "steps": ["팬에 김치를 볶는다"]
            }
          ]
        }
        """,
    }

    result = _validate_recipes(state)

    assert [recipe["name"] for recipe in result["recipes"]["microwave"]] == ["계란찜"]


def test_validate_recipes_matches_prepared_owned_ingredient_names():
    state = {
        "normalized_input": {
            "ingredients": ["두부", "양파"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": [],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
          "beginner": [
            {
              "name": "두부조림",
              "ingredients": ["다진 두부", "채 썬 양파", "간장"],
              "ingredient_amounts": {"다진 두부": "1/2모", "채 썬 양파": "50g", "간장": "1큰술"},
              "missing_ingredients": ["다진 두부", "채 썬 양파", "간장"]
            }
          ],
          "microwave": []
        }
        """,
    }

    result = _validate_recipes(state)
    recipe = result["recipes"]["beginner"][0]

    assert recipe["ingredients"] == ["두부", "양파", "간장"]
    assert recipe["missing_ingredients"] == ["간장"]


def test_validate_recipes_limits_each_category_to_three():
    recipes = ",".join(
        f'{{"name": "김치볶음밥 {idx}", "ingredients": ["김치", "밥"]}}'
        for idx in range(5)
    )
    state = {
        "normalized_input": {
            "ingredients": ["김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": ["전자레인지"],
            "extra_ingredients": [],
        },
        "llm_text": f"""
        {{
          "beginner": [{recipes}],
          "microwave": [{recipes}]
        }}
        """,
    }

    result = _validate_recipes(state)

    assert len(result["recipes"]["beginner"]) == 3
    assert len(result["recipes"]["microwave"]) == 3


def test_validate_recipes_normalizes_top_recipes_to_five():
    recipes = ",".join(
        f'{{"name": "김치볶음밥 {idx}", "ingredients": ["김치", "밥"]}}'
        for idx in range(7)
    )
    state = {
        "normalized_input": {
            "ingredients": ["김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": [],
            "extra_ingredients": [],
        },
        "llm_text": f"""
        {{
          "top_recipes": [{recipes}],
          "beginner": []
        }}
        """,
        "logs": ["재료 정리 완료"],
    }

    result = _validate_recipes(state)

    assert len(result["top_recipes"]) == 5
    assert "JSON 파싱/정규화 완료" in result["logs"]


def test_active_recipe_categories_depend_on_tools():
    base = {
        "ingredients": ["김치"],
        "required_ingredients": [],
        "expiring_ingredients": [],
        "sauces": [],
        "tools": [],
        "extra_ingredients": [],
    }

    without_tools = _active_recipe_categories(base)
    with_tools = _active_recipe_categories({**base, "tools": ["전자레인지"]})

    assert "microwave" not in without_tools
    assert "microwave" in with_tools
    assert "air_fryer" not in with_tools


def test_select_recipe_categories_limits_generation_scope(monkeypatch):
    monkeypatch.setattr("app.recipe_agent.random.sample", lambda values, count: list(values)[:count])

    selected = _select_recipe_categories([
        "beginner",
        "microwave",
        "korean_home",
        "soup_stew",
        "stir_fry",
    ])

    assert selected == ["beginner", "microwave", "korean_home"]


def test_normalize_ingredients_stores_selected_category_meta(monkeypatch):
    monkeypatch.setattr("app.recipe_agent.random.sample", lambda values, count: list(values)[:count])

    result = _normalize_ingredients(
        {
            "raw_input": {
                "ingredients": ["김치"],
                "tools": ["전자레인지"],
            },
            "logs": [],
        }
    )

    assert list(result["category_meta"].keys()) == ["beginner", "microwave", "korean_home"]
    assert "추천 카테고리 선정 완료: 초보 요리사 추천, 전자레인지 간편 요리, 한식 집밥" in result["logs"]


def test_validate_recipes_only_keeps_selected_categories():
    state = {
        "normalized_input": {
            "ingredients": ["김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": [],
            "tools": [],
            "extra_ingredients": [],
        },
        "category_meta": {"beginner": {"label": "초보 요리사 추천"}},
        "llm_text": """
        {
          "top_recipes": [],
          "beginner": [{"name": "김치볶음밥", "ingredients": ["김치", "밥"]}],
          "soup_stew": [{"name": "김치찌개", "ingredients": ["김치", "물"]}]
        }
        """,
    }

    result = _validate_recipes(state)

    assert set(result["recipes"].keys()) == {"beginner"}
    assert result["recipes"]["beginner"][0]["category_label"] == "초보 요리사 추천"


def test_attach_youtube_videos_ignores_lookup_failure(monkeypatch):
    envelope = {
        "top_recipes": [{"name": "김치볶음밥", "youtube_query": "김치볶음밥 레시피"}],
        "recipes": {},
        "category_meta": {},
        "logs": [],
    }

    def fail_lookup(api_key, query):
        raise RuntimeError("youtube down")

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    monkeypatch.setattr("app.recipe_agent._fetch_youtube_video", fail_lookup)

    result = _attach_youtube_videos(envelope)

    assert result["top_recipes"][0]["name"] == "김치볶음밥"
    assert "youtube_video" not in result["top_recipes"][0]
    assert "YouTube 영상 조회 실패" in result["logs"][0]


def test_attach_youtube_videos_adds_thumbnail(monkeypatch):
    envelope = {
        "top_recipes": [{"name": "김치볶음밥", "youtube_query": "김치볶음밥 레시피"}],
        "recipes": {},
        "category_meta": {},
        "logs": [],
    }

    def fake_lookup(api_key, query):
        return {
            "title": "김치볶음밥 만들기",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "url": "https://www.youtube.com/watch?v=abc",
        }

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    monkeypatch.setattr("app.recipe_agent._fetch_youtube_video", fake_lookup)

    result = _attach_youtube_videos(envelope)

    assert result["top_recipes"][0]["youtube_video"]["thumbnail_url"] == "https://example.com/thumb.jpg"


def test_attach_youtube_videos_continues_after_lookup_failure(monkeypatch):
    envelope = {
        "top_recipes": [
            {"name": "김치볶음밥", "youtube_query": "김치볶음밥 레시피"},
            {"name": "계란찜", "youtube_query": "계란찜 레시피"},
        ],
        "recipes": {},
        "category_meta": {},
        "logs": [],
    }
    calls = []

    def lookup(api_key, query):
        calls.append(query)
        if len(calls) == 1:
            raise RuntimeError("youtube down")
        return {
            "title": "계란찜 만들기",
            "thumbnail_url": "https://example.com/egg.jpg",
            "url": "https://www.youtube.com/watch?v=egg",
        }

    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    monkeypatch.setattr("app.recipe_agent._fetch_youtube_video", lookup)

    result = _attach_youtube_videos(envelope)

    assert "youtube_video" not in result["top_recipes"][0]
    assert result["top_recipes"][1]["youtube_video"]["thumbnail_url"] == "https://example.com/egg.jpg"


def test_extract_youtube_video_from_html_uses_first_search_video():
    html = """
    {"videoId":"first123","title":{"runs":[{"text":"첫 번째 레시피"}]}}
    {"videoId":"second456","title":{"runs":[{"text":"두 번째 레시피"}]}}
    """

    result = _extract_youtube_video_from_html("김치볶음밥 레시피", html)

    assert result == {
        "title": "김치볶음밥 레시피",
        "thumbnail_url": "https://i.ytimg.com/vi/first123/hqdefault.jpg",
        "url": "https://www.youtube.com/watch?v=first123",
    }
