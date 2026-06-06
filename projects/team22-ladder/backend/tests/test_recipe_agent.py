from app.recipe_agent import _looks_like_forced_combo, _parse_json_object, _validate_recipes


def test_validate_recipes_normalizes_missing_fields():
    state = {
        "normalized_input": {
            "ingredients": ["김치"],
            "required_ingredients": [],
            "expiring_ingredients": [],
            "sauces": ["간장"],
            "tools": [],
            "extra_ingredients": [],
        },
        "llm_text": """
        {
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
            "tools": [],
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
            "tools": [],
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
