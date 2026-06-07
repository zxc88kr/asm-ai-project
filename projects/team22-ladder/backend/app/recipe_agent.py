import json
import os
import random
import re
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph


class RecipeGenerationError(RuntimeError):
    pass


MAX_RETRY = 2


class RecipeState(TypedDict, total=False):
    raw_input: dict[str, Any]
    normalized_input: dict[str, list[str]]
    llm_text: str
    top_recipes: list[dict[str, Any]]
    recipes: dict[str, list[dict[str, Any]]]
    validated_recipes: dict[str, list[dict[str, Any]]]
    final_recipes: dict[str, list[dict[str, Any]]]
    category_meta: dict[str, dict[str, str]]
    logs: list[str]
    retry_count: int


RECIPE_CATEGORIES = {
    "beginner": {"label": "초보 요리사 추천"},
    "microwave": {"label": "전자레인지 간편 요리", "required_tool": "전자레인지"},
    "korean_home": {"label": "한식 집밥"},
    "soup_stew": {"label": "국/찌개"},
    "stir_fry": {"label": "볶음요리"},
    "rice_bowl": {"label": "덮밥/밥요리"},
    "noodle": {"label": "면요리"},
    "side_dish": {"label": "반찬"},
    "diet": {"label": "다이어트식"},
    "high_protein": {"label": "고단백"},
    "late_night": {"label": "야식"},
    "lunchbox": {"label": "도시락"},
    "snack_drink": {"label": "술안주"},
    "kid_friendly": {"label": "아이용"},
    "quick_15": {"label": "15분 요리"},
    "solo": {"label": "자취요리"},
    "fine_dining": {"label": "파인다이닝식"},
    "guest_table": {"label": "손님상"},
    "leftover": {"label": "남은재료 처리"},
}
TOP_RECIPES_LIMIT = 5
RECIPES_PER_CATEGORY = 3
RECIPE_FIELDS = {
    "name": "",
    "difficulty": 1,
    "time": "20분",
    "summary": "",
    "ingredients": [],
    "ingredient_amounts": {},
    "missing_ingredients": [],
    "steps": [],
    "youtube_query": "",
}

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


def generate_recipes(payload: dict[str, Any]) -> dict[str, Any]:
    graph = _build_graph()
    result = graph.invoke({"raw_input": payload, "logs": []})
    top_recipes = result.get("top_recipes", [])[:TOP_RECIPES_LIMIT]
    recipes = result.get("final_recipes", {})
    envelope = {
        "top_recipes": top_recipes,
        "recipes": recipes,
        "category_meta": result.get("category_meta", {}),
        "logs": result.get("logs", []),
    }
    return _attach_youtube_videos(envelope)


