import json
import re
from typing import Any


RECIPE_FIELDS: dict[str, Any] = {
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


def _parse_json_object(text: str, error_class: type[Exception] = ValueError) -> Any:
    text = _extract_json_text(text, error_class)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    repaired = _repair_common_json_errors(text)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as exc:
        raise error_class(f"레시피 생성 결과 JSON 문법을 복구하지 못했습니다: {exc}") from exc


def _extract_json_text(text: str, error_class: type[Exception] = ValueError) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1].strip()
    raise error_class("JSON 객체를 찾지 못했습니다.")


def _repair_common_json_errors(text: str) -> str:
    repaired = text.strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"}\s*{", "},{", repaired)
    repaired = re.sub(r"]\s*\"", "],\"", repaired)
    repaired = re.sub(r"}\s*\"", "},\"", repaired)
    return repaired


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


def _normalize_recipe_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).strip())


def _clean_recipe_name(name: Any) -> str:
    text = str(name).strip()
    text = re.sub(r"\s*\((?:다시|중복|전자레인지|초간단|간단)\)\s*$", "", text)
    return _normalize_recipe_name(text)


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
