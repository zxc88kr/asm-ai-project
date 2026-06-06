import json
import os
from typing import Any, TypedDict

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS  # type: ignore[no-redef]

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.utils.recipe_utils import (
    _dedupe_recipes,
    _normalize_recipe,
    _parse_json_object,
    _unique,
)


class TrendyRecipeGenerationError(RuntimeError):
    pass


class TrendyRecipeState(TypedDict, total=False):
    raw_input: dict[str, Any]
    normalized_input: dict[str, list[str]]
    search_context: str
    llm_text: str
    recipes: dict[str, list[dict[str, Any]]]


RECIPE_CATEGORIES = ("trendy", "sns")
RECIPES_PER_CATEGORY = 3


def generate_trendy_recipes(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    graph = _build_graph()
    result = graph.invoke({"raw_input": payload})
    return result["recipes"]


def _build_graph():
    graph = StateGraph(TrendyRecipeState)
    graph.add_node("normalize_ingredients", _normalize_ingredients)
    graph.add_node("search_trending_recipes", _search_trending_recipes)
    graph.add_node("generate_recipe_candidates", _generate_recipe_candidates)
    graph.add_node("validate_recipes", _validate_recipes)

    graph.set_entry_point("normalize_ingredients")
    graph.add_edge("normalize_ingredients", "search_trending_recipes")
    graph.add_edge("search_trending_recipes", "generate_recipe_candidates")
    graph.add_edge("generate_recipe_candidates", "validate_recipes")
    graph.add_edge("validate_recipes", END)
    return graph.compile()


def _normalize_ingredients(state: TrendyRecipeState) -> TrendyRecipeState:
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
        raise TrendyRecipeGenerationError("레시피 생성을 위한 재료가 없습니다.")

    return {**state, "normalized_input": normalized}


def _search_trending_recipes(state: TrendyRecipeState) -> TrendyRecipeState:
    normalized = state["normalized_input"]
    primary = _pick_primary_ingredients(normalized, max_count=3)

    queries = [
        f"{' '.join(primary)} 트렌디 레시피 인스타그램 SNS",
        "요즘 유행하는 한국 레시피 냉장고를 부탁해 트렌드",
    ]

    snippets: list[str] = []
    try:
        with DDGS() as ddgs:
            for query in queries:
                results = ddgs.text(query, max_results=3)
                for r in (results or []):
                    title = str(r.get("title", "")).strip()
                    body = str(r.get("body", "")).strip()
                    if body:
                        snippets.append(f"- {title}: {body}" if title else f"- {body}")
    except Exception:
        pass

    return {**state, "search_context": "\n".join(snippets)}


def _generate_recipe_candidates(state: TrendyRecipeState) -> TrendyRecipeState:
    api_key = os.getenv("UPSTAGE_API_KEY", "").strip()
    if not api_key:
        raise TrendyRecipeGenerationError("UPSTAGE_API_KEY가 설정되어 있지 않습니다.")

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1",
        model=os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3"),
        temperature=0.7,
    )

    search_context = state.get("search_context", "")
    if search_context:
        search_section = f"[실시간 트렌드 검색 결과]\n{search_context}\n\n"
    else:
        search_section = "[참고] 실시간 검색 결과를 가져오지 못했습니다. 일반적으로 알려진 트렌드 레시피를 추천하세요.\n\n"

    human_content = search_section + json.dumps(
        state["normalized_input"],
        ensure_ascii=False,
        indent=2,
    )

    messages = [
        SystemMessage(content=_system_prompt()),
        HumanMessage(content=human_content),
    ]
    response = llm.invoke(messages)
    llm_text = response.content

    try:
        _parse_json_object(llm_text, TrendyRecipeGenerationError)
    except TrendyRecipeGenerationError:
        repair_response = llm.invoke(
            [
                SystemMessage(content=_json_repair_prompt()),
                HumanMessage(content=llm_text),
            ]
        )
        llm_text = repair_response.content

    return {**state, "llm_text": llm_text}