def _attach_youtube_videos(envelope: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        _append_envelope_log(envelope, "YouTube API 키가 없어 영상 썸네일 조회를 건너뜀")
        return envelope

    for recipe in _iter_all_recipe_entries(envelope):
        query = str(recipe.get("youtube_query", "")).strip()
        if not query:
            continue
        try:
            if not recipe.get("youtube_video"):
                video = _fetch_youtube_video(api_key, query)
                if video:
                    recipe["youtube_video"] = video
                    _append_envelope_log(envelope, f"YouTube 영상 조회 완료: {recipe.get('name', query)}")
        except Exception as exc:
            _append_envelope_log(
                envelope,
                f"YouTube 영상 조회 실패: {recipe.get('name', query)} ({exc.__class__.__name__})",
            )
    return envelope


def _append_envelope_log(envelope: dict[str, Any], message: str) -> None:
    logs = envelope.setdefault("logs", [])
    if isinstance(logs, list):
        logs.append(message)
    print(f"[recipe_agent] {message}", flush=True)


def _iter_all_recipe_entries(envelope: dict[str, Any]):
    for recipe in envelope.get("top_recipes", []) or []:
        if isinstance(recipe, dict):
            yield recipe
    recipes = envelope.get("recipes", {})
    if not isinstance(recipes, dict):
        return
    for items in recipes.values():
        for recipe in items or []:
            if isinstance(recipe, dict):
                yield recipe


def _fetch_youtube_video(api_key: str, query: str) -> dict[str, str] | None:
    if api_key:
        video = _fetch_youtube_video_from_api(api_key, query)
        if video:
            return video
    return _fetch_youtube_video_from_search_page(query)


def _fetch_youtube_video_from_api(api_key: str, query: str) -> dict[str, str] | None:
    params = urlencode(
        {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": "1",
            "order": "relevance",
            "regionCode": "KR",
            "relevanceLanguage": "ko",
            "safeSearch": "none",
            "key": api_key,
        }
    )
    with urlopen(f"https://www.googleapis.com/youtube/v3/search?{params}", timeout=4) as response:
        data = json.loads(response.read().decode("utf-8"))
    items = data.get("items") or []
    if not items:
        return None
    item = items[0]
    video_id = item.get("id", {}).get("videoId")
    snippet = item.get("snippet", {})
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = (
        thumbnails.get("medium", {})
        or thumbnails.get("default", {})
        or thumbnails.get("high", {})
    ).get("url")
    if not video_id or not thumbnail:
        return None
    return {
        "title": str(snippet.get("title", "")).strip(),
        "thumbnail_url": thumbnail,
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def _fetch_youtube_video_from_search_page(query: str) -> dict[str, str] | None:
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=6) as response:
        html = response.read().decode("utf-8", errors="ignore")
    return _extract_youtube_video_from_html(query, html)


def _extract_youtube_video_from_html(query: str, html: str) -> dict[str, str] | None:
    match = re.search(r'"videoId":"([^"]+)"', html)
    if not match:
        return None
    video_id = match.group(1)
    return {
        "title": query,
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def _build_graph():
    graph = StateGraph(RecipeState)
    graph.add_node("normalize_ingredients", _normalize_ingredients)
    graph.add_node("generate_recipe_candidates", _generate_recipe_candidates)
    graph.add_node("validate_recipes", _validate_recipes)
    graph.add_node("llm_validate_recipes", _llm_validate_recipes)
    graph.add_node("llm_select_final_recipes", _llm_select_final_recipes)

    graph.set_entry_point("normalize_ingredients")
    graph.add_edge("normalize_ingredients", "generate_recipe_candidates")
    graph.add_edge("generate_recipe_candidates", "validate_recipes")
    graph.add_edge("validate_recipes", "llm_validate_recipes")
    graph.add_edge("llm_validate_recipes", "llm_select_final_recipes")
    graph.add_conditional_edges(
        "llm_select_final_recipes",
        _route_after_selection,
        {"retry": "generate_recipe_candidates", "done": END},
    )
    return graph.compile()


def _route_after_selection(state: RecipeState) -> str:
    final = state.get("final_recipes", {})
    has_recipes = bool(state.get("top_recipes")) or any(final.get(cat) for cat in final)
    retry_count = state.get("retry_count", 0)
    if not has_recipes and retry_count < MAX_RETRY:
        return "retry"
    return "done"


def _normalize_ingredients(state: RecipeState) -> RecipeState:
    state = _append_log(state, "재료 정리 시작")
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

    active_categories = _active_recipe_categories(normalized)
    selected_categories = _select_recipe_categories(active_categories)
    category_meta = {
        key: {"label": RECIPE_CATEGORIES[key]["label"]}
        for key in selected_categories
    }
    state = _append_log(
        {**state, "normalized_input": normalized, "category_meta": category_meta},
        "재료 정리 완료",
    )
    selected_labels = ", ".join(meta["label"] for meta in category_meta.values())
    return _append_log(state, f"추천 카테고리 선정 완료: {selected_labels}")


def _generate_recipe_candidates(state: RecipeState) -> RecipeState:
    state = _append_log(state, "레시피 후보 생성 시작")
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
        SystemMessage(
            content=_system_prompt(
                state["normalized_input"],
                _selected_recipe_categories(state),
            )
        ),
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
        _parse_json_object(llm_text)
    except RecipeGenerationError:
        repair_response = llm.invoke(
            [
                SystemMessage(content=_json_repair_prompt()),
                HumanMessage(content=llm_text),
            ]
        )
        llm_text = repair_response.content

    return _append_log({**state, "llm_text": llm_text}, "레시피 후보 생성 완료")


def _validate_recipes(state: RecipeState) -> RecipeState:
    parsed = _parse_json_object(state.get("llm_text", ""))
    if not isinstance(parsed, dict):
        raise RecipeGenerationError("레시피 생성 결과를 JSON으로 해석하지 못했습니다.")

    owned = set(
        state["normalized_input"]["ingredients"]
        + state["normalized_input"]["required_ingredients"]
        + state["normalized_input"]["expiring_ingredients"]
        + state["normalized_input"]["sauces"]
        + state["normalized_input"]["extra_ingredients"]
    )

    top_items = parsed.get("top_recipes", [])
    if not isinstance(top_items, list):
        top_items = []
    top_recipes = _select_recipe_candidates(
        [
            _normalize_recipe(item, owned)
            for item in top_items
            if isinstance(item, dict) and item.get("name")
        ],
        owned,
        "top_recipes",
    )[:TOP_RECIPES_LIMIT]

    active_categories = _selected_recipe_categories(state)
    recipes: dict[str, list[dict[str, Any]]] = {}
    for category in active_categories:
        raw_items = parsed.get(category, [])
        if not isinstance(raw_items, list):
            raw_items = []
        normalized_items = [
            _normalize_recipe(item, owned)
            for item in raw_items
            if isinstance(item, dict) and item.get("name")
        ]
        normalized_items = [
            _tag_recipe_category(item, category)
            for item in normalized_items
        ]
        recipes[category] = _select_recipe_candidates(normalized_items, owned, category)[:RECIPES_PER_CATEGORY]

    if not top_recipes and not any(recipes.values()):
        raise RecipeGenerationError("생성된 레시피 후보가 없습니다.")

    return _append_log({**state, "top_recipes": top_recipes, "recipes": recipes}, "JSON 파싱/정규화 완료")


def _llm_validate_recipes(state: RecipeState) -> RecipeState:
    """Agent 3: LLM이 각 레시피가 보유 재료로 실제로 만들 수 있는지 검증한다."""
    api_key = os.getenv("UPSTAGE_API_KEY", "").strip()
    if not api_key:
        return _append_log({**state, "validated_recipes": state["recipes"]}, "LLM 검증 완료")

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1",
        model=os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3"),
        temperature=0.0,
    )

    norm = state["normalized_input"]
    owned = list(set(
        norm["ingredients"]
        + norm["required_ingredients"]
        + norm["expiring_ingredients"]
        + norm["sauces"]
        + norm["extra_ingredients"]
    ))

    candidates = state["recipes"]
    all_recipes = []
    for category, items in candidates.items():
        for recipe in items:
            all_recipes.append({"category": category, **recipe})

    if not all_recipes:
        return _append_log({**state, "validated_recipes": candidates}, "LLM 검증 완료")

    prompt = f"""
너는 레시피 검증 Agent다.
사용자가 보유한 재료와 레시피 후보 목록이 주어진다.
각 레시피에 대해 missing_ingredients에 있는 재료를 제외하고,
보유 재료만으로 실제로 요리를 완성할 수 있는지 판단한다.

판단 기준:
- missing_ingredients가 없으면 "valid"
- missing_ingredients가 있어도 핵심 재료(예: 밥, 물, 소금 등 구하기 쉬운 것)만 없으면 "valid"
- 레시피의 핵심 재료가 누락되어 요리 자체가 불가능하면 "invalid"
- 레시피 이름에 재료명을 억지로 조합한 비현실적인 메뉴(예: 계란두부김치찜)면 "invalid"

보유 재료: {json.dumps(owned, ensure_ascii=False)}
레시피 후보:
{json.dumps(all_recipes, ensure_ascii=False, indent=2)}

반드시 아래 JSON 배열만 출력하고 설명을 붙이지 마라.
각 항목은 레시피 후보 순서와 동일하게 "valid" 또는 "invalid"만 포함한다.
[{{"name": "레시피명", "verdict": "valid"}}, ...]
""".strip()

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        verdicts = _parse_verdict_list(response.content, all_recipes)
    except Exception:
        return _append_log({**state, "validated_recipes": candidates}, "LLM 검증 완료")

    validated: dict[str, list[dict[str, Any]]] = {cat: [] for cat in candidates}
    for recipe, verdict in zip(all_recipes, verdicts):
        if verdict == "valid":
            category = recipe["category"]
            entry = {k: v for k, v in recipe.items() if k != "category"}
            validated[category].append(entry)

    # 검증 후 카테고리가 비면 원본 후보를 그대로 사용 (fallback)
    for category in candidates:
        if not validated[category]:
            validated[category] = candidates[category]

    return _append_log({**state, "validated_recipes": validated}, "LLM 검증 완료")


def _llm_select_final_recipes(state: RecipeState) -> RecipeState:
    """Agent 4: 검증된 후보 중 사용자 재료 활용도·다양성 기준으로 최종 레시피를 선정한다."""
    api_key = os.getenv("UPSTAGE_API_KEY", "").strip()
    if not api_key:
        return _append_log({**state, "final_recipes": state["validated_recipes"]}, "최종 추천 선정 완료")

    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.upstage.ai/v1",
        model=os.getenv("UPSTAGE_SOLAR_MODEL", "solar-pro3"),
        temperature=0.0,
    )

    norm = state["normalized_input"]
    required = norm["required_ingredients"]
    expiring = norm["expiring_ingredients"]
    owned = set(
        norm["ingredients"] + required + expiring
        + norm["sauces"] + norm["extra_ingredients"]
    )

    candidates = state["validated_recipes"]
    all_recipes = []
    for category, items in candidates.items():
        for recipe in items:
            all_recipes.append({"category": category, **recipe})

    if not all_recipes:
        return _append_log({**state, "final_recipes": candidates}, "최종 추천 선정 완료")

    prompt = f"""
너는 레시피 최종 선정 Agent다.
검증된 레시피 후보 중에서 카테고리별로 최대 {RECIPES_PER_CATEGORY}개를 선정한다.

선정 기준 (우선순위 순):
1. required_ingredients({json.dumps(required, ensure_ascii=False)})를 사용하는 레시피 우선
2. expiring_ingredients({json.dumps(expiring, ensure_ascii=False)})를 사용하는 레시피 우선
3. missing_ingredients가 적을수록 우선
4. 카테고리 내 레시피 간 중복 재료가 적어 다양성이 높을수록 우선

보유 재료: {json.dumps(list(owned), ensure_ascii=False)}
레시피 후보:
{json.dumps(all_recipes, ensure_ascii=False, indent=2)}

반드시 아래 JSON 객체만 출력하고 설명을 붙이지 마라.
카테고리별로 선정된 레시피 이름 목록을 반환한다.
{{
  "category_key": ["선정된 레시피명1", "선정된 레시피명2"]
}}
존재하는 카테고리 키만 포함한다.
""".strip()

    retry_count = state.get("retry_count", 0)

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        selected_names = _parse_json_object(response.content)
        if not isinstance(selected_names, dict):
            raise ValueError("unexpected format")
    except Exception:
        return _append_log({**state, "final_recipes": candidates, "retry_count": retry_count}, "최종 추천 선정 완료")

    final: dict[str, list[dict[str, Any]]] = {}
    for category, items in candidates.items():
        names = selected_names.get(category, [])
        if not isinstance(names, list) or not names:
            final[category] = items[:RECIPES_PER_CATEGORY]
            continue
        ordered = [r for name in names for r in items if r["name"] == name]
        selected_set = {r["name"] for r in ordered}
        fallback = [r for r in items if r["name"] not in selected_set]
        final[category] = (ordered + fallback)[:RECIPES_PER_CATEGORY]

    has_recipes = any(final.get(cat) for cat in final)
    new_retry_count = retry_count + 1 if not has_recipes else retry_count
    return _append_log({**state, "final_recipes": final, "retry_count": new_retry_count}, "최종 추천 선정 완료")


