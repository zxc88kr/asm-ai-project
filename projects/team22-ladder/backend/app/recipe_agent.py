import json
import os
import re
from typing import Any, TypedDict


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.utils.recipe_utils import (
    _dedupe_recipes,
    _normalize_recipe,
    _normalize_recipe_name,
    _parse_json_object,
    _unique,
)


class RecipeGenerationError(RuntimeError):
    pass


class RecipeState(TypedDict, total=False):
    raw_input: dict[str, Any]
    normalized_input: dict[str, list[str]]
    llm_text: str
    recipes: dict[str, list[dict[str, Any]]]


RECIPE_CATEGORIES = ("beginner", "microwave")
RECIPES_PER_CATEGORY = 3

COMMON_RECIPE_NAMES = {
    "김치볶음밥",
    "김치찌개",
    "돼지고기 김치찌개",
    "참치김치찌개",
    "김치전",
    "김치부침개",
    "김치볶음",
    "두부김치",
    "두부조림",
    "두부부침",
    "두부찌개",
    "두부전골",
    "순두부찌개",
    "된장찌개",
    "계란찜",
    "계란말이",
    "계란볶음밥",
    "계란국",
    "달걀국",
    "계란장조림",
    "제육볶음",
    "돼지고기볶음",
    "돼지고기 두루치기",
    "돼지고기 숙주볶음",
    "돼지고기 양파볶음",
    "목살구이",
    "마늘목살구이",
    "양파볶음",
    "양파계란덮밥",
    "오므라이스",
    "볶음밥",
    "마늘볶음밥",
}


def generate_recipes(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    graph = _build_graph()
    result = graph.invoke({"raw_input": payload})
    return result["recipes"]


def _build_graph():
    graph = StateGraph(RecipeState)
    graph.add_node("normalize_ingredients", _normalize_ingredients)
    graph.add_node("generate_recipe_candidates", _generate_recipe_candidates)
    graph.add_node("validate_recipes", _validate_recipes)

    graph.set_entry_point("normalize_ingredients")
    graph.add_edge("normalize_ingredients", "generate_recipe_candidates")
    graph.add_edge("generate_recipe_candidates", "validate_recipes")
    graph.add_edge("validate_recipes", END)
    return graph.compile()


def _normalize_ingredients(state: RecipeState) -> RecipeState:
    raw = state["raw_input"]
    normalized = {
        "ingredients": _unique(raw.get("ingredients", [])),
        "required_ingredients": _unique(raw.get("required_ingredients", [])),
        "expiring_ingredients": _unique(raw.get("expiring_ingredients", [])),
        "sauces": _unique(raw.get("sauces", [])),
        "tools": _unique(raw.get("tools", [])),
        "extra_ingredients": _unique(raw.get("extra_ingredients", [])),
    }

    all_food = (
        normalized["ingredients"]
        + normalized["required_ingredients"]
        + normalized["expiring_ingredients"]
        + normalized["sauces"]
        + normalized["extra_ingredients"]
    )
    if not _unique(all_food):
        raise RecipeGenerationError("레시피 생성을 위한 재료가 없습니다.")

    return {**state, "normalized_input": normalized}


def _generate_recipe_candidates(state: RecipeState) -> RecipeState:
    api_key = os.getenv("UPSTAGE_API_KEY", "").strip()
    if not api_key:
        raise RecipeGenerationError("UPSTAGE_API_KEY가 설정되어 있지 않습니다.")

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1",
        model=os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3"),
        temperature=0.2,
    )

    messages = [
        SystemMessage(content=_system_prompt()),
        HumanMessage(
            content=json.dumps(
                state["normalized_input"],
                ensure_ascii=False,
                indent=2,
            )
        ),
    ]
    response = llm.invoke(messages)
    llm_text = response.content

    try:
        _parse_json_object(llm_text, RecipeGenerationError)
    except RecipeGenerationError:
        repair_response = llm.invoke(
            [
                SystemMessage(content=_json_repair_prompt()),
                HumanMessage(content=llm_text),
            ]
        )
        llm_text = repair_response.content

    return {**state, "llm_text": llm_text}


