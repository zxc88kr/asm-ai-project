import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from views import step1, step2, step3, home

st.set_page_config(
    page_title="냉장고털이",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import base64, pathlib
logo_bytes = pathlib.Path("static/logo.png").read_bytes()
logo_b64 = base64.b64encode(logo_bytes).decode()

st.markdown(
    f"""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"] {{
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 16px;
    }}
    /* Streamlit 기본 툴바 숨기기 */
    header[data-testid="stHeader"] {{ display: none !important; }}
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}
    /* 전체 여백 줄이기 */
    .block-container {{ padding-top: 1.5rem !important; padding-bottom: 2rem !important; }}
    /* 헤더 컬럼 수직 중앙 정렬 */
    div[data-testid="stColumns"] > div[data-testid="stColumn"] {{
        display: flex;
        align-items: center;
    }}
    /* 공통 타이틀 */
    h1 {{ font-size: 2rem !important; font-weight: 800 !important; }}
    h2 {{ font-size: 1.5rem !important; font-weight: 700 !important; }}
    h3 {{ font-size: 1.2rem !important; font-weight: 700 !important; }}
    p, li, .stMarkdown {{ font-size: 1.05rem !important; }}
    label {{ font-size: 1.05rem !important; }}
    /* 버튼 터치 영역 */
    button {{
        min-height: 44px !important;
        font-size: 1rem !important;
    }}
    /* 모바일 최적화 */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}
        div[data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
        }}
        /* 기본 2열 */
        div[data-testid="stColumn"] {{
            flex: 1 1 45% !important;
            min-width: 45% !important;
        }}
        h1 {{ font-size: 1.5rem !important; }}
        h2 {{ font-size: 1.3rem !important; }}
        h3 {{ font-size: 1.1rem !important; }}
    }}
    /* iPhone XR (414px) 기준 */
    @media (max-width: 480px) {{
        /* 재료 그리드: 3열 유지 */
        div[data-testid="stColumn"] {{
            flex: 1 1 30% !important;
            min-width: 30% !important;
        }}
        button {{
            min-height: 44px !important;
            font-size: 0.85rem !important;
            padding: 0 4px !important;
        }}
        h1 {{ font-size: 1.3rem !important; }}
        /* 홈 스텝 카드 패딩 축소 */
        div[style*="padding:32px"] {{
            padding: 16px 8px !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 세션 상태 초기화
defaults = {
    "step": 0,
    "ingredients": [],
    "sauces": [],
    "tools": [],
    "extra_ingredients": [],
    "recipes": {},
    "top_recipes": [],
    "recipe_category_meta": {},
    "recipe_logs": [],
    "visible_recipe_categories": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

STEPS = [home, step1, step2, step3]

# 로고 클릭 시 홈 이동
if st.query_params.get("reset") == "1":
    st.query_params.clear()
    for k in [
        "ingredients",
        "sauces",
        "tools",
        "extra_ingredients",
        "recipes",
        "top_recipes",
        "recipe_category_meta",
        "recipe_logs",
        "visible_recipe_categories",
    ]:
        st.session_state[k] = {} if k in ["recipes", "recipe_category_meta"] else []
    st.session_state.step = 0
    st.rerun()

# 상단 헤더
col_logo, col_progress = st.columns([1, 5])
with col_logo:
    st.markdown(
        f'<a href="?reset=1" target="_self" style="display:inline-block">'
        f'<img src="data:image/png;base64,{logo_b64}" style="height:80px;cursor:pointer;object-fit:contain">'
        f'</a>',
        unsafe_allow_html=True,
    )

with col_progress:
    if st.session_state.step > 0:
        labels = ["재료 입력", "재료 보강", "레시피 결과"]
        current = st.session_state.step

        steps_html = '<div style="display:flex;align-items:center;justify-content:flex-end;height:110px;padding-right:24px">'
        for i, label in enumerate(labels):
            step_num = i + 1
            if step_num < current:
                circle_style = "background:#3b82f6;color:#fff;border:2px solid #3b82f6"
                label_style = "color:#3b82f6;font-weight:600"
                icon = "✓"
            elif step_num == current:
                circle_style = "background:#1d4ed8;color:#fff;border:2px solid #1d4ed8"
                label_style = "color:#1d4ed8;font-weight:700"
                icon = str(step_num)
            else:
                circle_style = "background:#fff;color:#9ca3af;border:2px solid #d1d5db"
                label_style = "color:#9ca3af;font-weight:400"
                icon = str(step_num)

            steps_html += f"""
            <div style="display:flex;flex-direction:column;align-items:center;min-width:48px">
                <div style="width:28px;height:28px;border-radius:50%;{circle_style};
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.85rem;font-weight:700;margin-bottom:4px">{icon}</div>
                <div style="font-size:0.75rem;{label_style};white-space:nowrap">{label}</div>
            </div>
            """
            if i < len(labels) - 1:
                line_color = "#3b82f6" if step_num < current else "#d1d5db"
                steps_html += f'<div style="width:20px;height:2px;background:{line_color};margin:0 2px;margin-bottom:18px;flex-shrink:0"></div>'

        steps_html += '</div>'
        st.markdown(steps_html, unsafe_allow_html=True)

st.markdown("<hr style='margin:4px 0 24px;border-color:#e5e7eb'>", unsafe_allow_html=True)

STEPS[st.session_state.step].render()