def _parse_verdict_list(text: str, recipes: list[dict[str, Any]]) -> list[str]:
    try:
        parsed = _parse_json_object(text)
        if isinstance(parsed, list):
            return [
                str(item.get("verdict", "valid")).lower()
                if isinstance(item, dict) else "valid"
                for item in parsed
            ]
    except Exception:
        pass
    return ["valid"] * len(recipes)


def _normalize_recipe(item: dict[str, Any], owned: set[str]) -> dict[str, Any]:
    recipe = {**RECIPE_FIELDS, **item}
    recipe["name"] = _clean_recipe_name(recipe["name"])
    recipe["difficulty"] = _clamp_int(recipe.get("difficulty"), 1, 5, 1)
    recipe["time"] = str(recipe.get("time") or "20분").strip()
    recipe["summary"] = str(recipe.get("summary") or recipe["name"]).strip()
    recipe["ingredients"], extracted_amounts = _normalize_recipe_ingredients(
        recipe.get("ingredients", []),
        owned,
    )
    recipe["ingredient_amounts"] = {
        **extracted_amounts,
        **_normalize_amounts(recipe.get("ingredient_amounts", {}), recipe["ingredients"], owned),
    }
    recipe["missing_ingredients"] = _normalize_missing_ingredients(
        recipe.get("missing_ingredients", []),
        recipe["ingredients"],
        owned,
    )
    recipe["steps"] = _normalize_steps(recipe.get("steps", []))

    if not recipe["missing_ingredients"]:
        recipe["missing_ingredients"] = [name for name in recipe["ingredients"] if name not in owned]
    if not recipe["youtube_query"]:
        core = " ".join(recipe["ingredients"][:3])
        recipe["youtube_query"] = f"{recipe['name']} {core} 레시피".strip()

    return recipe


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
    return _recipe_text_contains(recipe, "전자레인지")


