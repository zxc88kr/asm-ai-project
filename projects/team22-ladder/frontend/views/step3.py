import streamlit as st
from html import escape
from urllib.parse import quote_plus

DIFFICULTY_LABEL = {1: "매우 쉬움", 2: "쉬움", 3: "보통", 4: "어려움", 5: "매우 어려움"}


def render():
    st.title("🍳 레시피 추천")
    st.markdown("<hr style='margin:4px 0 20px;border-color:#e5e7eb'>", unsafe_allow_html=True)

    recipes = st.session_state.get("recipes", {})

    if not recipes:
        st.warning("아직 레시피가 없어요. 재료 보강 단계에서 레시피를 생성해주세요.")
        return

    st.caption("계량 기준: 종이컵 1컵=180ml · 밥숟가락 1큰술=15ml · 티스푼 1작은술=5ml")

    owned = {i["name"] for i in st.session_state.get("ingredients", [])}
    owned |= set(st.session_state.get("sauces", []))
    owned |= set(st.session_state.get("extra_ingredients", []))

    st.markdown("## 초보 요리사 추천")
    beginner = recipes.get("beginner", [])
    if beginner:
        _render_recipe_cards(beginner, owned)
    else:
        st.info("재료가 부족해요. 더 많은 재료를 추가해보세요.")

    st.markdown("---")

    st.markdown("## 전자레인지 간편 요리")
    microwave = recipes.get("microwave", [])
    if microwave:
        _render_recipe_cards(microwave, owned)
    else:
        st.info("재료가 부족해요. 더 많은 재료를 추가해보세요.")

    st.markdown("---")
    col_back, col_reset = st.columns([1, 1])
    if col_back.button("← 재료 보강으로"):
        st.session_state.step = 2
        st.rerun()
    if col_reset.button("처음부터 다시"):
        for k in ["ingredients", "sauces", "tools", "extra_ingredients", "recipes"]:
            st.session_state[k] = [] if k != "recipes" else {}
        st.session_state.step = 0
        st.rerun()


def _render_recipe_cards(recipe_list: list, owned: set):
    cols = st.columns(min(len(recipe_list), 3))
    for i, recipe in enumerate(recipe_list[:3]):
        with cols[i]:
            difficulty = recipe.get("difficulty", 1)
            raw_ingredients = recipe.get("ingredients", [])
            ingredients, extracted_amounts = _normalize_ingredient_display(raw_ingredients, owned)
            ingredient_amounts = {
                **extracted_amounts,
                **_normalize_amount_display(recipe.get("ingredient_amounts", {}), ingredients, owned),
            }
            explicit_missing = recipe.get("missing_ingredients", [])
            have = [r for r in ingredients if r in owned]
            missing = _normalize_missing_display(explicit_missing, ingredients, owned)
            if not missing:
                missing = [r for r in ingredients if r not in owned]

            with st.container(border=True):
                st.markdown(f"### {recipe.get('name', '이름 없는 레시피')}")
                st.markdown(
                    f"난이도: **{DIFFICULTY_LABEL.get(difficulty, '쉬움')}** &nbsp;|&nbsp; "
                    f"시간: {recipe.get('time', '20분')}"
                )
                st.markdown(f"_{recipe.get('summary', '')}_")

                st.markdown("**재료**")
                if have:
                    st.markdown(" ".join(f"`{_format_ingredient(r, ingredient_amounts)}`" for r in have))
                if missing:
                    st.markdown(
                        " ".join(
                            f'<span style="background:#dbeafe;padding:2px 6px;border-radius:4px;font-size:0.85em;color:#1d4ed8">{escape(_format_ingredient(r, ingredient_amounts))}</span>'
                            for r in missing
                        ),
                        unsafe_allow_html=True,
                    )
                    st.caption(f"없는 재료: {', '.join(missing)}")

                steps = recipe.get("steps", [])
                if steps:
                    with st.expander("조리 순서"):
                        for idx, step in enumerate(steps, start=1):
                            st.markdown(f"{idx}. {_strip_step_number(str(step))}")

                youtube_query = recipe.get("youtube_query")
                if youtube_query:
                    url = f"https://www.youtube.com/results?search_query={quote_plus(youtube_query)}"
                    st.markdown(
                        f"""
                        <a href="{escape(url)}" target="_blank" rel="noopener noreferrer"
                           style="display:block;text-align:center;text-decoration:none;
                                  background:#ffffff;color:#262730;border:1px solid rgba(49,51,63,0.2);
                                  border-radius:0.5rem;padding:0.55rem 0.75rem;font-weight:600">
                            영상 검색
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )


def _format_ingredient(name: str, ingredient_amounts: dict) -> str:
    amount = ingredient_amounts.get(name) if isinstance(ingredient_amounts, dict) else None
    if not amount:
        return name
    return f"{name} {amount}"


def _strip_step_number(value: str) -> str:
    import re

    text = value.strip()
    text = re.sub(r"^\s*\d+\s*[.)]\s*", "", text)
    text = re.sub(r"^\s*(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째|여덟째|아홉째|열째)\s*[,.)]?\s*", "", text)
    return text.strip()


def _normalize_missing_display(values: list, ingredients: list, owned: set) -> list[str]:
    normalized = []
    for value in values or []:
        name, _ = _split_ingredient_amount(str(value).strip(), set(ingredients) | owned)
        if name and name not in owned and name not in normalized:
            normalized.append(name)
    return normalized


def _match_ingredient_name(value: str, ingredients: list) -> str:
    name, _ = _split_ingredient_amount(value, set(ingredients))
    return name


def _normalize_ingredient_display(values: list, owned: set) -> tuple[list[str], dict[str, str]]:
    ingredients = []
    amounts = {}
    for value in values or []:
        name, amount = _split_ingredient_amount(str(value).strip(), owned)
        if name and name not in ingredients:
            ingredients.append(name)
        if name and amount and name not in amounts:
            amounts[name] = amount
    return ingredients, amounts


def _normalize_amount_display(values: dict, ingredients: list, owned: set) -> dict[str, str]:
    if not isinstance(values, dict):
        return {}

    result = {}
    known_names = set(ingredients) | owned
    for raw_name, raw_amount in values.items():
        name, _ = _split_ingredient_amount(str(raw_name).strip(), known_names)
        if name in ingredients:
            amount = str(raw_amount).strip()
            if amount:
                result[name] = amount
    return result


def _split_ingredient_amount(value: str, known_names: set) -> tuple[str, str]:
    text = value.strip()
    if not text:
        return "", ""
    if text in known_names:
        return text, ""
    for name in sorted(known_names, key=len, reverse=True):
        if text.startswith(name):
            amount = text[len(name):].strip()
            if amount:
                return name, amount
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and (parts[1][0].isdigit() or parts[1].startswith("적당량")):
        return parts[0], parts[1]
    return text, ""
