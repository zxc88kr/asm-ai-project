import streamlit as st
import os
import requests

SAUCE_OPTIONS = ["소금", "간장", "식용유", "고추장", "된장", "참기름", "굴소스", "설탕", "식초", "기타"]
TOOL_OPTIONS = ["전자레인지", "가스레인지", "에어프라이어", "오븐", "냄비", "프라이팬", "기타"]


def render():
    st.title("🧂 재료 보강")
    st.markdown(
        "<p style='color:#6b7280;font-size:1.05rem;margin-top:-8px'>"
        "기본 소스와 조리도구, 추가 재료를 선택해주세요.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:12px 0 20px;border-color:#e5e7eb'>", unsafe_allow_html=True)

    # 소스
    st.markdown("### 보유 소스")
    st.caption("보유한 소스/양념을 선택하세요.")
    sauce_cols = st.columns(5)
    selected_sauces = []
    for i, sauce in enumerate(SAUCE_OPTIONS):
        checked = sauce in st.session_state.sauces
        if sauce_cols[i % 5].checkbox(sauce, value=checked, key=f"sauce_{sauce}"):
            selected_sauces.append(sauce)
    st.session_state.sauces = selected_sauces

    st.markdown("---")

    # 조리도구
    st.markdown("### 사용 가능한 조리도구")
    st.caption("사용할 수 있는 조리도구를 선택하세요.")
    tool_cols = st.columns(4)
    selected_tools = []
    for i, tool in enumerate(TOOL_OPTIONS):
        checked = tool in st.session_state.tools
        if tool_cols[i % 4].checkbox(tool, value=checked, key=f"tool_{tool}"):
            selected_tools.append(tool)
    st.session_state.tools = selected_tools

    st.markdown("---")

    # 추가 재료
    st.markdown("### 추가 재료")
    st.caption("냉장고 밖에 있는 재료 (ex: 라면 사리, 밥 등)를 추가하세요.")
    with st.form("extra_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        extra_input = col_input.text_input(
            "", placeholder="재료명 입력", label_visibility="collapsed"
        )
        extra_submitted = col_btn.form_submit_button("추가", type="primary")
    if extra_submitted and extra_input.strip():
        name = extra_input.strip()
        if name not in st.session_state.extra_ingredients:
            st.session_state.extra_ingredients.append(name)
            st.rerun()

    if st.session_state.extra_ingredients:
        chip_cols = st.columns(6)
        to_remove = None
        for i, name in enumerate(st.session_state.extra_ingredients):
            if chip_cols[i % 6].button(f"✕ {name}", key=f"rm_extra_{name}"):
                to_remove = name
        if to_remove:
            st.session_state.extra_ingredients.remove(to_remove)
            st.rerun()

    st.markdown("---")

    # 최종 재료 미리보기
    st.markdown("### 최종 재료 목록")
    all_ingredients = (
        [i["name"] for i in st.session_state.ingredients]
        + st.session_state.sauces
        + st.session_state.extra_ingredients
    )

    if all_ingredients:
        required = [i["name"] for i in st.session_state.ingredients if i["status"] == "required"]
        expiring = [i["name"] for i in st.session_state.ingredients if i["status"] == "expiring"]
        normal = [i["name"] for i in st.session_state.ingredients if i["status"] == "normal"]

        if required:
            st.markdown("**필수 재료**")
            st.markdown(" · ".join(f"`{n}`" for n in required))
        if expiring:
            st.markdown("**유통기한 임박**")
            st.markdown(" · ".join(f"`{n}`" for n in expiring))
        if normal:
            st.markdown("**재료**")
            st.markdown(" · ".join(f"`{n}`" for n in normal))
        if st.session_state.sauces:
            st.markdown("**소스/양념**")
            st.markdown(" · ".join(f"`{n}`" for n in st.session_state.sauces))
        if st.session_state.extra_ingredients:
            st.markdown("**추가 재료**")
            st.markdown(" · ".join(f"`{n}`" for n in st.session_state.extra_ingredients))
        if st.session_state.tools:
            st.markdown("**조리도구**")
            st.markdown(" · ".join(f"`{n}`" for n in st.session_state.tools))
    else:
        st.warning("재료가 없어요! 재료 입력 단계에서 먼저 재료를 입력해주세요.")

    st.markdown("")
    col_back, col_next = st.columns([1, 3])
    if col_back.button("← 이전"):
        st.session_state.step = 1
        st.rerun()
    if col_next.button("레시피 생성하기", type="primary", use_container_width=True):
        if not all_ingredients:
            st.error("재료를 먼저 입력해주세요!")
        else:
            with st.spinner("레시피를 생성하는 중..."):
                recipes, error = _generate_recipes()
            if error:
                st.error(error)
            else:
                st.session_state.recipes = recipes
                st.session_state.step = 3
                st.rerun()


def _generate_recipes():
    backend_url = os.getenv("API_URL") or os.getenv("BACKEND_URL", "http://localhost:8000")
    backend_url = backend_url.rstrip("/")
    payload = {
        "ingredients": [i["name"] for i in st.session_state.ingredients if i["status"] == "normal"],
        "required_ingredients": [i["name"] for i in st.session_state.ingredients if i["status"] == "required"],
        "expiring_ingredients": [i["name"] for i in st.session_state.ingredients if i["status"] == "expiring"],
        "sauces": st.session_state.sauces,
        "tools": st.session_state.tools,
        "extra_ingredients": st.session_state.extra_ingredients,
    }
    try:
        response = requests.post(f"{backend_url}/recipes/generate", json=payload, timeout=60)
        response.raise_for_status()
        return response.json(), None
    except requests.HTTPError:
        detail = _extract_error_detail(response)
        return None, f"레시피 생성에 실패했습니다. {detail}"
    except requests.RequestException as exc:
        return None, f"Backend API에 연결하지 못했습니다. 서버 실행 상태를 확인해주세요. ({exc})"


def _extract_error_detail(response):
    try:
        data = response.json()
    except ValueError:
        return response.text
    return data.get("detail", str(data))