def _recipe_text_contains(recipe: dict[str, Any], keyword: str) -> bool:
    text = " ".join(
        [
            str(recipe.get("name", "")),
            str(recipe.get("summary", "")),
            *[str(step) for step in recipe.get("steps", [])],
        ]
    )
    return keyword in text


def _active_recipe_categories(normalized_input: dict[str, list[str]]) -> list[str]:
    tools = set(normalized_input.get("tools", []))
    active = []
    for key, meta in RECIPE_CATEGORIES.items():
        required_tool = meta.get("required_tool")
        if required_tool and required_tool not in tools:
            continue
        active.append(key)
    return active


def _select_recipe_categories(active_categories: list[str]) -> list[str]:
    if len(active_categories) <= 3:
        return active_categories

    return random.sample(active_categories, 3)


def _selected_recipe_categories(state: RecipeState) -> list[str]:
    category_meta = state.get("category_meta", {})
    if category_meta:
        return [key for key in category_meta if key in RECIPE_CATEGORIES]
    return _active_recipe_categories(state["normalized_input"])


def _tag_recipe_category(recipe: dict[str, Any], category: str) -> dict[str, Any]:
    label = RECIPE_CATEGORIES.get(category, {}).get("label", category)
    return {**recipe, "category": category, "category_label": label}