def _validate_recipes(state: RecipeState) -> RecipeState:
    parsed = _parse_json_object(state.get("llm_text", ""), RecipeGenerationError)
    if not isinstance(parsed, dict):
        raise RecipeGenerationError("레시피 생성 결과를 JSON으로 해석하지 못했습니다.")

    owned = set(
        state["normalized_input"]["ingredients"]
        + state["normalized_input"]["required_ingredients"]
        + state["normalized_input"]["expiring_ingredients"]
        + state["normalized_input"]["sauces"]
        + state["normalized_input"]["extra_ingredients"]
    )

    recipes: dict[str, list[dict[str, Any]]] = {}
    for category in RECIPE_CATEGORIES:
        raw_items = parsed.get(category, [])
        if not isinstance(raw_items, list):
            raw_items = []
        normalized_items = [
            _normalize_recipe(item, owned)
            for item in raw_items
            if isinstance(item, dict) and item.get("name")
        ]
        recipes[category] = _select_recipe_candidates(normalized_items, owned, category)[:RECIPES_PER_CATEGORY]

    if not any(recipes.values()):
        raise RecipeGenerationError("생성된 레시피 후보가 없습니다.")

    return {**state, "recipes": recipes}


def _select_recipe_candidates(
    recipes: list[dict[str, Any]],
    owned: set[str],
    category: str,
) -> list[dict[str, Any]]:
    if category == "microwave":
        microwave_recipes = [recipe for recipe in recipes if _uses_microwave(recipe)]
        if microwave_recipes:
            recipes = microwave_recipes

    safe_recipes = [recipe for recipe in recipes if not _looks_like_forced_combo(recipe["name"], owned)]
    if safe_recipes:
        return _dedupe_recipes(sorted(safe_recipes, key=_recipe_priority))
    return _dedupe_recipes(sorted(recipes, key=_recipe_priority))


def _uses_microwave(recipe: dict[str, Any]) -> bool:
    text = " ".join(
        [
            str(recipe.get("name", "")),
            str(recipe.get("summary", "")),
            *[str(step) for step in recipe.get("steps", [])],
        ]
    )
    return "전자레인지" in text


def _recipe_priority(recipe: dict[str, Any]) -> tuple[int, str]:
    return (0 if _normalize_recipe_name(recipe["name"]) in COMMON_RECIPE_NAMES else 1, recipe["name"])


def _looks_like_forced_combo(name: str, owned: set[str]) -> bool:
    normalized_name = _normalize_recipe_name(name)
    if normalized_name in COMMON_RECIPE_NAMES:
        return False

    compact_name = re.sub(r"\s+", "", normalized_name)
    matched_ingredients = {
        ingredient
        for ingredient in owned
        if len(ingredient) >= 2 and re.sub(r"\s+", "", ingredient) in compact_name
    }
    return len(matched_ingredients) >= 2


