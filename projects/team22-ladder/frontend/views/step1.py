import streamlit as st
import requests
import os
from openai import OpenAI

MOCK_INGREDIENTS_FROM_IMAGE = ["김치", "두부", "콩나물", "돼지고기", "달걀", "대파"]


@st.cache_data(show_spinner=False)
def translate_to_english(name: str) -> str:
    key = os.getenv("UPSTAGE_API_KEY", "")
    if not key:
        return name
    try:
        client = OpenAI(api_key=key, base_url="https://api.upstage.ai/v1")
        res = client.chat.completions.create(
            model="solar-mini",
            messages=[
                {"role": "system", "content": (
                    "Convert a Korean food ingredient name into a short English phrase "
                    "for searching stock photos on Unsplash. "
                    "Show the raw ingredient itself, not a cooked dish or a live animal. "
                    "Use internationally recognizable English terms that are commonly photographed. "
                    "For Korean-specific ingredients, use a descriptive Western equivalent. "
                    "Examples: 돼지고기 → raw pork slices, 두부 → fresh tofu block, 달걀 → fresh eggs, "
                    "김치 → fermented cabbage, 대파 → green onion, 된장 → soybean paste, 고추장 → red chili paste. "
                    "Reply with only the search phrase, nothing else."
                )},
                {"role": "user", "content": name},
            ],
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return name

INGREDIENT_EMOJI = {
    "김치": "🥬", "두부": "🧊", "콩나물": "🌱", "돼지고기": "🥩", "달걀": "🥚",
    "대파": "🧅", "양파": "🧅", "감자": "🥔", "고구마": "🍠", "당근": "🥕",
    "버섯": "🍄", "시금치": "🥦", "닭고기": "🍗", "소고기": "🥩", "새우": "🍤",
    "오징어": "🦑", "우유": "🥛", "치즈": "🧀", "버터": "🧈",
    "라면": "🍜", "밥": "🍚", "떡": "🍡",
}

STATUS_CONFIG = {
    "normal":   {"label": "",             "border": "#e2e8f0"},
    "required": {"label": "필수",         "border": "#ef4444"},
    "expiring": {"label": "유통기한임박", "border": "#f97316"},
}


def get_emoji(name: str) -> str:
    return INGREDIENT_EMOJI.get(name, "🥗")


@st.cache_data(show_spinner=False)
def fetch_unsplash_image(query: str) -> str | None:
    key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return None
    search_query = translate_to_english(query)
    try:
        res = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": search_query, "per_page": 1, "orientation": "squarish"},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=3,
        )
        data = res.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["small"]
    except Exception:
        pass
    return None


def render():
    st.title("재료 입력")
    st.caption("냉장고 속 재료를 추가하고, 필수 재료와 유통기한 임박 재료를 표시해보세요.")
    st.markdown("---")

    tab_image, tab_text = st.tabs(["사진 업로드", "직접 입력"])

    with tab_image:
        uploaded_files = st.file_uploader(
            "냉장고 사진 업로드 (여러 장 가능)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            img_cols = st.columns(min(len(uploaded_files), 4))
            for i, f in enumerate(uploaded_files):
                img_cols[i % 4].image(f, use_container_width=True)
            if st.button("재료 분석하기", type="primary"):
                with st.spinner("재료를 분석하는 중..."):
                    _add_ingredients(MOCK_INGREDIENTS_FROM_IMAGE)
                st.rerun()

    with tab_text:
        with st.form("single_form", clear_on_submit=True):
            col_in, col_btn = st.columns([5, 1])
            single_input = col_in.text_input(
                "", placeholder="재료 이름 입력 (예: 김치)", label_visibility="collapsed"
            )
            submitted = col_btn.form_submit_button("추가", type="primary")
        if submitted and single_input.strip():
            _add_ingredients([single_input.strip()])
            st.rerun()

        st.caption("여러 개 한번에:")
        with st.form("bulk_form", clear_on_submit=True):
            bulk = st.text_area("", placeholder="김치\n두부\n돼지고기", height=90, label_visibility="collapsed")
            bulk_submitted = st.form_submit_button("한번에 추가", type="primary", use_container_width=True)
        if bulk_submitted:
            items = [i.strip() for i in bulk.splitlines() if i.strip()]
            if items:
                _add_ingredients(items)
                st.rerun()

    st.markdown("---")

    if not st.session_state.ingredients:
        st.info("위에서 재료를 추가하면 목록이 채워져요.")
        return

    total = len(st.session_state.ingredients)
    req = sum(1 for i in st.session_state.ingredients if i["status"] == "required")
    exp = sum(1 for i in st.session_state.ingredients if i["status"] == "expiring")

    summary = f"재료 목록 &nbsp; <span style='font-size:0.85em;color:#6b7280'>총 {total}개</span>"
    if req:
        summary += f" &nbsp; <span style='color:#ef4444;font-size:0.85em'>필수 {req}개</span>"
    if exp:
        summary += f" &nbsp; <span style='color:#f97316;font-size:0.85em'>유통기한임박 {exp}개</span>"
    st.markdown(f"### {summary}", unsafe_allow_html=True)

    _render_ingredient_grid()

    st.markdown("---")
    col_reset, col_next = st.columns([1, 3])
    if col_reset.button("전체 초기화"):
        st.session_state.ingredients = []
        st.rerun()
    if col_next.button("다음 단계 → 재료 보강", type="primary", use_container_width=True):
        st.session_state.step = 2
        st.rerun()


def _render_ingredient_grid():
    ingredients = st.session_state.ingredients
    order = {"required": 0, "expiring": 1, "normal": 2}
    ordered = sorted(ingredients, key=lambda x: order[x["status"]])

    cols_per_row = 4
    for row_start in range(0, len(ordered), cols_per_row):
        row_items = ordered[row_start: row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col_idx, item in enumerate(row_items):
            with cols[col_idx]:
                cfg = STATUS_CONFIG[item["status"]]
                emoji = get_emoji(item["name"])
                img_url = fetch_unsplash_image(item["name"])

                with st.container(border=True):
                    if cfg["label"]:
                        st.markdown(
                            f"<div style='text-align:right;font-size:0.72em;color:{cfg['border']};margin-bottom:2px'>{cfg['label']}</div>",
                            unsafe_allow_html=True,
                        )

                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.markdown(
                            f"<div style='text-align:center;font-size:2em;padding:4px 0'>{emoji}</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"<div style='text-align:center;font-weight:600;font-size:0.9em;margin-bottom:6px'>{item['name']}</div>",
                        unsafe_allow_html=True,
                    )

                    b1, b2, b3 = st.columns(3)
                    is_req = item["status"] == "required"
                    is_exp = item["status"] == "expiring"

                    if b1.button("필수 ✓" if is_req else "필수", key=f"req_{item['name']}", use_container_width=True):
                        item["status"] = "normal" if is_req else "required"
                        st.rerun()
                    if b2.button("임박 ✓" if is_exp else "유통기한임박", key=f"exp_{item['name']}", use_container_width=True):
                        item["status"] = "normal" if is_exp else "expiring"
                        st.rerun()
                    if b3.button("삭제", key=f"del_{item['name']}", use_container_width=True):
                        st.session_state.ingredients = [
                            i for i in st.session_state.ingredients if i["name"] != item["name"]
                        ]
                        st.rerun()


def _add_ingredients(names: list[str]):
    existing = {i["name"] for i in st.session_state.ingredients}
    for name in names:
        if name not in existing:
            st.session_state.ingredients.append({"name": name, "status": "normal"})