def _append_log(state: RecipeState, message: str) -> RecipeState:
    logs = list(state.get("logs", []))
    logs.append(message)
    print(f"[recipe_agent] {message}", flush=True)
    return {**state, "logs": logs}


def _dedupe_recipes(recipes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    seen = set()
    for recipe in recipes:
        normalized_name = _normalize_recipe_name(recipe["name"])
        if normalized_name in seen:
            continue
        result.append(recipe)
        seen.add(normalized_name)
    return result


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


def _normalize_recipe_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).strip())


def _clean_recipe_name(name: Any) -> str:
    text = str(name).strip()
    text = re.sub(r"\s*\((?:다시|중복|전자레인지|초간단|간단)\)\s*$", "", text)
    return _normalize_recipe_name(text)


def _system_prompt(normalized_input: dict[str, list[str]], selected_categories: list[str]) -> str:
    category_lines = "\n".join(
        f'- "{key}": {RECIPE_CATEGORIES[key]["label"]}'
        for key in selected_categories
    )
    output_keys = ",\n".join(f'  "{key}": []' for key in selected_categories)
    return f"""
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
- fine_dining 카테고리는 새로운 퓨전 요리가 아니라 실제 가능한 기본 요리에 플레이팅과 표현만 조금 고급스럽게 적용한다.
- top_recipes와 각 카테고리 안에서 같은 메뉴를 이름만 바꿔 반복하지 않는다.
- 알레르기, 질병, 식단 제한, 건강 효능을 단정하지 않는다.
- 실제 YouTube 링크 대신 youtube_query 검색어만 만든다.

활성 카테고리:
{category_lines}

반드시 아래 JSON 객체만 출력하고, 코드블록이나 설명 문장을 붙이지 마라.
{{
  "top_recipes": [
    {{
      "name": "요리명",
      "difficulty": 1,
      "time": "15분",
      "summary": "짧은 설명",
      "ingredients": ["필요 재료"],
      "ingredient_amounts": {{"필요 재료": "1개"}},
      "missing_ingredients": ["없는 재료"],
      "steps": ["1단계", "2단계", "3단계"],
      "youtube_query": "요리명 핵심재료 레시피"
    }}
  ],
{output_keys}
}}

top_recipes는 정확히 5개를 생성한다.
각 활성 카테고리는 가능한 경우 정확히 3개를 생성한다.
각 카테고리 배열의 레시피 객체 형식은 top_recipes의 객체 형식과 동일하다.
특정 카테고리에 자연스러운 레시피가 없으면 빈 배열로 둔다.
""".strip()