def _system_prompt() -> str:
    return """
너는 냉장고 재료 기반 레시피 생성 Agent다.
사용자가 가진 재료를 참고하되, 재료를 조합해서 새 메뉴를 만들지 말고 실제로 널리 먹는 전형적인 가정식/기본 조리법 중심 레시피를 추천한다.
트렌디한 퓨전, 과장된 메뉴명, 검증하기 어려운 조합, 실제로 흔하지 않은 재료 조합은 피한다.

규칙:
- required_ingredients는 가능한 한 반드시 사용하는 레시피를 우선 추천한다.
- expiring_ingredients는 자연스럽게 어울리는 전형적인 요리가 있을 때 우선 반영한다.
- 일반 보유 재료는 전형적인 레시피에 자연스럽게 맞을 때만 사용하고, 억지로 모두 넣지 않는다.
- 레시피 이름은 실제 요리책, 포털 검색, 유튜브에서 흔히 찾을 수 있는 표준 메뉴명처럼 작성한다.
- "김치두부밥", "계란두부김치찜", "계란두부김치전"처럼 보유 재료명을 이어 붙여 만든 메뉴명은 금지한다.
- 표준 메뉴를 만들기 위해 밥, 된장, 고추장, 대파, 고춧가루처럼 핵심 재료가 부족하면 그 재료를 missing_ingredients에 넣고 메뉴명은 표준 메뉴명으로 유지한다.
- 예를 들어 김치, 두부, 목살, 계란, 양파, 마늘이 있을 때는 김치볶음밥, 돼지고기 김치찌개, 두부조림, 두부김치, 계란찜, 계란말이, 제육볶음처럼 흔한 메뉴를 우선한다.
- 표준 메뉴에 원래 잘 들어가지 않는 보유 재료를 억지로 추가하지 않는다. 예: 김치볶음밥에 두부를 넣지 말고, 계란말이에 두부를 넣지 않는다.
- ingredients는 해당 표준 메뉴를 만드는 데 필요한 기본 재료만 적고, 보유 재료를 모두 소진하려는 방식으로 늘리지 않는다.
- ingredients와 ingredient_amounts의 key는 "다진 두부", "채 썬 양파"처럼 손질 상태를 붙이지 말고 "두부", "양파" 같은 기본 재료명으로 적는다.
- 전형적인 요리를 만들기 위해 필요한 기본 재료가 부족하면 missing_ingredients에 표시하고 레시피 후보로 유지한다.
- 부족한 재료는 missing_ingredients에만 분리해서 적는다.
- 모든 ingredients에 대해 1인분 기준의 필요한 양을 ingredient_amounts에 적는다.
- ingredient_amounts의 key는 ingredients의 재료명과 정확히 같아야 한다.
- 무게나 부피로 확실히 표현할 수 있는 재료는 g 또는 ml를 우선 사용한다.
- 달걀, 두부, 대파처럼 관용 단위가 더 자연스러운 재료는 개, 모, 대 등을 사용할 수 있다.
- 컵, 큰술, 작은술을 사용할 경우 각각 종이컵 1컵=180ml, 밥숟가락 1큰술=15ml, 티스푼 1작은술=5ml 기준으로 작성한다.
- missing_ingredients에는 양을 붙이지 말고 재료명만 적는다.
- steps에는 "1.", "2)", "첫째," 같은 번호나 순서 접두어를 붙이지 말고 조리 문장만 적는다.
- 사용 가능한 tools에 전자레인지가 있으면 microwave 카테고리에 전자레인지 요리를 포함한다.
- microwave 카테고리는 전자레인지로 끝까지 조리 가능한 레시피만 넣고, steps에 전자레인지 사용 문장을 반드시 포함한다.
- beginner와 microwave 안에서 같은 메뉴를 이름만 바꿔 반복하지 않는다.
- 알레르기, 질병, 식단 제한, 건강 효능을 단정하지 않는다.
- 실제 YouTube 링크 대신 youtube_query 검색어만 만든다.

반드시 아래 JSON 객체만 출력하고, 코드블록이나 설명 문장을 붙이지 마라.
{
  "beginner": [
    {
      "name": "요리명",
      "difficulty": 1,
      "time": "15분",
      "summary": "짧은 설명",
      "ingredients": ["필요 재료"],
      "ingredient_amounts": {"필요 재료": "1개"},
      "missing_ingredients": ["없는 재료"],
      "steps": ["1단계", "2단계", "3단계"],
      "youtube_query": "요리명 핵심재료 레시피"
    }
  ],
  "microwave": []
}

beginner는 정확히 3개, microwave는 전자레인지가 사용 가능하면 정확히 3개를 생성한다.
전자레인지 요리가 자연스럽지 않거나 tools에 전자레인지가 없으면 microwave는 빈 배열로 둔다.
""".strip()


def _json_repair_prompt() -> str:
    return """
너는 깨진 JSON을 고치는 변환기다.
입력된 텍스트의 의미와 필드 값은 유지하고 JSON 문법만 고쳐라.
출력은 반드시 파싱 가능한 JSON 객체 하나만 반환한다.
코드블록, 설명, 사과, 주석은 절대 붙이지 마라.
최상위 키는 beginner와 microwave만 사용한다.
""".strip()