def _validate_recipes(state: TrendyRecipeState) -> TrendyRecipeState:
    parsed = _parse_json_object(state.get("llm_text", ""), TrendyRecipeGenerationError)
    if not isinstance(parsed, dict):
        raise TrendyRecipeGenerationError("레시피 생성 결과를 JSON으로 해석하지 못했습니다.")

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
        recipes[category] = _dedupe_recipes(normalized_items)[:RECIPES_PER_CATEGORY]

    if not any(recipes.values()):
        raise TrendyRecipeGenerationError("생성된 레시피 후보가 없습니다.")

    return {**state, "recipes": recipes}


def _pick_primary_ingredients(normalized: dict[str, list[str]], max_count: int) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for key in ("required_ingredients", "expiring_ingredients", "ingredients"):
        for item in normalized.get(key, []):
            if item not in seen:
                result.append(item)
                seen.add(item)
            if len(result) >= max_count:
                return result
    return result


def _system_prompt() -> str:
    return """
너는 SNS 트렌드 레시피 큐레이터다.
인스타그램, 틱톡, 유튜브 쇼츠, 냉장고를 부탁해 같은 TV 예능, 맛집 유튜버 사이에서 실제로 유행하는 레시피만 추천한다.

규칙:
- [실시간 트렌드 검색 결과]가 제공되면 그 내용을 최우선으로 반영한다.
- required_ingredients와 expiring_ingredients를 우선 활용하는 트렌드 레시피를 선택한다.
- trendy: TV 예능·유명 셰프·바이럴 유튜브에서 검증된 요즘 트렌드 레시피 3개 (예: 마약 계란장조림, 버터 간장 감자, 에어프라이어 닭볶음탕 등)
- sns: 인스타그램·틱톡에서 비주얼과 간편함으로 유행하는 레시피 3개 (예: 그릭 요거트 볼, 토스트 아트, 오트밀 컵케이크 등)
- trendy와 sns 안에서 같은 메뉴를 이름만 바꿔 반복하지 않는다.
- 재료명을 이어 붙인 메뉴명은 금지한다. 실제 유행하는 레시피 이름을 사용한다.
- 트렌드 레시피에 필요하지만 없는 재료는 missing_ingredients에 표시하고 레시피 이름은 유지한다.
- 부족한 재료는 missing_ingredients에만 분리해서 적는다.
- 모든 ingredients에 대해 1인분 기준의 필요한 양을 ingredient_amounts에 적는다.
- ingredient_amounts의 key는 ingredients의 재료명과 정확히 같아야 한다.
- 무게나 부피로 확실히 표현할 수 있는 재료는 g 또는 ml를 우선 사용한다.
- 달걀, 두부, 대파처럼 관용 단위가 더 자연스러운 재료는 개, 모, 대 등을 사용할 수 있다.
- missing_ingredients에는 양을 붙이지 말고 재료명만 적는다.
- steps에는 "1.", "2)", "첫째," 같은 번호나 순서 접두어를 붙이지 말고 조리 문장만 적는다.
- 알레르기, 질병, 식단 제한, 건강 효능을 단정하지 않는다.
- 실제 YouTube 링크 대신 youtube_query 검색어만 만든다.

반드시 아래 JSON 객체만 출력하고, 코드블록이나 설명 문장을 붙이지 마라.
{
  "trendy": [
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
  "sns": []
}

trendy는 정확히 3개를 생성한다.
sns는 SNS 비주얼 레시피가 자연스러우면 정확히 3개, 어울리지 않으면 빈 배열로 둔다.
""".strip()


def _json_repair_prompt() -> str:
    return """
너는 깨진 JSON을 고치는 변환기다.
입력된 텍스트의 의미와 필드 값은 유지하고 JSON 문법만 고쳐라.
출력은 반드시 파싱 가능한 JSON 객체 하나만 반환한다.
코드블록, 설명, 사과, 주석은 절대 붙이지 마라.
최상위 키는 trendy와 sns만 사용한다.
""".strip()