def _json_repair_prompt() -> str:
    return f"""
너는 깨진 JSON을 고치는 변환기다.
입력된 텍스트의 의미와 필드 값은 유지하고 JSON 문법만 고쳐라.
출력은 반드시 파싱 가능한 JSON 객체 하나만 반환한다.
코드블록, 설명, 사과, 주석은 절대 붙이지 마라.
최상위 키는 top_recipes와 다음 카테고리 키만 사용한다: {", ".join(RECIPE_CATEGORIES.keys())}
""".strip()


def _parse_json_object(text: str) -> Any:
    text = _extract_json_text(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    repaired = _repair_common_json_errors(text)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as exc:
        raise RecipeGenerationError(f"레시피 생성 결과 JSON 문법을 복구하지 못했습니다: {exc}") from exc


def _extract_json_text(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1].strip()
    raise RecipeGenerationError("JSON 객체를 찾지 못했습니다.")


def _repair_common_json_errors(text: str) -> str:
    repaired = text.strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"}\s*{", "},{", repaired)
    repaired = re.sub(r"]\s*\"", "],\"", repaired)
    repaired = re.sub(r"}\s*\"", "},\"", repaired)
    return repaired


def _unique(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    result = []
    seen = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _normalize_recipe_ingredients(values: Any, owned: set[str]) -> tuple[list[str], dict[str, str]]:
    ingredients = []
    amounts = {}
    for value in _unique(values):
        name, amount = _split_ingredient_amount(value, owned)
        if name and name not in ingredients:
            ingredients.append(name)
        if name and amount and name not in amounts:
            amounts[name] = amount
    return ingredients, amounts


def _normalize_amounts(values: Any, ingredients: list[str], owned: set[str]) -> dict[str, str]:
    if not isinstance(values, dict):
        return {}

    result = {}
    known_names = set(ingredients) | owned
    for raw_name, raw_amount in values.items():
        name, _ = _split_ingredient_amount(str(raw_name).strip(), known_names)
        if name not in ingredients:
            continue
        amount = str(raw_amount).strip()
        if amount:
            result[name] = amount
    return result


def _normalize_missing_ingredients(values: Any, ingredients: list[str], owned: set[str]) -> list[str]:
    normalized = []
    for value in _unique(values):
        name, _ = _split_ingredient_amount(value, set(ingredients) | owned)
        if name and name not in owned and name not in normalized:
            normalized.append(name)
    return normalized


def _normalize_steps(values: Any) -> list[str]:
    steps = []
    for value in _unique(values):
        step = _strip_step_number(value)
        if step and step not in steps:
            steps.append(step)
    return steps


def _strip_step_number(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^\s*\d+\s*[.)]\s*", "", text)
    text = re.sub(r"^\s*(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째|여덟째|아홉째|열째)\s*[,.)]?\s*", "", text)
    return text.strip()


def _split_ingredient_amount(value: str, known_names: set[str]) -> tuple[str, str]:
    text = value.strip()
    if not text:
        return "", ""

    text = _strip_ingredient_prep_prefix(text)

    if text in known_names:
        return text, ""

    for name in sorted(known_names, key=len, reverse=True):
        if text.startswith(name):
            amount = text[len(name) :].strip()
            if amount:
                return name, amount

    match = re.match(
        r"^(.+?)\s+((?:약\s*)?(?:\d+(?:/\d+)?(?:\.\d+)?|적당량).*)$",
        text,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()

    return text, ""


def _strip_ingredient_prep_prefix(value: str) -> str:
    return re.sub(r"^(?:다진|채\s*썬|썬|볶은|삶은|데친|으깬)\s+", "", value.strip())


def _match_ingredient_name(value: str, ingredients: list[str]) -> str:
    name, _ = _split_ingredient_amount(value, set(ingredients))
    return name


def _clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))
